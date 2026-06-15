import os
import re
import subprocess

import pytest
import yaml

PROJECT_DIR = "/home/user/project"
SPEC_PATH = os.path.join(PROJECT_DIR, "openapi.yaml")

TARGET_OPERATION_ID = "pst_user_create"
TARGET_METHOD_NAME = "createUser"


@pytest.fixture(scope="module")
def spec_doc():
    assert os.path.isfile(SPEC_PATH), f"OpenAPI spec {SPEC_PATH} does not exist."
    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _run_yq(expr: str) -> str:
    """Run `yq <expr> <SPEC_PATH>` and return stripped stdout."""
    result = subprocess.run(
        ["yq", expr, SPEC_PATH],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"yq invocation failed for expression {expr!r}.\n"
        f"exit={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    return (result.stdout or "").strip()


def test_spec_is_valid_yaml(spec_doc):
    assert isinstance(spec_doc, dict), "openapi.yaml must parse to a YAML mapping."


def test_spec_still_declares_openapi_3_0(spec_doc):
    version = str(spec_doc.get("openapi", ""))
    assert version.startswith("3.0"), (
        f"Expected OpenAPI version to remain 3.0.x, got {version!r}."
    )


def test_spec_preserves_target_operation(spec_doc):
    paths = spec_doc.get("paths") or {}
    users = paths.get("/users") or {}
    post_op = users.get("post") or {}
    assert post_op.get("operationId") == TARGET_OPERATION_ID, (
        "The original operationId 'pst_user_create' on POST /users must be preserved; "
        f"got {post_op.get('operationId')!r}."
    )


def test_spec_preserves_user_schema(spec_doc):
    components = spec_doc.get("components") or {}
    schemas = components.get("schemas") or {}
    assert "User" in schemas, "Schema component `User` is missing from openapi.yaml."


def _operation_level_override_via_yq() -> bool:
    """Return True iff the operation-level override is present and equal to TARGET_METHOD_NAME."""
    expr = '.paths."/users".post."x-speakeasy-name-override" // ""'
    value = _run_yq(expr)
    return value == TARGET_METHOD_NAME


def _global_level_override_matches(spec_doc) -> bool:
    """Return True iff a top-level x-speakeasy-name-override sequence contains a
    rule whose `operationId` regex matches the literal `pst_user_create`
    and whose `methodNameOverride` is exactly `createUser`."""
    rules = spec_doc.get("x-speakeasy-name-override")
    if not isinstance(rules, list):
        return False
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        method_override = rule.get("methodNameOverride")
        op_id_pattern = rule.get("operationId")
        if method_override != TARGET_METHOD_NAME:
            continue
        if not isinstance(op_id_pattern, str) or not op_id_pattern:
            continue
        try:
            if re.search(op_id_pattern, TARGET_OPERATION_ID):
                return True
        except re.error:
            # Speakeasy uses regexes; an invalid regex cannot match.
            continue
    return False


def test_x_speakeasy_name_override_renames_operation(spec_doc):
    """At least one of the two documented forms of x-speakeasy-name-override must apply.

    Form 1 (operation-level): paths./users.post.x-speakeasy-name-override == "createUser".
    Form 2 (global-level):    a top-level x-speakeasy-name-override list contains a rule
                              whose operationId regex matches 'pst_user_create' and whose
                              methodNameOverride equals 'createUser'.
    """
    op_level_ok = _operation_level_override_via_yq()
    global_level_ok = _global_level_override_matches(spec_doc)
    assert op_level_ok or global_level_ok, (
        "Could not find an x-speakeasy-name-override rule that renames "
        f"operationId {TARGET_OPERATION_ID!r} to {TARGET_METHOD_NAME!r}.\n"
        "Expected one of:\n"
        "  - operation-level: paths./users.post.x-speakeasy-name-override == 'createUser'\n"
        "  - global-level: top-level x-speakeasy-name-override list with an entry "
        "    {operationId: <regex matching 'pst_user_create'>, methodNameOverride: 'createUser'}"
    )


def test_speakeasy_lint_still_succeeds():
    """After the edit, `speakeasy lint openapi` must still exit 0 (spec stays valid)."""
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
        timeout=300,
    )
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    assert result.returncode == 0, (
        "`speakeasy lint openapi` exited non-zero after the edit; the spec is no longer valid.\n"
        f"exit={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    # Defensive: the linter's summary should not report any errors.
    error_summary = re.search(r"(\d+)\s+errors?", combined, flags=re.IGNORECASE)
    if error_summary is not None:
        count = int(error_summary.group(1))
        assert count == 0, (
            f"Speakeasy lint reported {count} errors after the edit.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
