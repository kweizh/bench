import json
import os
import re

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")
MGMT_BASE_URL = "https://control.knock.app"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID is not set; cannot derive expected workflow key."
    return run_id


def _workflow_key() -> str:
    return f"escalation-{_run_id()}"


def _service_token() -> str:
    token = os.environ.get("KNOCK_SERVICE_TOKEN")
    assert token, "KNOCK_SERVICE_TOKEN is not set; cannot query Knock Management API."
    return token


def _get_workflow_payload() -> dict:
    response = requests.get(
        f"{MGMT_BASE_URL}/v1/workflows/{_workflow_key()}",
        params={"environment": "development"},
        headers={
            "Authorization": f"Bearer {_service_token()}",
            "Accept": "application/json",
        },
        timeout=30,
    )
    assert response.status_code == 200, (
        f"GET workflow returned HTTP {response.status_code}: {response.text}"
    )
    payload = response.json()
    # The mgmt API for GET /v1/workflows/{key} returns the workflow at the top
    # level, but some endpoints wrap under `workflow`. Accept either shape.
    if isinstance(payload, dict) and "workflow" in payload and isinstance(payload["workflow"], dict):
        return payload["workflow"]
    return payload


def test_log_file_exists():
    assert os.path.isfile(LOG_PATH), (
        f"Expected log file {LOG_PATH} to exist after task execution."
    )


def test_log_file_contains_workflow_key_and_active_lines():
    with open(LOG_PATH) as f:
        log_text = f.read()
    expected_key_line = f"Workflow key: {_workflow_key()}"
    assert expected_key_line in log_text, (
        f"Expected log to contain '{expected_key_line}', got:\n{log_text}"
    )
    assert re.search(r"^Active:\s*true\s*$", log_text, re.IGNORECASE | re.MULTILINE), (
        f"Expected log to contain a line 'Active: true' (case-insensitive), got:\n{log_text}"
    )


def test_workflow_exists_and_is_active():
    workflow = _get_workflow_payload()
    assert workflow.get("key") == _workflow_key(), (
        f"Expected workflow.key == '{_workflow_key()}', got: {workflow.get('key')}"
    )
    assert workflow.get("active") is True, (
        f"Expected workflow.active == True, got: {workflow.get('active')}"
    )


def test_workflow_has_required_steps_in_order():
    workflow = _get_workflow_payload()
    steps = workflow.get("steps") or []
    assert isinstance(steps, list) and len(steps) >= 3, (
        f"Expected workflow to have at least 3 steps, got: {steps}"
    )

    in_app_idx = None
    delay_idx = None
    email_idx = None

    for i, step in enumerate(steps):
        step_type = step.get("type")
        if (
            in_app_idx is None
            and step_type == "channel"
            and step.get("channel_key") == "in-app"
        ):
            in_app_idx = i
        elif delay_idx is None and step_type == "delay":
            delay_idx = i
        elif (
            email_idx is None
            and step_type == "channel"
            and step.get("channel_key") == "mailtrap"
        ):
            email_idx = i

    assert in_app_idx is not None, (
        f"Expected a channel step with channel_key == 'in-app', got steps:\n"
        f"{json.dumps(steps, indent=2)}"
    )
    assert delay_idx is not None, (
        f"Expected a delay step in the workflow, got steps:\n"
        f"{json.dumps(steps, indent=2)}"
    )
    assert email_idx is not None, (
        f"Expected a channel step with channel_key == 'mailtrap', got steps:\n"
        f"{json.dumps(steps, indent=2)}"
    )

    assert in_app_idx < delay_idx < email_idx, (
        "Expected step order in-app -> delay -> mailtrap email, got indices "
        f"in_app={in_app_idx}, delay={delay_idx}, email={email_idx}"
    )


def test_delay_step_uses_5_minutes():
    workflow = _get_workflow_payload()
    steps = workflow.get("steps") or []
    delay_steps = [s for s in steps if s.get("type") == "delay"]
    assert delay_steps, "Expected at least one delay step in the workflow."

    matched = False
    for step in delay_steps:
        delay_for = ((step.get("settings") or {}).get("delay_for")) or {}
        if delay_for.get("unit") == "minutes" and delay_for.get("value") == 5:
            matched = True
            break
    assert matched, (
        "Expected a delay step with settings.delay_for == {'unit': 'minutes', "
        f"'value': 5}}, got delay steps:\n{json.dumps(delay_steps, indent=2)}"
    )


def test_mailtrap_step_has_engagement_status_condition():
    workflow = _get_workflow_payload()
    steps = workflow.get("steps") or []

    in_app_ref = None
    for step in steps:
        if step.get("type") == "channel" and step.get("channel_key") == "in-app":
            in_app_ref = step.get("ref")
            break
    assert in_app_ref, "Could not locate the in-app channel step's ref."

    mailtrap_step = None
    for step in steps:
        if step.get("type") == "channel" and step.get("channel_key") == "mailtrap":
            mailtrap_step = step
            break
    assert mailtrap_step is not None, "Could not locate the mailtrap channel step."

    conditions = mailtrap_step.get("conditions") or {}
    all_conditions = []
    if isinstance(conditions, dict):
        all_conditions.extend(conditions.get("all") or [])
        all_conditions.extend(conditions.get("any") or [])

    expected_variable = f"refs.{in_app_ref}.engagement_status"
    matched = False
    for cond in all_conditions:
        if (
            cond.get("variable") == expected_variable
            and cond.get("operator") == "not_contains"
            and cond.get("argument") == "$message.seen"
        ):
            matched = True
            break
    assert matched, (
        "Expected the mailtrap step to have a condition with "
        f"variable={expected_variable!r}, operator='not_contains', "
        f"argument='$message.seen'. Got conditions: "
        f"{json.dumps(conditions, indent=2)}"
    )


def test_workflow_has_trigger_data_json_schema():
    workflow = _get_workflow_payload()
    schema = workflow.get("trigger_data_json_schema") or {}
    assert schema.get("type") == "object", (
        f"Expected trigger_data_json_schema.type == 'object', got: {schema}"
    )
    required = schema.get("required") or []
    assert "onboarding_url" in required, (
        f"Expected 'onboarding_url' in trigger_data_json_schema.required, got: {required}"
    )
    properties = schema.get("properties") or {}
    onboarding = properties.get("onboarding_url") or {}
    assert onboarding.get("type") == "string", (
        "Expected trigger_data_json_schema.properties.onboarding_url.type == 'string', "
        f"got: {onboarding}"
    )
