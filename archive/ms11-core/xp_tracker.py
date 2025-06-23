"""
XP Tracker module for Android MS11.
Combines OCR and heuristic estimation to track character progression.
"""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ThreadPoolExecutor allows XP estimation to run concurrently
EXECUTOR = ThreadPoolExecutor()


def estimate_xp(action: str) -> int:
    """
    Heuristic estimation of XP based on known actions.
    E.g., 'quest_complete', 'mob_kill', 'healing_tick'
    """
    xp_table = {
        'quest_complete': 450,
        'mob_kill': 120,
        'healing_tick': 30,
    }
    return xp_table.get(action, 0)


async def estimate_xp_async(action: str) -> int:
    """Estimate XP asynchronously using a thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(EXECUTOR, estimate_xp, action)


def read_xp_via_ocr() -> int:
    """
    Placeholder for OCR-based XP reading from screen region.
    To be replaced with image scanning logic using Tesseract or EasyOCR.
    """
    print("[OCR] Scanning screen for XP value...")
    # TODO: Add screenshot and OCR parsing logic
    return 12345  # Simulated XP


async def track_xp(action=None, use_ocr=False) -> int:
    """Hybrid tracker. Estimates XP from action or uses OCR."""
    if use_ocr:
        xp = read_xp_via_ocr()
        print(f"[XP] OCR-detected XP: {xp}")
    else:
        xp = await estimate_xp_async(action)
        print(f"[XP] Estimated XP from '{action}': +{xp}")
    return xp


def track_xp_sync(action=None, use_ocr=False) -> int:
    """Synchronous wrapper for :func:`track_xp`."""
    return asyncio.run(track_xp(action=action, use_ocr=use_ocr))
