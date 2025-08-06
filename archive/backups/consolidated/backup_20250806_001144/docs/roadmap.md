# Project Roadmap

Android MS11 aims to be an advanced interface assistant for long-session open-world automation. The project is maintained by **Project Galactic Beholder** and builds on the archived MS11-Core code.


## Phase 1 Features

The initial release focuses on reliable quest execution and basic session tracking.

- `quest_selector.py` and `quest_executor.py` provide the quest flow logic.
- Movement helpers and the step executor automate travel between objectives.
- `xp_manager.py`, `xp_session.py`, and `xp_tracker.py` record XP and credit gains.

Todo work recorded in `NOTES.md` includes improving scoring and fleshing out step execution. Some modules still contain placeholders &ndash; for example the UI hook in `src/execution/dialogue.py` and walking logic in `src/movement/movement_profiles.py`.

## Phase 2 Plans

The next phase expands support functionality. Planned work includes:

- Finishing healer and buff modes such as `medic_mode.py` and `whisper_mode.py`.
- Adding trainer automation via `trainer_seeker.py` and the travel helpers under `modules/travel`.
- Integrating profession leveling data from `profession_logic` modules.

## Phase 3 Vision

Longer term development aims to incorporate AI-driven interaction. Early pieces already exist:

- `discord_relay.py` can forward whispers to Discord with optional AI replies.
- `story_generator.py` uses LangChain to produce short stories.

Future work will expand conversational loops and add smarter behavior modules.

Status markers used above:
- ✅ stable
- 🚧 in development
- 🔮 planned
