import shutil

def test_zuplo_cli_available():
    assert shutil.which("zuplo") is not None, "zuplo CLI is not found in PATH."

def test_npm_available():
    assert shutil.which("npm") is not None, "npm is not found in PATH."

def test_npx_available():
    assert shutil.which("npx") is not None, "npx is not found in PATH."
