"""Minimal HTTP service — demonstrates the test pipeline."""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
    """Handle health check and echo endpoints."""

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok"})
        elif self.path == "/":
            self._respond(200, {"message": "hello"})
        else:
            self._respond(404, {"error": "not found"})

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
