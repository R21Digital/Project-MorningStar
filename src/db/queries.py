import json
from .database import get_connection

def select_best_quest(character_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    # Prioritize official, validated quests
    cursor.execute("""
        SELECT id, title, steps
        FROM quests
        WHERE validated = 1 AND source_type = 'official' AND character = ?
        ORDER BY fallback_rank ASC
        LIMIT 1
    """, (character_name,))

    result = cursor.fetchone()
    conn.close()
    return result


def insert_quest(character, title, steps):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO quests (character, title, steps, validated, source_type, fallback_rank)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (character, title, json.dumps(steps), 1, 'official', 1))

    conn.commit()
    conn.close()


def insert_note(character: str, topic: str, content: str):
    """Insert a note for a given character."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
            INSERT INTO notes (character, topic, content)
            VALUES (?, ?, ?)
        """,
        (character, topic, content),
    )

    conn.commit()
    conn.close()


def get_notes(character: str, topic: str | None = None):
    """Retrieve notes for a character, optionally filtered by topic."""
    conn = get_connection()
    cursor = conn.cursor()

    if topic is None:
        cursor.execute(
            """
                SELECT id, character, topic, content, created_at
                FROM notes
                WHERE character = ?
                ORDER BY created_at DESC
            """,
            (character,),
        )
    else:
        cursor.execute(
            """
                SELECT id, character, topic, content, created_at
                FROM notes
                WHERE character = ? AND topic = ?
                ORDER BY created_at DESC
            """,
            (character, topic),
        )

    rows = cursor.fetchall()
    conn.close()
    return rows
