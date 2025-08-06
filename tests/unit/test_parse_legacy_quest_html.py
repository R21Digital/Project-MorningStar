import sys
import json
import types
from pathlib import Path

import importlib.util
if importlib.util.find_spec("bs4") is None:
    bs4_mod = types.ModuleType("bs4")
    bs4_mod.BeautifulSoup = object
    sys.modules["bs4"] = bs4_mod


from src.importers import legacy_quest_parser


def test_parse_legacy_quest_html(monkeypatch, tmp_path):
    fixture_path = Path("tests/fixtures/legacy_snippet.html").resolve()
    html_path = tmp_path / "legacy.html"
    html_path.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")

    output_path = Path("data/processed/test_legacy_output.json").resolve()

    monkeypatch.setattr(legacy_quest_parser, "RAW_HTML_PATH", str(html_path))
    monkeypatch.setattr(legacy_quest_parser, "OUTPUT_JSON_PATH", str(output_path))
    monkeypatch.setattr(legacy_quest_parser, "HASH_PATH", html_path.with_suffix(".hash"))
    monkeypatch.setattr(legacy_quest_parser, "file_changed", lambda *a, **k: True)

    legacy_quest_parser.parse_legacy_quest_html()

    with output_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    expected = [
        {
            "title": "Quest One",
            "steps": [
                {"step_title": "Step A", "description": "Do something", "notes": ["Note1", "Note2"]},
                {"step_title": "Step B", "description": "Finish up"},
            ],
        },
        {
            "title": "Quest Two",
            "steps": [
                {"step_title": "Intro", "description": "Talk to NPC"},
            ],
        },
    ]

    assert data == expected

    if output_path.exists():
        output_path.unlink()
