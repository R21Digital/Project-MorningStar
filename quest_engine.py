"""Simple quest step executor."""

from src.execution.action_router import get_handler


def handle_quest_step(step: dict) -> bool:
    """Execute a quest step using the action router."""
    step_type = step.get("type")
    data = step.get("data", {})

    print(f"[ENGINE] Handling step type: {step_type} with data: {data}")

    handler = get_handler(step_type)
    if not handler:
        print(f"[!] Unknown action type: {step_type}")
        return False

    handler(**data)
    return True
