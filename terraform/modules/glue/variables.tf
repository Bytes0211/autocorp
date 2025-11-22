# Glue Module Variables

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "data_lake_bucket_id" {
  description = "ID of the data lake S3 bucket"
  type        = string
}

variable "glue_role_arn" {
  description = "ARN of the Glue service role"
  type        = string
}

variable "enable_crawlers" {
  description = "Enable Glue crawlers"
  type        = bool
  default     = true
}

variable "crawler_schedule" {
  description = "Cron expression for crawler schedule"
  type        = string
  default     = "cron(0 2 * * ? *)"
}
