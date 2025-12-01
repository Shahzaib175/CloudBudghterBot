import boto3
import os

def send_alert_email(subject, message):
    # Get SNS Topic Name from environment
    topic_name = os.environ.get("SNS_TOPIC_NAME")
    if not topic_name:
        raise Exception("Environment variable SNS_TOPIC_NAME not set")

    # Get the full SNS Topic ARN by listing topics
    sns = boto3.client('sns')
    topics = sns.list_topics()["Topics"]
    topic_arn = next((t["TopicArn"] for t in topics if topic_name in t["TopicArn"]), None)

    if not topic_arn:
        raise Exception(f"SNS topic containing '{topic_name}' not found.")

    # Send the notification
    sns.publish(
        TopicArn=topic_arn,
        Subject=subject,
        Message=message
    )

if __name__ == "__main__":
    # Manual test (will fail if environment variable isn't set)
    send_alert_email(
        subject="CloudBudgter Test Alert",
        message="This is a test alert from your CloudBudgter project."
    )

