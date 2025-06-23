"""Utility for seeding the database with example quests."""

from src.db.models import create_schema
from src.db.queries import insert_quest


if __name__ == "__main__":
    # Create the tables if they don't exist
    create_schema()

    # Insert some sample quests for development/testing
    insert_quest(
        "Vornax",
        "Collect Bantha Hides",
        ["Go to Tatooine", "Hunt Banthas", "Return to Quest Giver"],
    )
    insert_quest(
        "Vornax",
        "Explore Abandoned Base",
        ["Travel to Dantooine", "Enter the base", "Download data", "Escape"],
    )
