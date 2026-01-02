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

variable "postgres_password" {
  description = "PostgreSQL password for replication"
  type        = string
  sensitive   = true
  default     = ""
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

# Athena Configuration
variable "athena_database_name" {
  description = "Glue/Athena database name for querying Hudi tables"
  type        = string
  default     = "autocorp_curated"
}

variable "athena_workgroup_name" {
  description = "Athena workgroup name"
  type        = string
  default     = "autocorp-analytics"
}

# CloudWatch Monitoring Configuration
variable "cloudwatch_alert_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
  default     = ""
}

variable "glue_job_names" {
  description = "List of Glue job names to monitor"
  type        = list(string)
  default     = [
    "sales_order_etl",
    "customers_etl",
    "auto_parts_etl",
    "service_etl",
    "service_parts_etl",
    "sales_order_parts_etl",
    "sales_order_services_etl",
    "analytics_sales_order_fact_etl",
    "analytics_sales_order_line_items_etl",
    "analytics_service_parts_catalog_etl"
  ]
}

# Bedrock Configuration (Phase 5)
variable "enable_bedrock" {
  description = "Enable Bedrock module for AI chatbox"
  type        = bool
  default     = false
}

variable "enable_bedrock_data_source" {
  description = "Enable Bedrock data source (set to true after uploading knowledge base data to S3)"
  type        = bool
  default     = false
}

variable "bedrock_embedding_model" {
  description = "Bedrock embedding model for vectorization"
  type        = string
  default     = "amazon.titan-embed-text-v1"
}

variable "bedrock_chunk_size" {
  description = "Maximum tokens per chunk for document chunking"
  type        = number
  default     = 300
}

variable "bedrock_chunk_overlap" {
  description = "Percentage overlap between chunks"
  type        = number
  default     = 20
}

# Lambda Chat Configuration (Phase 5)
variable "enable_lambda_chat" {
  description = "Enable Lambda functions and API Gateway for AI chatbox"
  type        = bool
  default     = false
}
