import json
import os
import re
import time
import uuid

import pytest
import requests

PROJECT_DIR = "/home/user/cancel_task"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
MGMT_BASE = "https://control.knock.app"
API_BASE = "https://api.knock.app"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID is not set in the verifier environment."
    return run_id


def _workflow_key() -> str:
    return f"cancel-flow-{_run_id()}"


def _cancellation_key() -> str:
    return f"cancel-{_run_id()}"


def _gmail_user_name() -> str:
    user = os.environ.get("GMAIL_USER_NAME")
    assert user, "GMAIL_USER_NAME is not set in the verifier environment."
    return user


def _gmail_address() -> str:
    return f"{_gmail_user_name()}+receiver-{_run_id()}@gmail.com"


def _mailtrap_domain() -> str:
    domain = os.environ.get("MAILTRAP_DOMAIN")
    assert domain, "MAILTRAP_DOMAIN is not set in the verifier environment."
    return domain


def _sender_address() -> str:
    return f"sender-{_run_id()}@{_mailtrap_domain()}"


def _read_log() -> str:
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()


def _extract_log_value(content: str, prefix: str) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}\s*(.+)\s*$", re.MULTILINE)
    match = pattern.search(content)
    assert match, f"Log file is missing a line starting with '{prefix}'."
    return match.group(1).strip()


def _assert_uuid(value: str, label: str) -> None:
    try:
        uuid.UUID(value)
    except ValueError:
        pytest.fail(f"{label} '{value}' is not a valid UUID.")


def _mgmt_headers() -> dict:
    token = os.environ.get("KNOCK_SERVICE_TOKEN")
    assert token, "KNOCK_SERVICE_TOKEN is not set in the verifier environment."
    return {"Authorization": f"Bearer {token}"}


def _api_headers() -> dict:
    token = os.environ.get("KNOCK_API_TOKEN")
    assert token, "KNOCK_API_TOKEN is not set in the verifier environment."
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Log file verification
# ---------------------------------------------------------------------------


def test_log_file_records_workflow_key():
    content = _read_log()
    value = _extract_log_value(content, "Workflow Key:")
    assert value == _workflow_key(), (
        f"Expected log to contain 'Workflow Key: {_workflow_key()}', got '{value}'."
    )


def test_log_file_records_workflow_run_id():
    content = _read_log()
    value = _extract_log_value(content, "Workflow Run ID:")
    _assert_uuid(value, "Workflow Run ID")


def test_log_file_records_cancellation_key():
    content = _read_log()
    value = _extract_log_value(content, "Cancellation Key:")
    assert value == _cancellation_key(), (
        f"Expected log to contain 'Cancellation Key: {_cancellation_key()}', got '{value}'."
    )


def test_log_file_records_recipient_email():
    content = _read_log()
    value = _extract_log_value(content, "Recipient Email:")
    assert value == _gmail_address(), (
        f"Expected log to contain 'Recipient Email: {_gmail_address()}', got '{value}'."
    )


