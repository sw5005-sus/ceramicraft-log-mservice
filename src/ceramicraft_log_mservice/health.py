"""Minimal HTTP health-check server for Kubernetes probes."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

_PING_RESPONSE = json.dumps({"status": "ok"}).encode()


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/log-ms/v1/ping":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(_PING_RESPONSE)
        else:
            self.send_error(404)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        # Silence default stderr logging to avoid noise.
        pass


def start_health_server(port: int = 8080) -> HTTPServer:
    """Start the health-check HTTP server on a daemon thread.

    Returns the ``HTTPServer`` instance so the caller can shut it down if
    needed.
    """
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
