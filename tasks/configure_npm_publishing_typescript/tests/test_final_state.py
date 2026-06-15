import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/project"
GEN_YAML = os.path.join(PROJECT_DIR, "gen.yaml")


def _yq(path):
    result = subprocess.run(
        ["yq", path, GEN_YAML],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"yq failed for path '{path}': {result.stderr.strip()}"
    )
    return result.stdout.strip()


def test_gen_yaml_still_exists():
    assert os.path.isfile(GEN_YAML), (
        f"gen.yaml must still exist at {GEN_YAML} after the task."
    )


def test_gen_yaml_is_valid_yaml():
    # `yq .` will fail with non-zero exit code if the file is not valid YAML.
    result = subprocess.run(
        ["yq", ".", GEN_YAML],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"gen.yaml is not valid YAML: {result.stderr.strip()}"
    )


def test_typescript_package_name_is_scoped_sdk():
    value = _yq(".typescript.packageName")
    assert value == "@example/my-sdk", (
        "Expected .typescript.packageName to be '@example/my-sdk' in gen.yaml, "
        f"got: {value!r}"
    )


def test_typescript_author_is_example_team():
    value = _yq(".typescript.author")
    assert value == "Example Team", (
        "Expected .typescript.author to be 'Example Team' in gen.yaml, "
        f"got: {value!r}"
    )


def test_typescript_version_field_preserved():
    value = _yq(".typescript.version")
    assert value and value != "null", (
        "Expected .typescript.version to still be present (non-empty) in gen.yaml "
        f"after the change, got: {value!r}"
    )


def test_config_version_preserved():
    value = _yq(".configVersion")
    assert value and value != "null", (
        "Expected top-level .configVersion to still be present in gen.yaml after "
        f"the change, got: {value!r}"
    )
