import pytest


from src.automation import automator
from src.automation import mode_manager


def test_set_mode_updates_current_mode():
    mode_manager.set_mode("combat")
    assert mode_manager.current_mode == "combat"
    with pytest.raises(ValueError):
        mode_manager.set_mode("invalid")


def test_run_state_monitor_loop_uses_selected_mode(monkeypatch):
    calls = []

    def combat_behavior():
        calls.append("combat")

    monkeypatch.setattr(automator, "MODE_BEHAVIORS", {"combat": combat_behavior})
    mode_manager.set_mode("combat")
    monkeypatch.setattr(automator.time, "sleep", lambda *_: None)
    automator.run_state_monitor_loop(delay=0, iterations=1)
    assert calls == ["combat"]
