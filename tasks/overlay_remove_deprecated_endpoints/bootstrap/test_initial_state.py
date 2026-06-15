import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"
OPENAPI_FILE = os.path.join(PROJECT_DIR, "openapi.yaml")

def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, "speakeasy binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_openapi_file_exists():
    assert os.path.isfile(OPENAPI_FILE), f"OpenAPI file {OPENAPI_FILE} does not exist."

def test_openapi_contains_deprecated_endpoint():
    with open(OPENAPI_FILE, "r") as f:
        content = f.read()
    assert "/old-endpoint" in content, "Expected '/old-endpoint' to be present in initial openapi.yaml."
    assert "deprecated: true" in content, "Expected '/old-endpoint' to be marked as deprecated in initial openapi.yaml."
