import core.legacy_dashboard as legacy_dashboard
import core.quest_state as qs


def test_display_legacy_progress(monkeypatch, capsys):
    steps = [
        {"id": 1, "title": "First"},
        {"id": 2, "title": "Second"},
    ]
    monkeypatch.setattr(qs, "read_saved_quest_log", lambda: ["quest 1 completed"])
    legacy_dashboard.display_legacy_progress(steps)
    captured = capsys.readouterr()
    assert "✅ Completed" in captured.out
    assert "❓ Unknown" in captured.out


def test_enriched_status_output(monkeypatch, capsys):
    steps = [
        {"id": 1, "title": "First"},
        {"id": 2, "title": "Second"},
        {"id": 3, "title": "Third"},
    ]

    monkeypatch.setattr(
        qs,
        "read_saved_quest_log",
        lambda: [
            "step 1 completed",
            "step 2 failed",
            "step 3 in progress",
        ],
    )
    legacy_dashboard.display_legacy_progress(steps)
    captured = capsys.readouterr()
    assert "✅ Completed" in captured.out
    assert "❌ Failed" in captured.out
    assert "⏳ In Progress" in captured.out
