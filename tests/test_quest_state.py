import core.quest_state as qs


def test_parse_quest_log_strips_and_filters_lines():
    text = "\nStep one\n\n  Step two  \nStep three\n"
    assert qs.parse_quest_log(text) == ["Step one", "Step two", "Step three"]


def test_is_step_completed_case_insensitive():
    text = "Gather items\nReturn to Base\n"
    assert qs.is_step_completed(text, "return to base") is True
    assert qs.is_step_completed(text, "missing step") is False


def test_read_saved_quest_log(tmp_path, monkeypatch):
    log_file = tmp_path / "logs" / "quest_log.txt"
    log_file.parent.mkdir()
    log_file.write_text("\n1\n 2 \n3\n")
    monkeypatch.chdir(tmp_path)
    assert qs.read_saved_quest_log() == ["1", "2", "3"]


def test_get_step_status(tmp_path, monkeypatch):
    log_file = tmp_path / "logs" / "quest_log.txt"
    log_file.parent.mkdir()
    log_file.write_text("1\n")
    monkeypatch.chdir(tmp_path)

    step_completed = {"id": "1"}
    step_active = {"id": "2", "active": True}
    step_pending = {"id": "3"}

    assert qs.get_step_status(step_completed) == "✅ Completed"
    assert qs.get_step_status(step_active) == "🕒 Active"
    assert qs.get_step_status(step_pending) == "⏭️ Pending"
