"""Support mode implementation using core helpers."""

from android_ms11.core import follow_manager, support_ai, party_monitor


def run(session=None, max_loops: int | None = None) -> None:
    """Entry point for support mode.

    Parameters
    ----------
    session : optional
        Active session object providing configuration. May be ``None``.
    max_loops : int, optional
        Number of cycles to run the support routines. If ``None``, run
        indefinitely.
    """

    cfg = getattr(session, "config", {})
    leader = cfg.get("support_leader_name", "LeaderBot")

    print(f"[SUPPORT] Assisting leader {leader}")

    loops = 0
    while True:
        follow_manager.follow_target_loop()
        support_ai.assist_party()
        party_monitor.auto_join_party()

        loops += 1
        if max_loops is not None and loops >= max_loops:
            break
