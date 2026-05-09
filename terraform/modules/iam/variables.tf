variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_account_id" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "phi_bucket_arn" {
  description = "ARN of the PHI S3 bucket"
  type        = string
}

variable "public_bucket_arn" {
  description = "ARN of the public content S3 bucket"
  type        = string
}

variable "phi_kms_key_arn" {
  description = "ARN of the KMS key used to encrypt PHI data"
  type        = string
}

variable "public_kms_key_arn" {
  description = "ARN of the KMS key used to encrypt public content"
  type        = string
}

variable "opensearch_collection_arn" {
  description = "ARN of the OpenSearch Serverless collection"
  type        = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
