import logging
import os
from importlib import reload
from datetime import datetime, timedelta

from core import logging_config


def test_log_retention_env_override(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LOG_RETENTION_DAYS", "1")
    reload(logging_config)

    base_logger = logging.getLogger("retention")
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)

    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    old_log = log_dir / "old.log"
    old_log.write_text("x")
    old_time = datetime.now() - timedelta(days=2)
    os.utime(old_log, (old_time.timestamp(), old_time.timestamp()))

    new_log = log_dir / "new.log"
    new_log.write_text("y")

    log_file = log_dir / "app.log"
    logger = logging_config.configure_logger(name="retention", log_file=str(log_file))
    logger.info("run")

    remaining = list(log_dir.glob("*.log"))
    assert log_file in remaining
    assert new_log in remaining
    assert old_log not in remaining
