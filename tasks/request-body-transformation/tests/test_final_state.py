import os
import requests
import socket
import pytest
from xprocess import ProcessStarter
import re

PROJECT_DIR = "/home/user/myproject"

@pytest.fixture(scope="session", autouse=True)
def setup_project():
    """
    Run npm install and npm run build before starting the app.
    """
    import subprocess
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)
    # The build script might not be present or needed depending on how the executor set it up,
    # but we'll try to run it if it exists.
    try:
        subprocess.run(["npm", "run", "build"], cwd=PROJECT_DIR, check=True)
    except subprocess.CalledProcessError:
        pass

@pytest.fixture(scope="session")
def start_app(xprocess):
    """
    Starts the zuplo dev server using xprocess. Confirms readiness via port check.
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

def test_request_body_transformation(start_app):
    """
    Verify that the JSON payload is transformed into the expected XML format.
    """
    url = "http://localhost:3000/api/submit"
    headers = {"Content-Type": "application/json"}
    payload = {
        "user": {
            "name": "Bob",
            "role": "developer"
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    
    # Remove whitespace to make the comparison robust against formatting differences
    actual_xml = re.sub(r'>\s+<', '><', response.text.strip())
    expected_xml = "<user><name>Bob</name><role>developer</role></user>"
    
    assert expected_xml in actual_xml, f"Expected transformed XML to contain '{expected_xml}', but got '{response.text}'"
