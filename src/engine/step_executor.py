from __future__ import annotations

from typing import Callable, Sequence

from src.game_state.feedback import watch_text


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
        if not success_markers:
            return True
        if watch_text(success_markers):
            return True
        attempts += 1
    return False
