output "lambda_function_name" {
  description = "Lambda Function Name"
  value       = aws_lambda_function.cloudbudgter.function_name
}


output "slack_webhook_ssm_path" {
  description = "SSM path for Slack webhook"
  value       = aws_ssm_parameter.slack_webhook.name
}

output "budget_threshold_ssm_path" {
  description = "SSM path for budget threshold"
  value       = aws_ssm_parameter.budget_threshold.name
}
