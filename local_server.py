#!/usr/bin/env python3
"""Local dev server for the POS demo: serves this folder AND proxies Airwallex API calls.

    python3 local_server.py            # http://localhost:8000
    python3 local_server.py 9000       # custom port

Then open http://localhost:8000 and set Setup -> API proxy URL to  http://localhost:8000
(requests to /demo/... and /prod/... are forwarded to api-demo / api.airwallex.com).
Replaces `python -m http.server`, which cannot handle POST (it answers 501). Stdlib only; stores nothing.
"""
import sys
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

TARGETS = {"demo": "https://api-demo.airwallex.com", "prod": "https://api.airwallex.com"}
FORWARD = {"authorization", "content-type", "x-client-id", "x-api-key", "x-on-behalf-of", "x-login-as"}


class Handler(SimpleHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", ",".join(sorted(FORWARD)))

    def _is_api(self):
        return self.path.split("/", 2)[1:2] in (["demo"], ["prod"])

    def _proxy(self):
        _, env, rest = self.path.split("/", 2)
        body = None
        if self.command == "POST":
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        headers = {k: v for k, v in self.headers.items() if k.lower() in FORWARD}
        if self.command == "POST" and "content-type" not in {k.lower() for k in headers}:
            headers["Content-Type"] = "application/json"  # urllib would default to form-urlencoded
        req = urllib.request.Request(f"{TARGETS[env]}/{rest}", data=body, headers=headers, method=self.command)
        try:
            resp = urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as e:  # pass Airwallex errors (401, 400, ...) straight through
            resp = e
        except Exception as e:  # network failure
            msg = f'{{"code":"proxy_error","message":"{type(e).__name__}: {e}"}}'.encode()
            self.send_response(502); self._cors()
            self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(msg)))
            self.end_headers(); self.wfile.write(msg); return
        data = resp.read()
        self.send_response(resp.status if hasattr(resp, "status") else resp.code); self._cors()
        self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.send_header("Content-Length", "0"); self.end_headers()

    def do_GET(self):
        return self._proxy() if self._is_api() else super().do_GET()

    def do_POST(self):
        if self._is_api():
            return self._proxy()
        self.send_error(404)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Serving http://localhost:{port}  (proxy URL for the page: http://localhost:{port})")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
