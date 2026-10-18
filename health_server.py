from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit


class _HealthRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path not in {"/", "/health"}:
            self.send_error(404, "Not Found")
            return

        body = json.dumps(
            {"status": "ok", "service": "noise-remover-bot"}
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        # Keep routine health probes out of application logs.
        return


def start_health_server(port: int) -> tuple[ThreadingHTTPServer, Thread]:
    server = ThreadingHTTPServer(("0.0.0.0", port), _HealthRequestHandler)
    thread = Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.5},
        name="health-http-server",
        daemon=True,
    )
    thread.start()
    return server, thread


def stop_health_server(
    server: ThreadingHTTPServer,
    thread: Thread,
) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
