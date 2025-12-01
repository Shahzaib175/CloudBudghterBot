import boto3
from datetime import datetime, timedelta

def get_aws_costs():
    client = boto3.client('ce')

    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    # Format dates
    start_yesterday = yesterday.strftime('%Y-%m-%d')
    end_yesterday = today.strftime('%Y-%m-%d')

    # 1. DAILY COST (Yesterday)
    actual_response = client.get_cost_and_usage(
        TimePeriod={'Start': start_yesterday, 'End': end_yesterday},
        Granularity='DAILY',
        Metrics=['UnblendedCost']
    )
    daily_cost = float(actual_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])

    # 2. MONTHLY FORECAST (From today to tomorrow)
    forecast_response = client.get_cost_forecast(
        TimePeriod={
            'Start': today.strftime('%Y-%m-%d'),
            'End': (today + timedelta(days=1)).strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Metric='UNBLENDED_COST'
    )
    forecast_cost = float(forecast_response['ForecastResultsByTime'][0]['MeanValue'])

    # 3. LAST MONTH TOTAL
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)

    last_month_response = client.get_cost_and_usage(
        TimePeriod={
            'Start': first_day_last_month.strftime('%Y-%m-%d'),
            'End': (last_day_last_month + timedelta(days=1)).strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )
    last_month_cost = float(last_month_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])

    return {
        'daily_cost': daily_cost,
        'forecast_cost': forecast_cost,
        'last_month_cost': last_month_cost
    }
