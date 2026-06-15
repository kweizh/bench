import os
import subprocess

PROJECT_DIR = "/home/user/project"
GEN_YAML = os.path.join(PROJECT_DIR, "gen.yaml")


def _yq(expr: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["yq", expr, GEN_YAML],
        capture_output=True,
        text=True,
        check=False,
    )


def _yq_r(expr: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["yq", "-r", expr, GEN_YAML],
        capture_output=True,
        text=True,
        check=False,
    )


def test_gen_yaml_still_exists():
    assert os.path.isfile(GEN_YAML), (
        f"Expected {GEN_YAML} to exist after the task, but the file is missing. "
        "The executor must edit gen.yaml in place rather than delete it."
    )


def test_oauth2_client_credentials_enabled_is_true():
    result = _yq_r(".generation.auth.oAuth2ClientCredentialsEnabled")
    assert result.returncode == 0, (
        "yq failed while reading "
        f".generation.auth.oAuth2ClientCredentialsEnabled from {GEN_YAML}. "
        f"stderr: {result.stderr.strip()}"
    )
    value = result.stdout.strip()
    assert value == "true", (
        "Expected .generation.auth.oAuth2ClientCredentialsEnabled to be 'true' "
        f"in {GEN_YAML}, but yq returned '{value}'."
    )


def test_config_version_preserved():
    result = _yq_r(".configVersion")
    assert result.returncode == 0, (
        f"yq failed while reading .configVersion from {GEN_YAML}. "
        f"stderr: {result.stderr.strip()}"
    )
    value = result.stdout.strip()
    assert value == "2.0.0", (
        f"Expected .configVersion to remain '2.0.0' in {GEN_YAML}, but got "
        f"'{value}'."
    )


def test_generation_block_still_present():
    result = _yq_r('has("generation")')
    assert result.returncode == 0, (
        f"yq failed while checking the top-level 'generation' key in {GEN_YAML}. "
        f"stderr: {result.stderr.strip()}"
    )
    assert result.stdout.strip() == "true", (
        f"The top-level 'generation' mapping is missing from {GEN_YAML} after "
        "the edit. It must remain present."
    )


def test_sdk_class_name_preserved():
    result = _yq_r(".generation.sdkClassName")
    assert result.returncode == 0, (
        f"yq failed while reading .generation.sdkClassName from {GEN_YAML}. "
        f"stderr: {result.stderr.strip()}"
    )
    value = result.stdout.strip()
    assert value and value != "null", (
        "Expected .generation.sdkClassName to remain a non-empty string in "
        f"{GEN_YAML}, but got '{value}'."
    )


def test_typescript_target_preserved():
    result = _yq_r('has("typescript")')
    assert result.returncode == 0, (
        f"yq failed while checking for the typescript target in {GEN_YAML}. "
        f"stderr: {result.stderr.strip()}"
    )
    assert result.stdout.strip() == "true", (
        f"The top-level 'typescript' target section is missing from {GEN_YAML} "
        "after the edit. It must remain present."
    )


def test_generation_auth_is_mapping():
    # Querying the .generation.auth subtree should return a non-null mapping,
    # not a scalar or null value.
    result = _yq(".generation.auth")
    assert result.returncode == 0, (
        f"yq failed while reading .generation.auth from {GEN_YAML}. "
        f"stderr: {result.stderr.strip()}"
    )
    output = result.stdout.strip()
    assert output and output.lower() != "null", (
        f"Expected .generation.auth in {GEN_YAML} to remain a mapping (not "
        f"null or a scalar). Got: '{output}'."
    )
    assert "oAuth2ClientCredentialsEnabled" in output, (
        "Expected the .generation.auth mapping to still contain the key "
        f"'oAuth2ClientCredentialsEnabled'. yq output was: {output}"
    )
