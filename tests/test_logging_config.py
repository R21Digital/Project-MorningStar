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
