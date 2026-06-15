import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/knock_task"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_knock_service_token_env():
    assert os.environ.get("KNOCK_SERVICE_TOKEN"), "KNOCK_SERVICE_TOKEN env var is not set."


def test_knock_api_token_env():
    assert os.environ.get("KNOCK_API_TOKEN"), "KNOCK_API_TOKEN env var is not set."


def test_zealt_run_id_env():
    assert os.environ.get("ZEALT_RUN_ID"), "ZEALT_RUN_ID env var is not set."


def test_knock_mgmt_sdk_preinstalled():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), f"{package_json} does not exist."
    with open(package_json) as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies", {}) or {})
    deps.update(pkg.get("devDependencies", {}) or {})
    assert "@knocklabs/mgmt" in deps, "@knocklabs/mgmt is not declared in package.json."
    assert "@knocklabs/node" in deps, "@knocklabs/node is not declared in package.json."


def test_node_modules_installed():
    node_modules = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(node_modules), f"node_modules directory {node_modules} does not exist."
    mgmt_pkg = os.path.join(node_modules, "@knocklabs", "mgmt", "package.json")
    node_pkg = os.path.join(node_modules, "@knocklabs", "node", "package.json")
    assert os.path.isfile(mgmt_pkg), f"@knocklabs/mgmt is not installed at {mgmt_pkg}."
    assert os.path.isfile(node_pkg), f"@knocklabs/node is not installed at {node_pkg}."


def test_no_pre_existing_output_log():
    log_path = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(log_path), (
        f"{log_path} should not exist before the task starts; it is created by the executor."
    )


def test_node_can_require_sdks():
    result = subprocess.run(
        [
            "node",
            "-e",
            "require('@knocklabs/mgmt'); require('@knocklabs/node'); console.log('ok');",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"Node failed to require Knock SDKs. stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, f"Unexpected output: {result.stdout!r}"
