import json
import os
import re
import time
from email.header import decode_header, make_header

import pytest
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

LOG_FILE = "/home/user/myproject/output.log"
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
KNOCK_MAPI_BASE = "https://control.knock.app"


def _run_id() -> str:
    value = os.environ.get("ZEALT_RUN_ID")
    assert value, "ZEALT_RUN_ID environment variable must be set."
    return value


def _workflow_key() -> str:
    return f"top-level-conditions-{_run_id()}"


def _expected_subject() -> str:
    return f"Admin alert {_run_id()}"


def _admin_email_local() -> str:
    return f"admin-{_run_id()}"


def _viewer_email_local() -> str:
    return f"viewer-{_run_id()}"


def _gmail_address(local_suffix: str) -> str:
    gmail_user = os.environ["GMAIL_USER_NAME"]
    return f"{gmail_user}+{local_suffix}@gmail.com"


def _decode_header(value: str) -> str:
    if not value:
        return ""
    return str(make_header(decode_header(value)))


def _get_header(headers, name):
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return _decode_header(header.get("value", ""))
    return ""


def _gmail_service():
    token_info = json.loads(os.environ["GMAIL_TOKEN_JSON"])
    creds = Credentials.from_authorized_user_info(token_info, GMAIL_SCOPES)
    return build("gmail", "v1", credentials=creds)


def _list_inbox_messages_matching(service, subject: str, max_results: int = 50):
    """Return a list of (to_header, subject) tuples for inbox messages with the
    exact `subject` value."""
    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=f'label:inbox subject:"{subject}"',
            maxResults=max_results,
        )
        .execute()
    )
    messages = response.get("messages", []) or []
    matched = []
    for msg in messages:
        detail = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["To", "Subject"],
            )
            .execute()
        )
        headers = detail.get("payload", {}).get("headers", [])
        msg_subject = _get_header(headers, "Subject")
        msg_to = _get_header(headers, "To")
        if msg_subject == subject:
            matched.append((msg_to, msg_subject))
    return matched


def test_output_log_contains_workflow_run_id():
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(
        r"^Workflow run ID: ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$",
        content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected a line matching 'Workflow run ID: <uuid>' in {LOG_FILE}, "
        f"got contents:\n{content}"
    )


def test_workflow_active_with_top_level_conditions():
    service_token = os.environ.get("KNOCK_SERVICE_TOKEN")
    assert service_token, "KNOCK_SERVICE_TOKEN must be set for verification."

    workflow_key = _workflow_key()
    url = f"{KNOCK_MAPI_BASE}/v1/workflows/{workflow_key}"
    response = requests.get(
        url,
        params={"environment": "development"},
        headers={"Authorization": f"Bearer {service_token}"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Expected HTTP 200 fetching workflow '{workflow_key}', got "
        f"{response.status_code}: {response.text}"
    )
    body = response.json()
    workflow = body.get("workflow", body)

    assert workflow.get("active") is True, (
        f"Workflow '{workflow_key}' must be active in development; "
        f"got active={workflow.get('active')}."
    )

    conditions = workflow.get("conditions")
    assert isinstance(conditions, dict), (
        f"Workflow conditions must be a ConditionGroup object, got: {conditions!r}"
    )
    all_rules = conditions.get("all")
    assert isinstance(all_rules, list) and len(all_rules) == 1, (
        f"Workflow conditions.all must contain exactly one rule, got: {all_rules!r}"
    )
    rule = all_rules[0]
    assert rule.get("variable") == "recipient.role", (
        f"Condition variable must be 'recipient.role', got: {rule.get('variable')!r}"
    )
    assert rule.get("operator") == "equal_to", (
        f"Condition operator must be 'equal_to', got: {rule.get('operator')!r}"
    )
    assert rule.get("argument") == "admin", (
        f"Condition argument must be 'admin', got: {rule.get('argument')!r}"
    )


def test_workflow_has_single_mailtrap_step_with_expected_subject():
    service_token = os.environ.get("KNOCK_SERVICE_TOKEN")
    assert service_token, "KNOCK_SERVICE_TOKEN must be set for verification."

    workflow_key = _workflow_key()
    url = f"{KNOCK_MAPI_BASE}/v1/workflows/{workflow_key}"
    response = requests.get(
        url,
        params={"environment": "development"},
        headers={"Authorization": f"Bearer {service_token}"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Expected HTTP 200 fetching workflow '{workflow_key}', got "
        f"{response.status_code}: {response.text}"
    )
    body = response.json()
    workflow = body.get("workflow", body)

    steps = workflow.get("steps") or []
    assert len(steps) == 1, (
        f"Workflow must contain exactly one step, got {len(steps)} steps: {steps!r}"
    )
    step = steps[0]
    assert step.get("type") == "channel", (
        f"The single workflow step must have type 'channel', got: {step.get('type')!r}"
    )
    assert step.get("channel_key") == "mailtrap", (
        f"The channel step must use channel_key 'mailtrap', got: "
        f"{step.get('channel_key')!r}"
    )
    template = step.get("template") or {}
    expected_subject = _expected_subject()
    assert template.get("subject") == expected_subject, (
        f"Email template subject must be '{expected_subject}', got: "
        f"{template.get('subject')!r}"
    )


def test_admin_received_email_but_viewer_did_not():
    service = _gmail_service()
    expected_subject = _expected_subject()
    admin_address = _gmail_address(_admin_email_local())
    viewer_address = _gmail_address(_viewer_email_local())

    deadline = time.time() + 180  # up to 3 minutes for Mailtrap → Gmail delivery
    matched = []
    while time.time() < deadline:
        matched = _list_inbox_messages_matching(service, expected_subject)
        if matched:
            break
        time.sleep(5)

    assert matched, (
        f"Did not find any inbox message with subject '{expected_subject}' "
        f"after polling for delivery."
    )

    admin_hits = [t for (t, _s) in matched if admin_address in t]
    viewer_hits = [t for (t, _s) in matched if viewer_address in t]

    assert len(admin_hits) >= 1, (
        f"Expected at least one Gmail message addressed to {admin_address} "
        f"with subject '{expected_subject}', got recipients: "
        f"{[t for (t, _s) in matched]!r}"
    )
    assert not viewer_hits, (
        f"Expected NO Gmail messages addressed to {viewer_address} with subject "
        f"'{expected_subject}' (the workflow's top-level condition should have "
        f"prevented delivery), but found: {viewer_hits!r}"
    )
