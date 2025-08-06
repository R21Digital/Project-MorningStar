import pytest
import core.unified_dashboard as unified
from core.constants import STATUS_EMOJI_MAP
from core.dashboard_utils import group_quests_by_category, print_summary_counts
from rich.console import Console


def test_filter_status_grouped(monkeypatch, capsys):
    Console.printed.clear() if hasattr(Console, "printed") else None
    steps = [
        {"id": 1, "title": "A", "category": "Tutorial", "completed": True},
        {"id": 2, "title": "B", "category": "Combat", "completed": True},
        {"id": 3, "title": "C", "category": "Tutorial"},
    ]
    monkeypatch.setattr(unified, "load_legacy_steps", lambda: steps)
    monkeypatch.setattr(unified, "load_themepark_chains", lambda: [])
    monkeypatch.setattr(
        unified,
        "get_step_status",
        lambda step, log_lines=None: STATUS_EMOJI_MAP["completed"]
        if step.get("completed")
        else STATUS_EMOJI_MAP["not_started"],
    )
    unified.show_unified_dashboard(
        mode="legacy",
        summary=True,
        filter_status=STATUS_EMOJI_MAP["completed"],
    )
    out = capsys.readouterr().out
    assert "Quest Progress Summary" in out
    assert "Tutorial" in out
    assert "Combat" in out


def test_print_summary_counts(monkeypatch, capsys):
    Console.printed.clear() if hasattr(Console, "printed") else None
    steps = [
        {"id": 1, "title": "Intro", "category": "Tutorial", "completed": True},
        {"id": 2, "title": "Next", "category": "Tutorial", "completed": True},
    ]
    monkeypatch.setattr(unified, "get_themepark_status", lambda q: STATUS_EMOJI_MAP["completed"])
    categories = group_quests_by_category(steps, ["Jabba"])
    print_summary_counts(categories)
    out = capsys.readouterr().out
    assert "Count" in out
    assert "Quest Progress Summary" in out


@pytest.mark.parametrize("status_key", ["completed", "in_progress", "not_started"])
def test_show_unified_dashboard_filter_summary(monkeypatch, capsys, status_key):
    """Dashboard summary should group quests and show only the filtered status."""

    Console.printed.clear() if hasattr(Console, "printed") else None

    steps = [
        {"id": 1, "title": "Step A", "category": "Tutorial", status_key: True},
        {"id": 2, "title": "Step B", "category": "Combat", status_key: True},
        {"id": 3, "title": "Step C", "category": "Tutorial"},
    ]

    monkeypatch.setattr(unified, "load_legacy_steps", lambda: steps)
    monkeypatch.setattr(unified, "load_themepark_chains", lambda: [])

    def fake_status(step, log_lines=None):
        return STATUS_EMOJI_MAP[status_key] if step.get(status_key) else STATUS_EMOJI_MAP["not_started"]

    monkeypatch.setattr(unified, "get_step_status", fake_status)

    unified.show_unified_dashboard(
        mode="legacy",
        summary=True,
        filter_status=STATUS_EMOJI_MAP[status_key],
    )
    out = capsys.readouterr().out

    assert "Quest Progress Summary" in out
    assert "Tutorial" in out
    assert "Combat" in out
    assert STATUS_EMOJI_MAP[status_key] in out

