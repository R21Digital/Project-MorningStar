"""Core step execution dispatcher."""

from .dialogue import execute_dialogue
from .movement import execute_movement
from src.logging.session_log import log_step


def execute_step(step: dict) -> None:
    """Dispatch a single step based on its ``type``."""
    step_type = step.get("type")
    log_step(step)
    if step_type == "dialogue":
        execute_dialogue(step)
    elif step_type == "move":
        execute_movement(step)
    elif step_type == "quest":
        from .quest import execute_quest
        execute_quest(step)
    else:
        print(f"[Unsupported] Step type '{step_type}' is not implemented.")
