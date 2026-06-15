import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/project"
GEN_YAML = os.path.join(PROJECT_DIR, "gen.yaml")


def test_speakeasy_binary_available():
    assert shutil.which("speakeasy") is not None, (
        "speakeasy CLI binary was not found in PATH. The Speakeasy CLI must be "
        "installed in the task environment."
    )


def test_yq_binary_available():
    assert shutil.which("yq") is not None, (
        "yq binary was not found in PATH. yq is required to query the gen.yaml "
        "configuration during verification."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist. The task expects a "
        "pre-seeded Speakeasy project at this path."
    )


def test_gen_yaml_exists():
    assert os.path.isfile(GEN_YAML), (
        f"Expected pre-seeded Speakeasy config at {GEN_YAML}, but the file is "
        "missing."
    )


def test_gen_yaml_initial_oauth_flag_is_false():
    result = subprocess.run(
        ["yq", "-r", ".generation.auth.oAuth2ClientCredentialsEnabled", GEN_YAML],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        "yq failed to read .generation.auth.oAuth2ClientCredentialsEnabled from "
        f"{GEN_YAML}. stderr: {result.stderr.strip()}"
    )
    value = result.stdout.strip()
    assert value == "false", (
        "Expected initial value of .generation.auth.oAuth2ClientCredentialsEnabled "
        f"to be 'false' in {GEN_YAML}, but got '{value}'."
    )


def test_gen_yaml_has_typescript_target():
    result = subprocess.run(
        ["yq", "-r", 'has("typescript")', GEN_YAML],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"yq failed while checking for the typescript target in {GEN_YAML}. "
        f"stderr: {result.stderr.strip()}"
    )
    assert result.stdout.strip() == "true", (
        f"Expected the seeded {GEN_YAML} to include a top-level 'typescript' "
        "target section."
    )


def test_gen_yaml_has_config_version():
    result = subprocess.run(
        ["yq", "-r", ".configVersion", GEN_YAML],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"yq failed while reading .configVersion from {GEN_YAML}. "
        f"stderr: {result.stderr.strip()}"
    )
    value = result.stdout.strip()
    assert value and value != "null", (
        f"Expected {GEN_YAML} to declare a non-empty .configVersion, but got "
        f"'{value}'."
    )
