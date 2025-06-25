import os
from collections import defaultdict

from .static_estimator import LOG_DIR, LOG_FILE


class LearningXPEstimator:
    """Update XP estimates from logged data."""

    def __init__(self, log_dir: str = LOG_DIR):
        self.log_dir = log_dir
        self.log_path = os.path.join(self.log_dir, LOG_FILE)
        self.estimates = {}

    def update(self) -> None:
        """Recompute averages using the saved log."""
        counts = defaultdict(lambda: [0, 0])
        if os.path.exists(self.log_path):
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) != 3:
                        continue
                    _, action, xp_str = parts
                    try:
                        xp = int(xp_str)
                    except ValueError:
                        continue
                    counts[action][0] += xp
                    counts[action][1] += 1
        self.estimates = {
            a: total / count if count else 0 for a, (total, count) in counts.items()
        }

    def estimate(self, action: str) -> float:
        """Return the current XP estimate for ``action``."""
        return self.estimates.get(action, 0.0)

