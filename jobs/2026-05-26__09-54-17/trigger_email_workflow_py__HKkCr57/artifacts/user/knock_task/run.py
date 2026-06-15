import os
import sys
import requests
from knockapi import Knock

def run():
    # 1. Read environment variables
    zealt_run_id = os.environ.get("ZEALT_RUN_ID")
    knock_service_token = os.environ.get("KNOCK_SERVICE_TOKEN")
    knock_api_token = os.environ.get("KNOCK_API_TOKEN")
    mailtrap_domain = os.environ.get("MAILTRAP_DOMAIN")
    gmail_user_name = os.environ.get("GMAIL_USER_NAME")

    if not all([zealt_run_id, knock_service_token, knock_api_token, mailtrap_domain, gmail_user_name]):
        print("Missing required environment variables")
        sys.exit(1)

    workflow_key = f"welcome-email-{zealt_run_id}"
    workflow_name = f"Welcome Email {zealt_run_id}"
    recipient_id = f"user-{zealt_run_id}"
    recipient_name = f"Knock User {zealt_run_id}"
    recipient_email = f"{gmail_user_name}+receiver-{zealt_run_id}@gmail.com"
    sender_email = f"sender-{zealt_run_id}@{mailtrap_domain}"
    dashboard_url = f"https://app.example.com/dashboard/{zealt_run_id}"

    # 2. Upsert Workflow using Management API
    mgmt_url = f"https://control.knock.app/v1/workflows/{workflow_key}?environment=development"
    headers = {
        "Authorization": f"Bearer {knock_service_token}",
        "Content-Type": "application/json"
    }

    workflow_payload = {
        "workflow": {
            "name": workflow_name,
            "active": True,
            "steps": [
                {
                    "type": "channel",
                    "channel_key": "mailtrap",
                    "ref": "welcome_email",
                    "template": {
                        "subject": "Welcome to Knock, {{ recipient.name }}!",
                        "html_body": "Hello {{ recipient.name }},<br>Your dashboard is available at: <a href=\"{{ data.dashboard_url }}\">{{ data.dashboard_url }}</a>",
                        "settings": {
                            "from_email_address": sender_email
                        }
                    }
                }
            ],
            "trigger_data_json_schema": {
                "type": "object",
                "properties": {
                    "dashboard_url": {"type": "string"}
                },
                "required": ["dashboard_url"]
            }
        }
    }

    print(f"Upserting workflow: {workflow_key}")
    response = requests.put(mgmt_url, json=workflow_payload, headers=headers)
    print(f"Upsert response: {response.status_code} {response.text}")
    if response.status_code not in [200, 201]:
        print(f"Failed to upsert workflow: {response.status_code} {response.text}")
        sys.exit(1)

    # 3. Activate Workflow
    print(f"Activating workflow: {workflow_key}")
    # Try the environment-specific activation/commit if needed
    # But often "active: true" in upsert is enough if it's already committed.
    # Let's try to commit it first.
    commit_url = f"https://control.knock.app/v1/workflows/{workflow_key}/commit?environment=development"
    response = requests.post(commit_url, json={"message": "Initial commit"}, headers=headers)
    print(f"Commit response: {response.status_code} {response.text}")
    
    activate_url = f"https://control.knock.app/v1/workflows/{workflow_key}/activate?environment=development"
    response = requests.post(activate_url, headers=headers)
    print(f"Activation response: {response.status_code} {response.text}")

    # 4. Use Knock Python SDK to Identify User and Trigger Workflow
    client = Knock(api_key=knock_api_token)

    print(f"Identifying user: {recipient_id}")
    client.users.update(user_id=recipient_id,
        name=recipient_name,
        email=recipient_email
    )

    print(f"Triggering workflow: {workflow_key}")
    workflow_run = client.workflows.trigger(
        key=workflow_key,
        recipients=[recipient_id],
        data={
            "dashboard_url": dashboard_url
        }
    )

    # In some versions of the SDK it might be workflow_run_id or workflow_run['workflow_run_id']
    # If it's a pydantic model, it might be .workflow_run_id
    try:
        workflow_run_id = workflow_run.workflow_run_id
    except AttributeError:
        try:
            workflow_run_id = workflow_run.id
        except AttributeError:
            # Fallback to dict access if it's that kind of object
            workflow_run_id = workflow_run['workflow_run_id']
            
    print(f"Workflow triggered. Run ID: {workflow_run_id}")

    # 5. Write log file
    log_path = "/home/user/knock_task/output.log"
    with open(log_path, "w") as f:
        f.write(f"Workflow key: {workflow_key}\n")
        f.write(f"Workflow run id: {workflow_run_id}\n")
        f.write(f"Recipient id: {recipient_id}\n")
        f.write(f"Recipient email: {recipient_email}\n")

    print(f"Log written to {log_path}")

if __name__ == "__main__":
    run()
