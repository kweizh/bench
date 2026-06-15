import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/project"
OPENAPI_PATH = os.path.join(PROJECT_DIR, "openapi.yaml")


def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, (
        "speakeasy CLI binary not found in PATH."
    )


def test_yq_binary_available():
    assert shutil.which("yq") is not None, "yq binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_openapi_spec_seeded():
    assert os.path.isfile(OPENAPI_PATH), (
        f"Seeded OpenAPI spec {OPENAPI_PATH} does not exist."
    )


def test_openapi_spec_has_internal_health_get():
    result = subprocess.run(
        ["yq", '.paths."/internal/health".get.operationId', OPENAPI_PATH],
        capture_output=True,
        text=True,
        check=True,
    )
    op_id = result.stdout.strip()
    assert op_id and op_id != "null", (
        "Seeded openapi.yaml is missing a GET operation under /internal/health."
    )


def test_openapi_spec_has_public_items_get():
    result = subprocess.run(
        ["yq", '.paths."/public/items".get.operationId', OPENAPI_PATH],
        capture_output=True,
        text=True,
        check=True,
    )
    op_id = result.stdout.strip()
    assert op_id == "listItems", (
        "Seeded openapi.yaml is missing the expected GET /public/items operation "
        f"with operationId 'listItems' (got {op_id!r})."
    )


def test_openapi_spec_has_no_speakeasy_ignore_initially():
    result = subprocess.run(
        ["yq", '.paths."/internal/health".get."x-speakeasy-ignore"', OPENAPI_PATH],
        capture_output=True,
        text=True,
        check=True,
    )
    value = result.stdout.strip()
    assert value == "null", (
        "Seeded openapi.yaml must NOT already contain x-speakeasy-ignore on "
        f"/internal/health.get (got {value!r})."
    )


def test_overlay_not_yet_created():
    assert not os.path.exists(os.path.join(PROJECT_DIR, "overlay.yaml")), (
        "overlay.yaml must not exist before the executor runs the task."
    )


def test_result_not_yet_created():
    assert not os.path.exists(os.path.join(PROJECT_DIR, "result.yaml")), (
        "result.yaml must not exist before the executor runs the task."
    )
