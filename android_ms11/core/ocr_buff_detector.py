"""Stub OCR buff detector."""

from __future__ import annotations


def detect_buffs() -> list[str]:
    """Return a list of missing buffs using OCR output."""
    print("📸 Capturing screen for OCR...")
    print("🔎 Running OCR to check active buffs...")
    missing = ["Might", "Shield", "Haste"]
    print(f"❌ Missing buffs detected: {', '.join(missing)}")
    return missing

__all__ = ["detect_buffs"]
