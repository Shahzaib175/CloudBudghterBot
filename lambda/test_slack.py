import boto3
import requests

def get_slack_webhook():
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(
        Name="/cloudbudgter/slack_webhook",
        WithDecryption=True
    )
    return response['Parameter']['Value']

def send_slack_message():
    webhook_url = get_slack_webhook()
    message = {
        "text": "✅ Slack integration test successful!"
    }
    response = requests.post(webhook_url, json=message)
    print("Status Code:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    send_slack_message()
