# AWS Infrastructure Sanity Checks

**Project:** AutoCorp Cloud Data Lakehouse  
**Created:** December 16, 2025  
**Purpose:** Quick validation commands to verify AWS infrastructure deployment

---

## Quick Health Check (Run All)

```bash
# Run all checks in sequence
echo "=== S3 Buckets ==="
aws s3 ls | grep autocorp

echo -e "\n=== IAM Roles ==="
aws iam list-roles --query 'Roles[?contains(RoleName, `autocorp`)].RoleName' --output table

echo -e "\n=== Secrets Manager ==="
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `autocorp`)].Name' --output table

echo -e "\n=== Glue Databases ==="
aws glue get-databases --query 'DatabaseList[?contains(Name, `autocorp`)].Name' --output table

echo -e "\n=== Glue Crawlers ==="
aws glue list-crawlers --query 'CrawlerNames[?contains(@, `autocorp`)]' --output table

echo -e "\n=== Glue Jobs ==="
aws glue list-jobs --query 'JobNames[?contains(@, `autocorp`)]' --output table

echo -e "\n=== DMS Replication Instances (if deployed) ==="
aws dms describe-replication-instances --query 'ReplicationInstances[?contains(ReplicationInstanceIdentifier, `autocorp`)].ReplicationInstanceIdentifier' --output table 2>/dev/null || echo "DMS not deployed or not accessible"
```

---

## 1. S3 Buckets

### Check if Data Lake bucket exists
```bash
aws s3 ls | grep autocorp-datalake
```

**Expected Output:**
```
2024-11-XX XX:XX:XX autocorp-datalake-dev
```

### Verify bucket structure
```bash
aws s3 ls s3://autocorp-datalake-dev/
```

**Expected Output:**
```
                           PRE curated/
                           PRE logs/
                           PRE raw/
                           PRE scripts/
```

### Check for Glue scripts
```bash
aws s3 ls s3://autocorp-datalake-dev/scripts/glue/
```

**Expected Output:**
```
2024-XX-XX XX:XX:XX    XXXXX analytics_sales_order_fact_etl.py
2024-XX-XX XX:XX:XX    XXXXX analytics_sales_order_line_items_etl.py
2024-XX-XX XX:XX:XX    XXXXX analytics_service_parts_catalog_etl.py
2024-XX-XX XX:XX:XX    XXXXX auto_parts_etl.py
2024-XX-XX XX:XX:XX    XXXXX customers_etl.py
2024-XX-XX XX:XX:XX    XXXXX sales_order_etl.py
2024-XX-XX XX:XX:XX    XXXXX sales_order_parts_etl.py
2024-XX-XX XX:XX:XX    XXXXX sales_order_services_etl.py
2024-XX-XX XX:XX:XX    XXXXX service_etl.py
2024-XX-XX XX:XX:XX    XXXXX service_parts_etl.py
```

**Status:** ✅ Should have 10 ETL scripts (7 operational + 3 analytics)

### Check Terraform state bucket
```bash
aws s3 ls | grep terraform-state
```

**Expected Output:**
```
2024-11-XX XX:XX:XX autocorp-terraform-state-XXXXXXXXXX
```

---

## 2. IAM Roles

### List all AutoCorp IAM roles
```bash
aws iam list-roles --query 'Roles[?contains(RoleName, `autocorp`)].{Name:RoleName,Created:CreateDate}' --output table
```

**Expected Roles:**
- `autocorp-glue-service-role-dev`
- `autocorp-dms-vpc-role-dev` (if DMS deployed)
- `autocorp-dms-cloudwatch-logs-role-dev` (if DMS deployed)

### Check Glue role policies
```bash
aws iam list-attached-role-policies --role-name autocorp-glue-service-role-dev
```

**Expected Output:**
```
{
    "AttachedPolicies": [
        {
            "PolicyName": "AWSGlueServiceRole",
            "PolicyArn": "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
        }
    ]
}
```

### Check Glue role inline policies
```bash
aws iam list-role-policies --role-name autocorp-glue-service-role-dev
```

**Expected Output:**
```
{
    "PolicyNames": [
        "autocorp-glue-s3-access-dev",
        "autocorp-glue-secrets-access-dev"
    ]
}
```

---

## 3. Secrets Manager

### List AutoCorp secrets
```bash
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `autocorp`)].{Name:Name,LastChanged:LastChangedDate}' --output table
```

**Expected Secrets:**
- `autocorp/dev/postgres/password`

### Verify secret exists (without revealing value)
```bash
aws secretsmanager describe-secret --secret-id autocorp/dev/postgres/password
```

