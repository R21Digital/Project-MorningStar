from core.utils import render_progress_bar
from core.constants import STATUS_EMOJI_MAP, STATUS_UNKNOWN


def test_render_progress_bar_mixed():
    statuses = [
        STATUS_EMOJI_MAP["completed"],
        STATUS_EMOJI_MAP["in_progress"],
        STATUS_EMOJI_MAP["not_started"],
        STATUS_EMOJI_MAP["failed"],
        STATUS_UNKNOWN,
    ]
    out = render_progress_bar(statuses)
    expected_blocks = "█▓░▒░"
    expected = f"{expected_blocks} {''.join(statuses)}"
    assert out == expected


def test_render_progress_bar_empty():
    assert render_progress_bar([]) == ""
