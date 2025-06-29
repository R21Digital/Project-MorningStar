"""Rare loot scanner mode implementation."""

from __future__ import annotations

from android_ms11.core import loot_session, ocr_loot_scanner, rls_logic
from utils.license_hooks import requires_license


@requires_license
def run(
    config: dict | None = None,
    session=None,
    *,
    loop_count: int | None = None,
) -> None:
    """Run the rare loot scanner using ``config`` options.

    Parameters
    ----------
    config:
        Optional configuration mapping. When provided, the ``iterations`` value
        controls the number of scanning loops.
    session:
        Unused session object placeholder for API parity with other modes.
    loop_count:
        Explicit iteration count which overrides the ``iterations`` value in the
        ``config`` mapping. This parameter allows tests or callers to bypass the
        configuration file and specify a loop count directly.
    """

    config = config or {}
    if loop_count is not None:
        iterations = int(loop_count)
    else:
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

