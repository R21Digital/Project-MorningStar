# Project-MorningStar
Project MorningStar (MS11-Core) is an advanced interface assistant for long-session open-world automation. Inspired by player realism, faction-based systems, and strategic progression loops.

## Lore
In the world of **Argent**, legendary guilds compete to recover the fragments of the star "Morning". Adventurers take on perilous quests to gain favor with their faction and earn the power needed to reunite the shards. MorningStar provides the tooling to script and observe these journeys, whether you are tracking combat victories or following a sprawling roleplay narrative.

## Basic Usage
Install the dependencies (the requirements file lives under `ms11-core/`) and then import the modules you need:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r ms11-core/requirements.txt
```
Generate a short story or track XP in your automation scripts:
```python
from src.story_generator import generate_story
from xp_manager import XPManager

print(generate_story("A rogue explores the ruins"))

xp = XPManager("Ezra")
xp.record_action("quest_complete")
xp.end_session()
```
The modules under `src/` offer simple building blocks that you can integrate into larger systems.

To try the questing demo, simply run:
```bash
python main.py
```
