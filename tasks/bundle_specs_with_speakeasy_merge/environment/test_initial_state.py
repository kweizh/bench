import os
import shutil
import subprocess

import pytest
import yaml

PROJECT_DIR = "/home/user/project"
SPEC_A = os.path.join(PROJECT_DIR, "spec_a.yaml")
SPEC_B = os.path.join(PROJECT_DIR, "spec_b.yaml")


def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, "speakeasy CLI binary not found in PATH."


def test_speakeasy_cli_runs():
    result = subprocess.run(
        ["speakeasy", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`speakeasy --version` failed with exit code {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_spec_a_exists():
    assert os.path.isfile(SPEC_A), f"Source spec {SPEC_A} does not exist."


def test_spec_b_exists():
    assert os.path.isfile(SPEC_B), f"Source spec {SPEC_B} does not exist."


def test_spec_a_is_valid_openapi3_with_users_path():
    with open(SPEC_A) as f:
        doc = yaml.safe_load(f)
    assert isinstance(doc, dict), f"{SPEC_A} did not parse as a YAML mapping."
    openapi_version = doc.get("openapi")
    assert isinstance(openapi_version, str) and openapi_version.startswith("3."), (
        f"{SPEC_A} should declare an OpenAPI 3.x version, got {openapi_version!r}."
    )
    paths = doc.get("paths") or {}
    assert "/users" in paths, f"{SPEC_A} should contain the `/users` path. Found: {list(paths.keys())}"


def test_spec_b_is_valid_openapi3_with_products_path():
    with open(SPEC_B) as f:
        doc = yaml.safe_load(f)
    assert isinstance(doc, dict), f"{SPEC_B} did not parse as a YAML mapping."
    openapi_version = doc.get("openapi")
    assert isinstance(openapi_version, str) and openapi_version.startswith("3."), (
        f"{SPEC_B} should declare an OpenAPI 3.x version, got {openapi_version!r}."
    )
    paths = doc.get("paths") or {}
    assert "/products" in paths, f"{SPEC_B} should contain the `/products` path. Found: {list(paths.keys())}"


def test_merged_yaml_not_yet_created():
    merged_path = os.path.join(PROJECT_DIR, "merged.yaml")
    assert not os.path.exists(merged_path), (
        f"{merged_path} should not exist before the task is executed."
    )
