from importlib import reload

import utils.logger as base_logger


def test_log_info_prints(capsys):
    base_logger.log_info("hello world")
    captured = capsys.readouterr()
    assert "hello world" in captured.out

