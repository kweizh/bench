import os
import socket
import pytest
import requests
import json
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"

@pytest.fixture(scope="session")
def start_app(xprocess):
    """
    Starts the Zuplo dev server using xprocess. Confirms readiness via port check.
    """
    class Starter(ProcessStarter):
        name = "zuplo_dev"
        args = ["npx", "zuplo", "dev", "--port", "3000"]
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

def test_missing_tenant_id_header(start_app):
    """Verify that omitting the header returns a 401 Unauthorized."""
    response = requests.get("http://localhost:3000/api/data")
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

def test_route_to_tenant_a(start_app):
    """Verify routing to tenant-a backend."""
    headers = {"x-mock-tenant-id": "tenant-a"}
    response = requests.get("http://localhost:3000/api/data", headers=headers)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    data = response.json()
    url = data.get("url", "")
    assert "echo.zuplo.io/tenant-a/data" in url, f"Expected url to contain 'echo.zuplo.io/tenant-a/data', got: {url}"

def test_route_to_tenant_b(start_app):
    """Verify routing to tenant-b backend."""
    headers = {"x-mock-tenant-id": "tenant-b"}
    response = requests.get("http://localhost:3000/api/data", headers=headers)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    data = response.json()
    url = data.get("url", "")
    assert "echo.zuplo.io/tenant-b/data" in url, f"Expected url to contain 'echo.zuplo.io/tenant-b/data', got: {url}"
