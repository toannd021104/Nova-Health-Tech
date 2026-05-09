variable "aws_region" {
  description = "AWS region for prod environment"
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
  description = "ECR image URI for the RAG service (set by CI/CD pipeline)"
  type        = string
}

variable "bedrock_model_units" {
  description = "Number of Bedrock Provisioned Throughput model units"
  type        = number
  default     = 2
}

variable "callback_urls" {
  description = "OAuth callback URLs for the clinical app"
  type        = list(string)
}

variable "logout_urls" {
  description = "OAuth logout URLs for the clinical app"
  type        = list(string)
}
