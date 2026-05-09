variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "callback_urls" {
  description = "Allowed OAuth callback URLs for the app client"
  type        = list(string)
}

variable "logout_urls" {
  description = "Allowed logout URLs for the app client"
  type        = list(string)
}

variable "mfa_configuration" {
  description = "MFA setting: OFF, ON, or OPTIONAL"
  type        = string
  default     = "ON"
}

variable "password_minimum_length" {
  type    = number
  default = 14
}

variable "tags" {
  type    = map(string)
  default = {}
}
