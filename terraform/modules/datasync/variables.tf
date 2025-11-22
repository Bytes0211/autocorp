# DataSync Module Variables

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "datasync_agent_arns" {
  type = list(string)
}

variable "target_bucket_arn" {
  type = string
}

variable "datasync_role_arn" {
  type = string
}

variable "schedule_expression" {
  type = string
}
