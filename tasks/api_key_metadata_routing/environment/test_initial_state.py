import os
import shutil
import pytest

def test_zuplo_binary_available():
    assert shutil.which("zuplo") is not None or shutil.which("npx") is not None, "zuplo or npx binary not found in PATH."

def test_node_available():
    assert shutil.which("node") is not None, "Node.js is not installed."
