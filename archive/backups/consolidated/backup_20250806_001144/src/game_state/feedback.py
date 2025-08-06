import time
from typing import Sequence


def watch_text(targets: Sequence[str] | str, timeout: float = 10, interval: float = 1.0) -> bool:
    """Return ``True`` if any of ``targets`` appears on screen within ``timeout`` seconds.

    ``targets`` may be a single string or a sequence of strings. The OCR text
    from :func:`src.vision.ocr.screen_text` is polled every ``interval``
    seconds.
    """
    if isinstance(targets, str):
        targets = [targets]
    targets_lower = [t.lower() for t in targets]

    from src.vision.ocr import screen_text

    end_time = time.time() + timeout
    while time.time() < end_time:
        text = screen_text()
        text_lower = text.lower()
        if any(t in text_lower for t in targets_lower):
            return True
        time.sleep(max(interval, 0))
    return False
