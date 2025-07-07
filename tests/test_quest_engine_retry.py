from core import quest_engine

def test_log_retry_creates_csv(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    log_file = log_dir / "retry_log.txt"
    monkeypatch.setattr(quest_engine, "RETRY_LOG_PATH", str(log_file))

    quest_engine.log_retry("step1", 1, "boom")

    assert log_dir.is_dir()
    assert log_file.exists()
    line = log_file.read_text(encoding="utf-8").strip()
    parts = line.split(', ')
    assert len(parts) == 4
    assert parts[1] == "step1"
    assert parts[2] == "1"
    assert parts[3] == "boom"
