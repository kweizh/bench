import os
import subprocess
import requests
import socket
import pytest
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"

@pytest.fixture(scope="session")
def start_app(xprocess):
    """
    Starts the zuplo dev server on port 9200 using xprocess.
    """
    # First run npm install
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)

    class Starter(ProcessStarter):
        name = "zuplo_dev"
        args = ["zuplo", "dev", "--port", "9200"]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 9200)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()

def test_missing_query_parameter(start_app):
    """
    Request: GET http://localhost:9200/search
    Expected: Status 400, response body contains {"error": "Missing required query parameter: q"}
    """
    response = requests.get("http://localhost:9200/search")
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    data = response.json()
    assert "error" in data, "Expected 'error' in response body"
    assert "Missing required query parameter: q" in data["error"], f"Unexpected error message: {data['error']}"

def test_valid_query_parameter(start_app):
    """
    Request: GET http://localhost:9200/search?q=test_query
    Expected: Status 200, response body contains {"q": "test_query"}
    """
    response = requests.get("http://localhost:9200/search?q=test_query")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    data = response.json()
    assert "q" in data, "Expected 'q' in response body"
    assert data["q"] == "test_query", f"Expected q=test_query, got {data['q']}"
