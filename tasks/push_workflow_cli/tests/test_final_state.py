import os
import re

import pytest
import requests

PROJECT_DIR = "/home/user/knock-project"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
KNOCK_MAPI_BASE = "https://control.knock.app/v1"


def _run_id():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable must be set for verification."
    return run_id


def _service_token():
    token = os.environ.get("KNOCK_SERVICE_TOKEN", "")
    assert token, "KNOCK_SERVICE_TOKEN environment variable must be set for verification."
    return token


def _expected_workflow_key():
    return f"cli-welcome-{_run_id()}"


def _get_workflow(hide_uncommitted_changes: bool):
    key = _expected_workflow_key()
    params = {"environment": "development"}
    if hide_uncommitted_changes:
        params["hide_uncommitted_changes"] = "true"
    response = requests.get(
        f"{KNOCK_MAPI_BASE}/workflows/{key}",
        headers={"Authorization": f"Bearer {_service_token()}"},
        params=params,
        timeout=30,
    )
    return response


def _collect_channel_keys(workflow_json):
    """Return the set of channel_keys across whatever step list views are available
    in the workflow response payload, recursing into nested branch step children."""
    channel_keys = set()

    def visit(steps):
        if not isinstance(steps, list):
            return
        for step in steps:
            if not isinstance(step, dict):
                continue
            if step.get("type") == "channel" and step.get("channel_key"):
                channel_keys.add(step["channel_key"])
            # Recurse into branch children
            for child_key in ("branches", "steps"):
                if isinstance(step.get(child_key), list):
                    for branch in step[child_key]:
                        if isinstance(branch, dict):
                            visit(branch.get("steps", []))

    # The Knock workflow response may expose steps directly, or under
    # environment_versions[*].steps. Walk every possible location.
    if isinstance(workflow_json.get("steps"), list):
        visit(workflow_json["steps"])
    for env_version in workflow_json.get("environment_versions", []) or []:
        if isinstance(env_version, dict):
            visit(env_version.get("steps", []))

    return channel_keys


def _workflow_is_active(workflow_json):
    """Determine whether the workflow is active in development from whatever shape
    the Management API response uses."""
    # Top-level active flag (some API responses)
    if workflow_json.get("active") is True:
        return True
    # environment_versions array with per-env active flag
    for env_version in workflow_json.get("environment_versions", []) or []:
        if not isinstance(env_version, dict):
            continue
        env_name = (
            env_version.get("environment")
            or env_version.get("name")
            or env_version.get("slug")
        )
        if env_name == "development" and env_version.get("active") is True:
            return True
    return False


def test_output_log_records_workflow_key():
    assert os.path.isfile(LOG_FILE), f"Expected log file {LOG_FILE} to exist."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    expected_line = f"Workflow key: {_expected_workflow_key()}"
    assert re.search(
        rf"^{re.escape(expected_line)}\s*$", content, flags=re.MULTILINE
    ), (
        f"Expected log file {LOG_FILE} to contain a line exactly equal to "
        f"{expected_line!r}. Got contents:\n{content}"
    )


def test_workflow_exists_in_development_via_mapi():
    response = _get_workflow(hide_uncommitted_changes=False)
    assert response.status_code == 200, (
        f"Expected GET /v1/workflows/{_expected_workflow_key()}?environment=development "
        f"to return 200, but got {response.status_code}. Body: {response.text}"
    )
    body = response.json()
    assert body.get("key") == _expected_workflow_key(), (
        f"Expected workflow.key to equal {_expected_workflow_key()!r}, "
        f"got {body.get('key')!r}. Full response: {body}"
    )


def test_workflow_is_committed_in_development():
    response = _get_workflow(hide_uncommitted_changes=True)
    assert response.status_code == 200, (
        "Expected the workflow to be committed and therefore visible when "
        "uncommitted changes are hidden. "
        f"Got status {response.status_code}. Body: {response.text}"
    )


def test_workflow_is_active_in_development():
    response = _get_workflow(hide_uncommitted_changes=False)
    assert response.status_code == 200, (
        f"Could not fetch workflow for active check; status={response.status_code} "
        f"body={response.text}"
    )
    body = response.json()
    assert _workflow_is_active(body), (
        "Expected workflow to be active in the development environment. "
        f"Full workflow response: {body}"
    )


def test_workflow_has_in_app_and_email_channel_steps():
    response = _get_workflow(hide_uncommitted_changes=True)
    assert response.status_code == 200, (
        f"Could not fetch committed workflow for step check; "
        f"status={response.status_code} body={response.text}"
    )
    body = response.json()
    channel_keys = _collect_channel_keys(body)
    assert "in-app" in channel_keys, (
        f"Expected workflow to contain a channel step with channel_key 'in-app'. "
        f"Found channel_keys: {sorted(channel_keys)}. Full response: {body}"
    )
    assert "mailtrap" in channel_keys, (
        f"Expected workflow to contain a channel step with channel_key 'mailtrap'. "
        f"Found channel_keys: {sorted(channel_keys)}. Full response: {body}"
    )
