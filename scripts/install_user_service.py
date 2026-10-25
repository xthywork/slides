#!/usr/bin/env python3
"""Install this checkout as a per-user systemd presentation hub service."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
UNIT = 'presentation-hub.service'


def main():
    for value in (str(ROOT), sys.executable):
        if any(c.isspace() or c in '%"\\' for c in value):
            raise SystemExit('請使用不含空白、百分比或引號的專案與 Python 路徑。')
    destination = Path.home() / '.config' / 'systemd' / 'user' / UNIT
    if destination.exists() and str(ROOT / 'serve.py') not in destination.read_text():
        raise SystemExit('已存在不同的同名服務，未覆蓋。')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(f'''[Unit]
Description=Presentation Hub local website
After=network.target

[Service]
Type=simple
WorkingDirectory={ROOT}
ExecStart={sys.executable} {ROOT}/serve.py --host 0.0.0.0 --port 49183
Restart=on-failure
RestartSec=2
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
''')
    for args in [('daemon-reload',), ('enable', UNIT), ('restart', UNIT)]:
        subprocess.run(['systemctl', '--user', *args], check=True)
    print('使用者常駐服務已啟動：' + UNIT)
    print('查看狀態：systemctl --user status ' + UNIT)


if __name__ == '__main__':
    main()
