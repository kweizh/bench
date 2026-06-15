#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

BASE_URL = "https://control.knock.app"


def request(method, url, token, payload=None):
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        return exc.code, body


def main():
    run_id = os.environ.get("ZEALT_RUN_ID")
    token = os.environ.get("KNOCK_SERVICE_TOKEN")
    if not run_id:
        print("Missing ZEALT_RUN_ID", file=sys.stderr)
        return 1
    if not token:
        print("Missing KNOCK_SERVICE_TOKEN", file=sys.stderr)
        return 1

    workflow_key = f"escalation-{run_id}"
    workflow_payload = {
        "workflow": {
            "key": workflow_key,
            "name": "Channel escalation workflow",
            "trigger_data_json_schema": {
                "type": "object",
                "properties": {
                    "onboarding_url": {"type": "string"}
                },
                "required": ["onboarding_url"],
                "additionalProperties": False,
            },
            "steps": [
                {
                    "ref": "in_app_feed_1",
                    "type": "channel",
                    "channel_key": "in-app",
                    "name": "In-app onboarding",
                    "template": {
                        "body": "**Welcome {{ recipient.name }}**\n\nVisit [your onboarding link]({{ data.onboarding_url }}).",
                    },
                },
                {
                    "ref": "delay_1",
                    "type": "delay",
                    "name": "Wait before escalation",
                    "settings": {
                        "delay_for": {"unit": "minutes", "value": 5}
                    },
                },
                {
                    "ref": "email_1",
                    "type": "channel",
                    "channel_key": "mailtrap",
                    "name": "Email escalation",
                    "conditions": [
                        {
                            "variable": "refs.in_app_feed_1.engagement_status",
                            "operator": "not_contains",
                            "argument": "$message.seen",
                        }
                    ],
                    "template": {
                        "subject": "Continue onboarding, {{ recipient.name }}",
                        "html": "<p>Hello {{ recipient.name }},</p><p>Continue onboarding here: <a href=\"{{ data.onboarding_url }}\">Onboarding</a>.</p>",
                    },
                },
            ],
        }
    }

    upsert_url = f"{BASE_URL}/v1/workflows/{workflow_key}?environment=development"
    status, body = request("PUT", upsert_url, token, workflow_payload)
    print(f"Upsert status: {status}")
    print(body)

    activate_url = f"{BASE_URL}/v1/workflows/{workflow_key}/activate?environment=development"
    activate_payload = {"status": True}
    activate_status, activate_body = request("PUT", activate_url, token, activate_payload)
    print(f"Activate status: {activate_status}")
    print(activate_body)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
