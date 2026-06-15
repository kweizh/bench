import os
import requests
import socket
import pytest
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"

@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "zuplo_dev"
        args = ["npx", "zuplo", "dev", "--editor-port", "9200"]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 9000)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()

def test_custom_not_found_handler(start_app):
    url = "http://localhost:9000/some-random-non-existent-route"
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to connect to Zuplo dev server at {url}: {e}")

    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    
    try:
        data = response.json()
    except ValueError:
        pytest.fail(f"Response is not valid JSON. Content: {response.text}")
        
    assert data.get("error") == "Not Found", f"Expected error to be 'Not Found', got {data.get('error')}"
    assert data.get("message") == "Custom 404 handler", f"Expected message to be 'Custom 404 handler', got {data.get('message')}"
