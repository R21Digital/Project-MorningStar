import core.legacy_dashboard as legacy_dashboard
from core.constants import STATUS_EMOJI_MAP


def test_display_legacy_progress(capsys):
    steps = [
        {"id": 1, "title": "First", "completed": True},
        {"id": 2, "title": "Second"},
    ]
    legacy_dashboard.display_legacy_progress(steps)
    captured = capsys.readouterr()
    assert STATUS_EMOJI_MAP["completed"] in captured.out
    assert STATUS_EMOJI_MAP["not_started"] in captured.out


def test_enriched_status_output(capsys):
    steps = [
        {"id": 1, "title": "First", "completed": True},
        {"id": 2, "title": "Second", "failed": True},
        {"id": 3, "title": "Third", "in_progress": True},
    ]
    legacy_dashboard.display_legacy_progress(steps)
    captured = capsys.readouterr()
    assert STATUS_EMOJI_MAP["completed"] in captured.out
    assert STATUS_EMOJI_MAP["failed"] in captured.out
    assert STATUS_EMOJI_MAP["in_progress"] in captured.out
