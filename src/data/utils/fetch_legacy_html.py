# src/data/utils/fetch_legacy_html.py

from playwright.sync_api import sync_playwright
import os

def fetch_legacy_quest_html():
    url = "https://swg.fandom.com/wiki/Legacy_Quest"
    output_path = "data/raw/legacy.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"🌐 Navigating to {url}...")
        page.goto(url)
        page.wait_for_selector("h1")  # Waits until page content is fully rendered
        html = page.content()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ Rendered HTML saved to {output_path}")
        browser.close()

if __name__ == "__main__":
    fetch_legacy_quest_html()
