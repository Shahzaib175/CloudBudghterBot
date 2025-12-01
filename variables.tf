variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
}

variable "slack_webhook_url" {
  description = "Slack Webhook URL"
  type        = string
  sensitive   = true
}

variable "budget_threshold" {
  description = "Monthly budget threshold"
  type        = number
  default     = 900
}

variable "alert_email" {
  description = "Email address to receive cost breach alerts"
  type        = string
}

variable "slack_namespace" {
  description = "Namespace used in Slack and SSM path"
  type        = string
}
