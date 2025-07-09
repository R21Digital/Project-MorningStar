from profession_logic.utils.logger import log_info


def test_log_info_caplog(caplog):
    with caplog.at_level("INFO", logger="ms11"):
        log_info("Logged via log_info()")
        assert "Logged via log_info()" in caplog.text

