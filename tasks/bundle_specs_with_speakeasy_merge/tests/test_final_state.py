import os
import subprocess

import pytest
import yaml

PROJECT_DIR = "/home/user/project"
MERGED_PATH = os.path.join(PROJECT_DIR, "merged.yaml")


def _load_merged():
    with open(MERGED_PATH) as f:
        return yaml.safe_load(f)


def test_merged_file_exists():
    assert os.path.isfile(MERGED_PATH), f"Expected merged spec at {MERGED_PATH}, but it does not exist."
    assert os.path.getsize(MERGED_PATH) > 0, f"Merged spec at {MERGED_PATH} is empty."


def test_merged_file_is_valid_yaml():
    try:
        doc = _load_merged()
    except yaml.YAMLError as exc:
        pytest.fail(f"{MERGED_PATH} is not valid YAML: {exc}")
    assert isinstance(doc, dict), f"{MERGED_PATH} did not parse as a YAML mapping."


def test_merged_file_is_openapi_3():
    doc = _load_merged()
    openapi_version = doc.get("openapi")
    assert isinstance(openapi_version, str), (
        f"Top-level `openapi` field is missing or not a string in {MERGED_PATH}. Got: {openapi_version!r}"
    )
    assert openapi_version.startswith("3."), (
        f"Merged spec must be an OpenAPI 3.x document. Got openapi={openapi_version!r}."
    )


def test_merged_file_contains_users_path():
    doc = _load_merged()
    paths = doc.get("paths") or {}
    assert "/users" in paths, (
        f"Merged spec must contain the `/users` path from spec_a.yaml. "
        f"Found paths: {list(paths.keys())}"
    )


def test_merged_file_contains_products_path():
    doc = _load_merged()
    paths = doc.get("paths") or {}
    assert "/products" in paths, (
        f"Merged spec must contain the `/products` path from spec_b.yaml. "
        f"Found paths: {list(paths.keys())}"
    )


def test_merged_file_passes_speakeasy_lint():
    result = subprocess.run(
        [
            "speakeasy",
            "lint",
            "openapi",
            "-s",
            MERGED_PATH,
            "--non-interactive",
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"`speakeasy lint openapi -s {MERGED_PATH} --non-interactive` returned "
        f"exit code {result.returncode}.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
