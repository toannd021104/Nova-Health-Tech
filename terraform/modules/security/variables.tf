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

variable "audit_bucket_arn" {
  type = string
}

variable "audit_bucket_id" {
  type = string
}

variable "public_kms_key_arn" {
  type = string
}

variable "phi_bucket_id" {
  type = string
}

variable "public_bucket_id" {
  type = string
}

variable "enable_macie" {
  description = "Enable Amazon Macie for PHI/PII detection"
  type        = bool
  default     = true
}

variable "alert_email" {
  description = "Email address for security alerts"
  type        = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
