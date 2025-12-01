import requests

def send_slack_notification(daily, forecast, last_month, webhook_url, extra_message=None, only_confirm=False):

    if only_confirm:
        payload = {"text": "✅ You have successfully configured AWS cost alarm monitoring!"}
        requests.post(webhook_url, json=payload)
        return

    msg = (
        f"📊 *AWS Cost Update*\n\n"
        f"💵 *Daily Spend:* ${daily:.2f}\n"
        f"📈 *Monthly Forecast:* ${forecast:.2f}\n"
        f"📆 *Last Month Total:* ${last_month:.2f}"
    )

    if extra_message:
        msg += f"\n\n{extra_message}"

    payload = {"text": msg}
    requests.post(webhook_url, json=payload)
