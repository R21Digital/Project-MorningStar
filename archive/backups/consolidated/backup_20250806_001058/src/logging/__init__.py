"""
Simple logging module for MS11.
"""

import logging
from typing import Optional

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get a logger with the specified name."""
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger

# Create a default logger
default_logger = get_logger("ms11") 