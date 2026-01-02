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
enable_dms            = true
dms_instance_class    = "dms.t3.medium"
dms_allocated_storage = 50
postgres_host         = "192.168.7.144"
postgres_port         = 5432
postgres_database     = "autocorp"
postgres_username     = "scotton"

# DataSync Configuration (disabled until agent is deployed)
enable_datasync       = false
datasync_agent_arns   = [] # Update after agent activation
datasync_schedule     = "rate(1 hour)"

# Athena Configuration
athena_database_name  = "autocorp_dev"

# Bedrock Configuration (Phase 5 - AI Chatbox)
enable_bedrock              = true
enable_bedrock_data_source  = true  # Knowledge base data uploaded to S3
bedrock_embedding_model     = "amazon.titan-embed-text-v2:0"
bedrock_chunk_size          = 300
bedrock_chunk_overlap       = 20

# Lambda Chat Configuration (Phase 5 - API Gateway + Lambda)
enable_lambda_chat          = true
