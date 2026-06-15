import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, "speakeasy binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_openapi_yaml_exists():
    openapi_path = os.path.join(PROJECT_DIR, "openapi.yaml")
    assert os.path.isfile(openapi_path), f"openapi.yaml file {openapi_path} does not exist."

def test_openapi_yaml_content():
    openapi_path = os.path.join(PROJECT_DIR, "openapi.yaml")
    with open(openapi_path, "r") as f:
        content = f.read()
    assert "/ping:" in content, "openapi.yaml should contain the /ping endpoint."
    assert "example:" not in content, "openapi.yaml should not already contain an example."