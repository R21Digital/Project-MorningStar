"""Estimate total XP rewards for quests."""


def estimate_quest_xp(step_count: int) -> int:
    """Return a rough XP estimate based on the number of quest steps."""
    return step_count * 100
