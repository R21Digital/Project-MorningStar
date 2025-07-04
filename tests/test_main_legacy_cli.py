import importlib
import sys

import main as legacy_main


def test_parse_args_legacy(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--legacy"])
    args = legacy_main.parse_args()
    assert args.legacy is True
    assert args.show_legacy_status is False


def test_parse_args_show_status(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--show-legacy-status"])
    args = legacy_main.parse_args()
    assert args.show_legacy_status is True
    assert args.legacy is False


def test_parse_args_show_themepark_status(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--show-themepark-status"])
    args = legacy_main.parse_args()
    assert args.show_themepark_status is True
    assert args.legacy is False


def test_main_runs_legacy_by_default(monkeypatch):
    legacy_main_mod = importlib.reload(legacy_main)
    called = {}
    monkeypatch.setattr(legacy_main_mod, "run_full_legacy_quest", lambda: called.setdefault("legacy", True))
    monkeypatch.setattr(legacy_main_mod, "display_legacy_progress", lambda steps: called.setdefault("status", True))
    legacy_main_mod.main([])
    assert called.get("legacy") is True
    assert "status" not in called


def test_main_show_status_only(monkeypatch):
    legacy_main_mod = importlib.reload(legacy_main)
    called = []
    monkeypatch.setattr(legacy_main_mod, "display_legacy_progress", lambda steps: called.append("status"))
    monkeypatch.setattr(legacy_main_mod, "run_full_legacy_quest", lambda: called.append("legacy"))
    monkeypatch.setattr(legacy_main_mod, "load_legacy_steps", lambda: [1])
    legacy_main_mod.main(["--show-legacy-status"])
    assert called == ["status"]


def test_main_legacy_flag(monkeypatch):
    legacy_main_mod = importlib.reload(legacy_main)
    called = {}
    monkeypatch.setattr(legacy_main_mod, "run_full_legacy_quest", lambda: called.setdefault("legacy", True))
    monkeypatch.setattr(legacy_main_mod, "display_legacy_progress", lambda steps: called.setdefault("status", True))
    legacy_main_mod.main(["--legacy"])
    assert called.get("legacy") is True
    assert "status" not in called


def test_main_themepark_status(monkeypatch):
    legacy_main_mod = importlib.reload(legacy_main)
    called = []
    monkeypatch.setattr(
        legacy_main_mod,
        "display_themepark_progress",
        lambda quests: called.append("themepark"),
    )
    monkeypatch.setattr(
        legacy_main_mod, "run_full_legacy_quest", lambda: called.append("legacy")
    )
    legacy_main_mod.main(["--show-themepark-status"])
    assert called == ["themepark"]


def test_parse_args_show_dashboard(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--show-dashboard"])
    args = legacy_main.parse_args()
    assert args.show_dashboard is True
    assert args.dashboard_mode == "all"


def test_parse_args_dashboard_mode(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--dashboard-mode", "legacy"])
    args = legacy_main.parse_args()
    assert args.dashboard_mode == "legacy"
    assert args.show_dashboard is False


def test_main_show_dashboard(monkeypatch):
    legacy_main_mod = importlib.reload(legacy_main)
    called = {}
    monkeypatch.setattr(
        legacy_main_mod,
        "show_unified_dashboard",
        lambda *, mode="all": called.setdefault("dashboard", mode),
    )
    monkeypatch.setattr(
        legacy_main_mod, "run_full_legacy_quest", lambda: called.setdefault("legacy", True)
    )
    legacy_main_mod.main(["--show-dashboard", "--dashboard-mode", "legacy"])
    assert called == {"dashboard": "legacy"}

