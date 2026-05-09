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

variable "enable_provisioned_throughput" {
  description = "Enable Bedrock Provisioned Throughput for guaranteed latency (recommended for prod)"
  type        = bool
  default     = false
}

variable "model_units" {
  description = "Number of model units for Provisioned Throughput (1 unit ~ 100 input tokens/sec)"
  type        = number
  default     = 1
}

variable "tags" {
  type    = map(string)
  default = {}
}
