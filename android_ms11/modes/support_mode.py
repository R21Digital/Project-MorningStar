"""Support mode implementation using core helpers."""

from android_ms11.core import follow_manager, support_ai, party_monitor


def run(session=None, max_loops: int = 1) -> None:
    """Entry point for support mode.

    Parameters
    ----------
    session : optional
        Active session object providing configuration. May be ``None``.
    max_loops : int, optional
        Number of cycles to run the support routines.
    """

    cfg = getattr(session, "config", {})
    leader = cfg.get("support_leader_name", "LeaderBot")

    print(f"[SUPPORT] Assisting leader {leader}")

    for _ in range(max_loops):
        follow_manager.follow_target_loop()
        support_ai.assist_party()
        party_monitor.auto_join_party()
