import json
import os
import re
import time
from email.header import decode_header, make_header

import pytest
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PROJECT_DIR = "/home/user/tenant_task"
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")

KNOCK_MAPI_BASE = "https://control.knock.app/v1"
KNOCK_API_BASE = "https://api.knock.app/v1"

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


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


def _fetch_tenant():
    run_id = _run_id()
    tenant_id = f"tenant-{run_id}"
    url = f"{KNOCK_API_BASE}/tenants/{tenant_id}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {_api_token()}"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"Expected tenant {tenant_id} to be retrievable (status 200), got "
        f"{resp.status_code}: {resp.text}"
    )
    return resp.json()


def test_log_file_contains_tenant_id():
    run_id = _run_id()
    content = _read_log()
    expected = f"Tenant ID: tenant-{run_id}"
    assert expected in content, (
        f"Expected the log to contain '{expected}', got:\n{content}"
    )


def test_log_file_contains_workflow_key():
    run_id = _run_id()
    content = _read_log()
    expected = f"Workflow Key: tenant-welcome-{run_id}"
    assert expected in content, (
        f"Expected the log to contain '{expected}', got:\n{content}"
    )


def test_log_file_contains_workflow_run_id():
    content = _read_log()
    match = re.search(r"Workflow Run ID:\s*(" + UUID_RE.pattern + ")", content)
    assert match, (
        "Expected the log to contain 'Workflow Run ID: <uuid>' where <uuid> is a UUID. "
        f"Log content:\n{content}"
    )


def test_log_file_contains_recipient_email():
    run_id = _run_id()
    gmail = _gmail_user_name()
    content = _read_log()
    expected = f"Recipient Email: {gmail}+receiver-{run_id}@gmail.com"
    assert expected in content, (
        f"Expected the log to contain '{expected}', got:\n{content}"
    )


def test_tenant_exists_with_branding_and_custom_property():
    run_id = _run_id()
    tenant = _fetch_tenant()
    assert tenant.get("id") == f"tenant-{run_id}", (
        f"Tenant id mismatch: {tenant}"
    )
    properties = tenant.get("properties") or {}
    name = tenant.get("name") or properties.get("name") or ""
    assert run_id in name, (
        f"Tenant name must contain the run id '{run_id}', got: {name!r}"
    )
    settings = tenant.get("settings") or {}
    branding = settings.get("branding") or {}
    primary_color = branding.get("primary_color")
    assert isinstance(primary_color, str) and primary_color.startswith("#") and len(primary_color) >= 4, (
        f"Tenant settings.branding.primary_color must be a non-empty hex color, got: {primary_color!r}"
    )
    app_name = tenant.get("app_name") or properties.get("app_name")
    assert isinstance(app_name, str) and app_name.strip(), (
        f"Tenant must carry a non-empty custom property 'app_name' (either at the top level "
        f"or under 'properties'), got tenant: {tenant}"
    )


def test_knock_workflow_exists_and_uses_tenant_templating():
    run_id = _run_id()
    workflow_key = f"tenant-welcome-{run_id}"
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
    workflow = body.get("workflow", body)
    assert workflow.get("active") is True, (
        f"Workflow {workflow_key} must be active in development. Response: {body}"
    )
    steps = workflow.get("steps") or []
    assert steps, f"Workflow {workflow_key} must have at least one step, got: {steps}"

    mailtrap_steps = [
        s for s in steps
        if s.get("type") == "channel" and s.get("channel_key") == "mailtrap"
    ]
    assert mailtrap_steps, (
        f"Workflow {workflow_key} must contain at least one channel step bound to "
        f"channel_key 'mailtrap'. Got steps: {steps}"
    )

    # Serialize the whole step (including template) and check for the tenant
    # template references. This avoids assumptions about the exact template
    # field layout while still verifying the required Liquid expressions are
    # present in the email step.
    matched_step = None
    for step in mailtrap_steps:
        blob = json.dumps(step)
        if (
            "tenant.app_name" in blob
            and "tenant.name" in blob
            and "recipient.name" in blob
        ):
            matched_step = step
            break

    assert matched_step is not None, (
        "Expected the mailtrap channel step to contain a subject template "
        "referencing 'tenant.app_name' and an HTML body referencing both "
        f"'tenant.name' and 'recipient.name'. Got mailtrap steps: {mailtrap_steps}"
    )


def test_knock_user_message_tagged_with_tenant():
    run_id = _run_id()
    user_id = f"user-{run_id}"
    workflow_key = f"tenant-welcome-{run_id}"
    expected_tenant = f"tenant-{run_id}"
    url = f"{KNOCK_API_BASE}/users/{user_id}/messages"
    headers = {"Authorization": f"Bearer {_api_token()}"}

    deadline = time.time() + 120
    last_payload = None
    matched = None
    while time.time() < deadline:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            last_payload = resp.json()
            items = last_payload.get("items") or last_payload.get("entries") or []
            for item in items:
                source = item.get("source") or {}
                if source.get("key") != workflow_key:
                    continue
                # Tenant may be reported either as a string id or as a
                # tenant-shaped object. Accept either representation.
                tenant_field = item.get("tenant")
                tenant_id = None
                if isinstance(tenant_field, str):
                    tenant_id = tenant_field
                elif isinstance(tenant_field, dict):
                    tenant_id = tenant_field.get("id")
                if tenant_id == expected_tenant:
                    matched = item
                    break
            if matched:
                break
        time.sleep(5)

    assert matched is not None, (
        f"Expected at least one Knock message for user {user_id} from workflow "
        f"{workflow_key} tagged with tenant '{expected_tenant}'. "
        f"Last response: {last_payload}"
    )

    status = matched.get("status")
    assert status in {"queued", "sent", "delivered", "delivery_attempted"}, (
        f"Unexpected message status '{status}' for workflow {workflow_key}: {matched}"
    )


def test_email_received_in_gmail_inbox_contains_tenant_app_name():
    run_id = _run_id()
    gmail_user = _gmail_user_name()
    expected_to_fragment = f"{gmail_user}+receiver-{run_id}@gmail.com"

    tenant = _fetch_tenant()
    properties = tenant.get("properties") or {}
    app_name = tenant.get("app_name") or properties.get("app_name")
    assert isinstance(app_name, str) and app_name.strip(), (
        f"Tenant must expose a non-empty 'app_name' before checking Gmail. Got: {tenant}"
    )

    token_info = json.loads(os.environ["GMAIL_TOKEN_JSON"])
    creds = Credentials.from_authorized_user_info(token_info, GMAIL_SCOPES)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    deadline = time.time() + 180
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
            if expected_to_fragment in to_header and app_name in subject:
                matched = {"to": to_header, "subject": subject}
                break
        if matched:
            break
        time.sleep(10)

    assert matched is not None, (
        "Expected an email in the Gmail inbox addressed to "
        f"'{expected_to_fragment}' with subject containing the tenant app_name "
        f"'{app_name}'. Found {len(last_inbox)} candidate(s)."
    )
