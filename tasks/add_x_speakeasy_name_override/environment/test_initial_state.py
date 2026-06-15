import os
import shutil
import subprocess

import pytest
import yaml

PROJECT_DIR = "/home/user/project"
SPEC_PATH = os.path.join(PROJECT_DIR, "openapi.yaml")


def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, (
        "speakeasy CLI binary not found in PATH; "
        "the task requires the real Speakeasy CLI."
    )


def test_yq_binary_available():
    assert shutil.which("yq") is not None, (
        "yq binary not found in PATH; the task uses yq to inspect openapi.yaml."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_openapi_spec_exists():
    assert os.path.isfile(SPEC_PATH), f"OpenAPI spec {SPEC_PATH} does not exist."


@pytest.fixture(scope="module")
def spec_doc():
    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_openapi_spec_is_valid_yaml(spec_doc):
    assert isinstance(spec_doc, dict), "openapi.yaml must parse to a YAML mapping."
    assert "openapi" in spec_doc, "openapi.yaml must declare an `openapi` field."
    assert str(spec_doc["openapi"]).startswith("3.0"), (
        f"Expected openapi 3.0.x in seed spec, got {spec_doc.get('openapi')!r}."
    )


def test_seed_spec_has_pst_user_create_operation(spec_doc):
    paths = spec_doc.get("paths") or {}
    users = paths.get("/users") or {}
    post_op = users.get("post") or {}
    assert post_op.get("operationId") == "pst_user_create", (
        "Seed spec must declare operationId 'pst_user_create' on POST /users, "
        f"got {post_op.get('operationId')!r}."
    )


def test_seed_spec_has_no_name_override(spec_doc):
    """The seed spec must NOT already contain x-speakeasy-name-override.

    If it did, the executor would have nothing to add.
    """
    assert "x-speakeasy-name-override" not in spec_doc, (
        "Seed spec should not already define a top-level x-speakeasy-name-override."
    )
    paths = spec_doc.get("paths") or {}
    users = paths.get("/users") or {}
    post_op = users.get("post") or {}
    assert "x-speakeasy-name-override" not in post_op, (
        "Seed spec should not already define an operation-level "
        "x-speakeasy-name-override on POST /users."
    )


def test_seed_spec_passes_speakeasy_lint():
    """The seed spec must currently be lint-clean so we can detect regressions later."""
    result = subprocess.run(
        [
            "speakeasy",
            "lint",
            "openapi",
            "-s",
            SPEC_PATH,
            "--non-interactive",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        "Seed openapi.yaml should pass `speakeasy lint openapi` before the executor edits it.\n"
        f"exit={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
