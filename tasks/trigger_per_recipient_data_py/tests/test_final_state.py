import base64
import json
import os
import re
import time
from email.header import decode_header, make_header

import pytest
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")

RUN_ID = os.environ.get("ZEALT_RUN_ID", "")
WORKFLOW_KEY = f"per-recipient-alert-{RUN_ID}"

OWNER_DASHBOARD_URL = f"https://jurassicpark.com/dashboard/owner-{RUN_ID}"
PALEO_DASHBOARD_URL = f"https://jurassicpark.com/dashboard/paleo-{RUN_ID}"

UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
GMAIL_POLL_TIMEOUT_SECONDS = 240
GMAIL_POLL_INTERVAL_SECONDS = 15


def _decode_mime_header(value: str) -> str:
    if not value:
        return ""
    return str(make_header(decode_header(value)))


def _get_header(headers, name):
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return _decode_mime_header(header.get("value", ""))
    return ""


def _decode_body_data(data: str) -> str:
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    try:
        decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
    except Exception:
        return ""
    try:
        return decoded.decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_body_text(payload) -> str:
    if not payload:
        return ""
    parts_text = []
    body = payload.get("body") or {}
    if body.get("data"):
        parts_text.append(_decode_body_data(body["data"]))
    for part in payload.get("parts", []) or []:
        parts_text.append(_extract_body_text(part))
    return "\n".join(filter(None, parts_text))


def _gmail_service():
    token_info = json.loads(os.environ["GMAIL_TOKEN_JSON"])
    creds = Credentials.from_authorized_user_info(token_info, GMAIL_SCOPES)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _search_gmail_message(service, recipient_address: str):
    """Return the first inbox message addressed to recipient_address, or None."""
    query = f"to:{recipient_address}"
    response = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=20)
        .execute()
    )
    for msg in response.get("messages", []) or []:
        detail = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )
        payload = detail.get("payload", {})
        headers = payload.get("headers", [])
        to_header = _get_header(headers, "To").lower()
        if recipient_address.lower() in to_header:
            subject = _get_header(headers, "Subject")
            body = _extract_body_text(payload)
            return {"subject": subject, "body": body, "to": to_header}
    return None


def _wait_for_gmail_message(recipient_address: str):
    service = _gmail_service()
    deadline = time.time() + GMAIL_POLL_TIMEOUT_SECONDS
    last_err = None
    while time.time() < deadline:
        try:
            match = _search_gmail_message(service, recipient_address)
            if match is not None:
                return match
        except Exception as exc:  # noqa: BLE001
            last_err = exc
        time.sleep(GMAIL_POLL_INTERVAL_SECONDS)
    raise AssertionError(
        f"No Gmail message addressed to {recipient_address} found within "
        f"{GMAIL_POLL_TIMEOUT_SECONDS} seconds (last error: {last_err})."
    )


