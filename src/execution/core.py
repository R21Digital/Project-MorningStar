"""Core step execution dispatcher."""

import logging
from typing import Dict, Any

from .dialogue import execute_dialogue
from .movement import execute_movement

try:
    from src.logging_utils.session_log import log_step
except ImportError:
    # Fallback logging if session_log is not available
    def log_step(step: Dict[str, Any]) -> None:
        """Fallback logging function."""
        logging.info(f"Executing step: {step.get('type', 'unknown')}")

logger = logging.getLogger(__name__)


def execute_step(step: Dict[str, Any]) -> None:
    """Dispatch a single step based on its ``type``."""
    if not isinstance(step, dict):
        logger.error(f"Invalid step format: expected dict, got {type(step)}")
        return
        
    step_type = step.get("type")
    if not step_type:
        logger.error("Step missing required 'type' field")
        return
        
    log_step(step)
    logger.info(f"Executing step type: {step_type}")
    
    try:
        if step_type == "dialogue":
            execute_dialogue(step)
        elif step_type == "move":
            execute_movement(step)
        elif step_type == "quest":
            from .quest import execute_quest
            execute_quest(step)
        else:
            logger.warning(f"Unsupported step type '{step_type}' - no handler available")
    except Exception as e:
        logger.error(f"Error executing step type '{step_type}': {e}", exc_info=True)
        raise