**Expected Output:**
```json
{
    "ARN": "arn:aws:secretsmanager:us-east-1:XXXXXXXXXXXX:secret:autocorp/dev/postgres/password-XXXXXX",
    "Name": "autocorp/dev/postgres/password",
    "Description": "PostgreSQL database password for AutoCorp dev environment",
    "LastChangedDate": "2024-XX-XXTXX:XX:XX.XXXXXX+00:00",
    "VersionIdsToStages": {
        "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx": [
            "AWSCURRENT"
        ]
    },
    "CreatedDate": "2024-XX-XXTXX:XX:XX.XXXXXX+00:00"
}
```

---

## 4. AWS Glue Data Catalog

### List Glue databases
```bash
aws glue get-databases --query 'DatabaseList[?contains(Name, `autocorp`)].{Name:Name,Description:Description}' --output table
```

**Expected Databases:**
- `autocorp_dev`

### Get database details
```bash
aws glue get-database --name autocorp_dev
```

### List tables in database
```bash
aws glue get-tables --database-name autocorp_dev --query 'TableList[].Name' --output table
```

**Expected Tables (after crawlers/ETL run):**
```
|  GetTables  |
+-------------+
|  auto_parts |
|  customers  |
|  sales_order|
|  service    |
|  ...        |
+-------------+
```

### Get specific table schema
```bash
aws glue get-table --database-name autocorp_dev --name sales_order
```

---

## 5. AWS Glue Crawlers

### List all crawlers
```bash
aws glue list-crawlers --query 'CrawlerNames[?contains(@, `autocorp`)]' --output table
```

**Expected Crawlers:**
- `autocorp-raw-database-crawler-dev`
- `autocorp-raw-csv-crawler-dev`

### Get crawler status
```bash
aws glue get-crawler --name autocorp-raw-database-crawler-dev --query 'Crawler.{Name:Name,State:State,LastCrawl:LastCrawl.Status}'
```

**Expected State:** `READY` (when not running)

### Get last crawl metrics
```bash
aws glue get-crawler-metrics --crawler-name-list autocorp-raw-database-crawler-dev
```

---

## 6. AWS Glue ETL Jobs

### List all Glue jobs
```bash
aws glue list-jobs --query 'JobNames[?contains(@, `autocorp`)]' --output table
```

**Expected Jobs (10 total):**

**Operational (7):**
- `autocorp-sales-order-etl-dev`
- `autocorp-customers-etl-dev`
- `autocorp-auto-parts-etl-dev`
- `autocorp-service-etl-dev`
- `autocorp-service-parts-etl-dev`
- `autocorp-sales-order-parts-etl-dev`
- `autocorp-sales-order-services-etl-dev`

**Analytics (3):**
- `autocorp-analytics-sales-order-fact-etl-dev`
- `autocorp-analytics-sales-order-line-items-etl-dev`
- `autocorp-analytics-service-parts-catalog-etl-dev`

### Get job details
```bash
aws glue get-job --job-name autocorp-sales-order-etl-dev
```

### Check recent job runs
```bash
aws glue get-job-runs --job-name autocorp-sales-order-etl-dev --max-results 5 --query 'JobRuns[].{RunId:Id,State:JobRunState,StartedOn:StartedOn,ExecutionTime:ExecutionTime}'
```

**Expected States:** `SUCCEEDED`, `RUNNING`, or `FAILED`

### Get all job run statuses (summary)
```bash
for job in $(aws glue list-jobs --query 'JobNames[?contains(@, `autocorp`)]' --output text); do
  echo "Job: $job"
  aws glue get-job-runs --job-name $job --max-results 1 --query 'JobRuns[0].{State:JobRunState,ExecutionTime:ExecutionTime,StartedOn:StartedOn}' --output table
  echo ""
done
```

---

## 7. DMS (If Deployed)

### List replication instances
```bash
aws dms describe-replication-instances --query 'ReplicationInstances[?contains(ReplicationInstanceIdentifier, `autocorp`)].{ID:ReplicationInstanceIdentifier,Status:ReplicationInstanceStatus,Class:ReplicationInstanceClass}' --output table
```

**Expected Instance:**
- `autocorp-dms-instance-dev` (Status: `available`)

### List endpoints
```bash
aws dms describe-endpoints --query 'Endpoints[?contains(EndpointIdentifier, `autocorp`)].{ID:EndpointIdentifier,Type:EndpointType,Engine:EngineName,Status:Status}' --output table
```

**Expected Endpoints:**
- `autocorp-dms-source-postgres-dev` (Type: `source`, Engine: `postgres`)
- `autocorp-dms-target-s3-dev` (Type: `target`, Engine: `s3`)

