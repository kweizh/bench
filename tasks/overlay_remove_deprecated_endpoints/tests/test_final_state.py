import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"
ORIGINAL_OPENAPI = os.path.join(PROJECT_DIR, "openapi.yaml")
MODIFIED_OPENAPI = os.path.join(PROJECT_DIR, "modified.yaml")
OVERLAY_FILE = os.path.join(PROJECT_DIR, "overlay.yaml")

def test_modified_yaml_exists():
    assert os.path.isfile(MODIFIED_OPENAPI), f"Expected {MODIFIED_OPENAPI} to be created."

def test_modified_yaml_removed_endpoint():
    with open(MODIFIED_OPENAPI, "r") as f:
        content = f.read()
    assert "/old-endpoint" not in content, "Expected '/old-endpoint' to be removed from modified.yaml."

def test_original_openapi_unchanged():
    with open(ORIGINAL_OPENAPI, "r") as f:
        content = f.read()
    assert "/old-endpoint" in content, "Expected original openapi.yaml to remain unchanged and contain '/old-endpoint'."

def test_overlay_apply_succeeds():
    assert os.path.isfile(OVERLAY_FILE), f"Expected {OVERLAY_FILE} to exist."
    result = subprocess.run(
        ["speakeasy", "overlay", "apply", "-s", "openapi.yaml", "-o", "overlay.yaml"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"'speakeasy overlay apply' failed: {result.stderr}"
    assert "/old-endpoint" not in result.stdout, "Expected '/old-endpoint' to be removed in the stdout of the applied overlay."
