import sys
import os

from src.execution.quest_engine import execute_quest_step


def test_execute_quest_step_with_unknown_type():
    step = {"type": "unsupported"}
    result = execute_quest_step(step)
    assert result is False


def test_execute_quest_step_success(monkeypatch):
    step = {"type": "move", "x": 10, "y": 20}

    def fake_handler(s):
        return f"Moved to {s['x']}, {s['y']}"

    monkeypatch.setattr(
        "src.execution.action_router.get_handler", lambda *_: fake_handler
    )
    # Because quest_engine imported get_handler directly, patch its reference too
    monkeypatch.setattr(
        "src.execution.quest_engine.get_handler", lambda *_: fake_handler
    )

    result = execute_quest_step(step)
    assert result == "Moved to 10, 20"

