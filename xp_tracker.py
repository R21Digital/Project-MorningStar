"""XP Tracker wrapper for MorningStar (formerly MS11-Core)."""
import asyncio
from concurrent.futures import ThreadPoolExecutor

EXECUTOR = ThreadPoolExecutor()


def estimate_xp(action: str) -> int:
    """Estimate XP based on known actions."""
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
    """Simulate OCR-based XP reading."""
    print("[OCR] Scanning screen for XP value...")
    return 12345


async def track_xp(action=None, *, mode=None, use_ocr=False) -> int:
    """Estimate or read XP. Accepts ``action`` or ``mode`` as alias."""
    if action is None:
        action = mode

    if use_ocr:
        xp = read_xp_via_ocr()
        print(f"[XP] OCR-detected XP: {xp}")
    else:
        xp = await estimate_xp_async(action)
        print(f"[XP] Estimated XP from '{action}': +{xp}")
    return xp


def track_xp_sync(action=None, *, mode=None, use_ocr=False) -> int:
    """Synchronous wrapper for :func:`track_xp`."""
    return asyncio.run(track_xp(action=action, mode=mode, use_ocr=use_ocr))
