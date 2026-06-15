import json
import os
import re
import time
import uuid

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
MGMT_BASE = "https://control.knock.app"
API_BASE = "https://api.knock.app"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID is not set in the verifier environment."
    return run_id


def _workflow_key() -> str:
    return f"branch-flow-{_run_id()}"


def _gmail_address() -> str:
    user = os.environ.get("GMAIL_USER_NAME")
    assert user, "GMAIL_USER_NAME is not set in the verifier environment."
    return f"{user}+receiver-{_run_id()}@gmail.com"


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
    key = _extract_log_value(content, "Workflow Key:")
    assert key == _workflow_key(), (
        f"Expected log to contain 'Workflow Key: {_workflow_key()}', got '{key}'."
    )


def test_log_file_records_email_run_id():
    content = _read_log()
    value = _extract_log_value(content, "Email Run ID:")
    _assert_uuid(value, "Email Run ID")


def test_log_file_records_inapp_run_id():
    content = _read_log()
    value = _extract_log_value(content, "InApp Run ID:")
    _assert_uuid(value, "InApp Run ID")


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
    # Endpoint may return the workflow at top-level or wrapped under 'workflow'.
    return body.get("workflow", body)


def test_workflow_exists_in_development(fetched_workflow):
    assert fetched_workflow.get("key") == _workflow_key(), (
        f"Expected workflow key '{_workflow_key()}', got '{fetched_workflow.get('key')}'."
    )
    assert fetched_workflow.get("environment") == "development", (
        "Workflow must be created in the development environment."
    )


def test_workflow_is_active(fetched_workflow):
    assert fetched_workflow.get("active") is True, (
        "Workflow must be active in the development environment."
    )


def _find_branch_step(workflow: dict) -> dict:
    for step in workflow.get("steps", []):
        if step.get("type") == "branch":
            return step
    pytest.fail("Workflow does not contain a top-level branch step.")


def _branches_of(branch_step: dict) -> list:
    branches = branch_step.get("branches")
    if isinstance(branches, list):
        return branches
    # Some SDK representations may nest branches under settings.
    settings = branch_step.get("settings") or {}
    if isinstance(settings.get("branches"), list):
        return settings["branches"]
    pytest.fail("Branch step does not expose a 'branches' array.")


def _step_channel_key(step: dict) -> str:
    if step.get("type") != "channel":
        return ""
    return step.get("channel_key") or ""


def _branch_nested_steps(branch: dict) -> list:
    steps = branch.get("steps")
    if isinstance(steps, list):
        return steps
    return []


def _is_default_branch(branch: dict) -> bool:
    return bool(
        branch.get("default")
        or branch.get("is_default")
        or (branch.get("name") or "").lower() == "default"
        or branch.get("conditions") in (None, {}, {"all": []}, {"any": []})
    )


def test_branch_step_has_email_branch(fetched_workflow):
    branch_step = _find_branch_step(fetched_workflow)
    branches = _branches_of(branch_step)

    email_branch_found = False
    for branch in branches:
        conditions = branch.get("conditions") or {}
        clauses = conditions.get("all") or conditions.get("any") or []
        references_channel_pref = any(
            (c.get("variable") == "data.channel_preference"
             and c.get("operator") == "equal_to"
             and c.get("argument") == "email")
            for c in clauses
        )
        if not references_channel_pref:
            continue
        nested = _branch_nested_steps(branch)
        if any(_step_channel_key(s) == "mailtrap" for s in nested):
            email_branch_found = True
            break

    assert email_branch_found, (
        "Expected a non-default branch with conditions on "
        "data.channel_preference == 'email' containing a channel step "
        "bound to channel_key 'mailtrap'."
    )


def test_branch_step_has_default_inapp_branch(fetched_workflow):
    branch_step = _find_branch_step(fetched_workflow)
    branches = _branches_of(branch_step)

    default_inapp_found = False
    for branch in branches:
        if not _is_default_branch(branch):
            continue
        nested = _branch_nested_steps(branch)
        if any(_step_channel_key(s) == "in-app" for s in nested):
            default_inapp_found = True
            break

    assert default_inapp_found, (
        "Expected a default branch containing a channel step "
        "bound to channel_key 'in-app'."
    )


