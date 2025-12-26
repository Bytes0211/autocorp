output "workgroup_id" {
  description = "ID of the Athena workgroup"
  value       = aws_athena_workgroup.autocorp.id
}

output "workgroup_arn" {
  description = "ARN of the Athena workgroup"
  value       = aws_athena_workgroup.autocorp.arn
}

output "workgroup_name" {
  description = "Name of the Athena workgroup"
  value       = aws_athena_workgroup.autocorp.name
}

output "query_results_location" {
  description = "S3 location for Athena query results"
  value       = "s3://${var.query_results_bucket}/athena-results/"
}

output "named_queries" {
  description = "Map of named query IDs"
  value = {
    sales_summary       = aws_athena_named_query.sales_summary.id
    top_parts          = aws_athena_named_query.top_parts.id
    customer_orders    = aws_athena_named_query.customer_orders.id
    service_performance = aws_athena_named_query.service_performance.id
    hudi_time_travel   = aws_athena_named_query.hudi_time_travel.id
  }
}
