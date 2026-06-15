import json
import os
import subprocess

import pytest
import yaml

PROJECT_DIR = "/home/user/project"
GEN_YAML = os.path.join(PROJECT_DIR, "gen.yaml")


def _load_gen_yaml():
    assert os.path.isfile(GEN_YAML), f"Expected {GEN_YAML} to exist after the task."
    with open(GEN_YAML) as f:
        return yaml.safe_load(f)


def test_gen_yaml_is_valid_yaml():
    data = _load_gen_yaml()
    assert isinstance(data, dict), (
        f"{GEN_YAML} must still parse as a YAML mapping after editing."
    )


def test_python_block_still_present():
    data = _load_gen_yaml()
    assert "python" in data and isinstance(data["python"], dict), (
        f"Top-level 'python' mapping must still exist in {GEN_YAML} after editing."
    )


def test_python_package_name_is_example_my_sdk_pyyaml():
    data = _load_gen_yaml()
    package_name = data["python"].get("packageName")
    assert package_name == "example-my-sdk", (
        f"Expected .python.packageName == 'example-my-sdk' in {GEN_YAML}, got {package_name!r}."
    )


def test_python_authors_contains_example_team_pyyaml():
    data = _load_gen_yaml()
    authors = data["python"].get("authors")
    assert isinstance(authors, list), (
        f"Expected .python.authors to be a YAML sequence in {GEN_YAML}, got {type(authors).__name__}."
    )
    assert "Example Team" in authors, (
        f"Expected 'Example Team' to appear in .python.authors in {GEN_YAML}, got {authors!r}."
    )


def test_python_package_name_via_yq():
    """Cross-check using the yq CLI installed in the environment."""
    result = subprocess.run(
        ["yq", "-r", ".python.packageName", GEN_YAML],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`yq` failed to read .python.packageName from {GEN_YAML}: {result.stderr}"
    )
    value = result.stdout.strip()
    assert value == "example-my-sdk", (
        f"Expected `yq` to report .python.packageName == 'example-my-sdk', got {value!r}."
    )


def test_python_authors_via_yq_contains_example_team():
    """Cross-check the authors list using yq -o=json for robust parsing."""
    result = subprocess.run(
        ["yq", "-o=json", ".python.authors", GEN_YAML],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`yq` failed to read .python.authors from {GEN_YAML}: {result.stderr}"
    )
    try:
        authors = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"`yq` did not return valid JSON for .python.authors: {exc}; stdout={result.stdout!r}"
        )
    assert isinstance(authors, list), (
        f"Expected .python.authors to be a JSON array from yq, got {type(authors).__name__}: {authors!r}."
    )
    assert "Example Team" in authors, (
        f"Expected 'Example Team' in .python.authors via yq, got {authors!r}."
    )
