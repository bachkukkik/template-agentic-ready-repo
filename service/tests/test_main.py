"""Service unit + integration tests — pytest."""
import json
import os
import signal
import subprocess
import time
import urllib.error
import urllib.request

import pytest

SERVICE_URL = "http://127.0.0.1:18000"
SERVICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def service():
    """Start the service in a subprocess, yield, then stop it."""
    proc = subprocess.Popen(
        ["python", "-m", "src.main"],
        cwd=SERVICE_DIR,
        env={**os.environ, "PORT": "18000"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(1)
    yield proc
    proc.send_signal(signal.SIGTERM)
    proc.wait(timeout=5)


def test_health_endpoint(service):
    """AC-SVC-001: /health returns 200 with status=ok."""
    with urllib.request.urlopen(f"{SERVICE_URL}/health") as resp:
        assert resp.status == 200
        body = json.loads(resp.read())
        assert body["status"] == "ok"


def test_root_endpoint(service):
    """AC-SVC-002: / returns 200 with a message."""
    with urllib.request.urlopen(f"{SERVICE_URL}/") as resp:
        assert resp.status == 200
        body = json.loads(resp.read())
        assert "message" in body


def test_404_unknown_path(service):
    """AC-SVC-003: unknown path returns 404."""
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(f"{SERVICE_URL}/nonexistent")
    assert exc.value.code == 404
