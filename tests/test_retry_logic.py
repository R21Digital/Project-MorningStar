import os
import core.quest_engine as quest_engine
import pytest


@pytest.fixture(autouse=True)
def clear_retry_log():
    """Remove the retry log before each test."""
    path = quest_engine.RETRY_LOG_PATH
    if os.path.exists(path):
        os.remove(path)
    yield
    if os.path.exists(path):
        os.remove(path)


def _read_log_lines():
    path = quest_engine.RETRY_LOG_PATH
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return [line for line in fh.read().splitlines() if line]


def test_success_first_try(monkeypatch):
    calls = []

    def fake_step(step):
        calls.append(step)
        return True

    monkeypatch.setattr(quest_engine, "execute_quest_step", fake_step)

    result = quest_engine.execute_with_retry("step", max_retries=3)

    assert result is True
    assert len(calls) == 1
    assert _read_log_lines() == []


def test_fail_once_then_success(monkeypatch):
    calls = []

    def fake_step(step):
        calls.append(step)
        return len(calls) >= 2

    monkeypatch.setattr(quest_engine, "execute_quest_step", fake_step)

    result = quest_engine.execute_with_retry("step", max_retries=3)

    assert result is True
    assert len(calls) == 2
    assert len(_read_log_lines()) == 1


def test_always_fail(monkeypatch):
    calls = []

    def fake_step(step):
        calls.append(step)
        return False

    monkeypatch.setattr(quest_engine, "execute_quest_step", fake_step)

    result = quest_engine.execute_with_retry("step", max_retries=3)

    assert result is False
    assert len(calls) == 3
    assert len(_read_log_lines()) == 3


def test_always_fail_with_fallback(monkeypatch):
    """Fallback should run once after all retries fail."""
    step_calls = []
    fallback_calls = []

    def fake_step(step):
        step_calls.append(step)
        return False

    def fake_fallback(step):
        fallback_calls.append(step)
        return True

    monkeypatch.setattr(quest_engine, "execute_quest_step", fake_step)

    result = quest_engine.execute_with_retry(
        "step", max_retries=3, fallback=fake_fallback
    )

    assert result is True
    assert len(step_calls) == 3
    assert fallback_calls == ["step"]
