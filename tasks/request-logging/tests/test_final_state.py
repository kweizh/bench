import pytest
import os
import socket
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = "/home/user/server.log"

@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "zuplo_dev"
        args = ["bash", "-c", f"npx zuplo dev --editor-port 9200 --port 3000 > {LOG_FILE} 2>&1"]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 3000)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()

def test_route_response(start_app):
    url = "http://localhost:3000/hello"
    headers = {"x-custom-id": "harbor-test-123"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert response.text == "Hello World", f"Expected 'Hello World', got '{response.text}'"

def test_server_logs(start_app):
    assert os.path.isfile(LOG_FILE), f"Log file not found at {LOG_FILE}"
    with open(LOG_FILE, "r") as f:
        logs = f.read()
    assert "Custom ID: harbor-test-123" in logs, f"Expected log 'Custom ID: harbor-test-123' not found in server logs. Logs: {logs}"
