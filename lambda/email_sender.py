import boto3

def send_alert_email(subject, message):
    # Get SNS Topic ARN from SSM Parameter Store
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name='/cloudbudgter/sns_topic_arn')
    sns_topic_arn = response['Parameter']['Value']

    # Send notification using SNS
    sns = boto3.client('sns')
    sns.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

if __name__ == "__main__":
    # Manual test example
    send_alert_email(
        subject="CloudBudgter Test Alert",
        message="This is a test alert from your CloudBudgter project."
    )
