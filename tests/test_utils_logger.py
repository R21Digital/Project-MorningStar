import os
import sys
import types
from importlib import reload



def test_save_screenshot_creates_file(tmp_path, monkeypatch):
    fake_cv2 = types.SimpleNamespace(imwrite=lambda p, img: open(p, "wb").close())
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    import src.utils.logger as logger
    reload(logger)

    out_dir = tmp_path / "shots"
    file_path = logger.save_screenshot(object(), directory=str(out_dir))
    assert os.path.exists(file_path)


def test_log_ocr_text(tmp_path):
    from src.utils import logger
    log_file = tmp_path / "ocr.log"
    logger.log_ocr_text("hello", log_path=str(log_file))
    content = log_file.read_text()
    assert "hello" in content


def test_log_event(tmp_path):
    from src.utils import logger
    log_file = tmp_path / "ev.log"
    logger.log_event("hi", log_path=str(log_file))
    assert log_file.exists()
    content = log_file.read_text()
    assert "hi" in content


def test_log_performance_summary(tmp_path):
    from src.utils import logger

    csv_file = tmp_path / "perf.csv"
    stats = {"quests": 1, "xp": 42}
    logger.log_performance_summary(stats, csv_path=str(csv_file))

    assert csv_file.exists(), "CSV file was not created"
    lines = csv_file.read_text().strip().splitlines()
    assert lines[0] == "quests,xp"
    assert lines[1] == "1,42"

