# dynamo_state.py

import boto3
from utils import get_today

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cloudbudgter-state')  # Use your actual DynamoDB table name

def check_breach_state(today=None):
    if not today:
        today = get_today()

    try:
        response = table.get_item(Key={"id": "budget_status"})
        item = response.get('Item', {})
        return item.get('breach_detected', False)
    except Exception as e:
        print(f"Error checking breach state: {e}")
        return False

def update_breach_state(today=None):
    if not today:
        today = get_today()

    try:
        table.put_item(
            Item={
                "id": "budget_status",
                "breach_detected": True,
                "breach_date": today
            }
        )
        print("🔁 Breach state updated in DynamoDB.")
    except Exception as e:
        print(f"Error updating breach state: {e}")
