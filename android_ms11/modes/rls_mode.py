"""Rare loot scanner mode implementation."""

from __future__ import annotations

from android_ms11.core import loot_session, ocr_loot_scanner, rls_logic


def run(config: dict | None = None, session=None) -> None:
    """Run the rare loot scanner using ``config`` options."""

    config = config or {}
    iterations = int(config.get("iterations", 1))

    print("[RLS] Starting rare loot scanner")
    for idx in range(iterations):
        target = rls_logic.choose_next_target()
        if not target:
            print("[RLS] No available targets; stopping scan")
            break

        name = target.get("name", "Unknown")
        print(f"[RLS] ({idx + 1}/{iterations}) Target: {name}")

        loot = ocr_loot_scanner.scan_for_loot()
        for item in loot:
            loot_session.log_loot(item)

    path = loot_session.export_log()
    print(f"[RLS] Loot log exported to {path}")

