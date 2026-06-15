import importlib
import os

import pytest

PROJECT_DIR = "/home/user/knock_task"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_python_available():
    import sys

    assert sys.version_info >= (3, 9), "Python 3.9+ is required."


def test_knockapi_importable():
    try:
        importlib.import_module("knockapi")
    except Exception as exc:  # pragma: no cover - reported via assertion message
        pytest.fail(f"knockapi Python SDK must be importable: {exc}")


def test_requests_importable():
    try:
        importlib.import_module("requests")
    except Exception as exc:  # pragma: no cover
        pytest.fail(f"requests library must be importable: {exc}")


def test_required_env_vars_present():
    for name in (
        "ZEALT_RUN_ID",
        "KNOCK_SERVICE_TOKEN",
        "KNOCK_API_TOKEN",
        "MAILTRAP_DOMAIN",
        "GMAIL_USER_NAME",
    ):
        assert os.environ.get(name), f"Environment variable {name} must be set in the task environment."


def test_log_file_not_yet_created():
    log_path = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(log_path), (
        f"Log file {log_path} should not exist before the executor runs the task."
    )
