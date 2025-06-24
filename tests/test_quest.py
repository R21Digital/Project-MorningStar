import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.execution.quest import execute_quest


def test_quest_step_start(capfd):
    step = {"type": "quest", "id": "intro_mission", "action": "start"}
    execute_quest(step)
    out, _ = capfd.readouterr()
    assert "[QUEST] START quest 'intro_mission'" in out
