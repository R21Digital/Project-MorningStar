

from src.execution.core import execute_step


def test_execute_step_dialogue(capsys):
    step = {"type": "dialogue", "npc": "Trainer"}
    execute_step(step)
    captured = capsys.readouterr()
    assert "Interacting with Trainer" in captured.out


def test_execute_step_unknown(capsys):
    step = {"type": "dance"}
    execute_step(step)
    captured = capsys.readouterr()
    assert "[Unsupported] Step type 'dance' is not implemented." in captured.out
