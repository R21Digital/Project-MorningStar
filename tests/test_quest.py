

from src.execution.quest import execute_quest


def test_quest_step_start(capfd):
    step = {"type": "quest", "id": "intro_mission", "action": "start"}
    execute_quest(step)
    out, _ = capfd.readouterr()
    assert "[QUEST] START quest 'intro_mission'" in out
