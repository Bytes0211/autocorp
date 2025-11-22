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
