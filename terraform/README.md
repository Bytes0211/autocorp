# AutoCorp Data Lake Pipeline - Terraform Infrastructure

This directory contains Terraform Infrastructure as Code (IaC) for deploying the AutoCorp Data Lake Pipeline on AWS.

## Architecture Overview

The infrastructure implements a modern data lakehouse architecture with:
- **S3 Data Lake:** Raw, curated, and logs zones
- **AWS Glue:** Data catalog, crawlers, and ETL jobs
- **AWS DMS:** PostgreSQL to S3 replication with CDC
- **AWS DataSync:** Large CSV file transfers
- **IAM:** Least-privilege service roles
- **Secrets Manager:** Secure credential storage

## Project Structure

```
terraform/
├── main.tf                    # Root module orchestration
├── variables.tf               # Input variables
├── outputs.tf                 # Infrastructure outputs
├── terraform.tfvars           # Default variable values
├── backend.tf                 # Remote state configuration
├── versions.tf                # Provider version constraints
│
├── modules/
│   ├── s3/                    # Data lake storage [READY]
│   ├── iam/                   # Service roles [READY]
│   ├── secrets/               # Secrets Manager [READY]
│   ├── glue/                  # Data catalog & ETL [BASIC]
│   ├── dms/                   # Database replication [TODO]
│   └── datasync/              # File transfers [TODO]
│
└── environments/
    ├── dev.tfvars             # Development config
    ├── staging.tfvars         # Staging config
    └── prod.tfvars            # Production config
```

## Prerequisites

### Required Tools
- Terraform >= 1.5.0
- AWS CLI configured with credentials
- Access to AWS account with permissions to create resources

### AWS Resources (Manual Setup Required)
Before running Terraform, manually create:

1. **Terraform State Backend:**
   ```bash
   # Create S3 bucket for state
   aws s3 mb s3://autocorp-terraform-state-<account-id> --region us-east-1
   aws s3api put-bucket-versioning \
     --bucket autocorp-terraform-state-<account-id> \
     --versioning-configuration Status=Enabled

   # Create DynamoDB table for state locking
   aws dynamodb create-table \
     --table-name autocorp-terraform-locks \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --region us-east-1
   ```

2. **Update `backend.tf`:**
   ```hcl
   bucket = "autocorp-terraform-state-<your-account-id>"
   ```

## Quick Start

### 1. Initialize Terraform
```bash
cd terraform
terraform init
```

### 2. Review the Plan
```bash
terraform plan
```

### 3. Deploy Infrastructure (Dev Environment)
```bash
# Deploy S3, IAM, Secrets, and Glue (foundation)
terraform apply

# After resources are created, set PostgreSQL password
aws secretsmanager put-secret-value \
  --secret-id $(terraform output -raw postgres_secret_arn) \
  --secret-string "your-postgres-password"
```

### 4. Enable DMS (After PostgreSQL Connectivity)
```bash
# Update terraform.tfvars
enable_dms = true
postgres_host = "your-postgres-host"

# Apply changes
terraform apply
```

### 5. Enable DataSync (After Agent Deployment)
```bash
# Deploy DataSync agent on-premises, then:
enable_datasync = true
datasync_agent_arns = ["arn:aws:datasync:us-east-1:123456789012:agent/agent-xxxxx"]

# Apply changes
terraform apply
```

## Module Status

| Module | Status | Description |
|--------|--------|-------------|
| **S3** | ✅ READY | Data lake buckets, lifecycle policies, encryption |
| **IAM** | ✅ READY | Service roles for Glue, DMS, DataSync |
| **Secrets** | ✅ READY | PostgreSQL password storage |
| **Glue** | ⚠️ BASIC | Catalog and crawlers implemented, ETL jobs pending |
| **DMS** | ❌ TODO | Requires implementation after PostgreSQL setup |
| **DataSync** | ❌ TODO | Requires agent deployment first |

## Configuration

### Environment-Specific Overrides

```bash
# Deploy to production
terraform apply -var-file="environments/prod.tfvars"

# Deploy to staging
terraform apply -var-file="environments/staging.tfvars"
```

### Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aws_region` | `us-east-1` | AWS region |
| `environment` | `dev` | Environment (dev/staging/prod) |
| `enable_dms` | `false` | Enable DMS module |
| `enable_datasync` | `false` | Enable DataSync module |
| `s3_lifecycle_days` | `90` | Days before Glacier transition |

## Deployment Phases

### Phase 1: Foundation (Week 1) ✅
**Status:** READY TO DEPLOY

```bash
terraform apply -target=module.s3 -target=module.iam -target=module.secrets
```

**Delivers:**
- S3 data lake with folder structure
- IAM roles for all services
- Secrets Manager for credentials

### Phase 2: Glue Setup (Week 2) ⚠️
**Status:** BASIC IMPLEMENTATION

```bash
terraform apply -target=module.glue
```

**Delivers:**
- Glue Data Catalog
- Crawlers for raw zone
- TODO: ETL jobs with Hudi

### Phase 3: DMS Setup (Week 2-3) ❌
**Status:** REQUIRES IMPLEMENTATION

**Prerequisites:**
- PostgreSQL host accessible from AWS
- Logical replication enabled
- Network connectivity verified

### Phase 4: DataSync Setup (Week 3) ❌
**Status:** REQUIRES AGENT DEPLOYMENT

**Prerequisites:**
- DataSync agent deployed on-premises
- Agent activated and ARN obtained

## Cost Estimation

Expected monthly costs (dev environment):
- **S3:** $5-10 (1-2 TB with lifecycle)
- **Glue Crawlers:** $5-10 (daily runs)
- **Glue ETL:** $15-30 (20 DPU-hours/day)
- **DMS:** $50-80 (t3.medium continuous)
- **DataSync:** $10-20 (100 GB/day)
- **Secrets Manager:** $1
- **Total:** ~$86-151/month

## Security

### Secrets Management
- PostgreSQL password stored in AWS Secrets Manager
- Never commit secrets to Git
- Use IAM roles, not access keys

### Encryption
- S3: SSE-S3 encryption at rest
- Secrets Manager: KMS encryption
- DMS: TLS 1.2+ in transit

### IAM Least Privilege
- Each service has minimum required permissions
- S3 access scoped to specific paths
- CloudTrail audit logging enabled

## Maintenance

### Updating Infrastructure
```bash
# Check for drift
terraform plan

# Apply updates
terraform apply
```

### Destroying Infrastructure
```bash
# Destroy everything (CAUTION!)
terraform destroy

# Destroy specific module
terraform destroy -target=module.glue
```

### State Management
```bash
# View state
terraform state list

# Show specific resource
terraform state show module.s3.aws_s3_bucket.data_lake

# Import existing resource
terraform import module.s3.aws_s3_bucket.data_lake autocorp-datalake-dev
```

## Troubleshooting

### Common Issues

**Issue: Backend initialization fails**
```bash
# Ensure S3 bucket and DynamoDB table exist
aws s3 ls s3://autocorp-terraform-state-<account-id>
aws dynamodb describe-table --table-name autocorp-terraform-locks
```

**Issue: DMS module fails**
```bash
# Verify PostgreSQL connectivity
psql -h <postgres-host> -U scotton -d autocorp
# Enable DMS only after verification
```

**Issue: DataSync module fails**
```bash
# Ensure agent is activated
aws datasync list-agents
# Update datasync_agent_arns in terraform.tfvars
```

## Next Steps

1. ✅ Deploy Phase 1 (S3, IAM, Secrets)
2. ⚠️ Complete Glue ETL jobs with Hudi scripts
3. ❌ Implement DMS module (after PostgreSQL setup)
4. ❌ Implement DataSync module (after agent deployment)
5. ❌ Add Athena resources for querying
6. ❌ Add CloudWatch dashboards and alarms

## References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AutoCorp IAC_FEASIBILITY_ASSESSMENT.md](../IAC_FEASIBILITY_ASSESSMENT.md)
- [AutoCorp developer-approach.md](../developer-approach.md)
- [AWS DMS Best Practices](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html)
- [AWS Glue Developer Guide](https://docs.aws.amazon.com/glue/latest/dg/)

## Support

For questions or issues, refer to:
- IAC_FEASIBILITY_ASSESSMENT.md for architectural decisions
- developer-approach.md for overall project context
- Module-specific README files (coming soon)
