from __future__ import annotations

from src.execution.core import execute_step
from .step_executor import run_validated_step


def run_step_with_feedback(step: dict) -> bool:
    """Execute a quest ``step`` and validate via ``run_validated_step``."""
    success_markers = step.get("success_texts")
    return run_validated_step(lambda: execute_step(step), success_markers)
