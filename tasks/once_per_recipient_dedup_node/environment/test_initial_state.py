import os
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_python3_available():
    assert shutil.which("python3") is not None, (
        "python3 binary not found in PATH (required for the verifier)."
    )


def test_knock_service_token_env_present():
    assert os.environ.get("KNOCK_SERVICE_TOKEN"), (
        "KNOCK_SERVICE_TOKEN environment variable is not set."
    )


def test_knock_api_token_env_present():
    assert os.environ.get("KNOCK_API_TOKEN"), (
        "KNOCK_API_TOKEN environment variable is not set."
    )


def test_mailtrap_env_present():
    assert os.environ.get("MAILTRAP_DOMAIN"), (
        "MAILTRAP_DOMAIN environment variable is not set."
    )


def test_gmail_env_present():
    assert os.environ.get("GMAIL_USER_NAME"), (
        "GMAIL_USER_NAME environment variable is not set."
    )


def test_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."


def test_knock_mgmt_sdk_installed_in_project():
    # The project ships with the Knock SDKs pre-installed in node_modules so the
    # executor can `require` them directly without needing to run `npm install`.
    mgmt_pkg = os.path.join(PROJECT_DIR, "node_modules", "@knocklabs", "mgmt", "package.json")
    node_pkg = os.path.join(PROJECT_DIR, "node_modules", "@knocklabs", "node", "package.json")
    assert os.path.isfile(mgmt_pkg), (
        f"Expected @knocklabs/mgmt to be pre-installed at {mgmt_pkg}."
    )
    assert os.path.isfile(node_pkg), (
        f"Expected @knocklabs/node to be pre-installed at {node_pkg}."
    )


def test_node_can_load_knock_sdks():
    result = subprocess.run(
        [
            "node",
            "-e",
            "require('@knocklabs/mgmt'); require('@knocklabs/node'); console.log('ok');",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"node failed to load Knock SDKs: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        f"Expected sentinel 'ok' from Knock SDK load check, got {result.stdout!r}."
    )
