variable "aws_region" {
  description = "AWS region for dev environment"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "alert_email" {
  description = "Email address for security and operational alerts"
  type        = string
}

variable "container_image" {
  description = "ECR image URI for the RAG service (updated by CI/CD)"
  type        = string
  default     = "public.ecr.aws/amazonlinux/amazonlinux:latest"
}
