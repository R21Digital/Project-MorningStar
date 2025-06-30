import os
import sys

sys.path.insert(0, os.path.abspath("."))

from src.main import main
from src.db.models import create_schema
from src.db.queries import select_best_quest
from utils.logger import logger

if "--init-db" in sys.argv:
    logger.info("🗃️ Creating database schema...")
    create_schema()
    logger.info("✅ Database initialized.")
    sys.exit(0)

quest = select_best_quest("Vornax")
if quest:
    logger.info("✅ Loaded quest from DB:")
    logger.info("ID: %s, Title: %s", quest[0], quest[1])
    logger.info("Steps: %s", quest[2])
else:
    logger.info("⚠️ No suitable quest found.")

if __name__ == "__main__":
    main()
