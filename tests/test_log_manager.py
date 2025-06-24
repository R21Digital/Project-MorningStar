import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.log_manager import start_log


def test_start_log_creates_file(tmp_path, monkeypatch):
    log_file = tmp_path / "test.log"
    start_log(log_path=str(log_file))
    assert log_file.exists()
