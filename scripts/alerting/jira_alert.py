import requests
import json
import os
import sys

JIRA_URL = "https://your-jira-instance.atlassian.net/rest/api/2/issue"
JIRA_AUTH = os.getenv("JIRA_AUTH_BASIC")  # Base64-encoded user:token

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {JIRA_AUTH}"
}

def create_jira_ticket(summary, description):
    payload = {
        "fields": {
            "project": {"key": "CERT"},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Bug"},
            "priority": {"name": "High"}
        }
    }
    response = requests.post(JIRA_URL, headers=headers, json=payload)
    return response.status_code, response.json()

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        results = [json.loads(line) for line in f if line.strip()]
    failing = [r for r in results if r['status'] == 'FAIL']

    if failing:
        summary = f"SSL Certificate Expiry: {len(failing)} host(s)"
        description = "\n".join(
            f"{r['hostname']} expires in {r['days_left']} days" for r in failing
        )
        create_jira_ticket(summary, description)
