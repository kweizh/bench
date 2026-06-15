import os
import shutil
import pytest

def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."
    assert shutil.which("npm") is not None, "npm binary not found in PATH."
    assert shutil.which("npx") is not None, "npx binary not found in PATH."

def test_zuplo_cli_available():
    assert shutil.which("zuplo") is not None, "zuplo binary not found in PATH."
