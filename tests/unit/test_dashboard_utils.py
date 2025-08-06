from core.dashboard_utils import (
    group_quests_by_category,
    summarize_status_counts,
    calculate_completion_percentage,
)
from core.constants import STATUS_EMOJI_MAP


def test_group_quests_by_category_empty():
    assert group_quests_by_category() == {}


def test_summarize_status_counts():
    statuses = [
        STATUS_EMOJI_MAP["completed"],
        STATUS_EMOJI_MAP["completed"],
        STATUS_EMOJI_MAP["in_progress"],
    ]
    counts = summarize_status_counts(statuses)
    assert counts[STATUS_EMOJI_MAP["completed"]] == 2
    assert counts[STATUS_EMOJI_MAP["in_progress"]] == 1


def test_calculate_completion_percentage():
    counts = {
        STATUS_EMOJI_MAP["completed"]: 3,
        STATUS_EMOJI_MAP["in_progress"]: 1,
    }
    assert calculate_completion_percentage(counts) == 75.0
