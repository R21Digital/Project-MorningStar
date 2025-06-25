import os
import sys
import json
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.importers import profession_importer


def test_fetch_and_save(monkeypatch, tmp_path):
    sample_html = (
        "<h3>Prerequisites</h3>"
        "<ul><li>Novice Artisan</li><li>Combat Level 5</li></ul>"
        "<h3>Skill Tree</h3>"
        "<ul>"
        "<li>Novice Medic (General Crafting XP)</li>"
        "<li>Advanced Medicine (1,000 Medicine XP)</li>"
        "<li>Master Doctor (10,000 Medicine XP)</li>"
        "</ul>"
    )

    class DummyResponse:
        status_code = 200
        text = sample_html
        def raise_for_status(self):
            pass

    def fake_get(url):
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
