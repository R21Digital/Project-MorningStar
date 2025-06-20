from .database import get_connection

def create_schema():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quest_id TEXT,
        title TEXT,
        steps TEXT,
        source_type TEXT,
        validated INTEGER,
        fallback_rank INTEGER
    )
    """)
    conn.commit()
    conn.close()
