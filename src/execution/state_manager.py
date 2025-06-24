"""Simple state monitoring via OCR."""

from __future__ import annotations

import time
from typing import Callable, Mapping, MutableMapping

from src.vision import ocr


class StateManager:
    """Monitor on-screen text and trigger callbacks when keywords appear."""

    def __init__(
        self,
        callbacks: Mapping[str, Callable[[], None]],
        *,
        region=None,
        interval: float = 1.0,
    ) -> None:
        self.callbacks: MutableMapping[str, Callable[[], None]] = dict(callbacks)
        self.region = region
        self.interval = interval
        self._running = False

    def _check_once(self) -> None:
        image = ocr.capture_screen(region=self.region)
        text = ocr.extract_text(image).lower()
        for key, cb in list(self.callbacks.items()):
            if key.lower() in text:
                cb()

    def run(self, duration: float | None = None) -> None:
        """Run the monitoring loop optionally for ``duration`` seconds."""
        self._running = True
        end_time = time.time() + duration if duration is not None else None
        while self._running and (end_time is None or time.time() < end_time):
            self._check_once()
            time.sleep(max(self.interval, 0))

    def stop(self) -> None:
        """Stop the monitoring loop."""
        self._running = False
