import os
import time
import socket
import subprocess
import requests
import jwt
import pytest
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"
SECRET_KEY = "my-super-secret-key"

@pytest.fixture(scope="session")
def free_token():
    payload = {"sub": "user1", "plan": "free"}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token.decode("utf-8") if isinstance(token, bytes) else token

@pytest.fixture(scope="session")
def pro_token():
    payload = {"sub": "user2", "plan": "pro"}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token.decode("utf-8") if isinstance(token, bytes) else token

@pytest.fixture(scope="session")
def start_app(xprocess):
    # Ensure npm install is run first
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)

    class Starter(ProcessStarter):
        name = "start_app"
        args = ["npm", "run", "dev", "--", "--editor-port", "9200"]
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
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()

def test_unauthorized_request(start_app):
    url = "http://localhost:8787/api/data"
    response = requests.get(url)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

def test_free_plan_rate_limit(start_app, free_token):
    url = "http://localhost:8787/api/data"
    headers = {"Authorization": f"Bearer {free_token}"}
    
    # Send 3 requests
    for i in range(2):
        response = requests.get(url, headers=headers)
        assert response.status_code == 200, f"Expected 200 OK for free plan request {i+1}, got {response.status_code}"
        try:
            assert response.json() == {"data": "success"}, f"Expected {{'data': 'success'}}, got {response.text}"
        except ValueError:
            pytest.fail(f"Response is not valid JSON: {response.text}")
    
    response = requests.get(url, headers=headers)
    assert response.status_code == 429, f"Expected 429 Too Many Requests for free plan 3rd request, got {response.status_code}"

def test_pro_plan_rate_limit(start_app, pro_token):
    url = "http://localhost:8787/api/data"
    headers = {"Authorization": f"Bearer {pro_token}"}
    
    # Send 6 requests
    for i in range(5):
        response = requests.get(url, headers=headers)
        assert response.status_code == 200, f"Expected 200 OK for pro plan request {i+1}, got {response.status_code}"
        try:
            assert response.json() == {"data": "success"}, f"Expected {{'data': 'success'}}, got {response.text}"
        except ValueError:
            pytest.fail(f"Response is not valid JSON: {response.text}")
    
    response = requests.get(url, headers=headers)
    assert response.status_code == 429, f"Expected 429 Too Many Requests for pro plan 6th request, got {response.status_code}"
