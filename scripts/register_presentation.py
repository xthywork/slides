#!/usr/bin/env python3
"""Register or update a finished presentation in the hub catalog."""
import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re
from render_notes import render

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id', required=True, help='Unique URL slug, e.g. home-nas')
    parser.add_argument('--title', required=True)
    parser.add_argument('--subtitle', default='')
    parser.add_argument('--description', required=True)
    parser.add_argument('--category', default='主題介紹')
    parser.add_argument('--slides', type=int, required=True)
    parser.add_argument('--tags', nargs='*', default=['圖像動畫'])
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.id) or args.slides < 1:
        parser.error('Use a lowercase URL slug and a positive slide count.')
    folder = ROOT / 'presentations' / args.id
    if not (folder / 'index.html').is_file():
        parser.error(f'Create presentations/{args.id}/index.html first.')
    catalog_path = ROOT / 'presentations.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    entry = {'id': args.id, 'title': args.title, 'subtitle': args.subtitle,
             'description': args.description, 'category': args.category, 'tags': args.tags,
             'slides': args.slides, 'updated': date.today().isoformat(), 'status': '已完成',
             'path': f'presentations/{args.id}/', 'cover': f'assets/{args.id}.svg'}
    notes = folder / 'speaker-notes.md'
    if notes.is_file():
        render(notes, folder / 'notes.html')
        entry['notes'] = f'presentations/{args.id}/notes.html'
    cover = ROOT / entry['cover']
    if not cover.exists():
        title = escape(args.title[:25])
        cover.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600"><rect width="900" height="600" fill="#e8f2ec"/><rect x="100" y="100" width="660" height="380" rx="18" fill="#d7e6dc" transform="rotate(-5 430 290)"/><rect x="113" y="90" width="660" height="380" rx="18" fill="#f9fcfa" stroke="#bdd4c5" stroke-width="2"/><rect x="113" y="90" width="14" height="380" rx="6" fill="#187e64"/><text x="165" y="230" font-family="system-ui,sans-serif" font-size="38" font-weight="650" fill="#203f33">{title}</text><path d="M167 285h475m-475 35h360" stroke="#d0e3d6" stroke-width="14" stroke-linecap="round"/><text x="166" y="418" font-family="system-ui,sans-serif" font-size="20" fill="#6a8a76">{args.slides} 頁互動簡報</text></svg>''', encoding='utf-8')
    entries = catalog['presentations']
    for i, old in enumerate(entries):
        if old['id'] == args.id:
            entries[i] = entry
            break
    else:
        entries.append(entry)
    temporary = catalog_path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(catalog_path)
    print(f'Registered {args.id}; catalog now contains {len(entries)} presentation(s).')


if __name__ == '__main__':
    main()
