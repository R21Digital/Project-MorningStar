# src/utils/fetch_legacy_html.py

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_PATH = Path("data/raw/legacy.html")
LEGACY_QUEST_URL = "https://swg.fandom.com/wiki/Legacy_Quest"

def fetch_legacy_quest_html():
    print(f"🌐 Navigating to {LEGACY_QUEST_URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(LEGACY_QUEST_URL, wait_until="networkidle")
        html = page.content()
        browser.close()

    # Ensure the output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Rendered HTML saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    fetch_legacy_quest_html()
