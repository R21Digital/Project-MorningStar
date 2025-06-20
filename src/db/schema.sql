CREATE TABLE IF NOT EXISTS quests (
    quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    character TEXT,
    title TEXT,
    steps TEXT,
    validated INTEGER DEFAULT 1,
    source_type TEXT DEFAULT 'official',
    fallback_rank INTEGER DEFAULT 1
);
