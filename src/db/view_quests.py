from .database import get_connection
import json

def view_all_quests():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quests")
    rows = cursor.fetchall()

    if not rows:
        print("⚠️ No quests found in the database.")
    else:
        print(f"✅ Retrieved {len(rows)} quest(s):\n")
        for row in rows:
            id, character, title, steps, source_type, validated, fallback_rank, chain_id, step_number = row
            print(f"🧾 Quest ID: {id}")
            print(f"👤 Character: {character}")
            print(f"📌 Title: {title}")
            print(f"📜 Steps: {json.loads(steps)}")
            print(f"📦 Source Type: {source_type}")
            print(f"✔️ Validated: {'Yes' if validated else 'No'}")
            print(f"🔢 Fallback Rank: {fallback_rank}")
            print(f"🔗 Chain ID: {chain_id}")
            print(f"🔢 Step #: {step_number}")
            print("—" * 30)

    conn.close()

if __name__ == "__main__":
    view_all_quests()
