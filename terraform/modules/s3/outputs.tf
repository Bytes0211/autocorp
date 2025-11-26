# S3 Module Outputs

output "data_lake_bucket_id" {
  description = "ID of the data lake bucket"
  value       = aws_s3_bucket.data_lake.id
}

output "data_lake_bucket_arn" {
  description = "ARN of the data lake bucket"
  value       = aws_s3_bucket.data_lake.arn
}

output "data_lake_bucket_domain_name" {
  description = "Domain name of the data lake bucket"
  value       = aws_s3_bucket.data_lake.bucket_domain_name
}

output "s3_bucket_versioning" {
  description = "Versioning configuration of the data lake bucket"
  value = {
    status = aws_s3_bucket_versioning.data_lake.versioning_configuration[0].status
  }
}

output "s3_bucket_encryption" {
  description = "Encryption configuration of the data lake bucket"
  value = {
    sse_algorithm = [for rule in aws_s3_bucket_server_side_encryption_configuration.data_lake.rule : rule.apply_server_side_encryption_by_default[0].sse_algorithm][0]
  }
}

output "s3_public_access_block" {
  description = "Public access block configuration"
  value = {
    block_public_acls       = tostring(aws_s3_bucket_public_access_block.data_lake.block_public_acls)
    block_public_policy     = tostring(aws_s3_bucket_public_access_block.data_lake.block_public_policy)
    ignore_public_acls      = tostring(aws_s3_bucket_public_access_block.data_lake.ignore_public_acls)
    restrict_public_buckets = tostring(aws_s3_bucket_public_access_block.data_lake.restrict_public_buckets)
  }
}

output "s3_lifecycle_rules" {
  description = "Lifecycle rules configured for the bucket"
  value = {
    archive-raw-zone = "Enabled"
    expire-logs      = "Enabled"
  }
}
