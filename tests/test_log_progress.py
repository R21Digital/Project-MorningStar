import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.quest_utils import log_progress

# Example: PlayerX completed quest 3
log_progress("PlayerX", 3, completed=True)
print("✅ Progress logged.")
