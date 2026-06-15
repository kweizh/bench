import os
import requests
from knockapi import Knock

run_id = os.environ.get('ZEALT_RUN_ID', 'test-run')
service_token = os.environ.get('KNOCK_SERVICE_TOKEN')
api_token = os.environ.get('KNOCK_API_TOKEN')
gmail_user = os.environ.get('GMAIL_USER_NAME')

workflow_key = f"per-recipient-alert-{run_id}"

# 1. Upsert Workflow
headers = {
    'Authorization': f'Bearer {service_token}',
    'Content-Type': 'application/json'
}

workflow_data = {
    "workflow": {
        "name": f"Per-Recipient Alert {run_id}",
        "steps": [
            {
                "type": "channel",
                "channel_key": "mailtrap",
                "ref": "email_1",
                "template": {
                    "subject": "Alert: {{ data.alert_type }} for {{ data.role }}",
                    "html_body": "<p>Role: {{ data.role }}</p><p>Dashboard: {{ data.dashboard_url }}</p>",
                    "settings": {
                        "layout_key": "default"
                    }
                }
            }
        ]
    }
}

print(f"Upserting workflow {workflow_key}...")
resp = requests.put(
    f'https://control.knock.app/v1/workflows/{workflow_key}?environment=development&commit=true&commit_message=init',
    headers=headers,
    json=workflow_data
)
resp.raise_for_status()

# 2. Activate Workflow
print("Activating workflow...")
resp = requests.put(
    f'https://control.knock.app/v1/workflows/{workflow_key}/activate?environment=development',
    headers=headers
)
resp.raise_for_status()

# 3. Trigger Workflow
print("Triggering workflow...")
client = Knock(api_key=api_token)

recipients = [
    {
        "id": f"owner-{run_id}",
        "name": "John Hammond",
        "email": f"{gmail_user}+r1-{run_id}@gmail.com",
        "$trigger_data": {
            "role": "Park Owner",
            "dashboard_url": f"https://jurassicpark.com/dashboard/owner-{run_id}"
        }
    },
    {
        "id": f"paleo-{run_id}",
        "name": "Ellie Sattler",
        "email": f"{gmail_user}+r2-{run_id}@gmail.com",
        "$trigger_data": {
            "role": "Paleobotanist",
            "dashboard_url": f"https://jurassicpark.com/dashboard/paleo-{run_id}"
        }
    }
]

response = client.workflows.trigger(
    key=workflow_key,
    recipients=recipients,
    data={"alert_type": "security_breach"}
)

# In knockapi python SDK, TriggerWorkflowResponse has a workflow_run_id attribute? Or it's a dict?
# Let's check response type
try:
    workflow_run_id = response.workflow_run_id
except AttributeError:
    workflow_run_id = response.get('workflow_run_id', 'unknown')

print(f"Workflow key: {workflow_key}")
print(f"Workflow run ID: {workflow_run_id}")

with open('/home/user/myproject/output.log', 'w') as f:
    f.write(f"Workflow key: {workflow_key}\n")
    f.write(f"Workflow run ID: {workflow_run_id}\n")

