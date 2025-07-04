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

