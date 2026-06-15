import json
import os
import sys
from datetime import datetime, timezone

import requests
from knockapi import Knock

API_BASE = "https://api.knock.app/v1"
MANAGEMENT_API_BASE = "https://control.knock.app/v1"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def upsert_workflow(service_token: str, workflow_key: str) -> None:
    headers = {
        "Authorization": f"Bearer {service_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "workflow": {
            "key": workflow_key,
            "name": f"Per-recipient alert {workflow_key}",
            "steps": [
                {
                    "ref": "email_alert",
                    "type": "channel",
                    "channel_key": "mailtrap",
                    "template": {
                        "subject": "{{ data.alert_type }} alert for {{ data.role }}",
                        "html_body": (
                            "<p>Hello {{ data.role }},</p>"
                            "<p>Your dashboard: {{ data.dashboard_url }}</p>"
                        ),
                        "text_body": (
                            "Hello {{ data.role }},\n\n"
                            "Your dashboard: {{ data.dashboard_url }}\n"
                        ),
                        "settings": {"layout_key": "default"},
                    },
                }
            ],
        }
    }

    response = requests.put(
        f"{MANAGEMENT_API_BASE}/workflows/{workflow_key}",
        headers=headers,
        params={
            "environment": "development",
            "commit": "true",
            "commit_message": f"Activate {workflow_key} for run {workflow_key}",
        },
        data=json.dumps(payload),
        timeout=30,
    )
    response.raise_for_status()

    activate_response = requests.put(
        f"{MANAGEMENT_API_BASE}/workflows/{workflow_key}/activate",
        headers=headers,
        params={"environment": "development"},
        data=json.dumps({"status": True}),
        timeout=30,
    )
    activate_response.raise_for_status()


def trigger_workflow(api_token: str, workflow_key: str, run_id: str, gmail_user: str) -> str:
    client = Knock(api_key=api_token)
    recipients = [
        {
            "id": f"owner-{run_id}",
            "name": "John Hammond",
            "email": f"{gmail_user}+r1-{run_id}@gmail.com",
            "$trigger_data": {
                "role": "Park Owner",
                "dashboard_url": f"https://jurassicpark.com/dashboard/owner-{run_id}",
            },
        },
        {
            "id": f"paleo-{run_id}",
            "name": "Ellie Sattler",
            "email": f"{gmail_user}+r2-{run_id}@gmail.com",
            "$trigger_data": {
                "role": "Paleobotanist",
                "dashboard_url": f"https://jurassicpark.com/dashboard/paleo-{run_id}",
            },
        },
    ]

    response = client.workflows.trigger(
        workflow_key,
        recipients=recipients,
        data={"alert_type": "security_breach"},
    )

    workflow_run_id = getattr(response, "workflow_run_id", None)
    if not workflow_run_id and isinstance(response, dict):
        workflow_run_id = response.get("workflow_run_id") or response.get("id")
    if not workflow_run_id:
        raise RuntimeError(f"Missing workflow_run_id in response: {response}")
    return workflow_run_id


def main() -> None:
    run_id = require_env("ZEALT_RUN_ID")
    service_token = require_env("KNOCK_SERVICE_TOKEN")
    api_token = require_env("KNOCK_API_TOKEN")
    gmail_user = require_env("GMAIL_USER_NAME")

    workflow_key = f"per-recipient-alert-{run_id}"

    upsert_workflow(service_token, workflow_key)
    workflow_run_id = trigger_workflow(api_token, workflow_key, run_id, gmail_user)

    log_path = "/home/user/myproject/output.log"
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] Workflow key: {workflow_key}\n")
        log_file.write(f"[{timestamp}] Workflow run ID: {workflow_run_id}\n")

    print(f"Workflow key: {workflow_key}")
    print(f"Workflow run ID: {workflow_run_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
