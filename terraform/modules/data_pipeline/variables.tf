variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "aws_account_id" {
  type = string
}

variable "lambda_role_arn" {
  type = string
}

variable "step_functions_role_arn" {
  type = string
}

variable "scheduler_role_arn" {
  type = string
}

variable "public_bucket_id" {
  type = string
}

variable "phi_bucket_id" {
  type = string
}

variable "public_collection_endpoint" {
  type = string
}

variable "phi_collection_endpoint" {
  type = string
}

variable "document_metadata_table_name" {
  type = string
}

variable "app_config_secret_arn" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "lambda_sg_id" {
  type = string
}

variable "lambda_runtime" {
  description = "Lambda runtime for pipeline functions"
  type        = string
  default     = "python3.12"
}

variable "lambda_memory_mb" {
  type    = number
  default = 1024
}

variable "lambda_timeout_sec" {
  type    = number
  default = 900
}

variable "who_schedule_cron" {
  description = "EventBridge cron for WHO API ingestion (UTC)"
  type        = string
  default     = "cron(0 2 1 * ? *)"
}

variable "tags" {
  type    = map(string)
  default = {}
}
