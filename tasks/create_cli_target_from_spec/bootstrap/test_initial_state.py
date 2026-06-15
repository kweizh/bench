import os
import shutil
import pytest

PROJECT_DIR = "/home/user/myproject"

def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, "speakeasy binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_openapi_file_exists():
    openapi_path = os.path.join(PROJECT_DIR, "openapi.yaml")
    assert os.path.isfile(openapi_path), f"OpenAPI file {openapi_path} does not exist."
