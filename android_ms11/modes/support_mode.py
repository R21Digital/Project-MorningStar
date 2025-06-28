"""Support mode implementation using core helpers."""

from android_ms11.core import follow_manager, support_ai, party_monitor


def run(session=None):
    """Entry point for support mode."""
    follow_manager.follow_target_loop()
    support_ai.assist_party()
    party_monitor.auto_join_party()
