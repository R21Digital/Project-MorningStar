"""Combat helper functions."""


def engage_targets(target_name: str, count: int = 1) -> bool:
    """Simulate fighting a number of targets."""
    print(f"[COMBAT] Engaging {count}x {target_name}")
    # Placeholder for combat routine
    # Future: could hook into pixel detection or keyboard automation
    for i in range(count):
        print(f"  -> Defeated {target_name} #{i+1}")
    return True
