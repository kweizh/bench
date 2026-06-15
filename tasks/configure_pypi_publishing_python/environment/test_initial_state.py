import os
import shutil

import pytest
import yaml

PROJECT_DIR = "/home/user/project"
GEN_YAML = os.path.join(PROJECT_DIR, "gen.yaml")


def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, (
        "speakeasy binary not found in PATH; expected the Speakeasy CLI to be installed."
    )


def test_yq_binary_available():
    assert shutil.which("yq") is not None, (
        "yq binary not found in PATH; expected yq to be installed for YAML editing."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist; expected a pre-seeded Speakeasy project."
    )


def test_gen_yaml_exists():
    assert os.path.isfile(GEN_YAML), (
        f"Config file {GEN_YAML} does not exist; expected a seeded gen.yaml with a python target block."
    )


def test_gen_yaml_has_python_block():
    with open(GEN_YAML) as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), f"{GEN_YAML} did not parse as a YAML mapping."
    assert "python" in data, f"Expected a top-level 'python' block in {GEN_YAML}."
    assert isinstance(data["python"], dict), (
        f"Top-level 'python' key in {GEN_YAML} must be a mapping."
    )


def test_initial_python_package_name_is_default():
    with open(GEN_YAML) as f:
        data = yaml.safe_load(f)
    package_name = data.get("python", {}).get("packageName")
    assert package_name == "openapi", (
        f"Expected initial python.packageName to be the default 'openapi' in {GEN_YAML}, "
        f"got {package_name!r}."
    )


def test_initial_python_authors_is_speakeasy():
    with open(GEN_YAML) as f:
        data = yaml.safe_load(f)
    authors = data.get("python", {}).get("authors")
    assert isinstance(authors, list), (
        f"Expected python.authors to be a YAML sequence in {GEN_YAML}, got {type(authors).__name__}."
    )
    assert authors == ["Speakeasy"], (
        f"Expected initial python.authors to be ['Speakeasy'] in {GEN_YAML}, got {authors!r}."
    )
