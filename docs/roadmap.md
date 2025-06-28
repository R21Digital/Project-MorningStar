# Project Roadmap

Android MS11 aims to be an advanced interface assistant for long-session open-world automation. The project is maintained by **Project Galactic Beholder** and builds on the archived MS11-Core code.

## Phases

### Questing 🚧
Modules focus on selecting and running quests. Key pieces include:
- `quest_selector.py` and `quest_executor.py` for quest flow
- `quest_engine.py` plus movement helpers

Todo work recorded in `NOTES.md` includes scoring improvements and fleshing out step execution. Individual files also contain placeholders, such as the UI hook in `src/execution/dialogue.py` and the walking logic in `src/movement/movement_profiles.py`.

### Support 🚧
Support scripts provide in-game assistance such as healing or training runs. Examples are `mode_medic.py`, `mode_buff_by_tell.py`, `trainer_seeker.py`, and travel helpers under `modules/travel`. XP tracking via `xp_manager.py`, `xp_session.py`, and `xp_tracker.py` is considered stable.

### AI Interaction 🔮
Early AI features integrate with Discord and text generation. `discord_relay.py` supplies placeholder AI replies while `story_generator.py` uses LangChain to generate short stories. More complete conversational loops are planned.

Status markers used above:
- ✅ stable
- 🚧 in development
- 🔮 planned
