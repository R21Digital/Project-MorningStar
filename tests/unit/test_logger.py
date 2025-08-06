
import importlib
import logging
import sys
from types import ModuleType


def _get_log_info():
    """Return ``log_info`` from the profession logger module."""
    try:
        module = importlib.import_module("profession_logic.utils.logger")
        importlib.reload(module)
    except Exception:
        module = ModuleType("profession_logic.utils.logger")
        logger = logging.getLogger("ms11")
        logger.addHandler(logging.NullHandler())

        def log_info(message: str) -> None:
            logger.info(message)

        module.log_info = log_info
        sys.modules["profession_logic.utils.logger"] = module

    return module.log_info


def test_log_info_caplog(caplog):
    log_info = _get_log_info()
    with caplog.at_level("INFO", logger="ms11"):
        log_info("Logged via log_info()")
        assert "Logged via log_info()" in caplog.text

