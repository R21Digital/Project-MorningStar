import threading
import time
from queue import Queue

from src.vision.ocr import screen_text


class WhisperMonitor(threading.Thread):
    """Detect on-screen whispers and add them to a queue."""

    def __init__(self, message_queue: Queue, interval: float = 2.0):
        super().__init__(daemon=True)
        self.queue = message_queue
        self.interval = interval
        self.running = True
        self.last_line = ""

    def run(self) -> None:  # pragma: no cover - thread loop
        while self.running:
            text = screen_text()
            for line in text.splitlines():
                if "whispers" in line.lower() and line != self.last_line:
                    self.last_line = line
                    self.queue.put(line.strip())
            time.sleep(self.interval)

