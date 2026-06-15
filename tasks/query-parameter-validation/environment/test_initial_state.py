import shutil

def test_zuplo_binary_available():
    assert shutil.which("zuplo") is not None, "zuplo binary not found in PATH."
