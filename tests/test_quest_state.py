import core.quest_state as qs


def test_parse_quest_log_strips_and_filters_lines():
    text = "\nStep one\n\n  Step two  \nStep three\n"
    assert qs.parse_quest_log(text) == ["Step one", "Step two", "Step three"]


def test_is_step_completed_case_insensitive():
    text = "Gather items\nReturn to Base\n"
    assert qs.is_step_completed(text, "return to base") is True
    assert qs.is_step_completed(text, "missing step") is False
