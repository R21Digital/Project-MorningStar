import datetime
import os

# Directory for logs
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
# File path for step journal
log_path = os.path.join(log_dir, "step_journal.log")


def log_step(success: bool, ocr_text: str | None = None) -> None:
    """Append a journal entry recording ``success`` and ``ocr_text``."""
    timestamp = datetime.datetime.now().isoformat()
    with open(log_path, "a", encoding="utf-8") as f:
        ocr_display = ocr_text or ""
        f.write(f"{timestamp} | success={success} | ocr={ocr_display}\n")
