import os
import subprocess


PROJECT_DIR = "/home/user/project"
WORKFLOW_PATH = os.path.join(PROJECT_DIR, ".speakeasy", "workflow.yaml")
OPENAPI_PATH = os.path.join(PROJECT_DIR, "openapi.yaml")


def _yq(expr: str) -> str:
    """Run `yq` against the workflow file and return the trimmed stdout."""
    result = subprocess.run(
        ["yq", expr, WORKFLOW_PATH],
        capture_output=True, text=True
    )
    assert result.returncode == 0, (
        f"yq '{expr}' failed for {WORKFLOW_PATH}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    return result.stdout.strip()


def test_workflow_yaml_exists():
    assert os.path.isfile(WORKFLOW_PATH), (
        f"Expected workflow file at {WORKFLOW_PATH}, but it does not exist."
    )


def test_workflow_yaml_is_valid_yaml():
    """yq must be able to parse the file (round-trip the document)."""
    result = subprocess.run(
        ["yq", ".", WORKFLOW_PATH],
        capture_output=True, text=True
    )
    assert result.returncode == 0, (
        f"yq could not parse {WORKFLOW_PATH} as YAML.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_workflow_version_present():
    value = _yq(".workflowVersion")
    assert value and value.lower() != "null", (
        f"Top-level 'workflowVersion' is missing or null in {WORKFLOW_PATH}."
    )


def test_source_my_api_points_to_local_openapi():
    location = _yq('.sources."my-api".inputs[0].location')
    assert location == "./openapi.yaml", (
        f"Expected sources.my-api.inputs[0].location == './openapi.yaml', got '{location}'."
    )


def test_target_typescript_sdk_type():
    target_type = _yq('.targets."typescript-sdk".target')
    assert target_type == "typescript", (
        f"Expected targets.typescript-sdk.target == 'typescript', got '{target_type}'."
    )


def test_target_typescript_sdk_source_reference():
    source_ref = _yq('.targets."typescript-sdk".source')
    assert source_ref == "my-api", (
        f"Expected targets.typescript-sdk.source == 'my-api', got '{source_ref}'."
    )


def test_openapi_seed_unchanged():
    assert os.path.isfile(OPENAPI_PATH), (
        f"Seed OpenAPI file {OPENAPI_PATH} is missing after task execution."
    )
    with open(OPENAPI_PATH) as f:
        content = f.read()
    assert content.lstrip().startswith("openapi: 3."), (
        "Seed openapi.yaml no longer starts with an OpenAPI 3.x declaration."
    )


def test_speakeasy_run_help_accepts_workflow_layout():
    """Structural sanity check: the real Speakeasy CLI must accept the project."""
    result = subprocess.run(
        ["speakeasy", "run", "--help"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, (
        f"'speakeasy run --help' failed in {PROJECT_DIR}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    combined = (result.stdout + result.stderr).lower()
    assert "workflow" in combined, (
        "Expected `speakeasy run --help` output to mention 'workflow'. "
        f"Got:\n{result.stdout}\n{result.stderr}"
    )
