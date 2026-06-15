import os
import re

import pytest
import requests

PROJECT_DIR = "/home/user/knock_task"
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")

MGMT_BASE = "https://control.knock.app/v1"
API_BASE = "https://api.knock.app/v1"


@pytest.fixture(scope="module")
def run_id() -> str:
    value = os.environ.get("ZEALT_RUN_ID")
    assert value, "ZEALT_RUN_ID environment variable must be set for verification."
    return value


@pytest.fixture(scope="module")
def workflow_key(run_id: str) -> str:
    return f"order-confirmation-{run_id}"


@pytest.fixture(scope="module")
def service_token() -> str:
    token = os.environ.get("KNOCK_SERVICE_TOKEN")
    assert token, "KNOCK_SERVICE_TOKEN must be set to verify the workflow definition."
    return token


@pytest.fixture(scope="module")
def api_token() -> str:
    token = os.environ.get("KNOCK_API_TOKEN")
    assert token, "KNOCK_API_TOKEN must be set to verify trigger behavior."
    return token


@pytest.fixture(scope="module")
def log_contents() -> str:
    assert os.path.isfile(LOG_PATH), f"Expected log file {LOG_PATH} to exist."
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_log_contains_workflow_key(log_contents: str, workflow_key: str):
    expected = f"Workflow Key: {workflow_key}"
    assert expected in log_contents.splitlines(), (
        f"Expected line '{expected}' in {LOG_PATH}. Contents:\n{log_contents}"
    )


def test_log_contains_workflow_active(log_contents: str):
    expected = "Workflow Active: true"
    assert expected in log_contents.splitlines(), (
        f"Expected line '{expected}' in {LOG_PATH}. Contents:\n{log_contents}"
    )


def test_log_contains_valid_trigger_run_id(log_contents: str):
    pattern = re.compile(
        r"^Valid Trigger Workflow Run ID: ([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$",
        re.MULTILINE,
    )
    match = pattern.search(log_contents)
    assert match, (
        f"Expected a line matching 'Valid Trigger Workflow Run ID: <uuid>' in {LOG_PATH}. "
        f"Contents:\n{log_contents}"
    )


def test_log_contains_invalid_trigger_status(log_contents: str):
    expected = "Invalid Trigger Status: 422"
    assert expected in log_contents.splitlines(), (
        f"Expected line '{expected}' in {LOG_PATH}. Contents:\n{log_contents}"
    )


def test_workflow_exists_via_management_api(service_token: str, workflow_key: str):
    response = requests.get(
        f"{MGMT_BASE}/workflows/{workflow_key}",
        headers={"Authorization": f"Bearer {service_token}"},
        params={"environment": "development"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Management API GET workflow returned {response.status_code}: {response.text}"
    )
    payload = response.json()
    workflow = payload.get("workflow", payload)
    assert workflow.get("key") == workflow_key, (
        f"Expected workflow key {workflow_key}, got {workflow.get('key')}."
    )
    assert workflow.get("active") is True, (
        f"Expected workflow.active=true, got {workflow.get('active')}."
    )


def test_workflow_has_trigger_data_json_schema(service_token: str, workflow_key: str):
    response = requests.get(
        f"{MGMT_BASE}/workflows/{workflow_key}",
        headers={"Authorization": f"Bearer {service_token}"},
        params={"environment": "development"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Management API GET workflow returned {response.status_code}: {response.text}"
    )
    payload = response.json()
    workflow = payload.get("workflow", payload)
    schema = workflow.get("trigger_data_json_schema")
    assert isinstance(schema, dict), (
        f"Expected trigger_data_json_schema on workflow, got: {schema!r}"
    )
    required = schema.get("required") or []
    for field in ("order_id", "total_amount", "customer_email"):
        assert field in required, (
            f"Expected '{field}' in trigger_data_json_schema.required, got {required}."
        )
    properties = schema.get("properties") or {}
    assert properties.get("order_id", {}).get("type") == "string", (
        f"Expected properties.order_id.type='string', got {properties.get('order_id')}."
    )
    assert properties.get("total_amount", {}).get("type") == "number", (
        f"Expected properties.total_amount.type='number', got {properties.get('total_amount')}."
    )
    customer_email = properties.get("customer_email", {})
    assert customer_email.get("type") == "string", (
        f"Expected properties.customer_email.type='string', got {customer_email}."
    )
    assert customer_email.get("format") == "email", (
        f"Expected properties.customer_email.format='email', got {customer_email}."
    )


def test_workflow_has_in_app_channel_step(service_token: str, workflow_key: str):
    response = requests.get(
        f"{MGMT_BASE}/workflows/{workflow_key}",
        headers={"Authorization": f"Bearer {service_token}"},
        params={"environment": "development"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Management API GET workflow returned {response.status_code}: {response.text}"
    )
    payload = response.json()
    workflow = payload.get("workflow", payload)
    steps = workflow.get("steps") or []
    matching = [
        s for s in steps
        if s.get("type") == "channel" and s.get("channel_key") == "in-app"
    ]
    assert matching, (
        f"Expected at least one channel step with channel_key='in-app'; got steps={steps}"
    )


def test_valid_trigger_succeeds(api_token: str, workflow_key: str, run_id: str):
    response = requests.post(
        f"{API_BASE}/workflows/{workflow_key}/trigger",
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
        json={
            "recipients": [f"verifier-{run_id}"],
            "data": {
                "order_id": "ord_001",
                "total_amount": 12.5,
                "customer_email": "v@example.com",
            },
        },
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Expected 200 from valid trigger, got {response.status_code}: {response.text}"
    )
    body = response.json()
    assert "workflow_run_id" in body, (
        f"Expected workflow_run_id in trigger response, got {body}."
    )


def test_invalid_trigger_returns_422(api_token: str, workflow_key: str, run_id: str):
    response = requests.post(
        f"{API_BASE}/workflows/{workflow_key}/trigger",
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
        json={
            "recipients": [f"verifier-{run_id}"],
            "data": {
                "order_id": "ord_002",
                "total_amount": "oops",
                "customer_email": "v@example.com",
            },
        },
        timeout=30,
    )
    assert response.status_code == 422, (
        f"Expected 422 from invalid trigger, got {response.status_code}: {response.text}"
    )
