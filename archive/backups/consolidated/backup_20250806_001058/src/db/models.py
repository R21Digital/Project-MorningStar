from .database import get_connection

def create_schema():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character TEXT,
        title TEXT NOT NULL,
        steps TEXT NOT NULL,
        chain_id TEXT,                 -- For referencing quest chains
        step_number INTEGER,          -- Position within a chain
        validated BOOLEAN DEFAULT 0,
        source_type TEXT DEFAULT 'custom',
        fallback_rank INTEGER DEFAULT 99,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character TEXT,
        mode TEXT,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        xp_gained INTEGER DEFAULT 0,
        credits_gained INTEGER DEFAULT 0,
        notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character TEXT,
        topic TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database schema created.")
