from src.db.models import create_schema
from src.db.queries import insert_quest


def main() -> None:
    """Initialize the schema and insert sample quests."""

    # Run schema creation (optional but safe)
    create_schema()

    # Add your test data here
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


if __name__ == "__main__":
    main()
