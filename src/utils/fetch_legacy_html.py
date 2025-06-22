# src/utils/fetch_legacy_html.py

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_PATH = Path("data/raw/legacy.html")
LEGACY_URL = "https://swg.fandom.com/wiki/Legacy_Quest"

def fetch_legacy_quest_html():
    print("🌐 Launching headless browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"🌐 Navigating to {LEGACY_URL}...")
        try:
            page.goto(LEGACY_URL, wait_until="load", timeout=90000)
            page.wait_for_timeout(5000)  # Give time for JS content to render
            html = page.content()
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"✅ Rendered HTML saved to {OUTPUT_PATH}")
        except Exception as e:
            print(f"❌ Failed to fetch HTML: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_legacy_quest_html()
