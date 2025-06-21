import sqlite3

def initialize_database():
    conn = sqlite3.connect("morningstar.db")
    cursor = conn.cursor()

    # Drop and recreate progress table
    cursor.execute("DROP TABLE IF EXISTS progress;")
    cursor.execute("""
    CREATE TABLE progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        quest_id INTEGER,
        completed BOOLEAN
    );
    """)

    # Drop and recreate quests table
    cursor.execute("DROP TABLE IF EXISTS quests;")
    cursor.execute("""
    CREATE TABLE quests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chain_id INTEGER,
        step_number INTEGER,
        name TEXT,
        description TEXT
    );
    """)

    # ✅ Insert sample test quests
    sample_quests = [
        (1, 1, 'Start Quest', 'This is the first quest.'),
        (1, 2, 'Follow-up Quest', 'This is the second quest.'),
        (1, 3, 'Final Quest', 'This is the third quest.')
    ]

    cursor.executemany(
        "INSERT INTO quests (chain_id, step_number, name, description) VALUES (?, ?, ?, ?)",
        sample_quests
    )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
