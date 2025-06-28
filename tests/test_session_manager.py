import os
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.session_manager import SessionManager


def test_session_manager_log_creation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
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
