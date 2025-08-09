#!/usr/bin/env python3
"""
MS11 Control Center
- Starts the MS11 main interface if not running
- Opens a native window embedding the dashboard
- Keeps everything local and simple for players
"""
import os
import sys
import time
import subprocess
import threading
from pathlib import Path

import requests


HERE = Path(__file__).parent
ROOT = HERE.parents[1]


def is_server_up(url: str = "http://127.0.0.1:5000/api/status") -> bool:
    try:
        r = requests.get(url, timeout=1.5)
        return r.ok
    except Exception:
        return False


def start_main_interface() -> subprocess.Popen | None:
    script = HERE / 'ms11_main_interface.py'
    if not script.exists():
        return None
    env = os.environ.copy()
    env.setdefault('PYTHONIOENCODING', 'utf-8')
    try:
        p = subprocess.Popen([sys.executable, str(script)], cwd=HERE,
                             stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return p
    except Exception:
        return None


def ensure_server_running() -> subprocess.Popen | None:
    if is_server_up():
        return None
    proc = start_main_interface()
    # wait briefly for startup
    for _ in range(30):
        if is_server_up():
            break
        time.sleep(0.25)
    return proc


def run_window():
    try:
        import webview  # pywebview
    except Exception:
        # Fallback: open default browser
        import webbrowser
        webbrowser.open('http://127.0.0.1:5000/')
        print('Opened MS11 dashboard in your browser (pywebview not installed).')
        # Keep process alive for a bit so launcher does not exit immediately
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            return

    window = webview.create_window(
        title='MS11 Control Center',
        url='http://127.0.0.1:5000/',
        width=1200,
        height=800,
        resizable=True,
        confirm_close=True,
    )
    webview.start()


def main():
    proc = ensure_server_running()
    try:
        run_window()
    finally:
        # Do not force-kill the server; let the main interface live if others use it.
        pass


if __name__ == '__main__':
    main()


