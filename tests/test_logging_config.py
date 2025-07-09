import logging
import warnings
from importlib import reload

from core import logging_config


def test_configure_logger_creates_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reload(logging_config)
    base_logger = logging.getLogger("ms11")
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)
    warnings_logger = logging.getLogger("py.warnings")
    for h in list(warnings_logger.handlers):
        warnings_logger.removeHandler(h)
    logger = logging_config.configure_logger()
    logger.info("hello")
    warnings.warn("watch out")
    log_dir = tmp_path / "logs"
    log_file = log_dir / "app.log"
    warn_file = log_dir / "warnings.log"
    assert log_file.exists(), "Log file was not created"
    assert warn_file.exists(), "Warning log was not created"
    assert "hello" in log_file.read_text()
    assert "watch out" in warn_file.read_text()


def test_logger_reuse_prevents_duplicate_handlers(tmp_path, monkeypatch):
    """Calling configure_logger twice should not add handlers twice."""
    monkeypatch.chdir(tmp_path)
    reload(logging_config)

    base_logger = logging.getLogger("ms11")
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)
    warnings_logger = logging.getLogger("py.warnings")
    for h in list(warnings_logger.handlers):
        warnings_logger.removeHandler(h)

    log_file = tmp_path / "logs" / "app.log"
    warn_file = tmp_path / "logs" / "warnings.log"

    logger_first = logging_config.configure_logger(str(log_file), str(warn_file))
    first_handler_count = len(logger_first.handlers)

    logger_second = logging_config.configure_logger(str(log_file), str(warn_file))

    assert len(logger_second.handlers) == first_handler_count
