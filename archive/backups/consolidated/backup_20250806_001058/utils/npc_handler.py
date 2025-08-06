"""Basic NPC interaction helpers."""


def interact_with_npc(npc_name: str) -> bool:
    """Simulate interacting with an NPC."""
    print(f"[NPC] Interacting with {npc_name}")
    # Simulated result of interaction
    # Future: use OCR/image detection to validate interaction
    return True


def interact_with_trainer(trainer_name: str, skill: str) -> bool:
    """Simulate training with a profession trainer."""
    print(f"[TRAINER] Talking to {trainer_name}")
    interact_with_npc(trainer_name)
    print(f"[TRAINER] {trainer_name} teaches you {skill}")
    return True
