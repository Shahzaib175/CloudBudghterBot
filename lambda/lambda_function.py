import os
import boto3
from cost_checker import get_aws_costs
from slack_notifier import send_slack_notification
from email_sender import send_alert_email
from dynamo_state import check_breach_state, update_breach_state
from utils import get_today, get_ssm_parameter

# ---------------- SNS Publisher ----------------
def publish_to_sns(subject, message):
    sns = boto3.client("sns")
    topic_name = os.environ.get("SNS_TOPIC_NAME")

    # Find topic ARN containing name
    topics = sns.list_topics()["Topics"]
    topic_arn = next((t["TopicArn"] for t in topics if topic_name in t["TopicArn"]), None)

    if topic_arn:
        sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
    else:
        print("SNS Topic not found during publish().")


# ---------------- MAIN LAMBDA FUNCTION ----------------
def lambda_handler(event=None, context=None):

    # Check if this is terraform apply initialization
    initialize = event.get("initialize") if event else False

    # Fetch AWS costs
    costs = get_aws_costs()
    today = get_today()

    daily_cost = costs["daily_cost"]
    forecast_cost = costs["forecast_cost"]
    last_month_cost = costs["last_month_cost"]

    # Load SSM parameters
    budget_threshold = float(get_ssm_parameter(os.environ["BUDGET_THRESHOLD_SSM_PATH"]))
    slack_webhook_url = get_ssm_parameter(os.environ["SLACK_WEBHOOK_SSM_PATH"])

    # ---------------- INITIALIZATION MODE ----------------
    if initialize:
        # Only send confirmation message
        send_slack_notification(
            daily_cost, forecast_cost, last_month_cost,
            webhook_url=slack_webhook_url,
            only_confirm=True
        )

        return {
            "statusCode": 200,
            "body": "Initialization successful."
        }

    # ---------------- DAILY CRON EXECUTION ----------------
    # Always send daily cost update (not during initialize)
    send_slack_notification(
        daily_cost, forecast_cost, last_month_cost,
        webhook_url=slack_webhook_url
    )

    # Check if forecast is above threshold
    breached = forecast_cost > budget_threshold
    already_breached = check_breach_state(today)

    if breached and not already_breached:

        subject = "🚨 AWS Budget Breach Detected"
        message = (
            f"Your forecasted AWS cost (${forecast_cost:.2f}) exceeded your threshold (${budget_threshold}).\n"
            f"💵 Daily Spend: ${daily_cost:.2f}\n"
            f"📆 Last Month Total: ${last_month_cost:.2f}"
        )

        # Email + SNS notification
        send_alert_email(subject, message)
        publish_to_sns(subject, message)

        # Slack alert
        send_slack_notification(
            daily_cost, forecast_cost, last_month_cost,
            webhook_url=slack_webhook_url,
            extra_message="🚨 Cost threshold breached! Email + SNS alert sent."
        )

        update_breach_state(today)

    return {
        "statusCode": 200,
        "body": "Scheduled execution finished."
    }
