import logging
import os

DEFAULT_LOG_PATH = os.path.join("logs", "app.log")

logger = logging.getLogger("ms11")
if not logger.handlers:
    os.makedirs(os.path.dirname(DEFAULT_LOG_PATH), exist_ok=True)
    handler = logging.FileHandler(DEFAULT_LOG_PATH, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
