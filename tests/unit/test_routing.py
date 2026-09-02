"""Unit tier — pure logic, no transport. IDs: AC-EXM-0NN."""
from src.main import route


def test_health_route():
    """AC-EXM-001: /health maps to 200 with status=ok."""
    code, body = route("/health")
    assert code == 200
    assert body["status"] == "ok"


def test_root_route():
    """AC-EXM-002: / maps to 200 with a message."""
    code, body = route("/")
    assert code == 200
    assert "message" in body


def test_unknown_route():
    """AC-EXM-003: an unrouted path maps to 404."""
    code, body = route("/nonexistent")
    assert code == 404
    assert body["error"] == "not found"
