import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user"

def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, "speakeasy binary not found in PATH."

def test_working_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Working directory {PROJECT_DIR} does not exist."

def test_openapi_spec_exists():
    openapi_path = os.path.join(PROJECT_DIR, "openapi.yaml")
    assert os.path.isfile(openapi_path), f"OpenAPI specification {openapi_path} does not exist."

def test_initial_openapi_spec_missing_pagination():
    openapi_path = os.path.join(PROJECT_DIR, "openapi.yaml")
    with open(openapi_path) as f:
        content = f.read()
    assert "x-speakeasy-pagination" not in content, "Expected initial openapi.yaml to NOT contain x-speakeasy-pagination."
