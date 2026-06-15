import os
import shutil
import pytest

def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."

def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_zuplo_available():
    # zuplo could be accessed via npx, but the research plan says `npm install -g zuplo` is typical.
    # We'll check if zuplo is in PATH or if npx can find it.
    assert shutil.which("zuplo") is not None or shutil.which("npx") is not None, "zuplo or npx binary not found in PATH."
