variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "autocorp"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "data_lake_bucket_name" {
  description = "Name of the S3 data lake bucket"
  type        = string
}

variable "glue_job_names" {
  description = "List of Glue job names to monitor"
  type        = list(string)
  default     = []
}

variable "glue_crawler_names" {
  description = "List of Glue crawler names to monitor"
  type        = list(string)
  default     = []
}

variable "sns_topic_arn" {
  description = "ARN of existing SNS topic for alerts (optional)"
  type        = string
  default     = ""
}

variable "create_sns_topic" {
  description = "Create a new SNS topic for alerts"
  type        = bool
  default     = false
}

variable "alert_email" {
  description = "Email address for alert notifications"
  type        = string
  default     = ""
}

variable "enable_cost_alerts" {
  description = "Enable daily cost threshold alerts"
  type        = bool
  default     = true
}

variable "daily_cost_threshold" {
  description = "Daily cost threshold in USD for alerts"
  type        = number
  default     = 20.0
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 14
}
