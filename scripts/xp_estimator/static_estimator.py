import os
from datetime import datetime

LOG_DIR = "android_ms11/data/logs/xp_tracking"
LOG_FILE = "xp_actions.log"


class StaticXPEstimator:
    """Log actions and compute average XP per action."""

    def __init__(self, log_dir: str = LOG_DIR):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_path = os.path.join(self.log_dir, LOG_FILE)

    def log_action(self, action: str, xp: int) -> None:
        """Append an action entry to the log file."""
        timestamp = datetime.now().isoformat()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp},{action},{xp}\n")

    def average_xp(self, action: str) -> float:
        """Return the average XP recorded for ``action``."""
        if not os.path.exists(self.log_path):
            return 0.0
        total = 0
        count = 0
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) != 3:
                    continue
                _, act, xp_str = parts
                if act == action:
                    try:
                        total += int(xp_str)
                        count += 1
                    except ValueError:
                        continue
        return total / count if count else 0.0

