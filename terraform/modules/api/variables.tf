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

variable "cognito_user_pool_arn" {
  type = string
}

variable "alb_internal_dns" {
  type = string
}

variable "alb_internal_arn" {
  description = "NLB ARN for VPC Link target"
  type        = string
}

variable "alb_listener_arn" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "throttle_burst_limit" {
  type    = number
  default = 200
}

variable "throttle_rate_limit" {
  type    = number
  default = 100
}

variable "tags" {
  type    = map(string)
  default = {}
}
