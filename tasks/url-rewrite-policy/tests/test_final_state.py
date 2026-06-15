import pytest
import os
import requests
import socket
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"

@pytest.fixture(scope="session")
def start_app(xprocess):
    """
    Starts the npm service using xprocess. Confirms readiness via port check.
    """

    class Starter(ProcessStarter):
        name = "start_app"
        args = ["npm", "run", "dev", "--", "--port", "9200"]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            """
            Custom check: returns True if port 9200 is accepting connections.
            """
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 9200)) == 0

    xprocess.ensure(Starter.name, Starter)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()

def test_url_rewrite(start_app):
    """
    Test that the URL rewrite policy successfully rewrites /api/v1/users to /users
    before forwarding to echo.zuplo.io.
    """
    url = "http://localhost:9200/api/v1/users"
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        pytest.fail(f"Request to {url} failed: {e}")

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    
    try:
        data = response.json()
    except ValueError:
        pytest.fail(f"Response is not valid JSON: {response.text}")

    # echo.zuplo.io returns the full requested URL in the 'url' field
    assert data.get("url") == "https://echo.zuplo.io/users", \
        f"Expected the backend to receive path '/users', but it received URL: {data.get('url')}"
