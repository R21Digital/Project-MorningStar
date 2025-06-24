import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.execution.movement import execute_movement
from unittest.mock import patch


def test_execute_movement_prints_destination(capsys):
    step = {"type": "move", "to": {"planet": "Tatooine", "city": "Mos Eisley"}}
    execute_movement(step)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Moving to Tatooine, Mos Eisley"


class DummySession:
    def __init__(self):
        self.actions = []

    def add_action(self, action):
        self.actions.append(action)


@patch("src.movement.movement_profiles.time.sleep", return_value=None)
def test_patrol_route_with_waits(mock_sleep, capsys):
    from src.movement.agent_mover import MovementAgent
    from src.movement.movement_profiles import patrol_route

    session = DummySession()
    agent = MovementAgent(session=session)
    patrol_route(agent, "Anchorhead-Loop")

    captured = capsys.readouterr()
    output_lines = [line for line in captured.out.splitlines() if line.startswith("Moving")]
    assert len(output_lines) == 4
    assert output_lines[0] == "Moving from Theed to Anchorhead"
    assert mock_sleep.call_count == 4
    waiting_actions = [a for a in session.actions if str(a).startswith("Waiting ")]
    assert len(waiting_actions) == 4


def test_patrol_route_missing_route():
    from src.movement.agent_mover import MovementAgent
    from src.movement.movement_profiles import patrol_route

    session = DummySession()
    agent = MovementAgent(session=session)
    patrol_route(agent, "Nowhere")

    assert session.actions[-1] == "Route 'Nowhere' not found."
