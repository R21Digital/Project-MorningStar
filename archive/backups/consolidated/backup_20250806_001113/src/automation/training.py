def train_with_npc(step: dict):
    npc = step.get("npc", "Trainer")
    print(f"[TRAINING] Learning new abilities from {npc}")
