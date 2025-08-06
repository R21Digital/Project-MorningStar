import importlib
import sys

import main as legacy_main


def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog"])
    args = legacy_main.parse_args()
    assert args.legacy is False
    assert args.show_legacy_status is False
    assert args.show_dashboard is False
    assert args.dashboard_mode == "all"
    assert args.filter_status is None
    assert args.summary is False


def test_main_runs_legacy_by_default(monkeypatch):
    mod = importlib.reload(legacy_main)
    called = {}
    monkeypatch.setattr(mod, "run_full_legacy_quest", lambda: called.setdefault("legacy", True))
    monkeypatch.setattr(mod, "display_legacy_progress", lambda steps: called.setdefault("status", steps))
    mod.main([])
    assert called.get("legacy") is True
    assert "status" not in called


def test_main_show_dashboard(monkeypatch):
    mod = importlib.reload(legacy_main)
    called = {}
    monkeypatch.setattr(
        mod,
        "show_unified_dashboard",
        lambda *, mode="all", summary=False, filter_status=None: called.setdefault(
            "dash", (mode, summary, filter_status)
        ),
    )
    monkeypatch.setattr(mod, "run_full_legacy_quest", lambda: called.setdefault("legacy", True))
    mod.main(["--show-dashboard", "--dashboard-mode", "legacy"])
    assert called == {"dash": ("legacy", False, None)}


def test_main_show_legacy_status(monkeypatch):
    mod = importlib.reload(legacy_main)
    called = {}
    monkeypatch.setattr(mod, "load_legacy_steps", lambda: [1])
    monkeypatch.setattr(mod, "display_legacy_progress", lambda steps: called.setdefault("steps", steps))
    monkeypatch.setattr(mod, "run_full_legacy_quest", lambda: called.setdefault("legacy", True))
    mod.main(["--show-legacy-status"])
    assert called == {"steps": [1]}


def test_parse_args_filter_status(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--filter-status", "✅"])
    args = legacy_main.parse_args()
    assert args.filter_status == "✅"


def test_parse_args_summary(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--summary"])
    args = legacy_main.parse_args()
    assert args.summary is True


def test_parse_args_detailed(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--detailed"])
    args = legacy_main.parse_args()
    assert args.summary is False


def test_main_show_dashboard_filter(monkeypatch):
    mod = importlib.reload(legacy_main)
    called = {}
    monkeypatch.setattr(
        mod,
        "show_unified_dashboard",
        lambda *, mode="all", summary=False, filter_status=None: called.setdefault(
            "dash", (mode, summary, filter_status)
        ),
    )
    monkeypatch.setattr(mod, "run_full_legacy_quest", lambda: called.setdefault("legacy", True))
    mod.main(["--show-dashboard", "--filter-status", "✅"])
    assert called == {"dash": ("all", False, "✅")}


def test_main_show_dashboard_summary(monkeypatch):
    mod = importlib.reload(legacy_main)
    called = {}
    monkeypatch.setattr(
        mod,
        "show_unified_dashboard",
        lambda *, mode="all", summary=False, filter_status=None: called.setdefault(
            "dash", (mode, summary, filter_status)
        ),
    )
    monkeypatch.setattr(mod, "run_full_legacy_quest", lambda: called.setdefault("legacy", True))
    mod.main(["--show-dashboard", "--summary"])
    assert called == {"dash": ("all", True, None)}


def test_main_show_dashboard_detailed(monkeypatch):
    mod = importlib.reload(legacy_main)
    called = {}
    monkeypatch.setattr(
        mod,
        "show_unified_dashboard",
        lambda *, mode="all", summary=False, filter_status=None: called.setdefault(
            "dash", (mode, summary, filter_status)
        ),
    )
    monkeypatch.setattr(mod, "run_full_legacy_quest", lambda: called.setdefault("legacy", True))
    mod.main(["--show-dashboard", "--detailed"])
    assert called == {"dash": ("all", False, None)}
