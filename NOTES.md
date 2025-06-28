# Android MS11 Notes

## Current Features
- **XP tracking**: `xp_manager.py`, `xp_session.py`, and `xp_tracker.py` allow recording actions and saving session logs.
- **Mode runner**: `main.py` and `runner.py` provide CLI entry points to launch different automation modes.
- **Quest database**: `src/db` holds SQLite schema, quest insertion helpers, and utilities for viewing quests.
- **Training helpers**: `utils/load_trainers.py`, `trainer_visit.py`, and the `find_trainer.py` CLI load trainer data and automate visits.
- **Trainer navigator**: `scripts/logic/trainer_navigator.py` lists nearby trainers and records visits in `logs/training_log.txt`. It can also write JSON lines to `logs/training.json` using data from `data/trainers.json`.

## Modules Needing Work
- `quest_selector.py` – loads legacy quests and DB entries with filtering support; still needs scoring improvements.
- `quest_executor.py` – provides `execute_quest()` placeholder; expand with automation steps.
- `utils/source_verifier.py` – provides helpers for verifying quest data and detecting file changes.

## Planned Improvements
- Implement quest selection logic using user preferences and DB rankings.
- Flesh out quest execution with step-by-step automation.
- Verify and import external quest data safely.
- Expand mode scripts with real game macro calls and error handling.
