from __future__ import annotations

import time
from typing import Callable, Mapping, Any

from utils.logging_utils import log_event


def run_repeating_mode(
    mode: str,
    runner: Callable[[], Mapping[str, Any]],
    rest_time: int = 10,
) -> None:
    """Run ``runner`` continuously with a rest between iterations."""
    log_event(f"Repeat mode activated for: {mode}")
    while True:
        runner()
        log_event(
            f"Mode {mode} completed. Resting {rest_time} seconds before restarting..."
        )
        time.sleep(rest_time)


__all__ = ["run_repeating_mode"]
