import os
import sys


from src.log_manager import start_log


def test_start_log_creates_file(tmp_path, monkeypatch):
    log_file = tmp_path / "test.log"
    start_log(log_path=str(log_file))
    assert log_file.exists()
