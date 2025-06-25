import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.importers import legacy_quest_parser


def test_parse_legacy_quest_html(monkeypatch, tmp_path):
    sample_html = (
        '<div class="mw-parser-output">'
        '<h2>Quest One</h2>'
        '<h3>Step A</h3>'
        '<p>Do something</p>'
        '<ul><li>Note1</li><li>Note2</li></ul>'
        '<h3>Step B</h3>'
        '<p>Finish up</p>'
        '<h2>Quest Two</h2>'
        '<h3>Intro</h3>'
        '<p>Talk to NPC</p>'
        '</div>'
    )

    html_path = tmp_path / "legacy.html"
    html_path.write_text(sample_html, encoding="utf-8")

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
