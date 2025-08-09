from __future__ import annotations

from typing import Callable, Sequence

from src.game_state.feedback import watch_text
from src.logging_utils import journal


def run_validated_step(
    step_fn: Callable[[], None],
    success_markers: Sequence[str] | None = None,
    max_retries: int = 3,
) -> bool:
    """Execute ``step_fn`` and confirm success via on-screen text.

    ``success_markers`` is a list of expected substrings that should appear on
    the screen after executing the step. The step will be retried up to
    ``max_retries`` times if the text is not detected.
    """
    attempts = 0
    while attempts < max_retries:
        step_fn()
        # Import here to avoid heavy dependencies during module import
        from src.vision.ocr import screen_text
        if not success_markers:
            journal.log_step(True, None)
            return True

        success = watch_text(success_markers)
        text = screen_text()
        journal.log_step(success, text)
        if success:
            return True
        attempts += 1
    return False
