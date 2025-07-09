import logging
import os
import datetime
import csv
import sys
from pathlib import Path

DEFAULT_LOG_PATH = os.path.join("logs", "app.log")
DASHBOARD_LOG_PATH = os.path.join("logs", "dashboard_usage.log")
OCR_LOG_PATH = os.path.join("logs", "ocr_text.log")
SESSION_LOG_PATH = os.path.join("logs", "session.log")
PERFORMANCE_CSV_PATH = os.path.join("logs", "performance.csv")

logger = logging.getLogger("ms11")
if not logger.handlers:
    os.makedirs(os.path.dirname(DEFAULT_LOG_PATH), exist_ok=True)
    handler = logging.FileHandler(DEFAULT_LOG_PATH, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Configure a separate handler for dashboard usage if missing
    existing_files = {
        os.path.abspath(getattr(h, "baseFilename", ""))
        for h in logger.handlers
        if isinstance(h, logging.FileHandler)
    }
    dashboard_path = os.path.abspath(DASHBOARD_LOG_PATH)
    if dashboard_path not in existing_files:
        os.makedirs(os.path.dirname(DASHBOARD_LOG_PATH), exist_ok=True)
        dash_handler = logging.FileHandler(DASHBOARD_LOG_PATH, encoding="utf-8")
        dash_handler.setFormatter(formatter)
        logger.addHandler(dash_handler)


def log_info(message: str) -> None:
    """Print ``message`` with a timestamp to ``stderr``."""
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {message}", file=sys.stderr)


def save_screenshot(name: str = "screenshot") -> str:
    """Capture the current screen and save it under ``logs/screenshots``."""
    try:
        import cv2
        from PIL import ImageGrab
        import numpy as np
    except ImportError:
        log_info("OpenCV not installed, skipping screenshot.")
        return ""

    try:
        screenshot = ImageGrab.grab()
        screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        path = Path("logs/screenshots")
        path.mkdir(parents=True, exist_ok=True)
        filename = f"{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(str(path / filename), screenshot_np)
        log_info(f"Screenshot saved: {filename}")
        return str(path / filename)
    except Exception as e:  # pragma: no cover - best effort logging
        log_info(f"Screenshot failed: {e}")
        return ""


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

    If the file doesn't exist yet, a header row will be written first using the keys of ``stats``.
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

