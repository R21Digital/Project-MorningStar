import pytest

import core.legacy_dashboard as legacy_dashboard
import core.unified_dashboard as unified_dashboard
from core.constants import STATUS_EMOJI_MAP
from core.utils.render_progress_bar import render_progress_bar
from rich.console import Console


def test_show_unified_dashboard(monkeypatch, capsys):
    Console.printed.clear() if hasattr(Console, "printed") else None
    monkeypatch.setattr(unified_dashboard, "load_legacy_steps", lambda: [{"id": 1, "title": "First"}])
    monkeypatch.setattr(unified_dashboard, "load_themepark_chains", lambda: ["Jabba"])
    monkeypatch.setattr(unified_dashboard, "get_step_status", lambda step, log_lines=None: STATUS_EMOJI_MAP["completed"])
    monkeypatch.setattr(unified_dashboard, "get_themepark_status", lambda q: STATUS_EMOJI_MAP["completed"])
    unified_dashboard.show_unified_dashboard(mode="all")
    out = capsys.readouterr().out
    assert "Legacy Quest Progress" in out
    assert "Theme Park Quest" in out


def test_show_unified_dashboard_summary(monkeypatch, capsys):
    Console.printed.clear() if hasattr(Console, "printed") else None
    steps = [{"id": 1, "title": "Intro", "category": "Tutorial", "completed": True}]
    monkeypatch.setattr(unified_dashboard, "load_legacy_steps", lambda: steps)
    monkeypatch.setattr(unified_dashboard, "load_themepark_chains", lambda: [])
    monkeypatch.setattr(unified_dashboard, "get_step_status", lambda step, log_lines=None: STATUS_EMOJI_MAP["completed"])
    unified_dashboard.show_unified_dashboard(mode="legacy", summary=True)
    out = capsys.readouterr().out
    assert "Tutorial" in out
    assert render_progress_bar([STATUS_EMOJI_MAP["completed"]]) in out


def test_unified_dashboard_invalid_mode():
    with pytest.raises(ValueError):
        unified_dashboard.show_unified_dashboard(mode="bogus")


def test_show_legacy_dashboard(monkeypatch, capsys):
    Console.printed.clear() if hasattr(Console, "printed") else None
    monkeypatch.setattr(legacy_dashboard, "load_legacy_steps", lambda: [{"id": 1, "title": "Intro"}])
    legacy_dashboard.show_legacy_dashboard()
    out = capsys.readouterr().out
    assert "Legacy Quest Progress" in out

