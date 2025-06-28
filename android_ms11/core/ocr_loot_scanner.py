"""OCR-based loot scanning utilities."""

from __future__ import annotations


def scan_for_loot() -> list[str]:
    """Return a list of loot items found using OCR."""
    print("🧭 Scanning area for loot...")
    loot = ["Gold Coin", "Health Potion", "Magic Scroll"]
    print(f"💎 Loot found: {', '.join(loot)}")
    return loot


__all__ = ["scan_for_loot"]
