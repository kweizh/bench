import os
import requests
import json
from knockapi import Knock

def main():
    run_id = os.environ.get("ZEALT_RUN_ID")
    knock_service_token = os.environ.get("KNOCK_SERVICE_TOKEN")
    knock_api_token = os.environ.get("KNOCK_API_TOKEN")
    gmail_user = os.environ.get("GMAIL_USER_NAME")

    if not all([run_id, knock_service_token, knock_api_token, gmail_user]):
        print("Missing environment variables")
        return

    workflow_key = f"per-recipient-alert-{run_id}"
    log_file_path = "/home/user/myproject/output.log"

    # 1. Upsert the workflow using Management API
    # The Management API base URL is https://control.knock.app/v1
    # We use the service token for authentication
    
    management_headers = {
        "Authorization": f"Bearer {knock_service_token}",
        "Content-Type": "application/json"
    }

    workflow_payload = {
        "workflow": {
            "name": f"Per-recipient Alert {run_id}",
            "steps": [
                {
                    "type": "channel",
                    "channel_key": "mailtrap",
                    "ref": "email_1",
                    "template": {
                        "subject": "Alert: {{ data.alert_type }} - {{ data.role }}",
                        "html_body": "<p>Role: {{ data.role }}</p><p>Dashboard: <a href=\"{{ data.dashboard_url }}\">{{ data.dashboard_url }}</a></p>",
                        "text_body": "Role: {{ data.role }}\nDashboard: {{ data.dashboard_url }}",
                        "settings": {}
                    }
                }
            ]
        }
    }

    print(f"Upserting workflow: {workflow_key}")
    upsert_url = f"https://control.knock.app/v1/workflows/{workflow_key}?environment=development&commit=true&commit_message=Initial+commit"
    response = requests.put(upsert_url, headers=management_headers, json=workflow_payload)
    
    if response.status_code not in [200, 201]:
        print(f"Failed to upsert workflow: {response.status_code} {response.text}")
        return

    # 2. Activate the workflow
    print(f"Activating workflow: {workflow_key}")
    activate_url = f"https://control.knock.app/v1/workflows/{workflow_key}/activate?environment=development"
    response = requests.put(activate_url, headers=management_headers, json={"status": True})
    
    if response.status_code not in [200, 204]:
        print(f"Failed to activate workflow: {response.status_code} {response.text}")
        if response.status_code != 200:
            return

    # 3. Trigger the workflow using the backend SDK
    client = Knock(api_key=knock_api_token)

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

    print(f"Triggering workflow: {workflow_key}")
    trigger_response = client.workflows.trigger(
        key=workflow_key,
        recipients=recipients,
        data={
            "alert_type": "security_breach"
        }
    )

    # In newer SDK versions, trigger_response is a model object
    workflow_run_id = getattr(trigger_response, "workflow_run_id", None)
    if not workflow_run_id and isinstance(trigger_response, dict):
        workflow_run_id = trigger_response.get("workflow_run_id")
    
    # 4. Log the results
    with open(log_file_path, "w") as f:
        f.write(f"Workflow key: {workflow_key}\n")
        f.write(f"Workflow run ID: {workflow_run_id}\n")

    print(f"Successfully triggered workflow. Run ID: {workflow_run_id}")

if __name__ == "__main__":
    main()
