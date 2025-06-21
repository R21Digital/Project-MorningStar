import sqlite3
import os

# Define database path
DB_FILENAME = "morningstar.db"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", DB_FILENAME)

def get_connection():
    """
    Opens a new connection to the SQLite database.
    You must call .close() on the returned connection when done.
    """
    conn = sqlite3.connect(DB_PATH)
    return conn

def get_db():
    """
    Returns a connection with row_factory enabled for named access.
    Useful for scripts that need dict-like row access.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
