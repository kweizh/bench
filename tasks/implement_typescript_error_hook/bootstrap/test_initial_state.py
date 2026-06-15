import os
import pytest

PROJECT_DIR = "/home/user/sdk"

def test_sdk_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_hooks_directory_exists():
    hooks_dir = os.path.join(PROJECT_DIR, "src", "hooks")
    assert os.path.isdir(hooks_dir), f"Hooks directory {hooks_dir} does not exist."

def test_registration_ts_exists():
    registration_file = os.path.join(PROJECT_DIR, "src", "hooks", "registration.ts")
    assert os.path.isfile(registration_file), f"Registration file {registration_file} does not exist."

def test_types_ts_exists():
    types_file = os.path.join(PROJECT_DIR, "src", "hooks", "types.ts")
    assert os.path.isfile(types_file), f"Types file {types_file} does not exist."
