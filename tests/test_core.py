import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    assert "[TODO] Unsupported step type: dance" in captured.out
