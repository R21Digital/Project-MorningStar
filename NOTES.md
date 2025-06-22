# Android MS11 Notes

## Current Features
- **XP tracking**: `xp_manager.py`, `xp_session.py`, and `xp_tracker.py` allow recording actions and saving session logs.
- **Mode runner**: `main.py` and `runner.py` provide CLI entry points to launch different automation modes.
- **Quest database**: `src/db` holds SQLite schema, quest insertion helpers, and utilities for viewing quests.

## Modules Needing Work
- `quest_selector.py` – basic selection helpers implemented.
- `quest_executor.py` – stub execution logic added.
- `utils/source_verifier.py` – validates and sanitizes external quest data.

## Planned Improvements
- Implement quest selection logic using user preferences and DB rankings.
- Flesh out quest execution with step-by-step automation.
- Verify and import external quest data safely.
- Expand mode scripts with real game macro calls and error handling.
