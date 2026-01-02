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

output "dms_postgres_endpoint_arn" {
  description = "ARN of DMS PostgreSQL source endpoint"
  value       = var.enable_dms ? module.dms[0].postgres_endpoint_arn : null
}

output "dms_s3_endpoint_arn" {
  description = "ARN of DMS S3 target endpoint"
  value       = var.enable_dms ? module.dms[0].s3_endpoint_arn : null
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

# Athena Outputs
output "athena_workgroup_name" {
  description = "Name of the Athena workgroup"
  value       = module.athena.workgroup_name
}

output "athena_workgroup_arn" {
  description = "ARN of the Athena workgroup"
  value       = module.athena.workgroup_arn
}

output "athena_named_queries" {
  description = "Map of Athena named query IDs"
  value       = module.athena.named_queries
}

output "athena_query_results_location" {
  description = "S3 location for Athena query results"
  value       = module.athena.query_results_location
}

# CloudWatch Monitoring Outputs
output "cloudwatch_dashboard_arn" {
  description = "ARN of the CloudWatch dashboard"
  value       = module.monitoring.dashboard_arn
}

output "cloudwatch_dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = module.monitoring.dashboard_name
}

output "cloudwatch_alarm_arns" {
  description = "ARNs of CloudWatch alarms"
  value = {
    glue_job_failures   = module.monitoring.glue_job_failure_alarm_arn
    athena_failures     = module.monitoring.athena_failure_alarm_arn
    high_cost_alert     = module.monitoring.high_cost_alarm_arn
  }
}

output "cloudwatch_sns_topic_arn" {
  description = "ARN of the SNS topic for CloudWatch alerts"
  value       = module.monitoring.sns_topic_arn
}

# Bedrock Outputs (Phase 5)
output "bedrock_knowledge_base_id" {
  description = "ID of the Bedrock Knowledge Base"
  value       = var.enable_bedrock ? module.bedrock[0].knowledge_base_id : null
}

output "bedrock_knowledge_base_arn" {
  description = "ARN of the Bedrock Knowledge Base"
  value       = var.enable_bedrock ? module.bedrock[0].knowledge_base_arn : null
}

output "bedrock_opensearch_collection_arn" {
  description = "ARN of the OpenSearch Serverless collection"
  value       = var.enable_bedrock ? module.bedrock[0].opensearch_collection_arn : null
}

output "bedrock_opensearch_collection_endpoint" {
  description = "Endpoint of the OpenSearch Serverless collection"
  value       = var.enable_bedrock ? module.bedrock[0].opensearch_collection_endpoint : null
}

output "bedrock_kb_role_arn" {
  description = "ARN of the IAM role for Bedrock Knowledge Base"
  value       = var.enable_bedrock ? module.bedrock[0].bedrock_kb_role_arn : null
}

output "bedrock_data_source_id" {
  description = "ID of the Bedrock Knowledge Base data source"
  value       = var.enable_bedrock ? module.bedrock[0].data_source_id : null
}

output "bedrock_vector_index_name" {
  description = "Name of the vector index in OpenSearch"
  value       = var.enable_bedrock ? module.bedrock[0].vector_index_name : null
}

# Lambda Chat Outputs (Phase 5)
output "chat_handler_function_name" {
  description = "Name of the chat handler Lambda function"
  value       = var.enable_lambda_chat ? module.lambda_chat[0].chat_handler_function_name : null
}

output "analytics_query_function_name" {
  description = "Name of the analytics query Lambda function"
  value       = var.enable_lambda_chat ? module.lambda_chat[0].analytics_query_function_name : null
}

output "api_gateway_endpoint" {
  description = "Base URL for the API Gateway"
  value       = var.enable_lambda_chat ? module.lambda_chat[0].api_gateway_endpoint : null
}

output "chat_endpoint" {
  description = "Full URL for the chat endpoint"
  value       = var.enable_lambda_chat ? module.lambda_chat[0].chat_endpoint : null
}

output "analytics_endpoint" {
  description = "Full URL for the analytics endpoint"
  value       = var.enable_lambda_chat ? module.lambda_chat[0].analytics_endpoint : null
}

output "api_key_secret_arn" {
  description = "ARN of the Secrets Manager secret containing the API key"
  value       = var.enable_lambda_chat ? module.lambda_chat[0].api_key_secret_arn : null
  sensitive   = true
}
