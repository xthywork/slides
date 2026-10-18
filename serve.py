#!/usr/bin/env python3
"""Serve the final presentation and short speaker notes with clean URLs."""
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent


def notes_page():
    blocks = []
    for paragraph in (ROOT / 'speaker-notes.md').read_text(encoding='utf-8').split('\n\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if paragraph.startswith('## '):
            blocks.append('<h2>' + escape(paragraph[3:]) + '</h2>')
        elif paragraph.startswith('# '):
            blocks.append('<h1>' + escape(paragraph[2:]) + '</h1>')
        else:
            blocks.append('<p>' + escape(paragraph) + '</p>')
    return '''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Service Harbor｜簡易摘要講稿</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f6f8;color:#17212b;
font:17px/1.95 "Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif}
main{max-width:850px;margin:40px auto;padding:36px 42px;background:white;
border:1px solid #dce4e8;border-radius:12px}a{color:#168773;text-decoration:none}
nav{display:flex;flex-wrap:wrap;gap:24px;font-size:14px;padding-bottom:20px;
border-bottom:1px solid #dce4e8}h1{font-size:30px;line-height:1.5;margin:28px 0}
h2{font-size:20px;margin:30px 0 9px;color:#168773;line-height:1.6}
p{margin:0 0 18px}a:focus-visible{outline:3px solid #168773;outline-offset:4px}
@media(max-width:600px){main{margin:0;padding:24px;border:0;border-radius:0}
h1{font-size:26px}body{font-size:16px}}
@media print{body{background:white;font-size:12pt}main{border:0;margin:0;padding:0}
nav{display:none}h2{break-after:avoid}p{orphans:3;widows:3}}
</style><main><nav><a href="/" target="_blank" rel="noopener">開啟最新版簡報 ↗</a>
<a href="/speaker-notes.md">純文字講稿</a></nav>''' + ''.join(blocks) + '</main></html>'


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
        if url.path == '/index.html':
            return self.send_content(302, location='/')
        if url.path == '/':
            return self.send_content(200, (ROOT / 'index.html').read_bytes())
        if url.path == '/notes':
            return self.send_content(200, notes_page().encode('utf-8'))
        if url.path == '/speaker-notes.md':
            return self.send_content(200, (ROOT / 'speaker-notes.md').read_bytes(),
                                     'text/plain; charset=utf-8')
        self.send_content(404, '找不到這個頁面。'.encode('utf-8'))

    do_HEAD = do_GET


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 49183), Handler).serve_forever()
