import core.quest_state as qs
from core.constants import STATUS_EMOJI_MAP


def test_get_step_status():
    assert qs.get_step_status({"id": "1", "completed": True}) == STATUS_EMOJI_MAP["completed"]
    assert qs.get_step_status({"id": "2", "failed": True}) == STATUS_EMOJI_MAP["failed"]
    assert qs.get_step_status({"id": "3", "in_progress": True}) == STATUS_EMOJI_MAP["in_progress"]
    assert qs.get_step_status({"id": "4", "skipped": True}) == STATUS_EMOJI_MAP["not_started"]


def test_get_step_status_returns_not_started():
    from core.quest_state import get_step_status

    assert get_step_status({}) == STATUS_EMOJI_MAP["not_started"]
    assert get_step_status(None) == STATUS_EMOJI_MAP["not_started"]
    assert get_step_status({"id": "5"}) == STATUS_EMOJI_MAP["not_started"]

