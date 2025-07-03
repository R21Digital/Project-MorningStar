import core.quest_engine as quest_engine


def test_execute_with_retry_retries_and_logs(monkeypatch):
    calls = []
    def fake_step(step):
        calls.append(step)
        return len(calls) >= 3

    monkeypatch.setattr(quest_engine, "execute_quest_step", fake_step)
    log_calls = []
    def fake_log(step_id, attempt, error):
        log_calls.append((step_id, attempt, str(error)))
    monkeypatch.setattr(quest_engine, "log_retry", fake_log)

    result = quest_engine.execute_with_retry("step", max_retries=5)

    assert result is True
    assert len(calls) == 3
    assert log_calls == [
        ("step", 1, "false result"),
        ("step", 2, "false result"),
    ]
