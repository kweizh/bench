import os
import subprocess

PROJECT_DIR = "/home/user/project"
OPENAPI_PATH = os.path.join(PROJECT_DIR, "openapi.yaml")
OVERLAY_PATH = os.path.join(PROJECT_DIR, "overlay.yaml")
RESULT_PATH = os.path.join(PROJECT_DIR, "result.yaml")


def _yq(expr: str, path: str) -> str:
    result = subprocess.run(
        ["yq", expr, path],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_overlay_file_exists():
    assert os.path.isfile(OVERLAY_PATH), (
        f"Expected overlay file at {OVERLAY_PATH} but it was not found."
    )


def test_overlay_version_is_1_0_0():
    value = _yq(".overlay", OVERLAY_PATH)
    assert value == "1.0.0", (
        f"overlay.yaml must declare 'overlay: 1.0.0' (got {value!r})."
    )


def test_overlay_has_info_title_and_version():
    title = _yq(".info.title", OVERLAY_PATH)
    version = _yq(".info.version", OVERLAY_PATH)
    assert title and title != "null", "overlay.yaml must define info.title."
    assert version and version != "null", "overlay.yaml must define info.version."


def test_overlay_targets_internal_health_get_with_speakeasy_ignore():
    # Find any action whose target matches /internal/health AND get,
    # and verify it sets x-speakeasy-ignore to true via update.
    expr = (
        '[.actions[] '
        '| select((.target | test("/internal/health")) '
        'and (.target | test("get"))) '
        '| .update["x-speakeasy-ignore"]] | .[0]'
    )
    value = _yq(expr, OVERLAY_PATH)
    assert value == "true", (
        "overlay.yaml must contain an action targeting the GET operation on "
        "/internal/health with an update that sets x-speakeasy-ignore to true "
        f"(got {value!r})."
    )


def test_result_file_exists():
    assert os.path.isfile(RESULT_PATH), (
        f"Expected merged result spec at {RESULT_PATH} but it was not found."
    )


def test_result_has_x_speakeasy_ignore_on_internal_health_get():
    value = _yq('.paths."/internal/health".get."x-speakeasy-ignore"', RESULT_PATH)
    assert value == "true", (
        "result.yaml must set paths./internal/health.get.x-speakeasy-ignore "
        f"to true (got {value!r})."
    )


def test_result_preserves_public_operation_without_speakeasy_ignore():
    op_id = _yq('.paths."/public/items".get.operationId', RESULT_PATH)
    assert op_id == "listItems", (
        "result.yaml must preserve the public GET /public/items operation with "
        f"operationId 'listItems' (got {op_id!r})."
    )
    ignore_value = _yq('.paths."/public/items".get."x-speakeasy-ignore"', RESULT_PATH)
    assert ignore_value == "null", (
        "result.yaml must NOT add x-speakeasy-ignore to the public "
        f"/public/items GET operation (got {ignore_value!r})."
    )


def test_original_openapi_spec_unchanged():
    # The original spec must not have been modified by the executor.
    value = _yq('.paths."/internal/health".get."x-speakeasy-ignore"', OPENAPI_PATH)
    assert value == "null", (
        "The original openapi.yaml must not be modified; "
        "x-speakeasy-ignore should not be present on /internal/health.get "
        f"(got {value!r})."
    )
