# AutoCorp Data Lake Pipeline - Variable Definitions

# General Configuration
variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "autocorp"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "owner" {
  description = "Project owner for tagging"
  type        = string
  default     = "scotton"
}

# S3 Configuration
variable "enable_s3_versioning" {
  description = "Enable versioning on S3 buckets"
  type        = bool
  default     = true
}

variable "s3_lifecycle_days" {
  description = "Days before transitioning to Glacier"
  type        = number
  default     = 90
}

# Glue Configuration
variable "enable_glue_crawlers" {
  description = "Enable Glue crawlers"
  type        = bool
  default     = true
}

variable "glue_crawler_schedule" {
  description = "Cron expression for Glue crawler schedule"
  type        = string
  default     = "cron(0 2 * * ? *)" # Daily at 2 AM UTC
}

# DMS Configuration
variable "enable_dms" {
  description = "Enable DMS module (requires PostgreSQL connectivity)"
  type        = bool
  default     = false # Disabled by default until connectivity is verified
}

variable "dms_instance_class" {
  description = "DMS replication instance class"
  type        = string
  default     = "dms.t3.medium"
}

variable "dms_allocated_storage" {
  description = "DMS replication instance storage in GB"
  type        = number
  default     = 50
}

variable "postgres_host" {
  description = "PostgreSQL hostname"
  type        = string
  default     = ""
}

variable "postgres_port" {
  description = "PostgreSQL port"
  type        = number
  default     = 5432
}

variable "postgres_database" {
  description = "PostgreSQL database name"
  type        = string
  default     = "autocorp"
}

variable "postgres_username" {
  description = "PostgreSQL username for replication"
  type        = string
  default     = "scotton"
}

# DataSync Configuration
variable "enable_datasync" {
  description = "Enable DataSync module (requires agent deployment)"
  type        = bool
  default     = false # Disabled by default until agent is activated
}

variable "datasync_agent_arns" {
  description = "List of DataSync agent ARNs (deployed on-premises)"
  type        = list(string)
  default     = []
}

variable "datasync_schedule" {
  description = "DataSync task schedule expression"
  type        = string
  default     = "rate(1 hour)"
}
