# AutoCorp Data Lake Pipeline - Default Variable Values
# For environment-specific overrides, use environments/*.tfvars

aws_region   = "us-east-1"
project_name = "autocorp"
environment  = "dev"
owner        = "scotton"

# S3 Configuration
enable_s3_versioning = true
s3_lifecycle_days    = 90

# Glue Configuration
enable_glue_crawlers  = true
glue_crawler_schedule = "cron(0 2 * * ? *)" # Daily at 2 AM UTC

# DMS Configuration (disabled by default until PostgreSQL is accessible)
enable_dms            = false
dms_instance_class    = "dms.t3.medium"
dms_allocated_storage = 50
postgres_host         = "" # Update with your PostgreSQL host
postgres_port         = 5432
postgres_database     = "autocorp"
postgres_username     = "scotton"

# DataSync Configuration (disabled until agent is deployed)
enable_datasync       = false
datasync_agent_arns   = [] # Update after agent activation
datasync_schedule     = "rate(1 hour)"
