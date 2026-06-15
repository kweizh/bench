import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/myproject"

def test_workflow_yaml_exists():
    """Priority 3 fallback: check if workflow.yaml exists."""
    workflow_path = os.path.join(PROJECT_DIR, ".speakeasy", "workflow.yaml")
    assert os.path.isfile(workflow_path), f"Expected {workflow_path} to exist."
    with open(workflow_path) as f:
        content = f.read()
    assert "target: cli" in content or "cli:" in content, "Expected target cli in workflow.yaml"

def test_gen_yaml_exists():
    """Priority 3 fallback: check if gen.yaml exists."""
    gen_path = os.path.join(PROJECT_DIR, ".speakeasy", "gen.yaml")
    assert os.path.isfile(gen_path), f"Expected {gen_path} to exist."
    with open(gen_path) as f:
        content = f.read()
    assert "sdkClassName: TestAPI" in content, "Expected sdkClassName: TestAPI in gen.yaml"
    assert "cli:" in content, "Expected cli target definition in gen.yaml"

def test_speakeasy_lint_config():
    """Priority 1: Use speakeasy CLI to verify the configuration."""
    result = subprocess.run(
        ["speakeasy", "lint", "config"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"'speakeasy lint config' failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    assert "SDK generation configuration is valid" in result.stdout or "SDK generation configuration is valid" in result.stderr, \
        f"Expected configuration to be valid. Output: {result.stdout} {result.stderr}"
