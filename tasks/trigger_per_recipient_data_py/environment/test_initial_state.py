import importlib
import os
import shutil

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task runs."
    )


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


@pytest.mark.parametrize(
    "module_name",
    [
        "knockapi",
        "requests",
        "googleapiclient",
        "google.oauth2.credentials",
    ],
)
def test_required_python_modules_importable(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError as exc:
        pytest.fail(
            f"Expected Python module '{module_name}' to be importable before the task runs: {exc}"
        )


@pytest.mark.parametrize(
    "env_var",
    [
        "KNOCK_SERVICE_TOKEN",
        "KNOCK_API_TOKEN",
        "GMAIL_USER_NAME",
        "ZEALT_RUN_ID",
    ],
)
def test_required_env_vars_present(env_var):
    value = os.environ.get(env_var)
    assert value, f"Expected environment variable {env_var} to be set before the task runs."
