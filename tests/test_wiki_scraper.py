import os
import sys
import types
import pytest

# Provide a stub for the requests module if it's missing
if "requests" not in sys.modules:
    requests_mod = types.ModuleType("requests")
    requests_mod.get = lambda *a, **k: None
    sys.modules["requests"] = requests_mod

# Stub out BeautifulSoup dependency if missing
if "bs4" not in sys.modules:
    bs4_mod = types.ModuleType("bs4")
    bs4_mod.BeautifulSoup = object
    sys.modules["bs4"] = bs4_mod

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import wiki_scraper


def test_fetch_page_success(monkeypatch):
    expected_html = "<html>OK</html>"

    def fake_get(url):
        assert url == wiki_scraper.WikiScraper.BASE_URL + "page"
        return types.SimpleNamespace(status_code=200, text=expected_html)

    monkeypatch.setattr(wiki_scraper.requests, "get", fake_get)
    scraper = wiki_scraper.WikiScraper()
    html = scraper.fetch_page("page")
    assert html == expected_html


def test_fetch_page_error(monkeypatch):
    def fake_get(url):
        return types.SimpleNamespace(status_code=404, text="")

    monkeypatch.setattr(wiki_scraper.requests, "get", fake_get)
    scraper = wiki_scraper.WikiScraper()
    with pytest.raises(Exception):
        scraper.fetch_page("missing")
