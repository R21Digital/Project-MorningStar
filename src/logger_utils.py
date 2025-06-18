"""Logging utilities for MorningStar."""
import os
from typing import List

DEFAULT_LOG_PATH = "ms.log"

def read_logs(path: str = DEFAULT_LOG_PATH, num_lines: int = 5) -> List[str]:
    """Return the last ``num_lines`` lines from ``path``.

    If the file does not exist, an empty list is returned.
    """
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    return [line.rstrip("\n") for line in lines[-num_lines:]]
