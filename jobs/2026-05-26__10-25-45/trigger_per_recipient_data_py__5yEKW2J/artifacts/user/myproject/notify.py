"""
Knock per-recipient workflow: upsert, activate, commit, and trigger.

Reads configuration from environment variables:
  ZEALT_RUN_ID        - run identifier used to namespace all resources
  KNOCK_SERVICE_TOKEN - Management API service token
  KNOCK_API_TOKEN     - Backend SDK API key
  GMAIL_USER_NAME     - Gmail username (without @gmail.com)
"""

import os
import requests
from knockapi import Knock

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RUN_ID = os.environ["ZEALT_RUN_ID"]
SERVICE_TOKEN = os.environ["KNOCK_SERVICE_TOKEN"]
API_TOKEN = os.environ["KNOCK_API_TOKEN"]
GMAIL_USER = os.environ["GMAIL_USER_NAME"]

MGMT_BASE = "https://control.knock.app/v1"
MGMT_HEADERS = {
    "Authorization": f"Bearer {SERVICE_TOKEN}",
    "Content-Type": "application/json",
}

WORKFLOW_KEY = f"per-recipient-alert-{RUN_ID}"
LOG_FILE = os.path.join(os.path.dirname(__file__), "output.log")


def mgmt_upsert_workflow() -> dict:
    """Create or update the workflow via the Knock Management API."""
    url = f"{MGMT_BASE}/workflows/{WORKFLOW_KEY}"
    payload = {
        "workflow": {
            "name": f"Per-Recipient Alert {RUN_ID}",
            "steps": [
                {
                    "type": "channel",
                    "ref": "email_1",
                    "channel_key": "mailtrap",
                    "channel_type": "email",
                    "template": {
                        "subject": "Alert: {{ data.alert_type }} for {{ data.role }}",
                        "html_body": (
                            "<p>Hello {{ recipient.name }},</p>"
                            "<p>A <strong>{{ data.alert_type }}</strong> alert has been triggered.</p>"
                            "<p>Role: <strong>{{ data.role }}</strong></p>"
                            "<p>Dashboard: <a href=\"{{ data.dashboard_url }}\">{{ data.dashboard_url }}</a></p>"
                        ),
                        "text_body": (
                            "Hello {{ recipient.name }},\n\n"
                            "A {{ data.alert_type }} alert has been triggered.\n"
                            "Role: {{ data.role }}\n"
                            "Dashboard: {{ data.dashboard_url }}"
                        ),
                        "settings": {
                            "layout_key": "default",
                        },
                    },
                }
            ],
        }
    }
    resp = requests.put(url, headers=MGMT_HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()


def mgmt_activate_workflow() -> dict:
    """Ensure the workflow is active in the development environment."""
    url = f"{MGMT_BASE}/workflows/{WORKFLOW_KEY}/activate"
    resp = requests.put(url, headers=MGMT_HEADERS, json={"active": True})
    resp.raise_for_status()
    return resp.json()


def mgmt_commit_all() -> dict:
    """Commit all pending changes in the development environment."""
    resp = requests.put(
        f"{MGMT_BASE}/commits",
        headers=MGMT_HEADERS,
        params={
            "environment": "development",
            "commit_message": f"Publish {WORKFLOW_KEY}",
        },
    )
    resp.raise_for_status()
    return resp.json()


def trigger_workflow() -> str:
    """Trigger the workflow once for both inline recipients; return workflow_run_id."""
    client = Knock(api_key=API_TOKEN)

    result = client.workflows.trigger(
        WORKFLOW_KEY,
        recipients=[
            {
                "id": f"owner-{RUN_ID}",
                "name": "John Hammond",
                "email": f"{GMAIL_USER}+r1-{RUN_ID}@gmail.com",
                "$trigger_data": {
                    "role": "Park Owner",
                    "dashboard_url": f"https://jurassicpark.com/dashboard/owner-{RUN_ID}",
                },
            },
            {
                "id": f"paleo-{RUN_ID}",
                "name": "Ellie Sattler",
                "email": f"{GMAIL_USER}+r2-{RUN_ID}@gmail.com",
                "$trigger_data": {
                    "role": "Paleobotanist",
                    "dashboard_url": f"https://jurassicpark.com/dashboard/paleo-{RUN_ID}",
                },
            },
        ],
        data={"alert_type": "security_breach"},
    )
    return result.workflow_run_id


def main():
    print(f"[1/4] Upserting workflow '{WORKFLOW_KEY}' ...")
    upsert_resp = mgmt_upsert_workflow()
    wf = upsert_resp.get("workflow", {})
    print(f"      active={wf.get('active')}, valid={wf.get('valid')}, sha={wf.get('sha', '')[:12]}...")

    print(f"[2/4] Activating workflow ...")
    act_resp = mgmt_activate_workflow()
    print(f"      active={act_resp.get('workflow', {}).get('active')}")

    print(f"[3/4] Committing all changes to development environment ...")
    commit_resp = mgmt_commit_all()
    print(f"      result={commit_resp.get('result')}")

    print(f"[4/4] Triggering workflow for 2 inline recipients ...")
    run_id = trigger_workflow()
    print(f"      workflow_run_id={run_id}")

    # Write log file
    with open(LOG_FILE, "w") as fh:
        fh.write(f"Workflow key: {WORKFLOW_KEY}\n")
        fh.write(f"Workflow run ID: {run_id}\n")
    print(f"\nLog written to {LOG_FILE}")


if __name__ == "__main__":
    main()
