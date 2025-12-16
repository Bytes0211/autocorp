# Cost Management & Safe Destruction Guide

**Project:** AutoCorp Cloud Data Lakehouse  
**Created:** December 16, 2025  
**Purpose:** Safely manage AWS costs by selectively destroying/recreating resources

---

## Cost Analysis

### Current Monthly Costs (Phase 1-2 Deployed)

| Service | Resource | Monthly Cost | Can Destroy? |
|---------|----------|--------------|--------------|
| **S3** | Data Lake storage (~1 GB) | ~$0.02 | ❌ NO (contains data) |
| **S3** | Terraform state | ~$0.01 | ❌ NO (infrastructure state) |
| **Glue** | Data Catalog (database + tables) | $0 (free tier) | ✅ YES (can recreate) |
| **Glue** | Crawlers (idle) | $0 | ✅ YES |
| **Glue** | Jobs (not running) | $0 | ✅ YES |
| **IAM** | Roles and policies | $0 | ⚠️ KEEP (needed for recreation) |
| **Secrets Manager** | PostgreSQL password | ~$0.40 | ⚠️ KEEP (needed for DMS) |
| **DynamoDB** | Terraform locks | $0 (free tier) | ❌ NO (needed for Terraform) |
| **CloudWatch** | Logs (~100 MB) | ~$0.50 | ⚠️ OPTIONAL |
| | **TOTAL** | **~$0.93/month** | |

**Key Insight:** Your current infrastructure costs less than $1/month. The main cost would come from:
- Running Glue jobs (~$0.44/DPU-hour when running)
- DMS if deployed (~$125/month for t3.medium running 24/7)

---

## Safe Destruction Strategy

### Option 1: Destroy Glue Resources Only (Recommended)

**What to Destroy:**
- Glue ETL Jobs (no cost when idle)
- Glue Crawlers (no cost when idle)
- Glue Data Catalog tables (free tier)

**What to Keep:**
- S3 buckets (contains your data and scripts)
- IAM roles (needed to recreate resources)
- Secrets Manager (needed for future deployments)
- Terraform state (needed to recreate infrastructure)
- DynamoDB locks (needed for Terraform)

