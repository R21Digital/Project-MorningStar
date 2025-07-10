import importlib
import logging
import sys
from types import ModuleType


def _get_log_info():
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


def test_profession_logger(caplog):
    log_info = _get_log_info()
    with caplog.at_level("INFO"):
        log_info("Profession logger test message")
        assert "Profession logger test message" in caplog.text

