import os
import shutil


HOME_DIR = "/home/user"


def test_home_dir_exists():
    assert os.path.isdir(HOME_DIR), f"Home directory {HOME_DIR} does not exist."


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_npx_binary_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_run_id_env_var_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set for run-scoped resources."


def test_knock_service_token_present():
    assert os.environ.get("KNOCK_SERVICE_TOKEN"), "KNOCK_SERVICE_TOKEN environment variable must be set."


def test_knock_api_token_present():
    assert os.environ.get("KNOCK_API_TOKEN"), "KNOCK_API_TOKEN environment variable must be set."


def test_knock_public_api_token_present():
    assert os.environ.get("KNOCK_PUBLIC_API_TOKEN"), "KNOCK_PUBLIC_API_TOKEN environment variable must be set."


def test_knock_inapp_feed_channel_id_present():
    assert os.environ.get(
        "KNOCK_INAPP_FEED_CHANNEL_ID"
    ), "KNOCK_INAPP_FEED_CHANNEL_ID environment variable must be set."
