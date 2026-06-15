import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"
OPENAPI_FILE = os.path.join(PROJECT_DIR, "openapi.yaml")

def test_speakeasy_validate_success():
    """Priority 1: Use Speakeasy CLI to verify the OpenAPI specification is valid."""
    result = subprocess.run(
        ["speakeasy", "lint", "openapi", "-s", "openapi.yaml"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"'speakeasy lint openapi' failed: {result.stderr}\n{result.stdout}"

def test_openapi_yaml_has_retries_configuration():
    """Priority 3: Parse openapi.yaml to check for x-speakeasy-retries configuration."""
    assert os.path.isfile(OPENAPI_FILE), f"OpenAPI specification {OPENAPI_FILE} does not exist."
    
    with open(OPENAPI_FILE, "r") as f:
        content = f.read()
        
    assert "x-speakeasy-retries:" in content, "Expected 'x-speakeasy-retries:' in openapi.yaml"
    assert "strategy: backoff" in content or "strategy: \"backoff\"" in content or "strategy: 'backoff'" in content, "Expected strategy to be 'backoff'"
    assert "initialInterval: 500" in content, "Expected initialInterval to be 500"
    assert "maxInterval: 60000" in content, "Expected maxInterval to be 60000"
    assert "maxElapsedTime: 3600000" in content, "Expected maxElapsedTime to be 3600000"
    assert "exponent: 1.5" in content, "Expected exponent to be 1.5"
    assert "5XX" in content, "Expected '5XX' in statusCodes"
    assert "retryConnectionErrors: true" in content or "retryConnectionErrors: True" in content, "Expected retryConnectionErrors to be true"
