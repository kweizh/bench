import os
import requests
import socket
import subprocess
import pytest
from xprocess import ProcessStarter

# Read RUN_ID from environment
RUN_ID = os.environ.get("ZEALT_RUN_ID", "test-run")
PROJECT_DIR = f"/home/user/myproject-{RUN_ID}"
PORT = 9200

@pytest.fixture(scope="session")
def start_app(xprocess):
    """
    Starts the zuplo dev server using xprocess. Confirms readiness via port check.
    """
    # Ensure project directory exists
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

    # Run npm install synchronously before starting the server
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)

    class Starter(ProcessStarter):
        name = "zuplo_dev"
        args = ["zuplo", "dev", "--port", str(PORT)]
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

def test_users_route_get(start_app):
    """Test that GET /api/v1/users/{id} proxies to httpbin correctly."""
    url = f"http://localhost:{PORT}/api/v1/users/u-123"
    response = requests.get(url)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"
    
    data = response.json()
    expected_url = "https://httpbin.org/anything/users/u-123"
    assert data.get("url") == expected_url, f"Expected proxied url to be {expected_url}, got {data.get('url')}"

def test_products_route_post(start_app):
    """Test that POST /api/v1/products/{id} proxies to httpbin correctly and forwards body."""
    url = f"http://localhost:{PORT}/api/v1/products/p-456"
    payload = {"item": "laptop"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"
    
    data = response.json()
    expected_url = "https://httpbin.org/anything/products/p-456"
    assert data.get("url") == expected_url, f"Expected proxied url to be {expected_url}, got {data.get('url')}"
    
    json_body = data.get("json")
    assert json_body == payload, f"Expected forwarded json body to be {payload}, got {json_body}"
