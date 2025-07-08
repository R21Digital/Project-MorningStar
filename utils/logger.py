import logging
import os

DEFAULT_LOG_PATH = os.path.join("logs", "app.log")
DASHBOARD_LOG_PATH = os.path.join("logs", "dashboard_usage.log")

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
    """Log ``message`` at INFO level to all configured handlers."""
    logger.info(message)

