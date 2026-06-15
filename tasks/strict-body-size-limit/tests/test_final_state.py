import pytest
import os
import socket
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"

@pytest.fixture(scope="session")
def start_app(xprocess):
    """
    Starts the zuplo dev server using xprocess. Confirms readiness via port check.
    """
    
    # Run npm install first
    import subprocess
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)

    class Starter(ProcessStarter):
        name = "start_app"
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
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()

def test_valid_payload_size(start_app):
    """Test that a payload <= 1024 bytes is accepted."""
    url = "http://localhost:9200/upload"
    headers = {"Content-Type": "text/plain"}
    data = "Small payload"
    
    response = requests.post(url, headers=headers, data=data)
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"
    assert "Upload successful" in response.text, f"Expected 'Upload successful' in response text, got: {response.text}"

def test_payload_too_large(start_app):
    """Test that a payload > 1024 bytes is rejected."""
    url = "http://localhost:9200/upload"
    headers = {"Content-Type": "text/plain"}
    data = "A" * 1025
    
    response = requests.post(url, headers=headers, data=data)
    
    assert response.status_code == 413, f"Expected status 413, got {response.status_code}. Response: {response.text}"
    assert "Payload Too Large" in response.text, f"Expected 'Payload Too Large' in response text, got: {response.text}"

def test_missing_content_length(start_app):
    """Test that a request without Content-Length is rejected."""
    url = "http://localhost:9200/upload"
    # requests automatically adds Content-Length if data is provided as a string.
    # To send a chunked request without Content-Length, we can provide a generator.
    def generate_chunked_data():
        yield b"Chunked payload"
        
    headers = {"Content-Type": "text/plain"}
    
    response = requests.post(url, headers=headers, data=generate_chunked_data())
    
    assert response.status_code == 413, f"Expected status 413, got {response.status_code}. Response: {response.text}"
    assert "Payload Too Large" in response.text, f"Expected 'Payload Too Large' in response text, got: {response.text}"
