"""Simple quest step executor."""

from src.execution.action_router import get_handler
from utils.logger import logger


def handle_quest_step(step: dict) -> bool:
    """Execute a quest step using the action router."""
    step_type = step.get("type")
    data = step.get("data", {})

    logger.info("[ENGINE] Handling step type: %s with data: %s", step_type, data)

    handler = get_handler(step_type)
    if not handler:
        logger.warning("[!] Unknown action type: %s", step_type)
        return False

    handler(**data)
    return True
