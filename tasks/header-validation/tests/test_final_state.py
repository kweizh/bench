import pytest
import requests
import os
import socket
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"
PORT = 9200
BASE_URL = f"http://localhost:{PORT}"

@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "zuplo_dev"
        args = ["npx", "zuplo", "dev", "--port", str(PORT)]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", PORT)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()

def test_valid_request(start_app):
    """Test that a request with the correct custom header succeeds."""
    url = f"{BASE_URL}/protected"
    headers = {"x-custom-auth": "my-secret-token"}
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert data.get("message") == "success", f"Expected message 'success', got {data}"

def test_missing_header_request(start_app):
    """Test that a request without the custom header fails."""
    url = f"{BASE_URL}/protected"
    response = requests.get(url)
    
    assert response.status_code == 401, f"Expected status 401, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert data.get("error") == "Unauthorized", f"Expected error 'Unauthorized', got {data}"

def test_invalid_header_request(start_app):
    """Test that a request with an incorrect custom header fails."""
    url = f"{BASE_URL}/protected"
    headers = {"x-custom-auth": "wrong-token"}
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 401, f"Expected status 401, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert data.get("error") == "Unauthorized", f"Expected error 'Unauthorized', got {data}"
