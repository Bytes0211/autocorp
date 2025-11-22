# IAM Module Variables

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

variable "glue_scripts_bucket" {
  description = "S3 bucket for Glue ETL scripts"
  type        = string
}
