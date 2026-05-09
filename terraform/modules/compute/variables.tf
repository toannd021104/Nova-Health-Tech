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

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "ecs_task_role_arn" {
  type = string
}

variable "ecs_execution_role_arn" {
  type = string
}

variable "sg_ecs_tasks_id" {
  type = string
}

variable "sg_alb_id" {
  type = string
}

variable "opensearch_public_endpoint" {
  type = string
}

variable "opensearch_phi_endpoint" {
  type = string
}

variable "redis_endpoint" {
  type = string
}

variable "redis_port" {
  type = number
}

variable "app_config_secret_arn" {
  type = string
}

variable "guardrail_id" {
  type = string
}

variable "guardrail_version" {
  type = string
}

variable "task_cpu" {
  description = "ECS task CPU units (1024 = 1 vCPU)"
  type        = number
  default     = 2048
}

variable "task_memory_mb" {
  description = "ECS task memory in MB"
  type        = number
  default     = 4096
}

variable "min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks"
  type        = number
  default     = 10
}

variable "container_image" {
  description = "ECR image URI for the RAG service"
  type        = string
}

variable "log_retention_days" {
  type    = number
  default = 90
}

variable "tags" {
  type    = map(string)
  default = {}
}
