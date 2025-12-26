# AWS DMS Module - Database Replication

This module provisions AWS Database Migration Service (DMS) resources for continuous replication from PostgreSQL to S3.

## Overview

The DMS module creates:
- DMS Replication Instance
- Source Endpoint (PostgreSQL)
- Target Endpoint (S3)
- Replication Tasks (Full Load + CDC)
- VPC infrastructure for DMS networking
- Replication Subnet Group

## Important Prerequisites

### VPC Role Requirement

**CRITICAL:** AWS DMS requires a special VPC service-linked role named `dms-vpc-role` to be created before deploying DMS resources. This role allows DMS to manage VPC networking components.

#### Create the DMS VPC Role

You must create this role **once per AWS account** before deploying this module:

```bash
aws iam create-role \
  --role-name dms-vpc-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "dms.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'

aws iam attach-role-policy \
  --role-name dms-vpc-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonDMSVPCManagementRole
```

**Note:** This is a one-time setup per AWS account. If the role already exists, you'll get an error that can be safely ignored.

#### Check if VPC Role Exists

```bash
aws iam get-role --role-name dms-vpc-role
```

If the role doesn't exist, you'll see an error. Create it using the command above.

### PostgreSQL Configuration

The source PostgreSQL database must be configured for logical replication:

1. **Enable logical replication in postgresql.conf:**
   ```
   wal_level = logical
   max_replication_slots = 10
   max_wal_senders = 10
   ```

2. **Restart PostgreSQL:**
   ```bash
   sudo systemctl restart postgresql
   ```

3. **Verify configuration:**
   ```sql
   SHOW wal_level;  -- Should return 'logical'
   ```

See `docs/dms_postgresql_setup.md` for detailed configuration steps.

## Module Configuration

### Enable DMS in Terraform

By default, DMS is **disabled** to avoid deployment errors when prerequisites aren't met.

Enable DMS by setting in `terraform.tfvars`:

```hcl
enable_dms = true

# PostgreSQL connection details
postgres_host     = "your-postgres-host"
postgres_port     = 5432
postgres_database = "autocorp"
postgres_username = "scotton"
postgres_password = "your-secure-password"  # Or use Secrets Manager
```

### Security Considerations

- Never commit `terraform.tfvars` with passwords to version control
- Use AWS Secrets Manager for production credentials
- Ensure PostgreSQL allows connections from AWS DMS subnet
- Configure security groups to allow DMS → PostgreSQL connectivity

## VPC Architecture

This module creates:
- VPC (10.0.0.0/16)
- 2 Private Subnets (10.0.1.0/24, 10.0.2.0/24)
- Internet Gateway
- NAT Gateway (for S3 access)
- Route Tables
- Security Groups

**Important:** The DMS replication instance runs in the private subnets and requires:
- Outbound internet access (via NAT Gateway) to reach S3
- Inbound access from your PostgreSQL database
- The `dms-vpc-role` to manage these networking components

## Replication Instance

- **Instance Class:** `dms.t3.medium` (default)
- **Storage:** 50 GB (default)
- **Multi-AZ:** Disabled in dev, recommended for production
- **Encryption:** Enabled with default KMS key

## Replication Tasks

### Full Load Task
- Migrates all existing data from PostgreSQL to S3
- One-time execution
- Creates initial Parquet files in `s3://bucket/raw/database/`

### CDC Task
- Continuous replication of changes (INSERT/UPDATE/DELETE)
- <5 minute replication lag target
- Appends change records to S3

## Deployment Steps

1. **Create VPC role (one-time per AWS account):**
   ```bash
   aws iam create-role --role-name dms-vpc-role ...
   aws iam attach-role-policy --role-name dms-vpc-role ...
   ```

2. **Configure PostgreSQL for logical replication**
   - Set `wal_level = logical`
   - Restart PostgreSQL
   - Verify with `SHOW wal_level;`

3. **Set Terraform variables:**
   ```bash
   cd terraform
   # Edit terraform.tfvars
   enable_dms = true
   postgres_host = "your-host"
   postgres_password = "your-password"
   ```

4. **Deploy DMS module:**
   ```bash
   terraform plan -target=module.dms
   terraform apply -target=module.dms
   ```

5. **Start replication tasks:**
   ```bash
   aws dms start-replication-task \
     --replication-task-arn <task-arn> \
     --start-replication-task-type start-replication
   ```

## Monitoring

DMS metrics are available in CloudWatch:
- Replication lag
- Task status
- Data transfer rates
- Error counts

Monitor via:
- CloudWatch Dashboard (autocorp-dev-dashboard)
- AWS DMS Console
- CloudWatch Logs: `/aws/dms/tasks/`

## Troubleshooting

### Error: "The IAM Role arn:aws:iam::ACCOUNT:role/dms-vpc-role is not configured properly"

**Solution:** Create the `dms-vpc-role` as described in Prerequisites section above.

### Error: "Cannot connect to PostgreSQL endpoint"

**Solution:** 
- Verify PostgreSQL security groups allow DMS subnet CIDR
- Check `pg_hba.conf` allows connections from DMS
- Verify PostgreSQL is accessible from DMS VPC

### Error: "Logical replication slot does not exist"

**Solution:**
- Verify `wal_level = logical` in postgresql.conf
- Restart PostgreSQL after config changes
- Check `max_replication_slots` is > 0

## Cost Optimization

DMS costs:
- **Replication Instance:** ~$0.193/hour (dms.t3.medium)
- **Data Transfer:** S3 PUT requests + data transfer
- **Storage:** EBS volume for replication instance

**Development:** Use `dms.t3.micro` for testing (~$0.048/hour)
**Production:** Use `dms.t3.medium` or larger with Multi-AZ

## Cleanup

To remove DMS resources:

```bash
# Stop replication tasks first
aws dms stop-replication-task --replication-task-arn <arn>

# Destroy DMS infrastructure
terraform destroy -target=module.dms

# VPC role persists (shared across account)
```

## References

- [AWS DMS Documentation](https://docs.aws.amazon.com/dms/)
- [PostgreSQL Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html)
- [DMS Best Practices](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html)
- Project documentation: `docs/dms_postgresql_setup.md`

## Module Outputs

- `replication_instance_arn` - DMS replication instance ARN
- `postgres_endpoint_arn` - PostgreSQL source endpoint ARN
- `s3_endpoint_arn` - S3 target endpoint ARN
- `full_load_task_arn` - Full load replication task ARN
- `cdc_task_arn` - CDC replication task ARN
- `vpc_id` - VPC ID created for DMS
