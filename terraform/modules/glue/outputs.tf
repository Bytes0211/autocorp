# Glue Module Outputs

output "database_name" {
  description = "Name of the Glue Data Catalog database"
  value       = aws_glue_catalog_database.autocorp.name
}

output "crawler_names" {
  description = "Names of the Glue crawlers"
  value = concat(
    var.enable_crawlers ? [aws_glue_crawler.raw_database[0].name] : [],
    var.enable_crawlers ? [aws_glue_crawler.raw_csv[0].name] : []
  )
}

output "database_description" {
  description = "Description of the Glue Data Catalog database"
  value       = aws_glue_catalog_database.autocorp.description
}

output "raw_database_crawler_name" {
  description = "Name of the raw database crawler"
  value       = var.enable_crawlers ? aws_glue_crawler.raw_database[0].name : null
}

output "raw_csv_crawler_name" {
  description = "Name of the raw CSV crawler"
  value       = var.enable_crawlers ? aws_glue_crawler.raw_csv[0].name : null
}

output "raw_database_crawler_schedule" {
  description = "Schedule of the raw database crawler"
  value       = var.enable_crawlers ? aws_glue_crawler.raw_database[0].schedule : null
}

output "raw_csv_crawler_schedule" {
  description = "Schedule of the raw CSV crawler"
  value       = var.enable_crawlers ? aws_glue_crawler.raw_csv[0].schedule : null
}

output "raw_database_crawler_target" {
  description = "S3 target of the raw database crawler"
  value       = var.enable_crawlers ? aws_glue_crawler.raw_database[0].s3_target[0].path : null
}

output "raw_csv_crawler_target" {
  description = "S3 target of the raw CSV crawler"
  value       = var.enable_crawlers ? aws_glue_crawler.raw_csv[0].s3_target[0].path : null
}

output "raw_database_crawler_role" {
  description = "IAM role ARN of the raw database crawler"
  value       = var.enable_crawlers ? aws_glue_crawler.raw_database[0].role : null
}

output "raw_csv_crawler_role" {
  description = "IAM role ARN of the raw CSV crawler"
  value       = var.enable_crawlers ? aws_glue_crawler.raw_csv[0].role : null
}

output "raw_database_crawler_schema_policy" {
  description = "Schema change policy of the raw database crawler"
  value = var.enable_crawlers ? {
    delete_behavior = aws_glue_crawler.raw_database[0].schema_change_policy[0].delete_behavior
    update_behavior = aws_glue_crawler.raw_database[0].schema_change_policy[0].update_behavior
  } : null
}

output "etl_job_names" {
  description = "Names of the Glue ETL jobs"
  value = var.enable_etl_jobs ? [
    aws_glue_job.sales_order[0].name,
    aws_glue_job.customers[0].name,
    aws_glue_job.auto_parts[0].name,
    aws_glue_job.service[0].name,
    aws_glue_job.service_parts[0].name,
    aws_glue_job.sales_order_parts[0].name,
    aws_glue_job.sales_order_services[0].name
  ] : []
}

output "etl_job_arns" {
  description = "ARNs of the Glue ETL jobs"
  value = var.enable_etl_jobs ? [
    aws_glue_job.sales_order[0].arn,
    aws_glue_job.customers[0].arn,
    aws_glue_job.auto_parts[0].arn,
    aws_glue_job.service[0].arn,
    aws_glue_job.service_parts[0].arn,
    aws_glue_job.sales_order_parts[0].arn,
    aws_glue_job.sales_order_services[0].arn
  ] : []
}
