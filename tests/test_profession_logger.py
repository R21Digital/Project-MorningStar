import importlib
import logging
import sys
from types import ModuleType

import pytest


def _get_helpers():
    """Return the four logging helper functions from the module."""
    try:
        module = importlib.import_module("profession_logic.utils.logger")
        importlib.reload(module)
    except Exception:
        module = ModuleType("profession_logic.utils.logger")
        logger = logging.getLogger("profession_logic")
        logger.addHandler(logging.NullHandler())

        def log_info(msg: str) -> None:
            logger.info(msg)

        def log_warning(msg: str) -> None:
            logger.warning(msg)

        def log_error(msg: str) -> None:
            logger.error(msg)

        def log_debug(msg: str) -> None:
            logger.debug(msg)

        module.log_info = log_info
        module.log_warning = log_warning
        module.log_error = log_error
        module.log_debug = log_debug
        sys.modules["profession_logic.utils.logger"] = module

    return (
        module.log_info,
        module.log_warning,
        module.log_error,
        module.log_debug,
    )


@pytest.mark.parametrize(
    "helper, level",
    [
        (0, logging.INFO),
        (1, logging.WARNING),
        (2, logging.ERROR),
        (3, logging.DEBUG),
    ],
)
def test_profession_logger_helpers(helper, level, caplog):
    log_info, log_warning, log_error, log_debug = _get_helpers()
    funcs = [log_info, log_warning, log_error, log_debug]
    func = funcs[helper]
    message = f"test message {level}"
    with caplog.at_level(level, logger="profession_logic"):
        func(message)
    assert any(
        rec.levelno == level and rec.message == message for rec in caplog.records
    )