**Cost Savings:** $0 (Glue resources don't cost when idle)  
**Recreation Time:** 5-10 minutes with `terraform apply`

**Commands:**
```bash
cd terraform

# Preview what will be destroyed
terraform destroy -target=module.glue -dry-run

# Destroy only Glue resources
terraform destroy -target=module.glue

# Recreate when needed
terraform apply -target=module.glue
```

---

### Option 2: Destroy Everything Except Data & State (Aggressive)

**What to Destroy:**
- All Glue resources (jobs, crawlers, catalog)
- IAM roles (can recreate)
- Secrets Manager secrets (must re-enter password)

**What to Keep:**
- S3 data lake bucket (contains data/scripts)
- S3 Terraform state bucket (infrastructure state)
- DynamoDB lock table (Terraform dependency)

**Cost Savings:** ~$0.40/month (Secrets Manager)  
**Recreation Time:** 10-15 minutes  
**Risk:** Must re-enter PostgreSQL password

**Not Recommended:** The savings are minimal (~$0.40/month) and you'll need to re-enter secrets.

---

### Option 3: Nuclear Option - Destroy Everything (Not Recommended for Learning)

**⚠️ WARNING:** This destroys all infrastructure including Terraform state management.

**What Gets Destroyed:**
- ALL infrastructure
- Terraform state backend
- All data in S3 (unless you backup first)

**Cost Savings:** ~$0.93/month  
**Recreation Time:** 30-60 minutes (full redeployment)  
**Risk:** HIGH - Lose all state, must manually recreate backend

**Only Use If:** You're completely done with the project and want to start fresh later.

---

## Recommended Approach for Cost Savings

### Current State Analysis

Your infrastructure is **already cost-optimized**:
- ✅ No running compute (Glue jobs only run when triggered)
- ✅ Minimal storage (~1 GB)
- ✅ Using free tier services where possible
- ✅ No DMS deployed (would be $125/month)

**Recommendation:** **Keep everything as-is**. Your current costs are negligible (~$1/month).

### If You Must Reduce Costs Further

**Option A: Delete CloudWatch Logs (Save ~$0.50/month)**
```bash
# List log groups
aws logs describe-log-groups --query 'logGroups[?contains(logGroupName, `glue`)].logGroupName' --output table

# Delete specific log group
aws logs delete-log-group --log-group-name /aws-glue/jobs/output
aws logs delete-log-group --log-group-name /aws-glue/jobs/error
aws logs delete-log-group --log-group-name /aws-glue/crawlers
```

**Note:** Logs will be recreated automatically when you run Glue jobs again.

**Option B: Destroy Secrets Manager Secret (Save ~$0.40/month)**
```bash
cd terraform
terraform destroy -target=module.secrets

# When you need it back, recreate and re-enter password
terraform apply -target=module.secrets
```

---

## Safe Destruction Commands

### 1. Selective Resource Destruction

```bash
cd terraform

# Destroy ONLY Glue module (jobs, crawlers, catalog)
terraform destroy -target=module.glue

# Destroy ONLY Secrets module
terraform destroy -target=module.secrets

# Destroy ONLY IAM module (risky - needed to recreate other resources)
terraform destroy -target=module.iam
```

### 2. Preview Before Destroy

**Always preview first:**
```bash
# See what will be destroyed
terraform plan -destroy -target=module.glue

# Or use this to see specific resources
terraform state list | grep glue
```

### 3. Exclude Specific Resources

Create a `preserve.tf` file to prevent accidental destruction:

```hcl
# terraform/preserve.tf

lifecycle {
  prevent_destroy = true
}
```

Apply to specific resources:
```hcl
# In modules/s3/main.tf
resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-datalake-${var.environment}"
  
  lifecycle {
    prevent_destroy = true  # Prevent accidental destruction
  }
}
```

---

## Recreation Strategy

### Quick Recreation (After Selective Destroy)

```bash
cd terraform

# Recreate Glue resources
terraform apply -target=module.glue

# Recreate Secrets (will prompt for password)
terraform apply -target=module.secrets

# Recreate everything destroyed
terraform apply
```

**Time:** 5-10 minutes  
**Data Loss:** None (S3 data preserved)  
**State:** Preserved (Terraform knows what to recreate)

---

## What NOT to Destroy

### Critical Resources (Never Destroy)

1. **S3 Terraform State Bucket**
   ```bash
   # DON'T DO THIS
   aws s3 rb s3://autocorp-terraform-state-XXXXXXXXXX --force
   ```
   **Why:** Terraform state is the source of truth. Destroying this breaks Terraform's ability to manage infrastructure.

2. **DynamoDB Lock Table**
   ```bash
   # DON'T DO THIS
   aws dynamodb delete-table --table-name autocorp-terraform-locks
   ```
   **Why:** Prevents state corruption during concurrent Terraform operations.

3. **S3 Data Lake Bucket (if contains data)**
   ```bash
   # DON'T DO THIS if you have data you want to keep
   terraform destroy -target=module.s3
   ```
   **Why:** Contains your generated data, ETL scripts, and Hudi tables.

---

## Cost-Saving Best Practices

### 1. Stop Running Glue Jobs

Glue jobs only cost money when running:
```bash
# Check for running jobs
for job in $(aws glue list-jobs --query 'JobNames[?contains(@, `autocorp`)]' --output text); do
  aws glue get-job-runs --job-name $job --query 'JobRuns[?JobRunState==`RUNNING`]' --output table
done

# No running jobs = $0 cost
```

### 2. Use Glue Job Bookmarks

Already configured in your jobs - prevents reprocessing data:
```python
job.init(args['JOB_NAME'], args)  # Enable bookmarking
# ... process data ...
job.commit()  # Update bookmark
```

### 3. Set Glue Job Timeouts

Already configured - prevents runaway costs:
```hcl
resource "aws_glue_job" "etl" {
  timeout = 60  # Minutes - job will be killed if exceeds
}
```

### 4. Delete Old CloudWatch Logs

```bash
# Delete logs older than 30 days
aws logs put-retention-policy --log-group-name /aws-glue/jobs/output --retention-in-days 30
```

### 5. Lifecycle Policies (Already Configured)

Your S3 lifecycle policies automatically move data to cheaper storage:
```hcl
lifecycle_rule {
  transition {
    days          = 90
    storage_class = "GLACIER"  # $0.004/GB vs $0.023/GB
  }
}
```

---

## Cost Monitoring

### Set Up Billing Alert

```bash
# Create SNS topic for alerts
aws sns create-topic --name autocorp-billing-alerts

# Subscribe your email
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:XXXXXXXXXXXX:autocorp-billing-alerts --protocol email --notification-endpoint your-email@example.com

# Create billing alarm (triggers at $10/month)
aws cloudwatch put-metric-alarm \
  --alarm-name autocorp-monthly-cost-alarm \
  --alarm-description "Alert when AutoCorp costs exceed $10/month" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:XXXXXXXXXXXX:autocorp-billing-alerts
```

### Check Current Costs

```bash
# Current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

---

## Emergency Stop (If Costs Spike)

### If You See Unexpected Charges

**1. Stop All Running Glue Jobs Immediately:**
```bash
# Find and stop all running jobs
for job in $(aws glue list-jobs --query 'JobNames[?contains(@, `autocorp`)]' --output text); do
  runs=$(aws glue get-job-runs --job-name $job --query 'JobRuns[?JobRunState==`RUNNING`].Id' --output text)
  for run in $runs; do
    echo "Stopping job: $job, run: $run"
    aws glue batch-stop-job-run --job-name $job --job-run-ids $run
  done
done
```

**2. Check for DMS Replication Instances:**
```bash
# Stop DMS instances if accidentally deployed
aws dms describe-replication-instances --query 'ReplicationInstances[?contains(ReplicationInstanceIdentifier, `autocorp`)]'

# Stop if found
aws dms stop-replication-instance --replication-instance-arn <arn>
```

**3. Check for Running EC2 Instances:**
```bash
# Shouldn't exist in this project, but check anyway
aws ec2 describe-instances --filters "Name=tag:Project,Values=autocorp" "Name=instance-state-name,Values=running"
```

---

## Safe Destruction Workflow

### Step-by-Step Safe Destroy Process

```bash
# 1. Navigate to Terraform directory
cd /home/scotton/dev/projects/autocorp/terraform

# 2. Check current state
terraform state list

# 3. Preview destruction of specific module
terraform plan -destroy -target=module.glue

# 4. Review the plan carefully
#    - How many resources will be destroyed?
#    - Are any critical resources included?
#    - Can you recreate them easily?

# 5. If safe, destroy the specific module
terraform destroy -target=module.glue

# 6. Verify destruction
terraform state list | grep glue  # Should show nothing

# 7. Document what you destroyed
echo "Destroyed Glue module on $(date)" >> destruction_log.txt
```

---

## When to Destroy Resources

### Destroy If:
- ✅ Finished with the project for >30 days
- ✅ Need to rebuild from scratch (testing IaC)
- ✅ Experimenting with different configurations
- ✅ Actual monthly costs exceed $20 (investigate first)

### Keep If:
- ❌ Actively learning/developing
- ❌ Preparing for interviews (may need to demo)
- ❌ Costs are <$5/month (negligible)
- ❌ Might need to reference the work in next 30 days

---

## Conclusion & Recommendation

### For Your Current Situation

**Recommended Action: KEEP EVERYTHING**

**Reasoning:**
1. **Current Cost:** ~$1/month is negligible (<$12/year)
2. **Phase 4 In Progress:** You're actively working on analytics layer
3. **Interview Prep:** You may need to demo this for interviews
4. **Learning Value:** Having infrastructure deployed helps with learning
5. **Recreation Overhead:** Time spent destroying/recreating exceeds cost savings

**When to Revisit:**
- After Phase 4 completion
- If you won't touch the project for 3+ months
- If DMS gets deployed (would be $125/month - definitely tear down when not using)

### If You Deploy DMS Later

**Critical:** DMS is the only significant cost driver in this project.

```bash
# After testing DMS, immediately destroy it
cd terraform
terraform destroy -target=module.dms

# Cost savings: ~$125/month
# Recreation: 5 minutes with terraform apply -target=module.dms
```

---

## Quick Reference Commands

### Safe to Run Anytime (No Destruction)
```bash
# Check costs
aws ce get-cost-and-usage --time-period Start=2025-12-01,End=2025-12-16 --granularity MONTHLY --metrics BlendedCost

# Check running resources
aws glue get-job-runs --job-name autocorp-sales-order-etl-dev --query 'JobRuns[?JobRunState==`RUNNING`]'
```

### Selective Destruction (Reversible)
```bash
# Destroy Glue only (no data loss)
terraform destroy -target=module.glue

# Destroy Secrets only (must re-enter password)
terraform destroy -target=module.secrets
```

### Nuclear Option (Use with Extreme Caution)
```bash
# Destroy everything managed by Terraform
terraform destroy

# Destroy Terraform backend (DANGEROUS - only if starting completely fresh)
aws s3 rb s3://autocorp-terraform-state-XXXXXXXXXX --force
aws dynamodb delete-table --table-name autocorp-terraform-locks
```

---

**Document Version:** 1.0  
**Created:** December 16, 2025  
**Author:** scotton  
**Project:** AutoCorp Cloud Data Lakehouse  
**Status:** Cost Analysis Complete - Recommendation: Keep Current Infrastructure
