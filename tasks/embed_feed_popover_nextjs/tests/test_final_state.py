import os
import socket
import subprocess
import time

import pytest
import requests
from xprocess import ProcessStarter

from pochi_verifier import PochiVerifier


PROJECT_DIR = "/home/user/myproject"
PORT = 3000
BASE_URL = f"http://localhost:{PORT}"

MAPI_BASE = "https://control.knock.app"
API_BASE = "https://api.knock.app"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set."
    return run_id


def _workflow_key() -> str:
    return f"popover-demo-{_run_id()}"


def _recipient_id() -> str:
    return f"popover-user-{_run_id()}"


def _message_body() -> str:
    return f"hello from popover {_run_id()}"


def _mapi_headers() -> dict:
    token = os.environ["KNOCK_SERVICE_TOKEN"]
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _api_headers() -> dict:
    token = os.environ["KNOCK_API_TOKEN"]
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="session")
def reset_user_feed():
    """Archive any prior in-app feed messages for the run-scoped recipient before tests."""
    channel_id = os.environ["KNOCK_INAPP_FEED_CHANNEL_ID"]
    recipient = _recipient_id()
    url = f"{API_BASE}/v1/users/{recipient}/feeds/{channel_id}/messages"
    try:
        requests.delete(url, headers=_api_headers(), timeout=30)
    except Exception:
        # Best-effort cleanup; ignore errors so verification can continue.
        pass
    yield


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Build (if needed) and start the Next.js app on port 3000."""

    # Ensure a production build exists before starting.
    next_dir = os.path.join(PROJECT_DIR, ".next")
    if not os.path.isdir(next_dir):
        build = subprocess.run(
            ["npm", "run", "build"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=600,
        )
        assert build.returncode == 0, (
            f"'npm run build' failed in {PROJECT_DIR}: "
            f"stdout={build.stdout}\nstderr={build.stderr}"
        )

    class Starter(ProcessStarter):
        name = "next_app"
        args = ["npm", "start", "--", "-p", str(PORT)]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 240
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", PORT)) == 0

    xprocess.ensure(Starter.name, Starter)
    # Give the runtime a moment to fully boot the React routes.
    time.sleep(2)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()


def test_workflow_exists_and_active():
    """Verify the in-app workflow is provisioned and active in development via the Management API."""
    url = f"{MAPI_BASE}/v1/workflows/{_workflow_key()}"
    params = {"environment": "development"}
    response = requests.get(url, headers=_mapi_headers(), params=params, timeout=30)
    assert response.status_code == 200, (
        f"Management API returned {response.status_code} for {_workflow_key()}: {response.text}"
    )
    payload = response.json()
    workflow = payload.get("workflow", payload)

    active = workflow.get("active")
    if active is None:
        # Some responses report status differently; accept any truthy active flag or 'active' status.
        active = workflow.get("status") in ("active", "ACTIVE")
    assert active, (
        f"Workflow {_workflow_key()} is not active in development: {payload}"
    )

    steps = workflow.get("steps") or []
    channel_steps = [
        s for s in steps if s.get("type") == "channel" and s.get("channel_key") == "in-app"
    ]
    assert channel_steps, (
        f"Workflow {_workflow_key()} has no in-app channel step. Steps: {steps}"
    )

    body_template_found = False
    for step in channel_steps:
        template = step.get("template") or {}
        # Body may live under markdown_body, body, or html_body depending on layout.
        for field in ("markdown_body", "body", "html_body", "text_body"):
            value = template.get(field)
            if isinstance(value, str) and "data.body" in value.replace(" ", ""):
                body_template_found = True
                break
        if body_template_found:
            break
    assert body_template_found, (
        f"Workflow {_workflow_key()} in-app step template does not reference data.body. "
        f"Steps: {channel_steps}"
    )


def test_app_serves_root(start_app):
    """Verify the Next.js app responds and the page references Knock React assets."""
    response = requests.get(BASE_URL + "/", timeout=60)
    assert response.status_code == 200, (
        f"GET {BASE_URL}/ returned status {response.status_code}: {response.text[:500]}"
    )
    body = response.text
    assert "rnf-" in body, (
        "Expected Knock React class names (prefixed with 'rnf-') in the rendered HTML, "
        "indicating @knocklabs/react components and stylesheet are wired up."
    )


def test_popover_renders_triggered_notification(start_app, reset_user_feed):
    """Trigger the workflow and verify the popover displays the message via browser verification."""
    body_text = _message_body()
    trigger_url = f"{API_BASE}/v1/workflows/{_workflow_key()}/trigger"
    payload = {
        "recipients": [_recipient_id()],
        "data": {"body": body_text},
    }
    trigger_response = requests.post(
        trigger_url, headers=_api_headers(), json=payload, timeout=30
    )
    assert trigger_response.status_code == 200, (
        f"Workflow trigger failed: status={trigger_response.status_code} "
        f"body={trigger_response.text}"
    )
    trigger_body = trigger_response.json()
    assert trigger_body.get("workflow_run_id"), (
        f"Trigger response missing workflow_run_id: {trigger_body}"
    )

    # Allow the message to propagate through the Knock pipeline.
    time.sleep(5)

    reason = (
        "The Knock NotificationFeedPopover should be embedded in the Next.js app's root "
        "route, opened via a notification icon button, and display in-app feed messages "
        "produced by the Knock workflow."
    )
    truth = (
        f"Navigate to {BASE_URL}/. Locate the notification icon button rendered by "
        "@knocklabs/react (it has the CSS class 'rnf-notification-icon-button'). Click "
        "the icon button. Verify that a popover with CSS class "
        "'rnf-notification-feed-popover' becomes visible. Verify that the popover "
        f"contains the text '{body_text}', which corresponds to the in-app notification "
        "just delivered by the Knock workflow trigger."
    )

    verifier = PochiVerifier()
    result = verifier.verify(
        reason=reason,
        truth=truth,
        use_browser_agent=True,
        trajectory_dir="/logs/verifier/pochi/test_popover_renders_triggered_notification",
    )
    assert result.status == "pass", (
        f"Browser verification failed: {getattr(result, 'reason', result)}"
    )
