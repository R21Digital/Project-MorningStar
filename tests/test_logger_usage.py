from profession_logic.utils.logger import log_info


def test_profession_logger(caplog):
    with caplog.at_level("INFO"):
        log_info("Profession logger test message")
        assert "Profession logger test message" in caplog.text

