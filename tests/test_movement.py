import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.execution.movement import execute_movement


def test_execute_movement_logs_command(capsys):
    step = {"type": "move", "coords": [10, 20], "region": "Naboo"}
    execute_movement(step)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines == [
        "\U0001F4CD [Move] Navigating to [10, 20] in Naboo",
        "\U0001F9ED Executing: /navigate 10 20 --zone=Naboo",
    ]
