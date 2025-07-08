import os
import sys
import types
from importlib import reload
from pathlib import Path



def test_save_screenshot_creates_file(tmp_path, monkeypatch):
    fake_cv2 = types.SimpleNamespace(
        imwrite=lambda p, img: Path(p).open("wb").close(),
        cvtColor=lambda arr, flag: arr,
        COLOR_RGB2BGR=1,
    )
    fake_np = types.SimpleNamespace(array=lambda x: x)
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    monkeypatch.setitem(sys.modules, "numpy", fake_np)
    if "PIL.ImageGrab" not in sys.modules:
        pil_mod = sys.modules.setdefault("PIL", types.ModuleType("PIL"))
        grab_mod = types.ModuleType("PIL.ImageGrab")
        grab_mod.grab = lambda: object()
        sys.modules["PIL.ImageGrab"] = grab_mod
        pil_mod.ImageGrab = grab_mod
    else:
        monkeypatch.setattr("PIL.ImageGrab.grab", lambda: object())

    import utils.logger as logger
    reload(logger)

    monkeypatch.chdir(tmp_path)
    file_path = logger.save_screenshot("shot")
    assert Path(file_path).exists()


def test_log_ocr_text(tmp_path):
    from utils import logger
    log_file = tmp_path / "ocr.log"
    logger.log_ocr_text("hello", log_path=str(log_file))
    content = log_file.read_text()
    assert "hello" in content


def test_log_event(tmp_path):
    from utils import logger
    log_file = tmp_path / "ev.log"
    logger.log_event("hi", log_path=str(log_file))
    assert log_file.exists()
    content = log_file.read_text()
    assert "hi" in content


def test_log_performance_summary(tmp_path):
    from utils import logger

    csv_file = tmp_path / "perf.csv"
    stats = {"quests": 1, "xp": 42}
    logger.log_performance_summary(stats, csv_path=str(csv_file))

    assert csv_file.exists(), "CSV file was not created"
    lines = csv_file.read_text().strip().splitlines()
    assert lines[0] == "quests,xp"
    assert lines[1] == "1,42"

