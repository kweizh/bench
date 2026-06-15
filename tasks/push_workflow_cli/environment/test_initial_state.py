import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/knock-project"


def test_knock_cli_available():
    assert shutil.which("knock") is not None, (
        "Knock CLI ('knock') binary not found in PATH."
    )


def test_knock_cli_runs():
    result = subprocess.run(
        ["knock", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"`knock --version` failed with exit code {result.returncode}. "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_service_token_env_var_set():
    token = os.environ.get("KNOCK_SERVICE_TOKEN", "")
    assert token, (
        "KNOCK_SERVICE_TOKEN environment variable must be set so the Knock CLI can "
        "authenticate against the Knock Management API."
    )


def test_run_id_env_var_set():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, (
        "ZEALT_RUN_ID environment variable must be set so the task can isolate "
        "externally visible side effects with a per-run identifier."
    )
