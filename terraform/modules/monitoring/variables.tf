variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "ecs_cluster_name" {
  type = string
}

variable "ecs_service_name" {
  type = string
}

variable "api_gateway_id" {
  type = string
}

variable "alert_topic_arn" {
  type = string
}

variable "p95_latency_threshold_ms" {
  description = "Alert threshold for P95 API latency in milliseconds"
  type        = number
  default     = 2000
}

variable "error_rate_threshold_pct" {
  description = "Alert threshold for API 5xx error rate percentage"
  type        = number
  default     = 1
}

variable "tags" {
  type    = map(string)
  default = {}
}
