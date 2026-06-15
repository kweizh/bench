import os
import requests
import urllib.parse
from knockapi import Knock

def main():
    run_id = os.environ.get("ZEALT_RUN_ID")
    service_token = os.environ.get("KNOCK_SERVICE_TOKEN")
    api_token = os.environ.get("KNOCK_API_TOKEN")
    mailtrap_domain = os.environ.get("MAILTRAP_DOMAIN")
    gmail_user = os.environ.get("GMAIL_USER_NAME")

    workflow_key = f"welcome-email-{run_id}"
    recipient_id = f"user-{run_id}"
    recipient_email = f"{gmail_user}+receiver-{run_id}@gmail.com"

    # 1. Upsert workflow via Management API
    headers = {
        "Authorization": f"Bearer {service_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "workflow": {
            "name": f"Welcome Email {run_id}",
            "steps": [
                {
                    "ref": "welcome_email",
                    "type": "channel",
                    "channel_key": "mailtrap",
                    "settings": {
                        "from_email_address": f"sender-{run_id}@{mailtrap_domain}"
                    },
                    "template": {
                        "settings": {
                            "layout_key": "default"
                        },
                        "subject": "Welcome to Knock, {{ recipient.name }}!",
                        "html_body": "Hello {{ recipient.name }}, your dashboard is {{ data.dashboard_url }}"
                    }
                }
            ],
            "trigger_data_json_schema": {
                "type": "object",
                "properties": {
                    "dashboard_url": { "type": "string" }
                },
                "required": ["dashboard_url"]
            }
        }
    }

    commit_msg = urllib.parse.quote("Initial commit")
    url_upsert = f"https://control.knock.app/v1/workflows/{workflow_key}?environment=development&commit=true&commit_message={commit_msg}"
    
    res_upsert = requests.put(url_upsert, headers=headers, json=payload)
    res_upsert.raise_for_status()

    # 2. Activate the workflow
    url_activate = f"https://control.knock.app/v1/workflows/{workflow_key}/activate?environment=development"
    res_activate = requests.put(url_activate, headers=headers)
    res_activate.raise_for_status()

    # 3. Identify user and trigger
    client = Knock(api_key=api_token)

    client.users.update(
        user_id=recipient_id,
        name=f"Knock User {run_id}",
        email=recipient_email
    )

    res_trigger = client.workflows.trigger(
        key=workflow_key,
        recipients=[recipient_id],
        data={
            "dashboard_url": f"https://app.example.com/dashboard/{run_id}"
        }
    )

    # 4. Write log file
    log_content = (
        f"Workflow key: {workflow_key}\n"
        f"Workflow run id: {res_trigger.workflow_run_id}\n"
        f"Recipient id: {recipient_id}\n"
        f"Recipient email: {recipient_email}\n"
    )

    with open("/home/user/knock_task/output.log", "w") as f:
        f.write(log_content)

if __name__ == "__main__":
    main()
