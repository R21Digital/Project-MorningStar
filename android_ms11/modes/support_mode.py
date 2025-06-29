"""Support mode implementation using core helpers."""

from android_ms11.core import (
    pre_buff_manager,
    follow_manager,
    assist_manager,
    party_manager,
)
from utils.license_hooks import requires_license


@requires_license
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

    # Perform pre-buff routine before starting the assist loop
    pre_buff_manager.apply_pre_buffs()

    loops = 0
    while True:
        party_manager.check_and_join_party()
        assist_manager.assist_leader(leader)
        follow_manager.follow_leader(leader)

        loops += 1
        if max_loops is not None and loops >= max_loops:
            break