@pytest.fixture(scope="module")
def log_contents():
    assert os.path.isfile(LOG_FILE), (
        f"Expected the task to produce a log file at {LOG_FILE}, but it does not exist."
    )
    with open(LOG_FILE, "r", encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def gmail_user_name():
    value = os.environ.get("GMAIL_USER_NAME")
    assert value, "GMAIL_USER_NAME environment variable is not set."
    return value


@pytest.fixture(scope="module")
def owner_address(gmail_user_name):
    return f"{gmail_user_name}+r1-{RUN_ID}@gmail.com"


@pytest.fixture(scope="module")
def paleo_address(gmail_user_name):
    return f"{gmail_user_name}+r2-{RUN_ID}@gmail.com"


@pytest.fixture(scope="module")
def owner_message(owner_address):
    return _wait_for_gmail_message(owner_address)


@pytest.fixture(scope="module")
def paleo_message(paleo_address):
    return _wait_for_gmail_message(paleo_address)


@pytest.fixture(scope="module")
def workflow_payload():
    token = os.environ.get("KNOCK_SERVICE_TOKEN")
    assert token, "KNOCK_SERVICE_TOKEN environment variable is not set."
    url = f"https://control.knock.app/v1/workflows/{WORKFLOW_KEY}"
    response = requests.get(
        url,
        params={"environment": "development"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Expected GET {url} to return 200, got {response.status_code}: {response.text}"
    )
    return response.json()


def test_log_file_contains_workflow_key(log_contents):
    expected_line = f"Workflow key: {WORKFLOW_KEY}"
    assert expected_line in log_contents, (
        f"Expected log file {LOG_FILE} to contain the line '{expected_line}'. "
        f"Got contents:\n{log_contents}"
    )


def test_log_file_contains_workflow_run_id(log_contents):
    match = re.search(r"Workflow run ID:\s*([0-9a-fA-F-]+)", log_contents)
    assert match, (
        f"Expected log file {LOG_FILE} to contain a line like 'Workflow run ID: <uuid>'. "
        f"Got contents:\n{log_contents}"
    )
    assert UUID_RE.fullmatch(match.group(1)), (
        f"Expected the workflow run ID to be a UUID v4 formatted string, got '{match.group(1)}'."
    )


def test_workflow_exists_and_is_active(workflow_payload):
    workflow = workflow_payload.get("workflow", workflow_payload)
    key = workflow.get("key") or workflow_payload.get("key")
    assert key == WORKFLOW_KEY, (
        f"Expected the workflow key to be '{WORKFLOW_KEY}', got '{key}'."
    )
    active = workflow.get("active")
    if active is None:
        status = (workflow.get("status") or "").lower()
        assert status in ("active", "live"), (
            f"Expected the workflow to be active in development, got status '{status}'."
        )
    else:
        assert active, (
            "Expected the workflow to be active in the development environment."
        )


def test_workflow_has_single_mailtrap_channel_step(workflow_payload):
    workflow = workflow_payload.get("workflow", workflow_payload)
    steps = workflow.get("steps") or []
    channel_steps = [
        s for s in steps if (s.get("type") or "").lower() == "channel"
    ]
    assert len(channel_steps) == 1, (
        f"Expected exactly one channel step in the workflow, got {len(channel_steps)}: "
        f"{steps}"
    )
    step = channel_steps[0]
    channel_key = step.get("channel_key") or step.get("channelKey")
    assert channel_key == "mailtrap", (
        f"Expected the channel step's channel_key to be 'mailtrap', got '{channel_key}'."
    )


def test_workflow_template_references_per_recipient_data(workflow_payload):
    workflow = workflow_payload.get("workflow", workflow_payload)
    serialized = json.dumps(workflow)
    assert "data.role" in serialized, (
        "Expected the workflow's email template to reference 'data.role' (e.g. {{ data.role }})."
    )
    assert "data.dashboard_url" in serialized, (
        "Expected the workflow's email template to reference 'data.dashboard_url' "
        "(e.g. {{ data.dashboard_url }})."
    )


def test_owner_email_subject_mentions_role(owner_message):
    assert "Park Owner" in owner_message["subject"], (
        f"Expected the owner's email subject to mention 'Park Owner'. "
        f"Got subject: {owner_message['subject']!r}"
    )


def test_owner_email_body_mentions_role_and_dashboard(owner_message):
    body = owner_message["body"]
    assert "Park Owner" in body, (
        f"Expected the owner's email body to mention 'Park Owner'. Body was:\n{body}"
    )
    assert OWNER_DASHBOARD_URL in body, (
        f"Expected the owner's email body to include the dashboard URL "
        f"'{OWNER_DASHBOARD_URL}'. Body was:\n{body}"
    )


def test_paleo_email_subject_mentions_role(paleo_message):
    assert "Paleobotanist" in paleo_message["subject"], (
        f"Expected the paleobotanist's email subject to mention 'Paleobotanist'. "
        f"Got subject: {paleo_message['subject']!r}"
    )


def test_paleo_email_body_mentions_role_and_dashboard(paleo_message):
    body = paleo_message["body"]
    assert "Paleobotanist" in body, (
        f"Expected the paleobotanist's email body to mention 'Paleobotanist'. "
        f"Body was:\n{body}"
    )
    assert PALEO_DASHBOARD_URL in body, (
        f"Expected the paleobotanist's email body to include the dashboard URL "
        f"'{PALEO_DASHBOARD_URL}'. Body was:\n{body}"
    )


def test_per_recipient_data_does_not_leak_between_recipients(owner_message, paleo_message):
    assert "Paleobotanist" not in owner_message["subject"], (
        "Owner's email subject should not mention 'Paleobotanist' (per-recipient data leaked)."
    )
    assert "Paleobotanist" not in owner_message["body"], (
        "Owner's email body should not mention 'Paleobotanist' (per-recipient data leaked)."
    )
    assert PALEO_DASHBOARD_URL not in owner_message["body"], (
        "Owner's email body should not include the paleobotanist's dashboard URL."
    )
    assert "Park Owner" not in paleo_message["subject"], (
        "Paleobotanist's email subject should not mention 'Park Owner' (per-recipient data leaked)."
    )
    assert "Park Owner" not in paleo_message["body"], (
        "Paleobotanist's email body should not mention 'Park Owner' (per-recipient data leaked)."
    )
    assert OWNER_DASHBOARD_URL not in paleo_message["body"], (
        "Paleobotanist's email body should not include the owner's dashboard URL."
    )
