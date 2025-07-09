import builtins
import sys
import types
from utils.logger import log_info, save_screenshot


def test_log_info_caplog(caplog):
    with caplog.at_level("INFO", logger="ms11"):
        log_info("Logged via log_info()")
        assert "Logged via log_info()" in caplog.text


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
    save_screenshot("test_no_cv2")


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
    save_screenshot("test_fail_grab")
