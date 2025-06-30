import os
import json
import uuid
from datetime import datetime

from core.xp_estimator import XPEstimator
from utils.session_utils import track_xp_gain
from utils.license_hooks import requires_license
from utils.logger import logger

class SessionManager:
    @requires_license
    def __init__(self, mode: str = "unknown"):
        self.session_id = str(uuid.uuid4())[:8]
        self.mode = mode
        self.start_time = datetime.now()
        self.end_time = None
        self.start_credits = 0
        self.end_credits = 0
        self.start_xp = 0
        self.end_xp = None
        self.xp_gained = 0
        self.actions_log = []

        os.makedirs("logs", exist_ok=True)
        logger.info(
            "[SESSION STARTED] ID: %s | Mode: %s | Time: %s",
            self.session_id,
            self.mode,
            self.start_time,
        )

    def set_start_credits(self, credits: int) -> None:
        self.start_credits = credits

    def set_start_xp(self, xp: int) -> None:
        self.start_xp = xp

    def set_end_credits(self, credits: int) -> None:
        self.end_credits = credits

    def set_end_xp(self, xp: int) -> None:
        self.end_xp = xp

    def add_action(self, action: str) -> None:
        timestamp = datetime.now().isoformat()
        self.actions_log.append({"time": timestamp, "action": action})

    def end_session(self) -> None:
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds() / 60
        estimator = XPEstimator()
        if self.end_xp is None:
            # if end xp not explicitly set treat as no change
            self.end_xp = self.start_xp
        self.xp_gained = track_xp_gain(
            self.session_id,
            "session",
            self.start_xp,
            self.end_xp,
            estimator,
        )
        logger.info(
            "[SESSION ENDED] ID: %s | Duration: %.2f mins",
            self.session_id,
            self.duration,
        )
        self.save_log()

    def save_log(self) -> None:
        log_data = {
            "session_id": self.session_id,
            "mode": self.mode,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration,
            "start_credits": self.start_credits,
            "end_credits": self.end_credits,
            "credits_earned": self.end_credits - self.start_credits,
            "start_xp": self.start_xp,
            "end_xp": self.end_xp,
            "xp_gained": self.xp_gained,
            "actions": self.actions_log,
        }

        log_path = os.path.join("logs", f"session_{self.session_id}.json")
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=4)

        logger.info("[LOG SAVED] \u2192 %s", log_path)

