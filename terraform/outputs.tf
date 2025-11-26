# AutoCorp Data Lake Pipeline - Outputs

# S3 Outputs
output "data_lake_bucket_name" {
  description = "Name of the data lake S3 bucket"
  value       = module.s3.data_lake_bucket_id
}

output "data_lake_bucket_arn" {
  description = "ARN of the data lake S3 bucket"
  value       = module.s3.data_lake_bucket_arn
}

# IAM Outputs
output "glue_role_arn" {
  description = "ARN of the Glue service role"
  value       = module.iam.glue_role_arn
}

output "dms_role_arn" {
  description = "ARN of the DMS service role"
  value       = module.iam.dms_role_arn
}

output "datasync_role_arn" {
  description = "ARN of the DataSync service role"
  value       = module.iam.datasync_role_arn
}

# Secrets Manager Outputs
output "postgres_secret_arn" {
  description = "ARN of the PostgreSQL password secret"
  value       = module.secrets.postgres_password_secret_arn
  sensitive   = true
}

# Glue Outputs
output "glue_database_name" {
  description = "Name of the Glue Data Catalog database"
  value       = module.glue.database_name
}

output "glue_crawler_names" {
  description = "Names of the Glue crawlers"
  value       = module.glue.crawler_names
}

# DMS Outputs (if enabled)
output "dms_replication_instance_arn" {
  description = "ARN of the DMS replication instance"
  value       = var.enable_dms ? module.dms[0].replication_instance_arn : null
}

output "dms_endpoint_arns" {
  description = "ARNs of DMS endpoints"
  value       = var.enable_dms ? module.dms[0].endpoint_arns : null
}

# DataSync Outputs (if enabled)
output "datasync_task_arns" {
  description = "ARNs of DataSync tasks"
  value       = var.enable_datasync ? module.datasync[0].task_arns : null
}

# Additional outputs for testing
output "data_lake_bucket_id" {
  description = "ID of the data lake S3 bucket"
  value       = module.s3.data_lake_bucket_id
}

output "s3_bucket_versioning" {
  description = "S3 bucket versioning configuration"
  value       = module.s3.s3_bucket_versioning
}

output "s3_bucket_encryption" {
  description = "S3 bucket encryption configuration"
  value       = module.s3.s3_bucket_encryption
}

output "s3_public_access_block" {
  description = "S3 public access block configuration"
  value       = module.s3.s3_public_access_block
}

output "s3_lifecycle_rules" {
  description = "S3 lifecycle rules"
  value       = module.s3.s3_lifecycle_rules
}

output "glue_role_name" {
  description = "Name of the Glue IAM role"
  value       = module.iam.glue_role_name
}

output "dms_role_name" {
  description = "Name of the DMS IAM role"
  value       = module.iam.dms_role_name
}

output "datasync_role_name" {
  description = "Name of the DataSync IAM role"
  value       = module.iam.datasync_role_name
}

output "glue_assume_role_policy" {
  description = "Glue assume role policy JSON"
  value       = module.iam.glue_assume_role_policy
}

output "glue_inline_policy" {
  description = "Glue inline policy JSON"
  value       = module.iam.glue_inline_policy
}

output "dms_assume_role_policy" {
  description = "DMS assume role policy JSON"
  value       = module.iam.dms_assume_role_policy
}

output "dms_inline_policy" {
  description = "DMS inline policy JSON"
  value       = module.iam.dms_inline_policy
}

output "datasync_assume_role_policy" {
  description = "DataSync assume role policy JSON"
  value       = module.iam.datasync_assume_role_policy
}

output "datasync_inline_policy" {
  description = "DataSync inline policy JSON"
  value       = module.iam.datasync_inline_policy
}

output "glue_catalog_database_name" {
  description = "Name of the Glue catalog database"
  value       = module.glue.database_name
}

output "glue_catalog_database_description" {
  description = "Description of the Glue catalog database"
  value       = module.glue.database_description
}

output "glue_raw_database_crawler_name" {
  description = "Name of the raw database crawler"
  value       = module.glue.raw_database_crawler_name
}

output "glue_raw_csv_crawler_name" {
  description = "Name of the raw CSV crawler"
  value       = module.glue.raw_csv_crawler_name
}

output "glue_raw_database_crawler_schedule" {
  description = "Schedule of the raw database crawler"
  value       = module.glue.raw_database_crawler_schedule
}

output "glue_raw_csv_crawler_schedule" {
  description = "Schedule of the raw CSV crawler"
  value       = module.glue.raw_csv_crawler_schedule
}

output "glue_raw_database_crawler_target" {
  description = "S3 target of the raw database crawler"
  value       = module.glue.raw_database_crawler_target
}

output "glue_raw_csv_crawler_target" {
  description = "S3 target of the raw CSV crawler"
  value       = module.glue.raw_csv_crawler_target
}

output "glue_raw_database_crawler_role" {
  description = "IAM role of the raw database crawler"
  value       = module.glue.raw_database_crawler_role
}

output "glue_raw_csv_crawler_role" {
  description = "IAM role of the raw CSV crawler"
  value       = module.glue.raw_csv_crawler_role
}

output "glue_raw_database_crawler_schema_policy" {
  description = "Schema change policy of the raw database crawler"
  value       = module.glue.raw_database_crawler_schema_policy
}

output "postgres_password_secret_name" {
  description = "Name of the PostgreSQL password secret"
  value       = module.secrets.postgres_password_secret_name
}

output "postgres_password_secret_description" {
  description = "Description of the PostgreSQL password secret"
  value       = module.secrets.postgres_password_secret_description
}

output "glue_etl_job_names" {
  description = "Names of the Glue ETL jobs"
  value       = module.glue.etl_job_names
}

output "glue_etl_job_arns" {
  description = "ARNs of the Glue ETL jobs"
  value       = module.glue.etl_job_arns
}

output "raw_csv_crawler_schema_policy" {
  description = "Schema change policy of the raw CSV crawler"
  value       = module.glue.raw_database_crawler_schema_policy
}

output "postgres_password_secret_arn" {
  description = "ARN of the PostgreSQL password secret"
  value       = module.secrets.postgres_password_secret_arn
  sensitive   = true
}
