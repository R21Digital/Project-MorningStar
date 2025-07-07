import core.legacy_dashboard as legacy_dashboard
import core.quest_state as qs


def test_display_legacy_progress(capsys):
    steps = [
        {"id": 1, "title": "First", "completed": True},
        {"id": 2, "title": "Second"},
    ]
    legacy_dashboard.display_legacy_progress(steps)
    captured = capsys.readouterr()
    assert qs.STATUS_COMPLETED in captured.out
    assert qs.STATUS_NOT_STARTED in captured.out


def test_enriched_status_output(capsys):
    steps = [
        {"id": 1, "title": "First", "completed": True},
        {"id": 2, "title": "Second", "failed": True},
        {"id": 3, "title": "Third", "in_progress": True},
    ]
    legacy_dashboard.display_legacy_progress(steps)
    captured = capsys.readouterr()
    assert qs.STATUS_COMPLETED in captured.out
    assert qs.STATUS_FAILED in captured.out
    assert qs.STATUS_IN_PROGRESS in captured.out
