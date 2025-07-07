import core.quest_state as qs


def test_get_step_status():
    assert qs.get_step_status({"id": "1", "completed": True}) == qs.STATUS_COMPLETED
    assert qs.get_step_status({"id": "2", "failed": True}) == qs.STATUS_FAILED
    assert qs.get_step_status({"id": "3", "in_progress": True}) == qs.STATUS_IN_PROGRESS
    assert qs.get_step_status({"id": "4", "skipped": True}) == qs.STATUS_NOT_STARTED


def test_get_step_status_returns_not_started():
    from core.quest_state import get_step_status, STATUS_NOT_STARTED

    assert get_step_status({}) == STATUS_NOT_STARTED
    assert get_step_status(None) == STATUS_NOT_STARTED
    assert get_step_status({"id": "5"}) == STATUS_NOT_STARTED

