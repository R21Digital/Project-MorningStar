import logging
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
