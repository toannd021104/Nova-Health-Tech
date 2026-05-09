variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_account_id" {
  type = string
}

variable "phi_researcher_role_arn" {
  type = string
}

variable "lambda_pipeline_role_arn" {
  type = string
}

variable "ecs_task_role_arn" {
  type = string
}

variable "public_kms_key_arn" {
  type = string
}

variable "phi_kms_key_arn" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
