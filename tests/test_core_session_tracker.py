import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.session_tracker as session_tracker


def test_load_session_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    session_file = tmp_path / session_tracker.SESSION_FILE
    assert not session_file.exists()
    data = session_tracker.load_session()
    assert data == session_tracker.DEFAULT_SESSION


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = {"foo": 1, "bar": [1, 2, 3]}
    session_tracker.save_session(payload)
    assert (tmp_path / session_tracker.SESSION_FILE).exists()
    loaded = session_tracker.load_session()
    assert loaded == payload
