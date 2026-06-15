#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

import requests
from knockapi import Knock


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def upsert_workflow(service_token: str, workflow_key: str, workflow_name: str, mailtrap_domain: str, run_id: str) -> None:
    url = f"https://control.knock.app/v1/workflows/{workflow_key}?environment=development"
    headers = {
        "Authorization": f"Bearer {service_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "key": workflow_key,
        "name": workflow_name,
        "steps": [
            {
                "ref": "welcome_email",
                "type": "channel",
                "channel_key": "mailtrap",
                "settings": {
                    "from_email_address": f"sender-{run_id}@{mailtrap_domain}",
                    "subject": "Welcome to Knock, {{ recipient.name }}!",
                    "html_body": (
                        "<html><body>"
                        "<p>Hello {{ recipient.name }},</p>"
                        "<p>Visit your dashboard: <a href=\"{{ data.dashboard_url }}\">"
                        "{{ data.dashboard_url }}</a></p>"
                        "</body></html>"
                    ),
                },
            }
        ],
        "trigger_data_json_schema": {
            "type": "object",
            "properties": {
                "dashboard_url": {"type": "string"},
            },
            "required": ["dashboard_url"],
        },
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload), timeout=30)
    response.raise_for_status()



def activate_workflow(service_token: str, workflow_key: str) -> None:
    url = f"https://control.knock.app/v1/workflows/{workflow_key}/activate?environment=development"
    headers = {
        "Authorization": f"Bearer {service_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, timeout=30)
    response.raise_for_status()


def main() -> int:
    run_id = require_env("ZEALT_RUN_ID")
    service_token = require_env("KNOCK_SERVICE_TOKEN")
    api_token = require_env("KNOCK_API_TOKEN")
    mailtrap_domain = require_env("MAILTRAP_DOMAIN")
    gmail_user = require_env("GMAIL_USER_NAME")

    workflow_key = f"welcome-email-{run_id}"
    workflow_name = f"Welcome Email {run_id}"

    upsert_workflow(service_token, workflow_key, workflow_name, mailtrap_domain, run_id)
    activate_workflow(service_token, workflow_key)

    client = Knock(api_key=api_token)

    recipient_id = f"user-{run_id}"
    recipient_email = f"{gmail_user}+receiver-{run_id}@gmail.com"

    client.users.update(
        user_id=recipient_id,
        data={
            "name": f"Knock User {run_id}",
            "email": recipient_email,
        },
    )

    trigger_response = client.workflows.trigger(
        key=workflow_key,
        recipients=[recipient_id],
        data={"dashboard_url": f"https://app.example.com/dashboard/{run_id}"},
    )

    workflow_run_id = None
    if isinstance(trigger_response, dict):
        workflow_run_id = trigger_response.get("workflow_run_id") or trigger_response.get("id")
    else:
        workflow_run_id = getattr(trigger_response, "workflow_run_id", None) or getattr(
            trigger_response, "id", None
        )

    if not workflow_run_id:
        raise RuntimeError("Unable to determine workflow_run_id from trigger response")

    output_path = Path("/home/user/knock_task/output.log")
    output_path.write_text(
        "\n".join(
            [
                f"Workflow key: {workflow_key}",
                f"Workflow run id: {workflow_run_id}",
                f"Recipient id: {recipient_id}",
                f"Recipient email: {recipient_email}",
            ]
        )
        + "\n"
    )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
