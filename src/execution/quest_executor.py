"""Real-time quest executor loop.

This module loads a quest from a JSON file and iteratively processes each step
using ``execute_step``. A short delay is included between steps to emulate
in-game actions.
"""

from __future__ import annotations

import json
import time

from .core import execute_step


class QuestExecutor:
    """Execute quest steps sequentially."""

    def __init__(self, quest_path: str) -> None:
        self.quest_path = quest_path
        self.steps = self.load_steps()

    def load_steps(self) -> list[dict]:
        """Load quest step dictionaries from ``quest_path``."""
        with open(self.quest_path, "r") as file:
            return json.load(file)

    def run(self) -> None:
        """Run the quest, executing each step in order."""
        print("[QUEST EXECUTOR] Starting quest sequence...")
        for i, step in enumerate(self.steps, start=1):
            print(f"[QUEST EXECUTOR] Executing step {i}: {step}")
            execute_step(step)
            time.sleep(1)  # simulate delay between steps

