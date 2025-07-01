"""
Simple quest step executor.
Executes a single quest step using the action router.
Handles logging and reports.
"""
from src.execution.action_router import get_handler
from utils.logger import logger


def execute_quest_step(step):
    """Executes a single quest step using the appropriate handler."""
    action_type = step.get("type")
    handler = get_handler(action_type)
    if handler is None:
        logger.warning("[QuestEngine] No handler for action type: %s", action_type)
        return False
    try:
        logger.info("[QuestEngine] Executing step: %s", step)
        result = handler(step)
        logger.info("[QuestEngine] Step result: %s", result)
        return result
    except Exception as exc:
        logger.exception("[QuestEngine] Failed to execute step: %s", exc)
        return False
