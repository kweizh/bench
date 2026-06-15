import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/myproject"
TERRAFORM_DIR = os.path.join(PROJECT_DIR, "terraform")

def test_terraform_directory_exists():
    """Priority 3: Check if the terraform directory was created."""
    assert os.path.isdir(TERRAFORM_DIR), f"Expected terraform directory at {TERRAFORM_DIR} does not exist."

def test_provider_code_generated():
    """Priority 3: Check for key generated provider files."""
    provider_file_1 = os.path.join(TERRAFORM_DIR, "main.go")
    provider_file_2 = os.path.join(TERRAFORM_DIR, "internal", "provider", "provider.go")
    
    assert os.path.isfile(provider_file_1) or os.path.isfile(provider_file_2), \
        f"Neither {provider_file_1} nor {provider_file_2} found. Provider code may not have been generated correctly."

def test_pet_resource_generated():
    """Priority 3: Check if the Pet resource was generated based on OpenAPI annotations."""
    # The exact filename might vary slightly, but we can search for a file containing 'pet' in internal/provider
    provider_dir = os.path.join(TERRAFORM_DIR, "internal", "provider")
    
    if os.path.isdir(provider_dir):
        files = os.listdir(provider_dir)
        pet_files = [f for f in files if "pet" in f.lower()]
        assert len(pet_files) > 0, f"No file containing 'pet' found in {provider_dir}. Annotations may have been missed."
    else:
        # If internal/provider doesn't exist, maybe it generated flat structure
        files = os.listdir(TERRAFORM_DIR)
        pet_files = [f for f in files if "pet" in f.lower()]
        assert len(pet_files) > 0, f"No file containing 'pet' found in {TERRAFORM_DIR}. Annotations may have been missed."

def test_provider_compiles():
    """Priority 1: Run 'go build' to ensure the generated provider is valid Go code."""
    # First run go mod tidy
    tidy_result = subprocess.run(
        ["go", "mod", "tidy"],
        cwd=TERRAFORM_DIR,
        capture_output=True,
        text=True
    )
    assert tidy_result.returncode == 0, f"'go mod tidy' failed: {tidy_result.stderr}"
    
    # Then run go build
    build_result = subprocess.run(
        ["go", "build"],
        cwd=TERRAFORM_DIR,
        capture_output=True,
        text=True
    )
    assert build_result.returncode == 0, f"'go build' failed: {build_result.stderr}"
