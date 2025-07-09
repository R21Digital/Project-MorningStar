import time

from profession_logic.utils.logger import logger
from core.legacy_tracker import load_legacy_steps, read_quest_log
from core.quest_engine import execute_with_retry


def run_full_legacy_quest() -> None:
    """Execute all legacy quest steps sequentially."""
    steps = load_legacy_steps()
    completed_steps = read_quest_log()

    for step in steps:
        if step.get("id") in completed_steps:
            continue

        logger.info(
            f"[Legacy Loop] Executing step: {step.get('id')} - {step.get('description')}"
        )
        success = execute_with_retry(step, max_retries=3)

        if not success:
            logger.warning(
                f"[Legacy Loop] Failed to complete step {step.get('id')}. Halting loop."
            )
            break

        logger.info(
            f"[Legacy Loop] Step {step.get('id')} complete. Waiting before next step..."
        )
        time.sleep(3)

    logger.info("[Legacy Loop] Legacy Quest run complete.")
