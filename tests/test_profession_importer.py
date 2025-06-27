import os
import sys
import json
import types
from pathlib import Path

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

from scripts.importers import profession_importer


def test_fetch_and_save(monkeypatch, tmp_path):
    fixture_path = Path("tests/fixtures/profession_snippet.html").resolve()
    sample_html = fixture_path.read_text(encoding="utf-8")

    class DummyResponse:
        status_code = 200
        text = sample_html
        def raise_for_status(self):
            pass

    def fake_get(url, *args, **kwargs):
        assert url == profession_importer.BASE_URL + "Doctor/"
        return DummyResponse()

    monkeypatch.setattr(profession_importer.requests, "get", fake_get)
    out_dir = tmp_path / "professions"
    monkeypatch.setattr(profession_importer, "OUTPUT_DIR", out_dir)

    profession_importer.fetch_and_save("Doctor")

    out_file = out_dir / "doctor.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["prerequisites"] == ["Novice Artisan", "Combat Level 5"]
    assert "Novice Medic (General Crafting XP)" in data["skill_boxes"]
    assert data["xp_costs"]["Advanced Medicine"] == 1000
    assert data["xp_costs"]["Master Doctor"] == 10000
