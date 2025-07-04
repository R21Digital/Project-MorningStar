import core.unified_dashboard as unified
import core.legacy_tracker as legacy_tracker
import core.quest_state as qs
import core.themepark_tracker as tp


def test_show_unified_dashboard(monkeypatch, capsys):
    monkeypatch.setattr(legacy_tracker, "load_legacy_steps", lambda: [{"id": 1, "title": "First"}])
    monkeypatch.setattr(qs, "get_step_status", lambda step_id, log_lines=None: "Complete")
    monkeypatch.setattr(tp, "get_themepark_status", lambda q: "Done")

    unified.show_unified_dashboard(["Jabba"])
    out = capsys.readouterr().out
    assert "Legacy Quest Progress" in out
    assert "Theme Park Quest" in out
