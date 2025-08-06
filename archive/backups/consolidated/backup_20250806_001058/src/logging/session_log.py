"""Lightweight JSON session logger."""

import datetime
import json
import os

# All session logs are written under ``logs/`` with a consistent naming scheme
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = os.path.join(log_dir, f"session_{timestamp}.json")

# Internal structure for the active session
_session_data = {
    "start_time": datetime.datetime.now().isoformat(),
    "quests_completed": 0,
    "total_xp": 0,
    "time_spent": 0.0,
    "activity_breakdown": {},
    "steps": [],
}
_start_dt = datetime.datetime.now()


def log_step(step: dict) -> None:
    """Append ``step`` to the JSON log and update summary fields."""

    now = datetime.datetime.now()

    step_type = step.get("type", "unknown")
    _session_data["activity_breakdown"].setdefault(step_type, 0)
    _session_data["activity_breakdown"][step_type] += 1

    if step_type == "quest" and step.get("action") == "complete":
        _session_data["quests_completed"] += 1

    xp = step.get("xp")
    if isinstance(xp, (int, float)):
        _session_data["total_xp"] += xp

    _session_data["steps"].append({"time": now.isoformat(), **step})

    _session_data["time_spent"] = (now - _start_dt).total_seconds()

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(_session_data, f, indent=2) 