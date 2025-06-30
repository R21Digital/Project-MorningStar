import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.session_tracker as session_tracker


def test_load_session_default(tmp_path, monkeypatch):
    session_file = tmp_path / session_tracker.SESSION_FILE
    monkeypatch.setenv(session_tracker.SESSION_FILE_ENV, str(session_file))
    assert not session_file.exists()
    data = session_tracker.load_session()
    assert data == session_tracker.DEFAULT_SESSION


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    session_file = tmp_path / session_tracker.SESSION_FILE
    monkeypatch.setenv(session_tracker.SESSION_FILE_ENV, str(session_file))
    payload = {"foo": 1, "bar": [1, 2, 3]}
    session_tracker.save_session(payload)
    assert session_file.exists()
    loaded = session_tracker.load_session()
    assert loaded == payload


def test_log_farming_result(tmp_path, monkeypatch):
    session_file = tmp_path / session_tracker.SESSION_FILE
    monkeypatch.setenv(session_tracker.SESSION_FILE_ENV, str(session_file))

    monkeypatch.setattr(
        session_tracker,
        "AFFINITY_MAP",
        {"bounty_hunter": ["bandit"], "medic": ["thug"]},
    )

    session_tracker.log_farming_result(["bandit", "bandit", "thug"], 100)
    data = session_tracker.load_session()
    assert data["missions_completed"] == 1
    assert data["total_credits_earned"] == 100
    assert data["mob_counts"] == {"bandit": 2, "thug": 1}
    assert data["affinity_counts"] == {"bounty_hunter": 2, "medic": 1}

    session_tracker.log_farming_result(["bandit"], 50)
    data = session_tracker.load_session()
    assert data["missions_completed"] == 2
    assert data["total_credits_earned"] == 150
    assert data["mob_counts"] == {"bandit": 3, "thug": 1}
    assert data["affinity_counts"] == {"bounty_hunter": 3, "medic": 1}
