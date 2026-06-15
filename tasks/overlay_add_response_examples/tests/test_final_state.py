import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_openapi_modified_yaml_exists():
    modified_path = os.path.join(PROJECT_DIR, "openapi-modified.yaml")
    assert os.path.isfile(modified_path), f"openapi-modified.yaml not found at {modified_path}"

def test_openapi_modified_yaml_content():
    modified_path = os.path.join(PROJECT_DIR, "openapi-modified.yaml")
    with open(modified_path, "r") as f:
        content = f.read()
    
    assert "application/json" in content, "openapi-modified.yaml is missing 'application/json' content type."
    assert "example" in content, "openapi-modified.yaml is missing 'example' block."
    assert "pong" in content, "openapi-modified.yaml is missing the 'pong' example value."

def test_openapi_modified_is_valid():
    """Use Speakeasy CLI to validate the modified OpenAPI spec."""
    modified_path = os.path.join(PROJECT_DIR, "openapi-modified.yaml")
    result = subprocess.run(
        ["speakeasy", "lint", "openapi", "-s", modified_path],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"'speakeasy validate' failed on the modified spec: {result.stderr}\n{result.stdout}"

def test_original_openapi_yaml_unmodified():
    original_path = os.path.join(PROJECT_DIR, "openapi.yaml")
    with open(original_path, "r") as f:
        content = f.read()
    
    assert "application/json" not in content, "Original openapi.yaml was modified to include 'application/json'."
    assert "example" not in content, "Original openapi.yaml was modified to include 'example'."
