variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID"
  type        = string
}

variable "knowledge_base_arn" {
  description = "Bedrock Knowledge Base ARN"
  type        = string
}

variable "glue_database" {
  description = "Glue database name for Athena queries"
  type        = string
}

variable "athena_workgroup" {
  description = "Athena workgroup name"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket name for data lake"
  type        = string
}

variable "s3_bucket_arn" {
  description = "S3 bucket ARN for data lake"
  type        = string
}
