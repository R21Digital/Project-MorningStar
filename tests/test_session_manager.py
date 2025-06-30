import os
import json
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.session_manager import SessionManager


def test_session_manager_log_creation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    log_messages = []

    class DummyLogger:
        def info(self, msg, *args):
            log_messages.append(msg % args)

    monkeypatch.setattr("core.session_manager.logger", DummyLogger())

    session = SessionManager(mode="test")
    session.set_start_credits(100)
    session.add_action("start")
    session.set_end_credits(150)
    session.end_session()

    logs = list(tmp_path.joinpath("logs").glob("session_*.json"))
    assert len(logs) == 1
    data = json.loads(logs[0].read_text())
    assert data["credits_earned"] == 50
    assert data["actions"][0]["action"] == "start"
    assert data["mode"] == "test"
    assert any("[SESSION STARTED]" in m for m in log_messages)
    assert any("[SESSION ENDED]" in m for m in log_messages)
    assert any("[LOG SAVED]" in m for m in log_messages)
