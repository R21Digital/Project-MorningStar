from datetime import datetime
import json
import os

from .xp_paths import LOG_ROOT

# Store all XP session logs under the shared ``logs/xp_tracking`` directory
LOG_DIR = LOG_ROOT
os.makedirs(LOG_DIR, exist_ok=True)


class XPSession:
    def __init__(self, character: str, xp_start: int):
        self.character = character
        self.session_start = datetime.now().isoformat()
        self.xp_start = xp_start
        self.xp_end = None
        self.xp_gain = None
        self.actions = []

    def log_action(self, action_type: str, xp_value: int):
        timestamp = datetime.now().isoformat()
        self.actions.append({
            "timestamp": timestamp,
            "type": action_type,
            "xp": xp_value
        })

    def finalize(self, xp_end: int):
        self.xp_end = xp_end
        self.xp_gain = xp_end - self.xp_start

    def save(self):
        """Write the session log to ``logs/xp_tracking/session_*.json`` and return the path."""
        timestamp = self.session_start.replace(":", "-")
        path = os.path.join(LOG_DIR, f"session_{timestamp}.json")
        with open(path, "w") as f:
            json.dump(self.__dict__, f, indent=2)
        return path
