import pytest

import core.unified_dashboard as unified
import core.legacy_tracker as legacy_tracker
import core.quest_state as qs
import core.themepark_tracker as tp
from rich.console import Console


def test_show_unified_dashboard(monkeypatch, capsys):
    Console.printed.clear() if hasattr(Console, "printed") else None
    monkeypatch.setattr(legacy_tracker, "load_legacy_steps", lambda: [{"id": 1, "title": "First"}])
    monkeypatch.setattr(qs, "get_step_status", lambda step_id, log_lines=None: qs.STATUS_COMPLETED)
    monkeypatch.setattr(tp, "get_themepark_status", lambda q: qs.STATUS_COMPLETED)

    unified.show_unified_dashboard(["Jabba"])
    out = capsys.readouterr().out
    assert "Legacy Quest Progress" in out
    assert "Theme Park Quest" in out


@pytest.mark.parametrize("mode", ["legacy", "themepark", "all"])
def test_show_unified_dashboard_modes(monkeypatch, capsys, mode):
    Console.printed.clear() if hasattr(Console, "printed") else None
    monkeypatch.setattr(legacy_tracker, "load_legacy_steps", lambda: [{"id": 1, "title": "First"}])
    monkeypatch.setattr(tp, "load_themepark_chains", lambda: ["Jabba"])
    monkeypatch.setattr(qs, "get_step_status", lambda step_id, log_lines=None: qs.STATUS_COMPLETED)
    monkeypatch.setattr(tp, "get_themepark_status", lambda q: qs.STATUS_COMPLETED)

    unified.show_unified_dashboard(mode=mode)
    # Ensure some output was produced for sanity
    assert capsys.readouterr().out


def test_show_unified_dashboard_custom_steps(monkeypatch, capsys):
    """Providing ``legacy_steps`` should bypass ``load_legacy_steps``."""

    Console.printed.clear() if hasattr(Console, "printed") else None

    def fail():
        raise AssertionError("load_legacy_steps should not be called")

    monkeypatch.setattr(legacy_tracker, "load_legacy_steps", fail)
    monkeypatch.setattr(qs, "get_step_status", lambda step_id, log_lines=None: qs.STATUS_COMPLETED)
    monkeypatch.setattr(tp, "get_themepark_status", lambda q: qs.STATUS_COMPLETED)

    steps = [{"id": 1, "title": "First"}]
    unified.show_unified_dashboard(["Jabba"], legacy_steps=steps)
    out = capsys.readouterr().out
    assert "Legacy Quest Progress" in out
    assert "Theme Park Quest" in out
