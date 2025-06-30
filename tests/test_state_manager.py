import os
import sys
import time
from types import ModuleType


# Provide fake OCR module before importing StateManager
fake_ocr = ModuleType("src.vision.ocr")
texts = iter(["ignore", "quest accepted"])
fake_ocr.capture_screen = lambda *a, **k: None
fake_ocr.extract_text = lambda img: next(texts)
fake_ocr.screen_text = lambda *a, **k: next(texts)
sys.modules["src.vision.ocr"] = fake_ocr
if "src.vision" in sys.modules:
    sys.modules["src.vision"].ocr = fake_ocr

from src.state.state_manager import StateManager


def test_state_manager_callbacks(monkeypatch):
    times = iter([0, 0, 0.5, 1.5])
    monkeypatch.setattr(time, "time", lambda: next(times))
    monkeypatch.setattr(time, "sleep", lambda *_: None)

    triggered = []

    def on_quest():
        triggered.append("quest")

    manager = StateManager({"quest": on_quest}, interval=0)
    manager.run(duration=1)

    assert triggered == ["quest"]
    assert manager.current_state == "quest"
