# IAM Module Outputs

output "glue_role_arn" {
  description = "ARN of the Glue service role"
  value       = aws_iam_role.glue.arn
}

output "glue_role_name" {
  description = "Name of the Glue service role"
  value       = aws_iam_role.glue.name
}

output "dms_role_arn" {
  description = "ARN of the DMS service role"
  value       = aws_iam_role.dms.arn
}

output "dms_role_name" {
  description = "Name of the DMS service role"
  value       = aws_iam_role.dms.name
}

output "datasync_role_arn" {
  description = "ARN of the DataSync service role"
  value       = aws_iam_role.datasync.arn
}

output "datasync_role_name" {
  description = "Name of the DataSync service role"
  value       = aws_iam_role.datasync.name
}
