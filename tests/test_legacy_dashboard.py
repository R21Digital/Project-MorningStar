import core.legacy_dashboard as legacy_dashboard


def test_display_legacy_progress(monkeypatch, capsys):
    monkeypatch.setattr(
        legacy_dashboard,
        "load_legacy_steps",
        lambda: [
            {"id": 1, "title": "First"},
            {"id": 2, "title": "Second"},
        ],
    )
    monkeypatch.setattr(legacy_dashboard, "read_quest_log", lambda: ["1"])
    legacy_dashboard.display_legacy_progress()
    captured = capsys.readouterr()
    assert "Yes" in captured.out
    assert "No" in captured.out
