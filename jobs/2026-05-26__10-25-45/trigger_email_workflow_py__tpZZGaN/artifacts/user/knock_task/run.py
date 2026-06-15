#!/usr/bin/env python3
"""
Knock Email Workflow Automation Script.

Creates/upserts a Knock workflow with an email step (mailtrap channel),
commits and activates it, identifies a user, triggers the workflow, and
logs results.
"""

import os
import requests
import knockapi

# ---------------------------------------------------------------------------
# Read environment variables
# ---------------------------------------------------------------------------
ZEALT_RUN_ID = os.environ["ZEALT_RUN_ID"]
KNOCK_SERVICE_TOKEN = os.environ["KNOCK_SERVICE_TOKEN"]
KNOCK_API_TOKEN = os.environ["KNOCK_API_TOKEN"]
MAILTRAP_DOMAIN = os.environ["MAILTRAP_DOMAIN"]
GMAIL_USER_NAME = os.environ["GMAIL_USER_NAME"]

# ---------------------------------------------------------------------------
# Derived values
# ---------------------------------------------------------------------------
WORKFLOW_KEY = f"welcome-email-{ZEALT_RUN_ID}"
WORKFLOW_NAME = f"Welcome Email {ZEALT_RUN_ID}"
USER_ID = f"user-{ZEALT_RUN_ID}"
USER_NAME = f"Knock User {ZEALT_RUN_ID}"
USER_EMAIL = f"{GMAIL_USER_NAME}+receiver-{ZEALT_RUN_ID}@gmail.com"
FROM_EMAIL = f"sender-{ZEALT_RUN_ID}@{MAILTRAP_DOMAIN}"
DASHBOARD_URL = f"https://app.example.com/dashboard/{ZEALT_RUN_ID}"

MANAGEMENT_API_BASE = "https://control.knock.app/v1"
ENVIRONMENT = "development"

MGMT_HEADERS = {
    "Authorization": f"Bearer {KNOCK_SERVICE_TOKEN}",
    "Content-Type": "application/json",
}

# ---------------------------------------------------------------------------
# Step 1: Upsert the workflow via the Management API
# ---------------------------------------------------------------------------
print(f"Upserting workflow '{WORKFLOW_KEY}' in environment '{ENVIRONMENT}'...")

workflow_payload = {
    "workflow": {
        "name": WORKFLOW_NAME,
        "trigger_data_json_schema": {
            "type": "object",
            "properties": {
                "dashboard_url": {"type": "string"},
            },
            "required": ["dashboard_url"],
        },
        "steps": [
            {
                "ref": "welcome_email",
                "type": "channel",
                "channel_key": "mailtrap",
                "settings": {
                    "from_email_address": FROM_EMAIL,
                },
                "template": {
                    "settings": {
                        "from_email_address": FROM_EMAIL,
                    },
                    "subject": "Welcome to Knock, {{ recipient.name }}!",
                    "html_body": (
                        "<p>Hello {{ recipient.name }},</p>"
                        "<p>Welcome to Knock! Visit your dashboard: "
                        '<a href="{{ data.dashboard_url }}">{{ data.dashboard_url }}</a></p>'
                    ),
                },
            }
        ],
    }
}

upsert_url = f"{MANAGEMENT_API_BASE}/workflows/{WORKFLOW_KEY}?environment={ENVIRONMENT}"
resp = requests.put(upsert_url, json=workflow_payload, headers=MGMT_HEADERS)
resp.raise_for_status()
print(f"  Upsert response status: {resp.status_code}")

# ---------------------------------------------------------------------------
# Step 2: Commit the workflow changes in the development environment
# ---------------------------------------------------------------------------
print(f"Committing workflow '{WORKFLOW_KEY}' changes...")

commit_resp = requests.put(
    f"{MANAGEMENT_API_BASE}/commits",
    params={
        "environment": ENVIRONMENT,
        "resource_type": "workflow",
        "resource_id": WORKFLOW_KEY,
        "commit_message": "Initial commit",
    },
    headers=MGMT_HEADERS,
)
commit_resp.raise_for_status()
print(f"  Commit response: {commit_resp.json().get('result')}")

# ---------------------------------------------------------------------------
# Step 3: Activate the workflow in the development environment
# ---------------------------------------------------------------------------
print(f"Activating workflow '{WORKFLOW_KEY}'...")

activate_url = (
    f"{MANAGEMENT_API_BASE}/workflows/{WORKFLOW_KEY}/activate?environment={ENVIRONMENT}"
)
resp = requests.put(activate_url, json={"active": True}, headers=MGMT_HEADERS)
resp.raise_for_status()
activated = resp.json().get("workflow", {}).get("active", False)
print(f"  Activate response status: {resp.status_code}, active={activated}")

# ---------------------------------------------------------------------------
# Step 4: Identify the user via the Knock SDK
# ---------------------------------------------------------------------------
print(f"Identifying user '{USER_ID}'...")

client = knockapi.Knock(api_key=KNOCK_API_TOKEN)
client.users.update(
    USER_ID,
    name=USER_NAME,
    email=USER_EMAIL,
)
print(f"  User identified: id={USER_ID}, email={USER_EMAIL}")

# ---------------------------------------------------------------------------
# Step 5: Trigger the workflow for the user
# ---------------------------------------------------------------------------
print(f"Triggering workflow '{WORKFLOW_KEY}' for user '{USER_ID}'...")

trigger_response = client.workflows.trigger(
    WORKFLOW_KEY,
    recipients=[USER_ID],
    data={"dashboard_url": DASHBOARD_URL},
)
workflow_run_id = trigger_response.workflow_run_id
print(f"  Workflow run id: {workflow_run_id}")

# ---------------------------------------------------------------------------
# Step 6: Write the log file
# ---------------------------------------------------------------------------
log_path = "/home/user/knock_task/output.log"
log_lines = [
    f"Workflow key: {WORKFLOW_KEY}",
    f"Workflow run id: {workflow_run_id}",
    f"Recipient id: {USER_ID}",
    f"Recipient email: {USER_EMAIL}",
]

with open(log_path, "w") as f:
    f.write("\n".join(log_lines) + "\n")

print(f"\nLog written to {log_path}:")
for line in log_lines:
    print(f"  {line}")

print("\nDone.")
