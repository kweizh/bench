import os
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/project"
GEN_YAML = os.path.join(PROJECT_DIR, "gen.yaml")


def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, (
        "speakeasy binary not found in PATH."
    )


def test_yq_binary_available():
    assert shutil.which("yq") is not None, "yq binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_gen_yaml_exists():
    assert os.path.isfile(GEN_YAML), f"gen.yaml file {GEN_YAML} does not exist."


def test_gen_yaml_has_typescript_section():
    result = subprocess.run(
        ["yq", ".typescript", GEN_YAML],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"yq failed to read .typescript from gen.yaml: {result.stderr}"
    )
    output = result.stdout.strip()
    assert output and output != "null", (
        "Expected an existing .typescript section in gen.yaml."
    )


def test_initial_package_name_is_default():
    result = subprocess.run(
        ["yq", ".typescript.packageName", GEN_YAML],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"yq failed to read .typescript.packageName: {result.stderr}"
    )
    assert result.stdout.strip() == "openapi", (
        "Expected initial .typescript.packageName to be the default 'openapi' "
        "in gen.yaml."
    )
