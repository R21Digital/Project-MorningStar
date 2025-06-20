import os
import sys

sys.path.insert(0, os.path.abspath("."))

from src.main import main
from src.db.models import create_schema
from src.db.queries import select_best_quest

if "--init-db" in sys.argv:
    print("🗃️ Creating database schema...")
    create_schema()
    print("✅ Database initialized.")
    sys.exit(0)

quest = select_best_quest("Vornax")
if quest:
    print("✅ Loaded quest from DB:")
    print(f"ID: {quest[0]}, Title: {quest[1]}")
    print(f"Steps: {quest[2]}")
else:
    print("⚠️ No suitable quest found.")

if __name__ == "__main__":
    main()
