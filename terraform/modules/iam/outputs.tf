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

output "glue_assume_role_policy" {
  description = "Assume role policy for Glue role"
  value       = aws_iam_role.glue.assume_role_policy
}

output "glue_inline_policy" {
  description = "Inline policy for Glue role"
  value       = aws_iam_role_policy.glue_s3_catalog.policy
}

output "dms_assume_role_policy" {
  description = "Assume role policy for DMS role"
  value       = aws_iam_role.dms.assume_role_policy
}

output "dms_inline_policy" {
  description = "Inline policy for DMS role"
  value       = aws_iam_role_policy.dms_s3.policy
}

output "datasync_assume_role_policy" {
  description = "Assume role policy for DataSync role"
  value       = aws_iam_role.datasync.assume_role_policy
}

output "datasync_inline_policy" {
  description = "Inline policy for DataSync role"
  value       = aws_iam_role_policy.datasync_s3.policy
}
