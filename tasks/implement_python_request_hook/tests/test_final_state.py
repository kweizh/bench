import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_gen_yaml_exists():
    gen_yaml = os.path.join(PROJECT_DIR, "gen.yaml")
    assert os.path.isfile(gen_yaml), "gen.yaml does not exist."
    with open(gen_yaml) as f:
        content = f.read()
    assert "python:" in content.lower(), "gen.yaml is not configured for Python."

def test_sdk_installable():
    result = subprocess.run(
        ["pip3", "install", "--break-system-packages", "-e", "."],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Failed to install generated SDK: {result.stderr}\n{result.stdout}"

def test_hook_implementation_exists():
    hooks_dir = os.path.join(PROJECT_DIR, "src", "my_sdk", "hooks")
    assert os.path.isdir(hooks_dir), f"Hooks directory {hooks_dir} not found."
    
    found_header = False
    for root, _, files in os.walk(hooks_dir):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file)) as f:
                    content = f.read()
                    if "X-Organization-Id" in content and "org_12345" in content:
                        found_header = True
                        break
    
    assert found_header, "Could not find X-Organization-Id and org_12345 in any hook file."

def test_hook_execution():
    script = """
import sys
import httpx
try:
    from my_sdk import MySdk
except ImportError:
    print("my_sdk not found")
    sys.exit(1)

class MockTransport(httpx.BaseTransport):
    def __init__(self):
        self.request = None

    def handle_request(self, request):
        self.request = request
        return httpx.Response(200, json={"message": "ok"})

transport = MockTransport()
client = httpx.Client(transport=transport)
sdk = MySdk(client=client)

method_called = False
for attr in dir(sdk):
    if not attr.startswith("_"):
        obj = getattr(sdk, attr)
        if hasattr(obj, "get_hello"):
            obj.get_hello()
            method_called = True
            break
        if attr == "get_hello":
            obj()
            method_called = True
            break

if not method_called:
    req = client.build_request("GET", "https://api.example.com/hello")
    if hasattr(sdk, "sdk_configuration") and hasattr(sdk.sdk_configuration, "hooks"):
        try:
            from my_sdk.hooks.types import BeforeRequestContext
            context = BeforeRequestContext(hook_ctx_name="dummy", operation_id="dummy", security_source=None)
            req = sdk.sdk_configuration.hooks.before_request(context, req)
        except Exception as e:
            print(f"Error calling hook directly: {e}")
    else:
        print("Could not find hooks in SDK configuration")
        sys.exit(1)
    transport.request = req

if not transport.request:
    print("No request made")
    sys.exit(1)

if transport.request.headers.get("X-Organization-Id") != "org_12345":
    print(f"Header missing or wrong: {transport.request.headers}")
    sys.exit(1)

print("SUCCESS")
"""
    script_path = os.path.join(PROJECT_DIR, "test_hook.py")
    with open(script_path, "w") as f:
        f.write(script)

    result = subprocess.run(
        ["python3", "test_hook.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Hook verification failed: {result.stdout}\n{result.stderr}"
    assert "SUCCESS" in result.stdout, f"Hook did not inject the header correctly. Output: {result.stdout}"
