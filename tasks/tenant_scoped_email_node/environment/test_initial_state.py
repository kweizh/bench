import os
import shutil

import pytest

PROJECT_DIR = "/home/user/tenant_task"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary must be available in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary must be available in PATH."


def test_required_env_vars_present():
    for name in (
        "ZEALT_RUN_ID",
        "KNOCK_SERVICE_TOKEN",
        "KNOCK_API_TOKEN",
        "MAILTRAP_DOMAIN",
        "GMAIL_USER_NAME",
    ):
        assert os.environ.get(name), (
            f"Environment variable {name} must be set in the task environment."
        )


def test_log_file_not_yet_created():
    log_path = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(log_path), (
        f"Log file {log_path} should not exist before the executor runs the task."
    )
