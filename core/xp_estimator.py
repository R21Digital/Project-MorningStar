"""Simple XP estimator with rolling averages."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

DEFAULT_LOG_PATH = os.path.join("data", "session_logs", "xp_history.json")


class XPEstimator:
    """Track XP gained per action and compute rolling averages."""

    def __init__(self, log_path: str | None = None):
        if log_path is None:
            log_path = DEFAULT_LOG_PATH
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self.history: List[Dict] = []
        self._totals: Dict[str, List[int]] = defaultdict(lambda: [0, 0])  # action -> [total, count]
        self._load()

    # -----------------------------------------------------
    def _load(self) -> None:
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as fh:
                    self.history = json.load(fh)
            except Exception:
                self.history = []
        for entry in self.history:
            action = entry.get("action")
            xp = int(entry.get("xp", 0))
            self._totals[action][0] += xp
            self._totals[action][1] += 1

    def _save(self) -> None:
        with open(self.log_path, "w", encoding="utf-8") as fh:
            json.dump(self.history, fh, indent=2)

    # -----------------------------------------------------
    def log_action(self, action: str, xp: int) -> None:
        """Record ``xp`` gained for ``action`` and update averages."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "xp": xp,
        }
        self.history.append(entry)
        self._totals[action][0] += xp
        self._totals[action][1] += 1
        self._save()

    def average_xp(self, action: str) -> float:
        total, count = self._totals.get(action, (0, 0))
        return total / count if count else 0.0
