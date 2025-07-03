import core.legacy_dashboard as legacy_dashboard
import core.quest_state as qs


def test_display_legacy_progress(monkeypatch, capsys):
    monkeypatch.setattr(
        legacy_dashboard,
        "load_legacy_steps",
        lambda: [
            {"id": 1, "title": "First"},
            {"id": 2, "title": "Second"},
        ],
    )
    monkeypatch.setattr(qs, "read_saved_quest_log", lambda: ["quest 1 completed"])
    legacy_dashboard.display_legacy_progress()
    captured = capsys.readouterr()
    assert "✅ Completed" in captured.out
    assert "❓ Unknown" in captured.out
