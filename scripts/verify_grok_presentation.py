#!/usr/bin/env python3
"""Focused integration checks for the Grok Bot presentation and its hub entry.

Run against the existing serve.py service:
uv run --python 3.12 --with playwright --with pypdf python scripts/verify_grok_presentation.py
"""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urljoin, urlsplit
import zipfile

from playwright.sync_api import sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
SLUG = 'grok-bot-agent-architecture'
FOLDER = ROOT / 'presentations' / SLUG
KEY = 'presentation-hub:progress:' + SLUG


def check(value, message):
    if not value:
        raise AssertionError(message)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src') and value:
                self.links.append(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://127.0.0.1:49183/')
    args = parser.parse_args()
    base = args.base.rstrip('/') + '/'
    path = f'presentations/{SLUG}/'
    catalog = json.loads((ROOT / 'presentations.json').read_text())['presentations']
    original = json.loads(subprocess.check_output(['git', 'show', 'origin/main:presentations.json'], cwd=ROOT))['presentations']
    check([e for e in catalog if e['id'] != SLUG] == [e for e in original if e['id'] != SLUG], 'Existing catalog entries changed')
    entry = next(e for e in catalog if e['id'] == SLUG)
    check(entry['slides'] == 12 and entry['path'] == path, 'Registry count/path')
    check(len(PdfReader(FOLDER / 'grok-bot-slides.pdf').pages) == 12, 'PDF must have 12 pages')
    check(len(re.findall(r'^## \d+｜', (FOLDER / 'speaker-notes.md').read_text(), re.M)) == 12, 'Need a note section for every slide')
    for file in FOLDER.iterdir():
        if file.suffix not in ('.html', '.json', '.md'):
            continue
        content = file.read_text()
        check(not re.search(r'/home/|/tmp/opencode|192\.168\.\d+\.\d+|-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}', content), f'Private environment/credential material: {file.name}')
    with zipfile.ZipFile(FOLDER / 'grok-bot-slides.zip') as archive:
        check(archive.testzip() is None, 'ZIP integrity')
        check(archive.read('index.html') == (FOLDER / 'index.html').read_bytes(), 'ZIP HTML is stale')
        check('speaker-notes.md' in archive.namelist() and 'notes.html' in archive.namelist(), 'ZIP notes missing')
    errors = []
    layout_checks = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(reduced_motion='reduce', viewport={'width':1440, 'height':900})
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base)
        page.wait_for_function('(count) => document.querySelectorAll(".presentation-card").length === count', arg=len(catalog))
        page.locator('#search').fill('Grok')
        check(page.locator('.presentation-card').count() == 1, 'Hub search')
        card = page.locator(f'[data-id="{SLUG}"]')
        card.locator('.favorite').click()
        page.locator('[data-scope="favorites"]').click()
        check(page.locator('.presentation-card').count() == 1, 'Hub favorites')
        page.locator('[data-scope="all"]').click()
        page.locator('#search').fill('')
        page.locator('[data-category="技術報告"]').click()
        check(card.count() == 1, 'Category filter excludes new presentation')
        check(page.locator('.presentation-card').count() == len([e for e in catalog if e['category'] == '技術報告']), 'Category filter count')
        card.locator('.card-actions .primary').click()
        check(page.locator('.slide:visible').count() == 1, 'Presentation opens from hub')
        check(page.locator('.slide').count() == 12, 'Real slide count')
        for width, height in [(1440,900), (1280,720), (375,667), (390,844)]:
            page.set_viewport_size({'width':width, 'height':height})
            for i in range(1,13):
                page.evaluate('(i) => location.hash = `slide-${i}`', i)
                page.wait_for_function('(i) => !document.getElementById(`slide-${i}`).hidden', arg=i)
                check(page.evaluate('''() => {
                    const s = document.querySelector('.slide:not([hidden])');
                    return document.documentElement.scrollHeight <= innerHeight + 1 && document.documentElement.scrollWidth <= innerWidth + 1 && s.scrollHeight <= s.clientHeight + 1;
                }'''), f'Layout overflow {width} slide {i}')
                layout_checks += 1
        page.set_viewport_size({'width':1440, 'height':900})
        page.goto(base + path + '#slide-6')
        check(page.locator('#slide-6').is_visible(), 'Direct page hash')
        page.keyboard.press('ArrowRight')
        progress = page.evaluate('(key) => JSON.parse(localStorage.getItem(key))', KEY)
        check(progress['slide'] == 7 and progress['total'] == 12 and progress['visitedAt'] > 0, 'Progress persistence')
        page.locator('.brand').click()
        page.wait_for_selector(f'[data-id="{SLUG}"]')
        page.locator(f'[data-id="{SLUG}"] .read-progress a').click()
        check(page.locator('#slide-7').is_visible(), 'Hub resume')
        page.locator('#more-button').click()
        page.locator('.file-links a[href="notes.html"]').click()
        check(page.locator('h2').count() == 12, 'Rendered notes page')
        check(page.locator('nav a[href="../../"]').count() == 1, 'Notes hub link')
        for name in ['index.html', 'notes.html']:
            links = Links()
            links.feed((FOLDER / name).read_text())
            for href in links.links:
                if href.startswith(('#', 'https:', 'http:', 'mailto:', 'data:', 'blob:')):
                    continue
                url = urljoin(base + path + name, href)
                response = context.request.get(url)
                check(response.ok, f'Broken relative link: {name} → {href} ({response.status})')
        # Emulate a GitHub Pages repository prefix without changing serve.py.
        def prefix_route(route):
            url = route.request.url
            target = url.replace('/presentation-hub/', '/', 1)
            route.fulfill(response=route.fetch(url=target))
        page.route('**/presentation-hub/**', prefix_route)
        page.goto(base + 'presentation-hub/' + path + '#slide-3')
        check(page.locator('#slide-3').is_visible(), 'Prefixed direct link')
        check(urlsplit(page.locator('.brand').evaluate('(a) => a.href')).path == '/presentation-hub/', 'Hub link loses Pages prefix')
        page.locator('.brand').click()
        page.wait_for_selector(f'[data-id="{SLUG}"]')
        page.locator(f'[data-id="{SLUG}"] .card-actions a[href$="notes.html"]').click()
        check('/presentation-hub/' in page.url and page.locator('h2').count() == 12, 'Prefixed notes link')
        blocked = browser.new_context()
        blocked.add_init_script('''Object.defineProperty(Storage.prototype, 'getItem', {value(){throw new Error('blocked')}}); Object.defineProperty(Storage.prototype, 'setItem', {value(){throw new Error('blocked')}});''')
        fallback = blocked.new_page()
        fallback.on('pageerror', lambda error: errors.append(str(error)))
        fallback.goto(base + path)
        fallback.keyboard.press('ArrowRight')
        check(fallback.locator('#slide-2').is_visible(), 'Storage-disabled navigation')
        blocked.close()
        check(not errors, f'Browser errors: {errors}')
        browser.close()
    print(json.dumps({'status':'passed', 'slides':12, 'layout_checks':layout_checks, 'existing_entries_preserved':True, 'hub_search_filter_favorites_resume':True, 'relative_links_and_pages_prefix':True, 'notes_sections':12, 'storage_disabled':True, 'browser_errors':errors}, ensure_ascii=False))


if __name__ == '__main__':
    main()
