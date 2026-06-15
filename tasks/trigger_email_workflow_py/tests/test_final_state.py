import json
import os
import re
import time
from email.header import decode_header, make_header

import pytest
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PROJECT_DIR = "/home/user/knock_task"
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")

KNOCK_MAPI_BASE = "https://control.knock.app/v1"
KNOCK_API_BASE = "https://api.knock.app/v1"

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _run_id():
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, "ZEALT_RUN_ID must be set in the verifier environment."
    return rid


def _service_token():
    token = os.environ.get("KNOCK_SERVICE_TOKEN")
    assert token, "KNOCK_SERVICE_TOKEN must be set in the verifier environment."
    return token


def _api_token():
    token = os.environ.get("KNOCK_API_TOKEN")
    assert token, "KNOCK_API_TOKEN must be set in the verifier environment."
    return token


def _gmail_user_name():
    name = os.environ.get("GMAIL_USER_NAME")
    assert name, "GMAIL_USER_NAME must be set in the verifier environment."
    return name


def _read_log():
    assert os.path.isfile(LOG_PATH), f"Expected log file {LOG_PATH} to exist."
    with open(LOG_PATH) as f:
        return f.read()


def _decode_header(value: str) -> str:
    if not value:
        return ""
    return str(make_header(decode_header(value)))


def _get_header(headers, name):
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return _decode_header(h.get("value", ""))
    return ""


def test_log_file_contains_workflow_key():
    run_id = _run_id()
    content = _read_log()
    expected = f"Workflow key: welcome-email-{run_id}"
    assert expected in content, (
        f"Expected the log to contain '{expected}', got:\n{content}"
    )


def test_log_file_contains_workflow_run_id():
    content = _read_log()
    match = re.search(
        r"Workflow run id:\s*([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
        content,
    )
    assert match, (
        "Expected the log to contain 'Workflow run id: <uuid>' where <uuid> is a UUID. "
        f"Log content:\n{content}"
    )


def test_log_file_contains_recipient_id():
    run_id = _run_id()
    content = _read_log()
    expected = f"Recipient id: user-{run_id}"
    assert expected in content, (
        f"Expected the log to contain '{expected}', got:\n{content}"
    )


def test_log_file_contains_recipient_email():
    run_id = _run_id()
    gmail = _gmail_user_name()
    content = _read_log()
    expected = f"Recipient email: {gmail}+receiver-{run_id}@gmail.com"
    assert expected in content, (
        f"Expected the log to contain '{expected}', got:\n{content}"
    )


def test_knock_workflow_exists_and_active():
    run_id = _run_id()
    workflow_key = f"welcome-email-{run_id}"
    url = f"{KNOCK_MAPI_BASE}/workflows/{workflow_key}"
    resp = requests.get(
        url,
        params={"environment": "development"},
        headers={"Authorization": f"Bearer {_service_token()}"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"Expected workflow {workflow_key} to be retrievable (status 200), got "
        f"{resp.status_code}: {resp.text}"
    )
    body = resp.json()
    # The Management API wraps workflow in a "workflow" object or returns it flat;
    # support both shapes.
    workflow = body.get("workflow", body)
    assert workflow.get("active") is True, (
        f"Workflow {workflow_key} must be active in development. Response: {body}"
    )
    steps = workflow.get("steps") or []
    assert len(steps) == 1, (
        f"Workflow {workflow_key} must have exactly one step, got {len(steps)}: {steps}"
    )
    step = steps[0]
    assert step.get("type") == "channel", (
        f"Workflow step must be of type 'channel', got: {step}"
    )
    assert step.get("channel_key") == "mailtrap", (
        f"Workflow step must use the 'mailtrap' channel_key, got: {step}"
    )
    assert step.get("ref") == "welcome_email", (
        f"Workflow step ref must be 'welcome_email', got: {step}"
    )


def test_knock_user_identified_with_email():
    run_id = _run_id()
    user_id = f"user-{run_id}"
    url = f"{KNOCK_API_BASE}/users/{user_id}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {_api_token()}"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"Expected user {user_id} to exist in Knock (status 200), got "
        f"{resp.status_code}: {resp.text}"
    )
    body = resp.json()
    expected_email = f"{_gmail_user_name()}+receiver-{run_id}@gmail.com"
    assert body.get("email") == expected_email, (
        f"Expected user.email to be '{expected_email}', got: {body}"
    )
    assert run_id in (body.get("name") or ""), (
        f"Expected user.name to include the run id '{run_id}', got: {body}"
    )


def test_knock_user_message_for_workflow():
    run_id = _run_id()
    user_id = f"user-{run_id}"
    workflow_key = f"welcome-email-{run_id}"
    url = f"{KNOCK_API_BASE}/users/{user_id}/messages"
    headers = {"Authorization": f"Bearer {_api_token()}"}

    deadline = time.time() + 90
    last_payload = None
    matched = None
    while time.time() < deadline:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            last_payload = resp.json()
            items = last_payload.get("items") or last_payload.get("entries") or []
            for item in items:
                source = item.get("source") or {}
                if source.get("key") == workflow_key:
                    matched = item
                    break
            if matched:
                break
        time.sleep(5)

    assert matched is not None, (
        f"Expected at least one Knock message for user {user_id} from workflow "
        f"{workflow_key}. Last response: {last_payload}"
    )

    status = matched.get("status")
    assert status in {"sent", "delivered", "delivery_attempted", "queued"}, (
        f"Unexpected message status '{status}' for workflow {workflow_key}: {matched}"
    )


def test_email_received_in_gmail_inbox():
    run_id = _run_id()
    gmail_user = _gmail_user_name()
    expected_to_fragment = f"{gmail_user}+receiver-{run_id}@gmail.com"
    expected_subject_fragment = f"Welcome to Knock, Knock User {run_id}!"

    token_info = json.loads(os.environ["GMAIL_TOKEN_JSON"])
    creds = Credentials.from_authorized_user_info(token_info, GMAIL_SCOPES)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    deadline = time.time() + 120
    matched = None
    last_inbox = []
    while time.time() < deadline:
        query = f"to:{expected_to_fragment}"
        response = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=20)
            .execute()
        )
        last_inbox = response.get("messages", []) or []
        for msg in last_inbox:
            detail = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg["id"],
                    format="metadata",
                    metadataHeaders=["From", "To", "Subject", "Date"],
                )
                .execute()
            )
            headers = detail.get("payload", {}).get("headers", [])
            to_header = _get_header(headers, "To")
            subject = _get_header(headers, "Subject")
            if expected_to_fragment in to_header and expected_subject_fragment in subject:
                matched = {"to": to_header, "subject": subject}
                break
        if matched:
            break
        time.sleep(10)

    assert matched is not None, (
        "Expected an email in the Gmail inbox addressed to "
        f"'{expected_to_fragment}' with subject containing "
        f"'{expected_subject_fragment}'. Found {len(last_inbox)} candidate(s)."
    )
