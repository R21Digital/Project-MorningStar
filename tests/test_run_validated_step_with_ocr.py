import os
import sys
import time
from types import ModuleType


from src.engine.step_executor import run_validated_step
from src.engine.quest_executor import run_step_with_feedback


def test_run_validated_step_ocr_success(monkeypatch):
    fake_mod = ModuleType("src.vision.ocr")
    fake_mod.screen_text = lambda *a, **k: "mission success"
    monkeypatch.setitem(sys.modules, "src.vision.ocr", fake_mod)
    monkeypatch.setattr(time, "sleep", lambda x: None)
    executed = []

    def step():
        executed.append(True)

    assert run_validated_step(step, ["mission"], max_retries=1) is True
    assert len(executed) == 1


def test_run_validated_step_ocr_failure(monkeypatch):
    fake_mod = ModuleType("src.vision.ocr")
    fake_mod.screen_text = lambda *a, **k: "no match"
    monkeypatch.setitem(sys.modules, "src.vision.ocr", fake_mod)
    times = iter(range(100))
    monkeypatch.setattr(time, "time", lambda: next(times))
    monkeypatch.setattr(time, "sleep", lambda x: None)
    executed = []

    def step():
        executed.append(True)

    assert run_validated_step(step, ["expected"], max_retries=2) is False
    assert len(executed) == 2


def test_run_step_with_feedback_success(monkeypatch):
    fake_mod = ModuleType("src.vision.ocr")
    fake_mod.screen_text = lambda *a, **k: "intro mission started"
    monkeypatch.setitem(sys.modules, "src.vision.ocr", fake_mod)
    monkeypatch.setattr(time, "sleep", lambda x: None)
    executed = []
    monkeypatch.setattr("src.engine.quest_executor.execute_step", lambda s: executed.append(s))
    step = {"type": "quest", "action": "start", "success_texts": ["mission started"]}
    assert run_step_with_feedback(step) is True
    assert executed == [step]


def test_run_step_with_feedback_abort(monkeypatch):
    fake_mod = ModuleType("src.vision.ocr")
    fake_mod.screen_text = lambda *a, **k: "irrelevant"
    monkeypatch.setitem(sys.modules, "src.vision.ocr", fake_mod)
    times = iter(range(100))
    monkeypatch.setattr(time, "time", lambda: next(times))
    monkeypatch.setattr(time, "sleep", lambda x: None)
    executed = []
    monkeypatch.setattr("src.engine.quest_executor.execute_step", lambda s: executed.append(s))
    step = {"type": "quest", "action": "start", "success_texts": ["mission started"]}
    assert run_step_with_feedback(step) is False
    assert len(executed) == 3

