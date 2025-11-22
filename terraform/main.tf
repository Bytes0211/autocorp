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
