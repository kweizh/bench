import os
import shutil

PROJECT_DIR = "/home/user/cancel_task"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(
        PROJECT_DIR
    ), f"Expected project directory {PROJECT_DIR} to exist."


def test_knock_service_token_env_var_present():
    assert os.environ.get(
        "KNOCK_SERVICE_TOKEN"
    ), "KNOCK_SERVICE_TOKEN environment variable must be set for the Knock Management API."


def test_knock_api_token_env_var_present():
    assert os.environ.get(
        "KNOCK_API_TOKEN"
    ), "KNOCK_API_TOKEN environment variable must be set for the Knock trigger and cancel APIs."


def test_gmail_user_name_env_var_present():
    assert os.environ.get(
        "GMAIL_USER_NAME"
    ), "GMAIL_USER_NAME environment variable must be set for the recipient Gmail address."


def test_mailtrap_domain_env_var_present():
    assert os.environ.get(
        "MAILTRAP_DOMAIN"
    ), "MAILTRAP_DOMAIN environment variable must be set for the Mailtrap sender domain."


def test_zealt_run_id_env_var_present():
    assert os.environ.get(
        "ZEALT_RUN_ID"
    ), "ZEALT_RUN_ID environment variable must be set to scope task resources."
