#!/usr/bin/env python3
"""Render a presentation's short Markdown notes as a portable static page."""
import argparse
from html import escape
from pathlib import Path
import re


def inline(value):
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', escape(value))


def render(source, destination):
    text = source.read_text(encoding='utf-8')
    title = next((line[2:] for line in text.splitlines() if line.startswith('# ')), '簡報講稿')
    blocks = []
    for paragraph in text.split('\n\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if paragraph.startswith('## '):
            blocks.append('<h2>' + inline(paragraph[3:]) + '</h2>')
        elif paragraph.startswith('# '):
            blocks.append('<h1>' + inline(paragraph[2:]) + '</h1>')
        elif all(line.startswith('- ') for line in paragraph.splitlines()):
            blocks.append('<ul>' + ''.join('<li>' + inline(line[2:]) + '</li>' for line in paragraph.splitlines()) + '</ul>')
        else:
            blocks.append('<p>' + inline(paragraph).replace('\n', '<br>') + '</p>')
    page = '''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__｜我的簡報室</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f4f7f5;color:#1c3430;font:17px/1.95 "Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif}main{max-width:880px;margin:36px auto;padding:34px 42px;background:white;border:1px solid #dce6df;border-radius:12px}a{color:#187e64;text-decoration:none}a:hover{text-decoration:underline}nav{display:flex;flex-wrap:wrap;gap:22px;font-size:14px;padding-bottom:20px;border-bottom:1px solid #dce6df}h1{font-size:30px;line-height:1.5;margin:28px 0}h2{font-size:20px;margin:30px 0 9px;color:#187e64;line-height:1.6}p{margin:0 0 18px}code{background:#eef4f0;padding:2px 5px;border-radius:4px;font-size:.9em}a:focus-visible{outline:3px solid #187e64;outline-offset:4px}@media(max-width:600px){main{margin:0;padding:24px;border:0;border-radius:0}h1{font-size:26px}body{font-size:16px}}@media print{body{background:white;font-size:12pt}main{border:0;margin:0;padding:0}nav{display:none}h2{break-after:avoid}p{orphans:3;widows:3}}</style></head>
<body><main><nav><a href="../../">‹ 我的簡報室</a><a href="./">開啟簡報 ↗</a><a href="speaker-notes.md">純文字講稿</a><a href="#" onclick="window.print();return false">列印講稿</a></nav>__CONTENT__</main></body></html>'''
    destination.write_text(page.replace('__TITLE__', escape(title)).replace('__CONTENT__', ''.join(blocks)), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    render(args.source, args.output or args.source.with_name('notes.html'))