### List replication tasks
```bash
aws dms describe-replication-tasks --query 'ReplicationTasks[?contains(ReplicationTaskIdentifier, `autocorp`)].{ID:ReplicationTaskIdentifier,Status:Status,Progress:ReplicationTaskStats.FullLoadProgressPercent}' --output table
```

### Check replication task status
```bash
aws dms describe-replication-tasks --filters Name=replication-task-arn,Values=<task-arn> --query 'ReplicationTasks[0].{Status:Status,CDCLag:ReplicationTaskStats.ElapsedTimeMillis}'
```

---

## 8. CloudWatch Logs

### List Glue job log groups
```bash
aws logs describe-log-groups --query 'logGroups[?contains(logGroupName, `glue`)].logGroupName' --output table
```

**Expected Log Groups:**
- `/aws-glue/jobs/output`
- `/aws-glue/jobs/error`
- `/aws-glue/crawlers`

### Get recent Glue job logs
```bash
aws logs tail /aws-glue/jobs/output --since 1h --filter-pattern "autocorp-sales-order-etl-dev"
```

### Check for errors in last hour
```bash
aws logs tail /aws-glue/jobs/error --since 1h --filter-pattern "autocorp"
```

---

## 9. DynamoDB (Terraform State Lock)

### Check Terraform lock table
```bash
aws dynamodb describe-table --table-name autocorp-terraform-locks
```

**Expected Output:**
```json
{
    "Table": {
        "TableName": "autocorp-terraform-locks",
        "TableStatus": "ACTIVE",
        "KeySchema": [
            {
                "AttributeName": "LockID",
                "KeyType": "HASH"
            }
        ],
        ...
    }
}
```

### List current locks (should be empty unless terraform is running)
```bash
aws dynamodb scan --table-name autocorp-terraform-locks --query 'Items[]'
```

---

## 10. Cost Estimation Check

### Get current month's costs for AutoCorp resources
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=TAG,Key=Project \
  --filter file://<(cat <<EOF
{
  "Tags": {
    "Key": "Project",
    "Values": ["autocorp"]
  }
}
EOF
)
```

### Get service-level breakdown
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

---

## 11. Comprehensive Validation Script

Save this as `validate_aws_infrastructure.sh`:

```bash
#!/bin/bash

# AutoCorp AWS Infrastructure Validation Script
# Version: 1.0
# Date: December 16, 2025

set -e

echo "=================================="
echo "AutoCorp AWS Infrastructure Check"
echo "=================================="
echo "Date: $(date)"
echo "Region: $(aws configure get region)"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_resource() {
  local name=$1
  local command=$2
  local expected=$3
  
  echo -n "Checking $name... "
  if result=$(eval $command 2>/dev/null); then
    if [ -n "$expected" ] && ! echo "$result" | grep -q "$expected"; then
      echo -e "${YELLOW}WARNING${NC}: Resource exists but unexpected output"
      echo "  Expected pattern: $expected"
    else
      echo -e "${GREEN}OK${NC}"
    fi
  else
    echo -e "${RED}FAILED${NC}"
    return 1
  fi
}

# 1. S3 Buckets
echo "=== S3 Buckets ==="
check_resource "Data Lake Bucket" "aws s3 ls | grep autocorp-datalake-dev" "autocorp-datalake-dev"
check_resource "Terraform State Bucket" "aws s3 ls | grep terraform-state" "terraform-state"
check_resource "Glue Scripts" "aws s3 ls s3://autocorp-datalake-dev/scripts/glue/" "etl.py"
echo ""

# 2. IAM Roles
echo "=== IAM Roles ==="
check_resource "Glue Service Role" "aws iam get-role --role-name autocorp-glue-service-role-dev" "autocorp-glue-service-role-dev"
echo ""

# 3. Secrets Manager
echo "=== Secrets Manager ==="
check_resource "PostgreSQL Secret" "aws secretsmanager describe-secret --secret-id autocorp/dev/postgres/password" "autocorp/dev/postgres/password"
echo ""

# 4. Glue Data Catalog
echo "=== Glue Data Catalog ==="
check_resource "Glue Database" "aws glue get-database --name autocorp_dev" "autocorp_dev"
echo ""

# 5. Glue Crawlers
echo "=== Glue Crawlers ==="
check_resource "Raw Database Crawler" "aws glue get-crawler --name autocorp-raw-database-crawler-dev" "autocorp-raw-database-crawler-dev"
check_resource "Raw CSV Crawler" "aws glue get-crawler --name autocorp-raw-csv-crawler-dev" "autocorp-raw-csv-crawler-dev"
echo ""

