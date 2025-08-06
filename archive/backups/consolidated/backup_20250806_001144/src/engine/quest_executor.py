from __future__ import annotations

import os

from src.execution.core import execute_step
from .step_executor import run_validated_step

# Path to the retry log used by :mod:`core.quest_engine`
RETRY_LOG_PATH = os.path.join("logs", "retry_log.txt")


def run_step_with_feedback(step: dict) -> bool:
    """Execute a quest ``step`` and validate via ``run_validated_step``."""
    success_markers = step.get("success_texts")
    return run_validated_step(lambda: execute_step(step), success_markers)
