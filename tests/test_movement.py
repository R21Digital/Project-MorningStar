import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.execution.movement import execute_movement


def test_execute_movement_prints_destination(capsys):
    step = {"type": "move", "to": {"planet": "Tatooine", "city": "Mos Eisley"}}
    execute_movement(step)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Moving to Tatooine, Mos Eisley"
