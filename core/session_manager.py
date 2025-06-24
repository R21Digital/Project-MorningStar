import os
import json
import uuid
from datetime import datetime

class SessionManager:
    def __init__(self, mode: str = "unknown"):
        self.session_id = str(uuid.uuid4())[:8]
        self.mode = mode
        self.start_time = datetime.now()
        self.end_time = None
        self.start_credits = 0
        self.end_credits = 0
        self.xp_gained = 0
        self.actions_log = []

        os.makedirs("logs", exist_ok=True)
        print(
            f"[SESSION STARTED] ID: {self.session_id} | Mode: {self.mode} | Time: {self.start_time}"
        )

    def set_start_credits(self, credits: int) -> None:
        self.start_credits = credits

    def set_end_credits(self, credits: int) -> None:
        self.end_credits = credits

    def add_action(self, action: str) -> None:
        timestamp = datetime.now().isoformat()
        self.actions_log.append({"time": timestamp, "action": action})

    def end_session(self) -> None:
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds() / 60
        print(
            f"[SESSION ENDED] ID: {self.session_id} | Duration: {self.duration:.2f} mins"
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
            "xp_gained": self.xp_gained,
            "actions": self.actions_log,
        }

        log_path = os.path.join("logs", f"session_{self.session_id}.json")
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=4)

        print(f"[LOG SAVED] \u2192 {log_path}")

