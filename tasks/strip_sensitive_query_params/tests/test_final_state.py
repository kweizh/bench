import os
import time
import socket
import requests
import pytest
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"

@pytest.fixture(scope="session")
def start_app(xprocess):
    """
    Starts the zuplo dev server using xprocess. Confirms readiness via port check.
    """
    class Starter(ProcessStarter):
        name = "zuplo_dev"
        args = ["npx", "zuplo", "dev", "--port", "9200"]
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
    
    # Wait an additional few seconds to ensure the server is fully ready to handle requests
    time.sleep(5)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()

def test_query_parameter_removal(start_app):
    """
    Verify that the secret_token query parameter is removed before forwarding.
    """
    url = "http://localhost:9200/echo?foo=bar&secret_token=12345"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    try:
        data = response.json()
    except Exception as e:
        pytest.fail(f"Failed to parse response as JSON: {e}\nResponse text: {response.text}")
        
    # https://echo.zuplo.io/ returns the request details, usually in 'query' or 'url'
    # Check that 'foo' is present
    response_text = response.text
    
    assert "foo" in response_text and "bar" in response_text, \
        f"Expected query parameter 'foo=bar' to be preserved. Response: {response_text}"
        
    assert "secret_token" not in response_text and "12345" not in response_text, \
        f"Expected query parameter 'secret_token' to be removed. Response: {response_text}"

def test_normal_requests(start_app):
    """
    Verify that normal requests without secret_token are handled correctly.
    """
    url = "http://localhost:9200/echo?hello=world"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    response_text = response.text
    
    assert "hello" in response_text and "world" in response_text, \
        f"Expected query parameter 'hello=world' to be preserved. Response: {response_text}"
