#!/usr/bin/env python3
"""
Knock Channel-Escalation Workflow Author
Upserts a 3-step escalation workflow (in-app → delay → email) in the Knock
development environment using the Management API, then activates it.
"""

import json
import os
import sys
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KNOCK_SERVICE_TOKEN = os.environ.get("KNOCK_SERVICE_TOKEN", "")
ZEALT_RUN_ID = os.environ.get("ZEALT_RUN_ID", "")

if not KNOCK_SERVICE_TOKEN:
    print("ERROR: KNOCK_SERVICE_TOKEN environment variable is not set.", file=sys.stderr)
    sys.exit(1)

if not ZEALT_RUN_ID:
    print("ERROR: ZEALT_RUN_ID environment variable is not set.", file=sys.stderr)
    sys.exit(1)

WORKFLOW_KEY = f"escalation-{ZEALT_RUN_ID}"
ENVIRONMENT = "development"
BASE_URL = "https://control.knock.app"
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output.log")

# ---------------------------------------------------------------------------
# Workflow definition
# ---------------------------------------------------------------------------
# Step conditions must be a ConditionGroup map, e.g. {"all": [...]} or {"any": [...]}.
# In-app feed template requires action_url (or action_buttons) alongside markdown_body.
# Email template requires settings.layout_key.

WORKFLOW_PAYLOAD = {
    "workflow": {
        "name": f"Channel Escalation – {ZEALT_RUN_ID}",
        "trigger_data_json_schema": {
            "type": "object",
            "properties": {
                "onboarding_url": {
                    "type": "string",
                    "description": "The personalised onboarding URL for the recipient."
                }
            },
            "required": ["onboarding_url"]
        },
        "steps": [
            # Step 1 – In-app feed notification
            # action_url is required by the API alongside markdown_body.
            {
                "ref": "in_app_feed_1",
                "type": "channel",
                "channel_key": "in-app",
                "template": {
                    "markdown_body": (
                        "👋 **Welcome, {{ recipient.name }}!**\n\n"
                        "Get started with your onboarding: "
                        "[Open now]({{ data.onboarding_url }})"
                    ),
                    "action_url": "{{ data.onboarding_url }}"
                }
            },
            # Step 2 – 5-minute delay
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
            # Step 3 – Email, only when in-app message has NOT been seen.
            # conditions must be a ConditionGroup map: {"all": [...]} or {"any": [...]}.
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
                    "subject": (
                        "You have a new onboarding message, {{ recipient.name }}"
                    ),
                    "html_body": (
                        "<p>Hi {{ recipient.name }},</p>"
                        "<p>We noticed you haven't had a chance to check your "
                        "in-app notification yet.</p>"
                        "<p>Get started with your personalised onboarding:</p>"
                        "<p><a href=\"{{ data.onboarding_url }}\">"
                        "{{ data.onboarding_url }}</a></p>"
                        "<p>If you have any questions, just reply to this email.</p>"
                        "<p>Cheers,<br>The Team</p>"
                    ),
                    "settings": {
                        "layout_key": "default"
                    }
                }
            }
        ]
    }
}

# ---------------------------------------------------------------------------
# Helper – JSON HTTP request
# ---------------------------------------------------------------------------

def api_request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {KNOCK_SERVICE_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            # A descriptive UA avoids Cloudflare's default-UA block.
            "User-Agent": "knock-workflow-author/1.0 (python-urllib)",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP {exc.code} {exc.reason} for {method} {url}\n{body_text}"
        ) from exc


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log(f"Workflow key: {WORKFLOW_KEY}")
    log(f"Environment:  {ENVIRONMENT}")
    log("")

    # 1. Upsert the workflow
    log("── Step 1/2: Upserting workflow …")
    upsert_path = f"/v1/workflows/{WORKFLOW_KEY}?environment={ENVIRONMENT}"
    upsert_response = api_request("PUT", upsert_path, WORKFLOW_PAYLOAD)
    log(f"Upsert response: {json.dumps(upsert_response, indent=2)}")
    log("")

    # 2. Activate the workflow
    log("── Step 2/2: Activating workflow …")
    activate_path = (
        f"/v1/workflows/{WORKFLOW_KEY}/activate?environment={ENVIRONMENT}"
    )
    activate_response = api_request("PUT", activate_path, {"status": True})
    log(f"Activate response: {json.dumps(activate_response, indent=2)}")
    log("")

    # The activate endpoint wraps the result under the "workflow" key.
    workflow_obj = activate_response.get("workflow", activate_response)
    active_bool = bool(workflow_obj.get("active", False))

    log(f"Active: {str(active_bool).lower()}")
    log("Done.")

    # Write log file
    with open(LOG_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(log_lines) + "\n")

    print(f"\nLog written to: {LOG_PATH}")


if __name__ == "__main__":
    main()
