import logging
import os
from datetime import datetime, timedelta
from importlib import reload
from pathlib import Path

from core import logging_config


def test_logging_retention(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reload(logging_config)
    # Set custom retention and file limit
    monkeypatch.setenv(logging_config.LOG_RETENTION_ENV, "14")
    monkeypatch.setattr(logging_config, "MAX_LOG_FILES", 20)

    base_logger = logging.getLogger("retention")
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)
    if hasattr(base_logger, "_configured"):
        delattr(base_logger, "_configured")

    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    # Create old logs older than retention period
    for i in range(5):
        p = log_dir / f"old{i}.log"
        p.write_text("x")
        old_time = datetime.now() - timedelta(days=15)
        os.utime(p, (old_time.timestamp(), old_time.timestamp()))

    # Create many new logs to exceed limit
    for i in range(25):
        p = log_dir / f"new{i}.log"
        p.write_text("y")
        # new0 is oldest, new24 is newest
        new_time = datetime.now() - timedelta(minutes=25 - i)
        os.utime(p, (new_time.timestamp(), new_time.timestamp()))

    log_file = log_dir / "latest.log"
    logger = logging_config.configure_logger(name="retention", log_file=str(log_file))
    logger.info("hello")

    remaining = sorted(log_dir.glob("*.log"))
    # All old logs should be removed
    assert not any(f.name.startswith("old") for f in remaining)
    # Only the 20 newest new logs should remain
    new_logs = [f for f in remaining if f.name.startswith("new")]
    assert len(new_logs) == 20
    assert log_file in remaining
    # newest file should exist, oldest should be removed
    assert (log_dir / "new24.log") in new_logs
    assert (log_dir / "new0.log") not in new_logs
    # No log older than 14 days remains
    for f in remaining:
        age_days = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        assert age_days <= 14
