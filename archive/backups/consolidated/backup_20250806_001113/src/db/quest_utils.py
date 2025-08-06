from .database import get_connection

def get_next_quest_in_chain(chain_id, current_step):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM quests
        WHERE chain_id = ? AND step_number = ?
    """, (chain_id, current_step + 1))
    result = cursor.fetchone()
    conn.close()
    return result

def log_progress(user_id, quest_id, completed=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO progress (user_id, quest_id, completed)
        VALUES (?, ?, ?)
    """, (user_id, quest_id, completed))
    conn.commit()
    conn.close()
