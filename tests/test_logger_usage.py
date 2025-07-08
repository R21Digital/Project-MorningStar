from importlib import reload

import utils.logger as base_logger


def test_log_info_writes_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base_logger.logger.handlers.clear()
    reload(base_logger)

    log_file = tmp_path / "logs" / "dashboard_usage.log"
    base_logger.log_info("hello world")

    assert log_file.exists(), "dashboard log not created"
    assert "hello world" in log_file.read_text()

