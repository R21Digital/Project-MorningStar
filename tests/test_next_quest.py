from src.db.quest_utils import get_next_quest_in_chain

chain_id = 1
current_step = 1  # adjust based on your test data

next_quest = get_next_quest_in_chain(chain_id, current_step)

if next_quest:
    print("✅ Next quest found:", next_quest)
else:
    print("❌ No next quest found.")
