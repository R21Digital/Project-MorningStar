import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.logging.session_log import log_step


def test_log_step_creates_file():
    step = {"type": "test", "value": 123}
    log_step(step)
    files = os.listdir("logs")
    assert any("session_" in f and f.endswith(".log") for f in files)
