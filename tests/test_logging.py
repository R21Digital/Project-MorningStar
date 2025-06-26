import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.logging.session_log import log_step


def test_log_step_creates_file():
    step = {"type": "test", "value": 123, "xp": 10}
    log_step(step)
    files = [f for f in os.listdir("logs") if f.startswith("session_") and f.endswith(".json")]
    assert files
    with open(os.path.join("logs", files[0]), "r", encoding="utf-8") as f:
        data = __import__("json").load(f)
    assert data["total_xp"] >= 10
    assert data["activity_breakdown"]["test"] >= 1
