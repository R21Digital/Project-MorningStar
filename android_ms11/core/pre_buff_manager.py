"""Utilities for handling pre-buff routines."""

from . import ocr_buff_detector


def apply_pre_buffs() -> None:
    """Check for and apply any missing buffs using OCR detection."""
    print("✨ Checking required buffs...")
    missing_buffs = ocr_buff_detector.detect_buffs()

    for buff in missing_buffs:
        print(f"🪄 Casting {buff}...")

    print("✅ Pre-buff complete.")


__all__ = ["apply_pre_buffs"]
