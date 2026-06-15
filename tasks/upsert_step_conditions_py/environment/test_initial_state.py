import os
import shutil

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist at initial state."
    )


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_requests_importable():
    # The task instructs the executor to call the Knock Management API. The
    # widely-used `requests` library should be available in the environment.
    try:
        import requests  # noqa: F401
    except ImportError:
        pytest.fail("Python `requests` package is not importable in the environment.")


def test_knock_service_token_set():
    token = os.environ.get("KNOCK_SERVICE_TOKEN")
    assert token, "KNOCK_SERVICE_TOKEN is not set in the environment."


def test_zealt_run_id_set():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID is not set in the environment."


def test_output_log_does_not_exist_yet():
    # The executor is expected to create this artifact; it must not pre-exist.
    log_path = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(log_path), (
        f"Output log {log_path} already exists at initial state; it should be "
        "created by the executor."
    )
