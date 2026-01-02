# AutoCorp Data Lake Pipeline - Main Terraform Configuration
# This orchestrates all infrastructure modules for the data lakehouse

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AutoCorp"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.owner
    }
  }
}

# S3 Module - Data Lake Storage
module "s3" {
  source = "./modules/s3"

  project_name        = var.project_name
  environment         = var.environment
  enable_versioning   = var.enable_s3_versioning
  lifecycle_days      = var.s3_lifecycle_days
}

# IAM Module - Service Roles and Policies
module "iam" {
  source = "./modules/iam"

  project_name        = var.project_name
  environment         = var.environment
  data_lake_bucket_id = module.s3.data_lake_bucket_id
  glue_scripts_bucket = module.s3.data_lake_bucket_id
}

# Secrets Manager - PostgreSQL Credentials
module "secrets" {
  source = "./modules/secrets"

  project_name = var.project_name
  environment  = var.environment
}

# Glue Module - Data Catalog and ETL Jobs
module "glue" {
  source = "./modules/glue"

  project_name          = var.project_name
  environment           = var.environment
  data_lake_bucket_id   = module.s3.data_lake_bucket_id
  glue_role_arn         = module.iam.glue_role_arn
  enable_crawlers       = var.enable_glue_crawlers
  crawler_schedule      = var.glue_crawler_schedule
}

# DMS Module - Database Replication (Optional - requires PostgreSQL connectivity)
module "dms" {
  source = "./modules/dms"
  count  = var.enable_dms ? 1 : 0

  project_name             = var.project_name
  environment              = var.environment
  replication_instance_class = var.dms_instance_class
  postgres_host            = var.postgres_host
  postgres_port            = var.postgres_port
  postgres_database        = var.postgres_database
  postgres_username        = var.postgres_username
  postgres_password        = var.postgres_password
  postgres_secret_arn      = module.secrets.postgres_password_secret_arn
  target_bucket_arn        = module.s3.data_lake_bucket_arn
  dms_role_arn             = module.iam.dms_role_arn
  allocated_storage        = var.dms_allocated_storage
}

# DataSync Module - CSV File Transfers (Optional - requires agent)
module "datasync" {
  source = "./modules/datasync"
  count  = var.enable_datasync ? 1 : 0

  project_name         = var.project_name
  environment          = var.environment
  datasync_agent_arns  = var.datasync_agent_arns
  target_bucket_arn    = module.s3.data_lake_bucket_arn
  datasync_role_arn    = module.iam.datasync_role_arn
  schedule_expression  = var.datasync_schedule
}

# Athena Module - Query Workgroup and Named Queries
module "athena" {
  source = "./modules/athena"

  project_name          = var.project_name
  environment           = var.environment
  query_results_bucket  = module.s3.data_lake_bucket_id
  glue_database_name    = var.athena_database_name
}

# CloudWatch Monitoring - Dashboard and Alarms
module "monitoring" {
  source = "./modules/monitoring"

  project_name          = var.project_name
  environment           = var.environment
  data_lake_bucket_name = module.s3.data_lake_bucket_id
  glue_job_names        = var.glue_job_names
  alert_email           = var.cloudwatch_alert_email
  create_sns_topic      = var.cloudwatch_alert_email != "" ? true : false
}

# Bedrock Module - AI Knowledge Base with RAG (Phase 5)
module "bedrock" {
  source = "./modules/bedrock"
  count  = var.enable_bedrock ? 1 : 0

  project_name               = var.project_name
  environment                = var.environment
  knowledge_base_bucket_arn  = module.s3.data_lake_bucket_arn
  bedrock_execution_role_arn = ""  # Will use module-created role
  enable_data_source         = var.enable_bedrock_data_source
  embedding_model            = var.bedrock_embedding_model
  chunk_size_tokens          = var.bedrock_chunk_size
  chunk_overlap_percentage   = var.bedrock_chunk_overlap
}

# Lambda Chat Module - Lambda Functions + API Gateway (Phase 5)
module "lambda_chat" {
  source = "./modules/lambda-chat"
  count  = var.enable_lambda_chat ? 1 : 0

  project_name       = var.project_name
  environment        = var.environment
  aws_region         = var.aws_region
  knowledge_base_id  = var.enable_bedrock ? module.bedrock[0].knowledge_base_id : ""
  knowledge_base_arn = var.enable_bedrock ? module.bedrock[0].knowledge_base_arn : ""
  glue_database      = var.athena_database_name
  athena_workgroup   = module.athena.workgroup_name
  s3_bucket_name     = module.s3.data_lake_bucket_id
  s3_bucket_arn      = module.s3.data_lake_bucket_arn

  depends_on = [module.bedrock, module.athena]
}
