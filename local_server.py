#!/usr/bin/env python3
"""Multi-threaded practice endpoint (10 worker slots) with a 100 ms response delay."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import BoundedSemaphore
import time

slots = BoundedSemaphore(10)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/slow", "/"):
            self.send_error(404)
            return
        with slots:
            time.sleep(0.1)
            body = b"local k6 practice endpoint\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print("Serving only on http://127.0.0.1:8000/slow (100 ms delay)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
