import os
import sys
from types import SimpleNamespace, ModuleType

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.game_state.feedback import watch_text
from src.engine.step_executor import run_validated_step


def test_watch_text_detects(monkeypatch):
    calls = iter(["nope", "still nothing", "target found"])
    fake_module = ModuleType("src.vision.ocr")
    fake_module.screen_text = lambda *a, **k: next(calls)
    sys.modules["src.vision.ocr"] = fake_module
    assert watch_text("target", timeout=1, interval=0) is True


def test_run_validated_step_retries(monkeypatch):
    outputs = iter([False, True])
    monkeypatch.setattr(
        "src.engine.step_executor.watch_text", lambda *a, **k: next(outputs)
    )
    fake_mod = ModuleType("src.vision.ocr")
    fake_mod.screen_text = lambda *a, **k: "dummy"
    sys.modules["src.vision.ocr"] = fake_mod
    executed = []

    def step():
        executed.append(True)

    success = run_validated_step(step, ["ok"], max_retries=2)
    assert success is True
    assert len(executed) == 2
