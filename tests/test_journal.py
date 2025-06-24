import os
import sys
from types import ModuleType

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine.step_executor import run_validated_step
from src.logging import journal


def test_run_validated_step_logs_success(monkeypatch, tmp_path):
    log_file = tmp_path / "journal.log"
    monkeypatch.setattr(journal, "log_path", str(log_file))

    fake_mod = ModuleType("src.vision.ocr")
    fake_mod.screen_text = lambda *a, **k: "success text"
    monkeypatch.setitem(sys.modules, "src.vision.ocr", fake_mod)
    monkeypatch.setattr("src.engine.step_executor.watch_text", lambda *a, **k: True)

    def step():
        pass

    assert run_validated_step(step, ["success"]) is True
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "success=True" in content
    assert "success text" in content


def test_run_validated_step_logs_failure(monkeypatch, tmp_path):
    log_file = tmp_path / "journal.log"
    monkeypatch.setattr(journal, "log_path", str(log_file))

    fake_mod = ModuleType("src.vision.ocr")
    fake_mod.screen_text = lambda *a, **k: "fail text"
    monkeypatch.setitem(sys.modules, "src.vision.ocr", fake_mod)
    monkeypatch.setattr("src.engine.step_executor.watch_text", lambda *a, **k: False)

    def step():
        pass

    assert run_validated_step(step, ["expected"], max_retries=1) is False
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "success=False" in content
    assert "fail text" in content
