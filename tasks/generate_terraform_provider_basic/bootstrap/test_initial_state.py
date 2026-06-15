import os
import shutil
import pytest

PROJECT_DIR = "/home/user/myproject"

def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, "speakeasy binary not found in PATH."

def test_go_binary_available():
    assert shutil.which("go") is not None, "go binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_openapi_spec_exists():
    spec_path = os.path.join(PROJECT_DIR, "openapi.yaml")
    assert os.path.isfile(spec_path), f"OpenAPI spec {spec_path} does not exist."