# ---------------------------------------------------------------------------
# Workflow verification (Management API)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def fetched_workflow() -> dict:
    url = f"{MGMT_BASE}/v1/workflows/{_workflow_key()}"
    response = requests.get(
        url,
        headers=_mgmt_headers(),
        params={"environment": "development"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Failed to fetch workflow {_workflow_key()}: "
        f"{response.status_code} {response.text}"
    )
    body = response.json()
    return body.get("workflow", body)


def test_workflow_exists_in_development(fetched_workflow):
    assert fetched_workflow.get("key") == _workflow_key(), (
        f"Expected workflow key '{_workflow_key()}', got '{fetched_workflow.get('key')}'."
    )


def test_workflow_is_active(fetched_workflow):
    assert fetched_workflow.get("active") is True, (
        "Workflow must be active in the development environment."
    )


def _delay_total_seconds(step: dict) -> float:
    settings = step.get("settings") or {}
    delay_for = settings.get("delay_for") or step.get("delay_for") or {}
    unit = (delay_for.get("unit") or "").lower()
    value = delay_for.get("value")
    if not isinstance(value, (int, float)):
        return 0.0
    multipliers = {
        "seconds": 1,
        "second": 1,
        "minutes": 60,
        "minute": 60,
        "hours": 3600,
        "hour": 3600,
        "days": 86400,
        "day": 86400,
        "weeks": 604800,
        "week": 604800,
    }
    return float(value) * multipliers.get(unit, 0)


def test_workflow_has_delay_then_mailtrap_email(fetched_workflow):
    steps = fetched_workflow.get("steps") or []
    assert steps, "Workflow does not expose any steps."

    delay_index = None
    for idx, step in enumerate(steps):
        if step.get("type") == "delay":
            seconds = _delay_total_seconds(step)
            if seconds >= 30:
                delay_index = idx
                break
    assert delay_index is not None, (
        "Workflow must contain a 'delay' function step of at least 30 seconds "
        "(so the run can be cancelled before email delivery)."
    )

    has_mailtrap_after_delay = False
    for step in steps[delay_index + 1 :]:
        if step.get("type") == "channel" and (step.get("channel_key") or "") == "mailtrap":
            has_mailtrap_after_delay = True
            break
    assert has_mailtrap_after_delay, (
        "Workflow must contain an email channel step bound to channel_key 'mailtrap' "
        "AFTER the delay step."
    )


# ---------------------------------------------------------------------------
# Workflow run verification (Knock public API)
# ---------------------------------------------------------------------------


def _list_messages_for_run(run_id: str, timeout_seconds: int = 30) -> list:
    """Best-effort listing of messages for a workflow run id."""
    url = f"{API_BASE}/v1/messages"
    deadline = time.time() + timeout_seconds
    last_items: list = []
    while time.time() < deadline:
        response = requests.get(
            url,
            headers=_api_headers(),
            params={"workflow_run_id": run_id, "page_size": 50},
            timeout=30,
        )
        if response.status_code != 200:
            time.sleep(2)
            continue
        body = response.json()
        items = body.get("items") or body.get("entries") or []
        last_items = items
        # Stop early once we've waited long enough to be confident no message
        # is going to be delivered.
        time.sleep(3)
    return last_items


def _message_delivery_status(message: dict) -> str:
    return (
        message.get("delivery_status")
        or message.get("status")
        or ""
    ).lower()


def test_workflow_run_did_not_deliver_email():
    content = _read_log()
    workflow_run_id = _extract_log_value(content, "Workflow Run ID:")
    # Wait for the delay window (>=30s) to fully elapse and any cancellation
    # to be reconciled before inspecting message state.
    time.sleep(45)

    messages = _list_messages_for_run(workflow_run_id, timeout_seconds=30)

    # Either no messages were ever produced for this run, or none of them
    # reached a delivered/sent state.
    delivered_states = {"sent", "delivered", "seen", "read"}
    delivered = [
        m
        for m in messages
        if _message_delivery_status(m) in delivered_states
    ]
    assert not delivered, (
        f"Workflow run {workflow_run_id} unexpectedly produced delivered messages: "
        f"{delivered}. The cancellation should have prevented email delivery."
    )


# ---------------------------------------------------------------------------
# Gmail inbox verification (third-party integration)
# ---------------------------------------------------------------------------


def _gmail_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    token_json = os.environ.get("GMAIL_TOKEN_JSON")
    assert token_json, "GMAIL_TOKEN_JSON is not set in the verifier environment."
    creds = Credentials.from_authorized_user_info(
        json.loads(token_json),
        ["https://www.googleapis.com/auth/gmail.readonly"],
    )
    return build("gmail", "v1", credentials=creds)


def _find_matching_gmail_messages():
    service = _gmail_service()
    address = _gmail_address()
    sender = _sender_address()
    query = f'to:{address} from:"{sender}"'
    response = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=10)
        .execute()
    )
    return response.get("messages", []) or []


def test_no_email_arrived_in_gmail_inbox():
    # Allow generous wait time well past the workflow's >=30s delay
    # so that, if cancellation failed, the email would have arrived.
    poll_until = time.time() + 120
    matches: list = []
    while time.time() < poll_until:
        matches = _find_matching_gmail_messages()
        if matches:
            break
        time.sleep(10)

    assert not matches, (
        f"Found {len(matches)} email(s) in the Gmail inbox of {_gmail_address()} "
        f"from {_sender_address()}; the workflow cancellation should have "
        "prevented delivery."
    )
