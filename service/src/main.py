"""Minimal HTTP service — demonstrates the three-tier test pipeline."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 8000))


def route(path: str) -> tuple[int, dict]:
    """Map a request path to (status code, body).

    Pure: no socket, no I/O. This is what the unit tier exercises — the
    transport is left to the integration and e2e tiers.
    """
    if path == "/health":
        return 200, {"status": "ok"}
    if path == "/":
        return 200, {"message": "hello"}
    return 404, {"error": "not found"}


class Handler(BaseHTTPRequestHandler):
    """Handle health check and echo endpoints."""

    def do_GET(self):
        self._respond(*route(self.path))

    def _respond(self, code: int, body: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, *args):
        pass  # silence logs in tests


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Service listening on :{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
