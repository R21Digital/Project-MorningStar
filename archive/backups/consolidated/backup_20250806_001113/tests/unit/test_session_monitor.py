

from core.session_monitor import monitor_session
import core.state_tracker as state_tracker


def test_low_xp_triggers_bounty(monkeypatch):
    state = {"fatigue_level": 2}

    monkeypatch.setattr(state_tracker, "get_state", lambda: dict(state))
    monkeypatch.setattr(state_tracker, "update_state", lambda **kw: state.update(kw))

    result = monitor_session({"xp_rate": 10.0})
    assert result.get("mode") == "bounty_mode"


def test_high_xp_returns_none(monkeypatch):
    state = {"fatigue_level": 2}

    monkeypatch.setattr(state_tracker, "get_state", lambda: dict(state))
    monkeypatch.setattr(state_tracker, "update_state", lambda **kw: state.update(kw))

    result = monitor_session({"xp_rate": 250.0})
    assert result.get("mode") is None

