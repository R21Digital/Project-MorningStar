import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import xp_estimator
from core.session_manager import SessionManager
from src import session_logger


def test_session_manager_logs_xp(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(xp_estimator, "DEFAULT_LOG_PATH", str(tmp_path / "xp_history.json"), raising=False)
    monkeypatch.setattr(session_logger, "LOG_DIR", str(tmp_path))

    session = SessionManager(mode="test")
    session.set_start_xp(1000)
    session.set_end_xp(1100)
    session.end_session()

    history = json.loads((tmp_path / "xp_history.json").read_text())
    assert history[0]["xp"] == 100

    log_files = list(tmp_path.glob(f"{session.session_id}.json"))
    assert log_files, "session log not created"
    log_data = json.loads(log_files[0].read_text())
    assert log_data[0]["start_xp"] == 1000
    assert log_data[0]["end_xp"] == 1100
    assert log_data[0]["xp_gain"] == 100
