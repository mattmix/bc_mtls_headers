#!/usr/bin/env python3
"""Plain HTTP server that displays request headers."""
import html
import http.server
import mimetypes
from pathlib import Path
import sys
from urllib.parse import unquote


class HeaderHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve static files from the current working directory.
        requested = unquote(self.path.split("?", 1)[0].split("#", 1)[0])
        if requested.startswith("/"):
            requested = requested[1:]

        if requested:
            base_dir = Path.cwd().resolve()
            candidate = (base_dir / requested).resolve()
            if base_dir in candidate.parents and candidate.is_file():
                content_type = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
                data = candidate.read_bytes()

                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        rows = []
        for name, value in sorted(self.headers.items()):
            rows.append(
                f"<tr><td><code>{html.escape(name)}</code></td>"
                f"<td><code>{html.escape(value)}</code></td></tr>"
            )

        body = f"""<!DOCTYPE html>
<html>
<head>
  <title>mTLS Header Viewer</title>
  <style>
    body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 2em; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ text-align: left; padding: 8px; border: 1px solid #ddd; }}
    th {{ background-color: #337ab7; color: white; }}
    tr:nth-child(even) {{ background-color: #f9f9f9; }}
    h1 {{ color: #333; }}
    h2 {{ color: #555; margin-top: 2em; }}
    .meta {{ color: #888; font-size: 0.9em; }}
  </style>
</head>
<body>
  <h1>mTLS Header Viewer</h1>
  <p class="meta">Request: {html.escape(self.command)} {html.escape(self.path)} {html.escape(self.request_version)}</p>
  <h2>Image Path Test</h2>
  <p>
    <img src="test_relative.png" alt="Relative path test" width="195" height="107">
    <img src="/test_absolute.png" alt="Absolute path test" width="195" height="107">
  </p>
  <h2>Request Headers (as seen by backend)</h2>
  <table>
    <tr><th>Header</th><th>Value</th></tr>
    {''.join(rows)}
  </table>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode())))
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, format, *args):
        sys.stderr.write(f"[header_server] {format % args}\n")


def main():
    port = int(sys.argv[1])
    server = http.server.HTTPServer(("127.0.0.1", port), HeaderHandler)
    print(f"HTTP header server listening on http://127.0.0.1:{port}")
    sys.stdout.flush()
    server.serve_forever()


if __name__ == "__main__":
    main()
