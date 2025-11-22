# DMS Module Variables

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "replication_instance_class" {
  type = string
}

variable "postgres_host" {
  type = string
}

variable "postgres_port" {
  type = number
}

variable "postgres_database" {
  type = string
}

variable "postgres_username" {
  type = string
}

variable "postgres_secret_arn" {
  type = string
}

variable "target_bucket_arn" {
  type = string
}

variable "dms_role_arn" {
  type = string
}

variable "allocated_storage" {
  type = number
}
