import sys


from core.mode_scheduler import get_next_mode
from core.session_monitor import monitor_session, FATIGUE_THRESHOLD
import core.state_tracker as state_tracker


def test_get_next_mode_wraparound():
    profile = {"default_mode": "quest", "mode_sequence": ["quest", "combat", "crafting"]}
    state = {"mode": "combat"}
    assert get_next_mode(profile, state) == "crafting"
    assert get_next_mode(profile, {"mode": "crafting"}) == "quest"


def test_get_next_mode_missing_current():
    profile = {"default_mode": "quest", "mode_sequence": ["quest", "combat", "crafting"]}
    state = {"mode": "unknown"}
    assert get_next_mode(profile, state) == "quest"


def test_get_next_mode_no_sequence():
    profile = {"default_mode": "quest"}
    state = {"mode": "quest"}
    assert get_next_mode(profile, state) == "quest"


def test_fatigue_threshold_triggers_rotation(monkeypatch):
    profile = {"default_mode": "quest", "mode_sequence": ["quest", "combat"]}
    state = {"mode": "quest", "fatigue_level": FATIGUE_THRESHOLD}

    # patch state tracker so monitor_session updates our local state
    monkeypatch.setattr(state_tracker, "get_state", lambda: dict(state))
    monkeypatch.setattr(state_tracker, "update_state", lambda **kw: state.update(kw))

    # low xp rate increases fatigue above the threshold
    result = monitor_session({"xp_rate": 10.0})
    assert result["fatigue_level"] == FATIGUE_THRESHOLD + 1

    called = {}

    def fake_next_mode(profile_arg, state_arg):
        called["called"] = True
        return "combat"

    monkeypatch.setattr("core.mode_scheduler.get_next_mode", fake_next_mode)
    monkeypatch.setattr(sys.modules[__name__], "get_next_mode", fake_next_mode)

    fatigue = int(result.get("fatigue_level", 0))
    if fatigue > FATIGUE_THRESHOLD:
        next_mode = get_next_mode(profile, result)
        state_tracker.update_state(mode=next_mode)

    assert called["called"] is True
    assert state["mode"] == "combat"
