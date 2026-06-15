import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_knock_service_token_env_present():
    assert os.environ.get("KNOCK_SERVICE_TOKEN"), (
        "KNOCK_SERVICE_TOKEN environment variable must be set in the task environment."
    )


def test_knock_api_token_env_present():
    assert os.environ.get("KNOCK_API_TOKEN"), (
        "KNOCK_API_TOKEN environment variable must be set in the task environment."
    )


def test_gmail_user_name_env_present():
    assert os.environ.get("GMAIL_USER_NAME"), (
        "GMAIL_USER_NAME environment variable must be set in the task environment."
    )


def test_mailtrap_domain_env_present():
    assert os.environ.get("MAILTRAP_DOMAIN"), (
        "MAILTRAP_DOMAIN environment variable must be set in the task environment."
    )


def test_zealt_run_id_env_present():
    assert os.environ.get("ZEALT_RUN_ID"), (
        "ZEALT_RUN_ID environment variable must be set in the task environment."
    )
