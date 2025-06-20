from src.db.models import create_schema
from src.db.queries import insert_quest

# Run schema creation (optional but safe)
create_schema()

# Add your test data here
insert_quest("Vornax", "Collect Bantha Hides", ["Go to Tatooine", "Hunt Banthas", "Return to Quest Giver"])
insert_quest("Vornax", "Explore Abandoned Base", ["Travel to Dantooine", "Enter the base", "Download data", "Escape"])
