# DMS Module Outputs

output "replication_instance_arn" {
  description = "ARN of the DMS replication instance"
  value       = aws_dms_replication_instance.main.replication_instance_arn
}

output "replication_instance_id" {
  description = "ID of the DMS replication instance"
  value       = aws_dms_replication_instance.main.replication_instance_id
}

output "postgres_endpoint_arn" {
  description = "ARN of PostgreSQL source endpoint"
  value       = aws_dms_endpoint.postgres_source.endpoint_arn
}

output "s3_endpoint_arn" {
  description = "ARN of S3 target endpoint"
  value       = aws_dms_endpoint.s3_target.endpoint_arn
}

output "full_load_task_arn" {
  description = "ARN of full load replication task"
  value       = aws_dms_replication_task.full_load.replication_task_arn
}

output "cdc_task_arn" {
  description = "ARN of CDC replication task"
  value       = aws_dms_replication_task.cdc.replication_task_arn
}

output "vpc_id" {
  description = "VPC ID for DMS"
  value       = aws_vpc.dms.id
}
