import os
import shutil


PROJECT_DIR = "/home/user/project"


def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, "speakeasy binary not found in PATH."


def test_yq_binary_available():
    assert shutil.which("yq") is not None, "yq binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_openapi_seed_exists():
    openapi_path = os.path.join(PROJECT_DIR, "openapi.yaml")
    assert os.path.isfile(openapi_path), f"Seed OpenAPI file {openapi_path} does not exist."
    with open(openapi_path) as f:
        content = f.read()
    assert content.lstrip().startswith("openapi: 3."), \
        "Seed openapi.yaml must declare an OpenAPI 3.x document."


def test_workflow_yaml_not_pre_created():
    """The agent must author this file themselves; it must not be seeded."""
    workflow_path = os.path.join(PROJECT_DIR, ".speakeasy", "workflow.yaml")
    assert not os.path.exists(workflow_path), \
        f"{workflow_path} must NOT exist in the initial state; the agent is expected to create it."
