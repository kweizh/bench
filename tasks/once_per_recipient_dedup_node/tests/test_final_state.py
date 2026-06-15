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

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

KNOCK_CONTROL_URL = "https://control.knock.app"


# ---------------------------------------------------------------------------
# Shared helpers / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def run_id():
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, "ZEALT_RUN_ID env var is not set; test runner misconfigured."
    return rid


@pytest.fixture(scope="module")
def workflow_key(run_id):
    return f"dedup-test-{run_id}"


@pytest.fixture(scope="module")
def workflow_payload(workflow_key):
    """Fetch the workflow from the Knock Management API and return parsed JSON."""
    service_token = os.environ.get("KNOCK_SERVICE_TOKEN")
    assert service_token, "KNOCK_SERVICE_TOKEN env var is not set."
    url = f"{KNOCK_CONTROL_URL}/v1/workflows/{workflow_key}"
    resp = requests.get(
        url,
        params={"environment": "development"},
        headers={"Authorization": f"Bearer {service_token}"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"Knock Management API GET workflow {workflow_key} returned "
        f"status {resp.status_code}: {resp.text}"
    )
    return resp.json()


def _decode_mime_header(value):
    if not value:
        return ""
    return str(make_header(decode_header(value)))


def _get_header(headers, name):
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return _decode_mime_header(h.get("value", ""))
    return ""


def _list_matching_gmail_messages(subject_substr, recipient_email, deadline_seconds=120):
    """Poll Gmail inbox until either we find at least one matching message or
    we exceed `deadline_seconds`. Returns the full list of matches seen at the
    final poll (so callers can detect over-delivery as well)."""
    token_info = json.loads(os.environ["GMAIL_TOKEN_JSON"])
    creds = Credentials.from_authorized_user_info(token_info, GMAIL_SCOPES)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    # Gmail query restricts the search server-side, dramatically cutting noise.
    query = f'label:inbox to:"{recipient_email}" subject:"{subject_substr}"'

    matches = []
    deadline = time.time() + deadline_seconds
    while True:
        resp = service.users().messages().list(
            userId="me", q=query, maxResults=25
        ).execute()
        ids = [m["id"] for m in resp.get("messages", [])]
        matches = []
        for mid in ids:
            detail = service.users().messages().get(
                userId="me",
                id=mid,
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"],
            ).execute()
            headers = detail.get("payload", {}).get("headers", [])
            entry = {
                "id": mid,
                "from": _get_header(headers, "From"),
                "to": _get_header(headers, "To"),
                "subject": _get_header(headers, "Subject"),
                "date": _get_header(headers, "Date"),
            }
            if (
                subject_substr in entry["subject"]
                and recipient_email in entry["to"]
            ):
                matches.append(entry)
        if matches:
            # Once at least one matching email has arrived, give Knock a short
            # grace period to deliver any additional (incorrect) duplicates so
            # we can detect over-delivery.
            extra_wait = min(20.0, max(0.0, deadline - time.time()))
            if extra_wait > 0:
                time.sleep(extra_wait)
            resp = service.users().messages().list(
                userId="me", q=query, maxResults=25
            ).execute()
            ids = [m["id"] for m in resp.get("messages", [])]
            matches = []
            for mid in ids:
                detail = service.users().messages().get(
                    userId="me",
                    id=mid,
                    format="metadata",
                    metadataHeaders=["From", "To", "Subject", "Date"],
                ).execute()
                headers = detail.get("payload", {}).get("headers", [])
                entry = {
                    "id": mid,
                    "from": _get_header(headers, "From"),
                    "to": _get_header(headers, "To"),
                    "subject": _get_header(headers, "Subject"),
                    "date": _get_header(headers, "Date"),
                }
                if (
                    subject_substr in entry["subject"]
                    and recipient_email in entry["to"]
                ):
                    matches.append(entry)
            return matches
        if time.time() >= deadline:
            return matches
        time.sleep(5)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_workflow_trigger_frequency_is_once_per_recipient(workflow_payload):
    freq = workflow_payload.get("trigger_frequency")
    assert freq == "once_per_recipient", (
        "Expected workflow.trigger_frequency == 'once_per_recipient', "
        f"got {freq!r}. Full payload keys: {sorted(workflow_payload.keys())}"
    )


def test_workflow_is_active_in_development(workflow_payload):
    # The workflow representation returned by the Management API exposes
    # `active` as a boolean indicating whether the workflow is active in the
    # queried environment (development).
    assert workflow_payload.get("active") is True, (
        "Expected workflow to be active in the development environment, "
        f"got active={workflow_payload.get('active')!r}."
    )


def test_workflow_has_mailtrap_channel_step(workflow_payload):
    steps = workflow_payload.get("steps") or []
    assert steps, "Workflow has no steps."
    channel_keys = [
        s.get("channel_key")
        for s in steps
        if s.get("type") == "channel"
    ]
    assert "mailtrap" in channel_keys, (
        "Workflow does not contain a channel step with channel_key 'mailtrap'. "
        f"Channel keys present: {channel_keys}"
    )


def test_log_file_has_two_workflow_run_id_lines():
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."
    with open(LOG_FILE) as f:
        content = f.read()
    lines = [ln for ln in content.splitlines() if ln.strip()]
    assert len(lines) >= 2, (
        f"Expected at least two non-empty lines in {LOG_FILE}, "
        f"got {len(lines)}: {lines!r}"
    )

    first_re = re.compile(r"^First trigger workflow_run_id:\s+(.+)$")
    second_re = re.compile(r"^Second trigger workflow_run_id:\s+(.+)$")

    first_match = None
    second_match = None
    for ln in lines:
        if first_match is None and first_re.match(ln):
            first_match = first_re.match(ln)
            continue
        if first_match is not None and second_match is None and second_re.match(ln):
            second_match = second_re.match(ln)
            break

    assert first_match is not None, (
        "Log file is missing the 'First trigger workflow_run_id: <value>' line. "
        f"Content was:\n{content}"
    )
    assert second_match is not None, (
        "Log file is missing the 'Second trigger workflow_run_id: <value>' line "
        "(must appear after the first line). "
        f"Content was:\n{content}"
    )
    first_val = first_match.group(1).strip()
    second_val = second_match.group(1).strip()
    assert first_val, "First trigger workflow_run_id value is empty."
    assert second_val, "Second trigger workflow_run_id value is empty."


def test_exactly_one_email_was_delivered(run_id, workflow_key):
    gmail_user = os.environ["GMAIL_USER_NAME"]
    mailtrap_domain = os.environ["MAILTRAP_DOMAIN"]
    recipient_email = f"{gmail_user}+receiver-{run_id}@gmail.com"
    subject_substr = workflow_key  # `dedup-test-{run-id}`

    matches = _list_matching_gmail_messages(
        subject_substr=subject_substr,
        recipient_email=recipient_email,
        deadline_seconds=120,
    )

    assert len(matches) >= 1, (
        f"No matching email arrived in Gmail within the timeout. "
        f"Looked for subject containing {subject_substr!r} to {recipient_email!r}."
    )
    assert len(matches) == 1, (
        "once_per_recipient should have suppressed the second trigger, but "
        f"{len(matches)} matching emails were delivered: "
        f"{[(m['subject'], m['from']) for m in matches]}"
    )

    sender = matches[0]["from"]
    assert f"@{mailtrap_domain}" in sender, (
        f"Email sender {sender!r} does not contain the expected "
        f"Mailtrap domain @{mailtrap_domain}."
    )
