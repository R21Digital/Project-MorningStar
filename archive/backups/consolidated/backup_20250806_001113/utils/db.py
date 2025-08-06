import os


def get_db_connection():
    """Return a MongoDB connection using environment settings."""
    from pymongo import MongoClient  # Imported locally to avoid hard dependency

    uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.environ.get("MONGO_DB_NAME", "android_ms11")
    client = MongoClient(uri)
    return client[db_name]
