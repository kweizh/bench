import os
import json
import requests

def main():
    run_id = os.environ.get("ZEALT_RUN_ID", "default")
    service_token = os.environ.get("KNOCK_SERVICE_TOKEN")
    workflow_key = f"escalation-{run_id}"
    base_url = "https://control.knock.app"
    
    headers = {
        "Authorization": f"Bearer {service_token}",
        "Content-Type": "application/json"
    }
    
    workflow_payload = {
        "workflow": {
            "name": f"Escalation Workflow {run_id}",
            "trigger_data_json_schema": {
                "type": "object",
                "properties": {
                    "onboarding_url": { "type": "string" }
                },
                "required": ["onboarding_url"]
            },
            "steps": [
                {
                    "ref": "in_app_feed_1",
                    "type": "channel",
                    "channel_key": "in-app",
                    "template": {
                        "markdown_body": "Hello {{ recipient.name }}, please complete your onboarding here: [Onboarding]({{ data.onboarding_url }})",
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
                    "template": {
                        "subject": "Don't forget to onboard!",
                        "html_body": "<p>Hi {{ recipient.name }},</p><p>We noticed you haven't seen your in-app notification. Please click <a href='{{ data.onboarding_url }}'>here</a> to complete your onboarding.</p>",
                        "settings": {}
                    },
                    "conditions": {
                        "all": [
                            {
                                "variable": "refs.in_app_feed_1.engagement_status",
                                "operator": "not_contains",
                                "argument": "$message.seen"
                            }
                        ]
                    }
                }
            ]
        }
    }
    
    # Upsert workflow
    upsert_url = f"{base_url}/v1/workflows/{workflow_key}?environment=development"
    response = requests.put(upsert_url, headers=headers, json=workflow_payload)
    response.raise_for_status()
    
    # Activate workflow
    activate_url = f"{base_url}/v1/workflows/{workflow_key}/activate?environment=development"
    activate_response = requests.put(activate_url, headers=headers, json={"status": True})
    activate_response.raise_for_status()
    
    res_json = activate_response.json()
    workflow_data = res_json.get("workflow", {})
    active_status = workflow_data.get("active", False)
    
    log_path = "/home/user/myproject/output.log"
    with open(log_path, "w") as f:
        f.write(f"Workflow key: {workflow_key}\n")
        f.write(f"Active: {str(active_status).lower()}\n")

if __name__ == "__main__":
    main()
