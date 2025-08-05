import requests
import json
import os
import sys

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK, json=payload)
    return response.status_code

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        results = [json.loads(line) for line in f if line.strip()]
    failing = [r for r in results if r['status'] == 'FAIL']

    if failing:
        msg = "*SSL Cert Expiry Alert:*\n" + "\n".join(
            f"{r['hostname']} expires in {r['days_left']} days" for r in failing
        )
        send_slack_alert(msg)
