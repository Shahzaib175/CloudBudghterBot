# utils.py

from datetime import datetime, timezone
import boto3

def get_today():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')

def get_ssm_parameter(name):
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']