# 6. Glue Jobs
echo "=== Glue ETL Jobs ==="
jobs=(
  "autocorp-sales-order-etl-dev"
  "autocorp-customers-etl-dev"
  "autocorp-auto-parts-etl-dev"
  "autocorp-service-etl-dev"
  "autocorp-service-parts-etl-dev"
  "autocorp-sales-order-parts-etl-dev"
  "autocorp-sales-order-services-etl-dev"
  "autocorp-analytics-sales-order-fact-etl-dev"
  "autocorp-analytics-sales-order-line-items-etl-dev"
  "autocorp-analytics-service-parts-catalog-etl-dev"
)

for job in "${jobs[@]}"; do
  check_resource "$job" "aws glue get-job --job-name $job" "$job"
done
echo ""

# 7. DynamoDB
echo "=== DynamoDB ==="
check_resource "Terraform Lock Table" "aws dynamodb describe-table --table-name autocorp-terraform-locks" "autocorp-terraform-locks"
echo ""

# 8. DMS (Optional - may not be deployed)
echo "=== DMS (Optional) ==="
if aws dms describe-replication-instances --query 'ReplicationInstances[?contains(ReplicationInstanceIdentifier, `autocorp`)]' --output text 2>/dev/null | grep -q "autocorp"; then
  check_resource "DMS Replication Instance" "aws dms describe-replication-instances --query 'ReplicationInstances[?contains(ReplicationInstanceIdentifier, \`autocorp\`)].ReplicationInstanceIdentifier' --output text" "autocorp"
  echo -e "${GREEN}DMS is deployed${NC}"
else
  echo -e "${YELLOW}DMS not deployed (expected for Phase 3 IaC only)${NC}"
fi
echo ""

echo "=================================="
echo "Validation Complete!"
echo "=================================="
echo ""
echo "Summary:"
echo "- All core infrastructure should show ${GREEN}OK${NC}"
echo "- ${YELLOW}WARNING${NC} indicates resource exists but may need review"
echo "- ${RED}FAILED${NC} indicates missing resource"
echo ""
echo "For detailed logs, check CloudWatch Logs:"
echo "  aws logs tail /aws-glue/jobs/output --since 1h"
```

**Usage:**
```bash
chmod +x validate_aws_infrastructure.sh
./validate_aws_infrastructure.sh
```

---

## 12. Quick Troubleshooting Commands

### Check if Glue job is stuck
```bash
aws glue get-job-runs --job-name autocorp-sales-order-etl-dev --query 'JobRuns[?JobRunState==`RUNNING`]' --output table
```

### Check S3 bucket permissions
```bash
aws s3api get-bucket-policy --bucket autocorp-datalake-dev
aws s3api get-bucket-acl --bucket autocorp-datalake-dev
```

### Test Glue role can access S3
```bash
aws sts assume-role --role-arn $(aws iam get-role --role-name autocorp-glue-service-role-dev --query 'Role.Arn' --output text) --role-session-name test-session
```

### Check Glue job execution errors
```bash
aws glue get-job-runs --job-name autocorp-sales-order-etl-dev --query 'JobRuns[?JobRunState==`FAILED`][0].ErrorMessage'
```

---

## Expected Results Summary

**Phase 1-2 Deployment (Complete):**
- ✅ S3 Data Lake bucket with folder structure
- ✅ S3 Terraform state bucket
- ✅ IAM Glue service role with policies
- ✅ Secrets Manager secret for PostgreSQL
- ✅ Glue Data Catalog database
- ✅ 2 Glue Crawlers
- ✅ 10 Glue ETL jobs (7 operational + 3 analytics)
- ✅ DynamoDB Terraform lock table
- ✅ CloudWatch log groups

**Phase 3 (IaC Ready - Not Deployed):**
- ⏸️ DMS replication instance (Terraform defined, not deployed)
- ⏸️ DMS endpoints (Terraform defined, not deployed)
- ⏸️ DMS replication tasks (Terraform defined, not deployed)
- 📝 DataSync documented (manual deployment guide ready)

**Phase 4 (In Progress):**
- 🟡 Athena workgroups (configuration in progress)
- 🟡 Athena saved queries (to be created)
- 🟡 CloudWatch dashboards (to be created)

---

## Notes

- **Region:** All commands assume `us-east-1`. Update if different.
- **Profile:** Add `--profile <profile-name>` if not using default AWS profile
- **Permissions:** Requires read access to S3, IAM, Secrets Manager, Glue, DMS, CloudWatch, and DynamoDB
- **Cost:** All read-only commands above are free or negligible cost

---

**Document Version:** 1.0  
**Created:** December 16, 2025  
**Author:** scotton  
**Project:** AutoCorp Cloud Data Lakehouse
