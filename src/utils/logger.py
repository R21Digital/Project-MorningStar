import os
import datetime
import csv
import cv2

SCREENSHOT_DIR = os.path.join("logs", "screenshots")
OCR_LOG_PATH = os.path.join("logs", "ocr_text.log")
SESSION_LOG_PATH = os.path.join("logs", "session.log")
PERFORMANCE_CSV_PATH = os.path.join("logs", "performance.csv")


def save_screenshot(image, *, directory: str = SCREENSHOT_DIR) -> str:
    """Save ``image`` to ``directory`` with a timestamped filename."""
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(directory, f"{timestamp}.png")
    try:
        cv2.imwrite(path, image)
    except Exception as e:  # pragma: no cover - best effort logging
        print(f"[LOGGER] Failed to save screenshot: {e}")
    return path


def log_ocr_text(text: str, *, log_path: str = OCR_LOG_PATH) -> str:
    """Append ``text`` to ``log_path`` with a timestamp."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = datetime.datetime.now().isoformat()
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {text}\n")
    except Exception as e:  # pragma: no cover - best effort logging
        print(f"[LOGGER] Failed to log OCR text: {e}")
    return log_path


def log_event(message: str, *, log_path: str = SESSION_LOG_PATH) -> str:
    """Append ``message`` to ``log_path`` with a timestamp."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = datetime.datetime.now().isoformat()
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {message}\n")
    except Exception as e:  # pragma: no cover - best effort logging
        print(f"[LOGGER] Failed to log event: {e}")
    return log_path


def log_performance_summary(stats: dict, *, csv_path: str = PERFORMANCE_CSV_PATH) -> str:
    """Append a row of ``stats`` to ``csv_path``.

    If the file doesn't exist yet, a header row will be written first
    using the keys of ``stats``.
    """

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    file_exists = os.path.exists(csv_path)
    try:
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(stats.keys()))
            if not file_exists:
                writer.writeheader()
            writer.writerow(stats)
    except Exception as e:  # pragma: no cover - best effort logging
        print(f"[LOGGER] Failed to log performance summary: {e}")
    return csv_path
