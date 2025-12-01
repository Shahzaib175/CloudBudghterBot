provider "aws" {
  region = var.aws_region
}

#-----------------------------
# SSM Parameters (Slack + Threshold)
#-----------------------------
resource "aws_ssm_parameter" "slack_webhook" {
  name  = "/cloudbudgter/${var.slack_namespace}/slack_webhook"
  type  = "String"
  value = var.slack_webhook_url
}

resource "aws_ssm_parameter" "budget_threshold" {
  name  = "/cloudbudgter/${var.slack_namespace}/budget_threshold"
  type  = "String"
  value = var.budget_threshold
}

#-----------------------------
# SNS Topic + Subscription (Email)
#-----------------------------
resource "aws_sns_topic" "alerts" {
  name = "cloudbudgter-alerts-${var.slack_namespace}"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

#-----------------------------
# IAM Role & Policies for Lambda
#-----------------------------
resource "aws_iam_role" "lambda_exec" {
  name = "Hybytes_AWS_Cost_Rule"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "ce_permissions" {
  name        = "Hybytes_AWS_CostExplorerPermissions"
  description = "Allows Lambda to access CE, SSM, SNS, DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "ssm:GetParameter",
        "ssm:GetParameters",
        "sns:Publish",
        "sns:ListTopics",
        "dynamodb:PutItem",
        "dynamodb:GetItem"
      ],
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "ce_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.ce_permissions.arn
}

#-----------------------------
# Lambda Function
#-----------------------------
resource "aws_lambda_function" "cloudbudgter" {
  filename         = "cloudbudgter.zip"
  function_name    = "cloudbudgter"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  timeout          = 30
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = filebase64sha256("cloudbudgter.zip")

  environment {
    variables = {
      BUDGET_THRESHOLD_SSM_PATH = aws_ssm_parameter.budget_threshold.name
      SLACK_WEBHOOK_SSM_PATH    = aws_ssm_parameter.slack_webhook.name
      ALERT_EMAIL               = var.alert_email
      SNS_TOPIC_NAME            = aws_sns_topic.alerts.name
    }
  }
}

#-----------------------------
# Lambda One-Time Invocation (terraform apply)
#-----------------------------
resource "aws_lambda_invocation" "initialize_sns" {
  function_name = aws_lambda_function.cloudbudgter.function_name

  input = jsonencode({
    initialize = true
  })

  depends_on = [
    aws_lambda_function.cloudbudgter
  ]
}

#-----------------------------
# CloudWatch Daily Trigger (Mon–Fri 11:30 AM IST)
#-----------------------------
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "cloudbudgter-daily-schedule"
  schedule_expression = "cron(0 6 ? * MON-FRI *)" # UTC 6:00 AM = 11:30 AM IST
}

resource "aws_cloudwatch_event_target" "invoke_lambda" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "cloudbudgter"
  arn       = aws_lambda_function.cloudbudgter.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cloudbudgter.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}

#-----------------------------
# DynamoDB Table for Breach State
#-----------------------------
resource "aws_dynamodb_table" "budget_breach_tracker" {
  name         = "cloudbudgter-breach-tracker"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "date"

  attribute {
    name = "date"
    type = "S"
  }

  tags = {
    Project     = "CloudBudgter"
    Environment = "Production"
  }
}
