from typing import List, Dict


def execute_steps(steps: List[str]) -> List[str]:
    """Simulate executing quest steps and return progress messages."""
    if not isinstance(steps, list):
        raise TypeError("steps must be a list")

    executed = []
    for step in steps:
        if not isinstance(step, str):
            raise ValueError("Each step must be a string")
        executed.append(f"Executed: {step}")
    return executed


def run_quest(quest: Dict) -> List[str]:
    """Run the quest described by ``quest`` using :func:`execute_steps`."""
    if not isinstance(quest, dict):
        raise TypeError("quest must be a dict")
    steps = quest.get("steps", [])
    return execute_steps(steps)
