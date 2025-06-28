import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from android_ms11.core import session_monitor


def test_monitor_session_updates_state(monkeypatch, tmp_path):
    from core import state_tracker  # noqa: F401

    state = {}
    monkeypatch.setattr(session_monitor, "update_state", lambda **kw: state.update(kw))
    monkeypatch.setattr(session_monitor, "get_state", lambda: state)

    logged = {}
    monkeypatch.setattr(session_monitor, "log_performance_summary", lambda stats, csv_path=str(tmp_path/"perf.csv"): logged.setdefault("stats", stats))

    metrics = {"xp": 200, "xp_rate": 100.0, "loot": ["Gem"]}
    result = session_monitor.monitor_session(metrics)

    assert state["xp"] == 200
    assert state["loot"] == ["Gem"]
    assert result == state
    assert logged["stats"]["xp_rate"] == 100.0
