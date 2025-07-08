import builtins
import sys
import types
from utils import logger


def test_log_info(capsys):
    logger.log_info("Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_save_screenshot_without_cv2(monkeypatch):
    orig_import = builtins.__import__

    if "PIL.ImageGrab" not in sys.modules:
        pil_mod = sys.modules.setdefault("PIL", types.ModuleType("PIL"))
        grab_mod = types.ModuleType("PIL.ImageGrab")
        grab_mod.grab = lambda: None
        sys.modules["PIL.ImageGrab"] = grab_mod
        pil_mod.ImageGrab = grab_mod

    def fake_import(name, *args, **kwargs):
        if name == "cv2":
            raise ImportError
        return orig_import(name, *args, **kwargs)

    monkeypatch.setitem(builtins.__dict__, "__import__", fake_import)
    logger.save_screenshot("test_no_cv2")


def test_save_screenshot_failure(monkeypatch):
    if "PIL.ImageGrab" not in sys.modules:
        pil_mod = sys.modules.setdefault("PIL", types.ModuleType("PIL"))
        grab_mod = types.ModuleType("PIL.ImageGrab")
        grab_mod.grab = lambda: None
        sys.modules["PIL.ImageGrab"] = grab_mod
        pil_mod.ImageGrab = grab_mod
    def fake_grab():
        raise RuntimeError("Test grab failure")

    monkeypatch.setattr("PIL.ImageGrab.grab", fake_grab)
    logger.save_screenshot("test_fail_grab")
