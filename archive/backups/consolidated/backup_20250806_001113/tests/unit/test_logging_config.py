import logging
import os
from datetime import datetime, timedelta
from importlib import reload

from core import logging_config


def test_configure_logger_creates_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reload(logging_config)
    base_logger = logging.getLogger("ms11")
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)
    log_file = tmp_path / "logs" / "app.log"
    logger = logging_config.configure_logger(log_file=str(log_file))
    logger.info("hello")
    assert log_file.exists(), "Log file was not created"
    assert "hello" in log_file.read_text()


def test_logger_reuse_prevents_duplicate_handlers(tmp_path, monkeypatch):
    """Calling configure_logger twice should not add handlers twice."""
    monkeypatch.chdir(tmp_path)
    reload(logging_config)

    base_logger = logging.getLogger("ms11")
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)
    log_file = tmp_path / "logs" / "app.log"

    logger_first = logging_config.configure_logger(log_file=str(log_file))
    first_handler_count = len(logger_first.handlers)

    logger_second = logging_config.configure_logger(log_file=str(log_file))

    assert len(logger_second.handlers) == first_handler_count


def test_configure_logger_respects_level(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    reload(logging_config)

    base_logger = logging.getLogger("ms11_level")
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)

    logger = logging_config.configure_logger(name="ms11_level")
    assert logger.level == logging.WARNING

    logger_param = logging_config.configure_logger(
        name="ms11_param", level=logging.DEBUG
    )
    assert logger_param.level == logging.DEBUG


def test_configure_logger_cleans_old_logs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reload(logging_config)

    base_logger = logging.getLogger("cleanup")
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)

    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    # Create old logs exceeding limits
    for i in range(logging_config.MAX_LOG_FILES + 2):
        p = log_dir / f"old{i}.log"
        p.write_text("x")
        old_time = datetime.now() - timedelta(days=logging_config.MAX_LOG_AGE_DAYS + 1)
        os.utime(p, (old_time.timestamp(), old_time.timestamp()))

    log_file = log_dir / "app.log"
    logger = logging_config.configure_logger(name="cleanup", log_file=str(log_file))
    logger.info("new")

    remaining = list(log_dir.glob("*.log"))
    assert log_file in remaining
    assert len(remaining) <= logging_config.MAX_LOG_FILES
    for f in remaining:
        age_days = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        assert age_days <= logging_config.MAX_LOG_AGE_DAYS
