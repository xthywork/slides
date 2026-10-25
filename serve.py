#!/usr/bin/env python3
"""Serve the presentation hub locally using only the Python standard library."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import mimetypes

ROOT = Path(__file__).resolve().parent
LEGACY = {'/notes': '/presentations/service-harbor/notes.html',
          '/speaker-notes.md': '/presentations/service-harbor/speaker-notes.md',
          '/index.html': '/'}
TYPES = {'.html': 'text/html; charset=utf-8', '.json': 'application/json; charset=utf-8',
         '.svg': 'image/svg+xml; charset=utf-8', '.md': 'text/plain; charset=utf-8',
         '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8'}


class Handler(BaseHTTPRequestHandler):
    def send_content(self, status, body=b'', content_type='text/html; charset=utf-8', location=None):
        self.send_response(status)
        self.send_header('Cache-Control', 'no-store')
        if location:
            self.send_header('Location', location)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.query:
            return self.send_content(302, location=url.path or '/')
        if url.path in LEGACY:
            return self.send_content(302, location=LEGACY[url.path])
        path = unquote(url.path)
        parts = Path(path).parts
        if any(part.startswith('.') for part in parts if part != '/'):
            return self.send_content(404, '找不到這個頁面。'.encode())
        target = (ROOT / path.lstrip('/')).resolve()
        if not target.is_relative_to(ROOT):
            return self.send_content(404)
        allowed = path == '/' or path == '/presentations.json' or path.startswith(('/presentations/', '/assets/'))
        if not allowed:
            return self.send_content(404, '找不到這個頁面。'.encode())
        if target.is_dir():
            if not path.endswith('/'):
                return self.send_content(302, location=url.path + '/')
            target = target / 'index.html'
        if not target.is_file():
            return self.send_content(404, '找不到這個頁面。'.encode())
        return self.send_content(200, target.read_bytes(), TYPES.get(target.suffix, mimetypes.guess_type(target.name)[0] or 'application/octet-stream'))

    do_HEAD = do_GET


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=49183)
    args = parser.parse_args()
    print(f'Presentation hub serving on {args.host}:{args.port}', flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
