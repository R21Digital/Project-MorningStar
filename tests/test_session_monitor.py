import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from android_ms11.core import session_monitor


def test_low_xp_rate_suggests_quest(monkeypatch):
    state = {"mode": "quest"}

    def fake_update_state(**kw):
        state.update(kw)

    monkeypatch.setattr(session_monitor, "update_state", fake_update_state)
    monkeypatch.setattr(session_monitor, "get_state", lambda: state)
    monkeypatch.setattr(session_monitor, "log_performance_summary", lambda stats: None)

    result = session_monitor.monitor_session({"xp": 50, "xp_rate": 10.0})
    assert state["xp"] == 50
    assert result["mode"] == "quest"


def test_high_xp_rate_suggests_combat(monkeypatch):
    state = {"mode": "combat"}

    def fake_update_state(**kw):
        state.update(kw)

    monkeypatch.setattr(session_monitor, "update_state", fake_update_state)
    monkeypatch.setattr(session_monitor, "get_state", lambda: state)
    monkeypatch.setattr(session_monitor, "log_performance_summary", lambda stats: None)

    result = session_monitor.monitor_session({"xp": 200, "xp_rate": 250.0})
    assert state["xp"] == 200
    assert result["mode"] == "combat"
