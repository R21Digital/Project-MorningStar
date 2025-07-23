import logging
from datetime import datetime, timedelta
from importlib import reload
from pathlib import Path

from core import logging_config


def _reset_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    for h in list(logger.handlers):
        logger.removeHandler(h)
    if hasattr(logger, "_configured"):
        delattr(logger, "_configured")
    return logger


def test_log_retention(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    old_dt = datetime.now() - timedelta(days=10)
    recent_dt = datetime.now() - timedelta(days=2)
    old_log = log_dir / f"{old_dt.strftime('%Y%m%d_%H%M%S')}.log"
    recent_log = log_dir / f"{recent_dt.strftime('%Y%m%d_%H%M%S')}.log"

    old_log.write_text("old")
    recent_log.write_text("recent")

    monkeypatch.setenv("LOG_RETENTION_DAYS", "7")
    _reset_logger("ms11_retention")
    reload(logging_config)

    logging_config.configure_logger(name="ms11_retention", log_file=str(log_dir / "app.log"))

    assert not old_log.exists(), "Expired log was not removed"
    assert recent_log.exists(), "Recent log was incorrectly removed"
