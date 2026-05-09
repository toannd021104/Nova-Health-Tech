variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "redis_sg_id" {
  type = string
}

variable "kms_key_arn" {
  type = string
}

variable "max_cache_gb" {
  description = "Maximum cache storage in GB (ElastiCache Serverless scales within this limit)"
  type        = number
  default     = 10
}

variable "tags" {
  type    = map(string)
  default = {}
}
