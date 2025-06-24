"""Core step execution dispatcher."""

from .dialogue import execute_dialogue
from .movement import execute_movement


def execute_step(step: dict) -> None:
    """Dispatch a single step based on its ``type``."""
    step_type = step.get("type")
    if step_type == "dialogue":
        execute_dialogue(step)
    elif step_type == "move":
        execute_movement(step)
    else:
        print(f"[TODO] Unsupported step type: {step_type}")
