"""Real-time quest executor loop.

This module loads a quest from a JSON file and iteratively processes each step
using ``execute_step``. A short delay is included between steps to emulate
in-game actions.
"""

from __future__ import annotations

from core.quest_loader import load_quest_steps
from utils.logger import log_info
from src.quest_executor import run_steps


class QuestExecutor:
    """Execute quest steps sequentially."""

    def __init__(self, quest_path: str) -> None:
        self.quest_path = quest_path
        self.steps = load_quest_steps(self.quest_path)

    def run(self) -> None:
        """Run the quest, executing each step in order."""
        log_info("[QUEST EXECUTOR] Starting quest sequence...")

        def formatter(i: int, step: dict) -> str:
            return f"[QUEST EXECUTOR] Executing step {i}: {step}"

        run_steps(self.steps, log_fn=log_info, delay=1, formatter=formatter)