# ---------------------------------------------------------------------------
# Message verification (Knock public API)
# ---------------------------------------------------------------------------


def _list_messages_for_run(run_id: str) -> list:
    """Poll the messages endpoint for a workflow run, allowing time for delivery."""
    url = f"{API_BASE}/v1/messages"
    deadline = time.time() + 60
    last_items: list = []
    while time.time() < deadline:
        response = requests.get(
            url,
            headers=_api_headers(),
            params={"workflow_run_id": run_id, "page_size": 50},
            timeout=30,
        )
        assert response.status_code == 200, (
            f"Failed to list messages for run {run_id}: "
            f"{response.status_code} {response.text}"
        )
        body = response.json()
        items = body.get("items") or body.get("entries") or []
        if items:
            return items
        last_items = items
        time.sleep(3)
    return last_items


def _message_workflow_key(message: dict) -> str:
    if message.get("workflow"):
        return message["workflow"]
    source = message.get("source") or {}
    return source.get("key", "")


def _message_channel_key(message: dict) -> str:
    # The public API exposes channel through the source object via channel_key
    # or via channel_type fallback for older payloads.
    source = message.get("source") or {}
    return (
        message.get("channel_key")
        or source.get("channel_key")
        or message.get("channel_type")
        or source.get("channel_type")
        or ""
    )


def test_email_run_produced_mailtrap_message():
    content = _read_log()
    email_run_id = _extract_log_value(content, "Email Run ID:")
    messages = _list_messages_for_run(email_run_id)
    assert messages, f"No messages were produced for the email run {email_run_id}."

    expected_key = _workflow_key()
    keys_match = [m for m in messages if _message_workflow_key(m) == expected_key]
    assert keys_match, (
        f"None of the messages for run {email_run_id} belong to workflow {expected_key}."
    )

    # In-app messages should not be produced for the email branch.
    inapp_messages = [
        m for m in keys_match if _message_channel_key(m).lower() in ("in-app", "in_app_feed")
    ]
    assert not inapp_messages, (
        f"Email run unexpectedly produced in-app messages: {inapp_messages}."
    )


def test_inapp_run_produced_in_app_message():
    content = _read_log()
    inapp_run_id = _extract_log_value(content, "InApp Run ID:")
    messages = _list_messages_for_run(inapp_run_id)
    assert messages, f"No messages were produced for the in-app run {inapp_run_id}."

    expected_key = _workflow_key()
    keys_match = [m for m in messages if _message_workflow_key(m) == expected_key]
    assert keys_match, (
        f"None of the messages for run {inapp_run_id} belong to workflow {expected_key}."
    )

    # Default branch should not produce an email message.
    email_messages = [
        m for m in keys_match if _message_channel_key(m).lower() in ("email", "mailtrap")
    ]
    assert not email_messages, (
        f"In-app run unexpectedly produced email messages: {email_messages}."
    )


# ---------------------------------------------------------------------------
# Gmail inbox verification (third-party integration)
# ---------------------------------------------------------------------------


def _gmail_service():
    from email.header import decode_header, make_header  # noqa: F401  (used indirectly)
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    token_json = os.environ.get("GMAIL_TOKEN_JSON")
    assert token_json, "GMAIL_TOKEN_JSON is not set in the verifier environment."
    creds = Credentials.from_authorized_user_info(
        json.loads(token_json),
        ["https://www.googleapis.com/auth/gmail.readonly"],
    )
    return build("gmail", "v1", credentials=creds)


def test_email_arrived_in_gmail_inbox():
    service = _gmail_service()
    address = _gmail_address()
    query = f"to:{address}"

    deadline = time.time() + 120
    while time.time() < deadline:
        response = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=5)
            .execute()
        )
        if response.get("messages"):
            return
        time.sleep(5)

    pytest.fail(
        f"No email addressed to {address} arrived in the Gmail inbox within the timeout."
    )
