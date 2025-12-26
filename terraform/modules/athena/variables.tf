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

variable "query_results_bucket" {
  description = "S3 bucket name for Athena query results"
  type        = string
}

variable "glue_database_name" {
  description = "Name of the Glue database containing tables"
  type        = string
  default     = "autocorp_curated"
}

variable "athena_execution_role_arn" {
  description = "IAM role ARN for Athena execution (optional, for Lake Formation)"
  type        = string
  default     = ""
}

variable "enable_lakeformation" {
  description = "Enable AWS Lake Formation permissions"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
