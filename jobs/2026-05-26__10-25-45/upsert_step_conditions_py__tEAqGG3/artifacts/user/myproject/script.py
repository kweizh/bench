import os
import requests
import json

def main():
    run_id = os.environ.get("ZEALT_RUN_ID", "default")
    workflow_key = f"escalation-{run_id}"
    token = os.environ.get("KNOCK_SERVICE_TOKEN")
    
    if not token:
        print("KNOCK_SERVICE_TOKEN is not set")
        return

    base_url = "https://control.knock.app"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    workflow_payload = {
        "workflow": {
            "name": f"Escalation Workflow {run_id}",
            "key": workflow_key,
            "trigger_data_json_schema": {
                "type": "object",
                "properties": {
                    "onboarding_url": {
                        "type": "string"
                    }
                },
                "required": ["onboarding_url"]
            },
            "steps": [
                {
                    "ref": "in_app_feed_1",
                    "type": "channel",
                    "channel_key": "in-app",
                    "template": {
                        "markdown_body": "Hello {{ recipient.name }}, please check out {{ data.onboarding_url }}",
                        "action_url": "{{ data.onboarding_url }}"
                    }
                },
                {
                    "ref": "delay_1",
                    "type": "delay",
                    "settings": {
                        "delay_for": {
                            "unit": "minutes",
                            "value": 5
                        }
                    }
                },
                {
                    "ref": "email_1",
                    "type": "channel",
                    "channel_key": "mailtrap",
                    "conditions": {
                        "all": [
                            {
                                "variable": "refs.in_app_feed_1.engagement_status",
                                "operator": "not_contains",
                                "argument": "$message.seen"
                            }
                        ]
                    },
                    "template": {
                        "subject": "Action Required",
                        "html_body": "<p>Hello {{ recipient.name }}, please check out <a href='{{ data.onboarding_url }}'>{{ data.onboarding_url }}</a></p>",
                        "settings": {
                            "layout_key": "default"
                        }
                    }
                }
            ]
        }
    }

    # Upsert
    upsert_url = f"{base_url}/v1/workflows/{workflow_key}?environment=development"
    upsert_resp = requests.put(upsert_url, headers=headers, json=workflow_payload)
    
    print(f"Upsert status: {upsert_resp.status_code}")
    if not upsert_resp.ok:
        print(f"Upsert failed: {upsert_resp.text}")
        return

    # Activate
    activate_url = f"{base_url}/v1/workflows/{workflow_key}/activate?environment=development"
    activate_resp = requests.put(activate_url, headers=headers, json={"status": True})
    
    print(f"Activate status: {activate_resp.status_code}")
    if not activate_resp.ok:
        print(f"Activate failed: {activate_resp.text}")
        return

    # Write log
    with open("/home/user/myproject/output.log", "w") as f:
        f.write(f"Workflow key: {workflow_key}\n")
        f.write("Active: true\n")
        f.write(f"Upsert response: {upsert_resp.status_code}\n")
        f.write(f"Activate response: {activate_resp.status_code}\n")

if __name__ == "__main__":
    main()
