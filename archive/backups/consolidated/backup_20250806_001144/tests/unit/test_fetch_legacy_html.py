import sys
import types


# Provide a stub for the playwright module before importing the target module
if "playwright" not in sys.modules:
    playwright_mod = types.ModuleType("playwright")
    sync_api_mod = types.ModuleType("playwright.sync_api")
    playwright_mod.sync_api = sync_api_mod
    sync_api_mod.sync_playwright = lambda: None
    sys.modules["playwright"] = playwright_mod
    sys.modules["playwright.sync_api"] = sync_api_mod

from utils import fetch_legacy_html


def test_fetch_legacy_quest_html_saves(monkeypatch, tmp_path):
    html_content = "<html>legacy</html>"
    visited = {}

    class DummyPage:
        def goto(self, url, wait_until=None):
            visited["url"] = url
        def content(self):
            return html_content

    class DummyBrowser:
        def __init__(self):
            self.page = DummyPage()
        def new_page(self):
            return self.page
        def close(self):
            visited["closed"] = True

    def launch(headless=True):
        return DummyBrowser()

    def fake_sync_playwright():
        class Manager:
            def __enter__(self, *a, **k):
                return types.SimpleNamespace(chromium=types.SimpleNamespace(launch=launch))
            def __exit__(self, exc_type, exc, tb):
                pass
        return Manager()

    monkeypatch.setattr(fetch_legacy_html, "sync_playwright", fake_sync_playwright)
    out_file = tmp_path / "legacy.html"
    monkeypatch.setattr(fetch_legacy_html, "OUTPUT_PATH", out_file)

    fetch_legacy_html.fetch_legacy_quest_html()

    assert visited["url"] == fetch_legacy_html.LEGACY_QUEST_URL
    assert out_file.exists()
    assert out_file.read_text() == html_content
