import os
import datetime
import cv2

SCREENSHOT_DIR = os.path.join("logs", "screenshots")
OCR_LOG_PATH = os.path.join("logs", "ocr_text.log")


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
