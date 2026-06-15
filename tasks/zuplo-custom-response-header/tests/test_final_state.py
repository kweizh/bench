import os
import socket
import pytest
import requests
import base64
import time
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"

@pytest.fixture(scope="session")
def start_app(xprocess):
    """
    Starts the npm service using xprocess. Confirms readiness via port check.
    """
    
    # Run npm install first
    import subprocess
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)

    class Starter(ProcessStarter):
        name = "start_app"
        args = ["npm", "run", "dev"]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 8787)) == 0

    xprocess.ensure(Starter.name, Starter)
    
    # Wait a bit more for zuplo to fully initialize after the port is open
    time.sleep(15)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()

def test_custom_response_header(start_app):
    """Test the GET /hello route and its custom response header."""
    response = requests.get("http://localhost:8787/hello")
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    data = response.json()
    assert data.get("message") == "Hello World", f"Expected message 'Hello World', got {data.get('message')}"
    
    # The signature should be base64 encoded string of the response body text
    # Let's get the exact text from the response
    body_text = response.text
    expected_signature = base64.b64encode(body_text.encode('utf-8')).decode('utf-8')
    
    actual_signature = response.headers.get("x-signature")
    assert actual_signature is not None, "x-signature header is missing"
    assert actual_signature == expected_signature, f"Expected x-signature to be '{expected_signature}', got '{actual_signature}'"
