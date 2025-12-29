variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "autocorp"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "knowledge_base_bucket_arn" {
  description = "ARN of the S3 bucket containing knowledge base documents"
  type        = string
}

variable "bedrock_execution_role_arn" {
  description = "ARN of the IAM role for Bedrock execution (will use bedrock_kb role if not provided)"
  type        = string
  default     = ""
}

variable "enable_data_source" {
  description = "Whether to create the Bedrock data source (set to false initially, true after uploading KB data)"
  type        = bool
  default     = false
}

variable "embedding_model" {
  description = "Bedrock embedding model to use"
  type        = string
  default     = "amazon.titan-embed-text-v1"
}

variable "chunk_size_tokens" {
  description = "Maximum tokens per chunk for document chunking"
  type        = number
  default     = 300
}

variable "chunk_overlap_percentage" {
  description = "Percentage overlap between chunks"
  type        = number
  default     = 20
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
