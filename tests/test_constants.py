import core


def test_constants_values():
    assert core.STATUS_COMPLETED == "✅ Completed"
    assert core.STATUS_FAILED == "❌ Failed"
    assert core.STATUS_IN_PROGRESS == "⏳ In Progress"
    assert core.STATUS_UNKNOWN == "❓ Unknown"

