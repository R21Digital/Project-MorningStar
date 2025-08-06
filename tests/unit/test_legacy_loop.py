import types
import core.legacy_loop as legacy_loop


def test_run_full_legacy_quest_executes_all(monkeypatch):
    steps = [
        {"id": "1", "description": "first"},
        {"id": "2", "description": "second"},
    ]
    executed = []

    monkeypatch.setattr(legacy_loop, "load_legacy_steps", lambda: steps)
    monkeypatch.setattr(legacy_loop, "read_quest_log", lambda: [])
    monkeypatch.setattr(
        legacy_loop,
        "execute_with_retry",
        lambda step, max_retries=3: executed.append(step["id"]) or True,
    )
    monkeypatch.setattr(legacy_loop, "time", types.SimpleNamespace(sleep=lambda x: None))

    legacy_loop.run_full_legacy_quest()
    assert executed == ["1", "2"]


def test_run_full_legacy_quest_stops_on_failure(monkeypatch):
    steps = [
        {"id": "1", "description": "first"},
        {"id": "2", "description": "second"},
        {"id": "3", "description": "third"},
    ]
    executed = []

    monkeypatch.setattr(legacy_loop, "load_legacy_steps", lambda: steps)
    monkeypatch.setattr(legacy_loop, "read_quest_log", lambda: [])

    def exec_step(step):
        executed.append(step["id"])
        return step["id"] != "2"

    monkeypatch.setattr(legacy_loop, "execute_with_retry", lambda step, max_retries=3: exec_step(step))
    monkeypatch.setattr(legacy_loop, "time", types.SimpleNamespace(sleep=lambda x: None))

    legacy_loop.run_full_legacy_quest()
    assert executed == ["1", "2"]
