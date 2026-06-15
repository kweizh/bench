import os
import shutil
import pytest

def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."

def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_zuplo_available():
    assert shutil.which("zuplo") is not None, "zuplo CLI binary not found in PATH."