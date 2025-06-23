# Android MS11
Version: 0.1.0
Android MS11 is an advanced interface assistant for long-session open-world automation maintained by **Project Galatic Beholder**.

The original MS11-Core implementation has been archived under `archive/ms11-core` to preserve legacy code.

## Lore
In the world of **Argent**, legendary guilds compete to recover ancient relics. Adventurers take on perilous quests to gain favor with their faction and earn the power needed to reunite the shards. Android MS11 provides the tooling to script and observe these journeys, whether you are tracking combat victories or following a sprawling roleplay narrative.

## Basic Usage
Install the dependencies and then import the modules you need.
The `requirements.txt` file now includes `requests>=2.0`:
```bash
pip install -r requirements.txt
```
Generate a short story or track XP in your automation scripts:
```python
from src.story_generator import generate_story
from src.xp_manager import XPManager

print(generate_story("A rogue explores the ruins"))

xp = XPManager("Ezra")
xp.record_action("quest_complete")
xp.end_session()
```
The modules under `src/` offer simple building blocks that you can integrate into larger systems.

## Working with Quests

Three lightweight helpers provide a basic quest pipeline:

- `quest_selector.select_quest` picks the next mission for a character.
- `quest_executor.execute_quest` iterates through the quest steps.
- `utils.source_verifier.verify_source` checks that the data you loaded is trustworthy.

```python
from src.quest_selector import select_quest
from src.quest_executor import execute_quest
from utils.source_verifier import verify_source

quest = select_quest("Ezra") or {
    "title": "Tutorial",
    "steps": ["Talk to trainer", "Complete objectives"],
}
if verify_source(quest):
    execute_quest(quest)
```

## Getting Started

This section walks through a fresh setup so you can try the project locally.

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourname/Android-MS11.git
   cd Android-MS11
   ```

2. **(Optional) Create a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
   The requirements file includes `requests>=2.0`.

4. **Run the example application**

   Launch the main script to see the questing demo:

   ```bash
   python src/main.py
   ```

   You can also run the CLI runner directly and select a mode:

   ```bash
   python -m src.runner --mode quest
   ```

5. **Run the tests**

   The repository contains a small test suite powered by `pytest`. The
   tests rely on packages such as `langchain` and `transformers`, so
   make sure all dependencies are installed first:

   ```bash
   pip install -r requirements.txt
   pytest
   # includes requests>=2.0
   ```

These steps should give you a working copy of Android MS11 and confidence
that the provided modules function as expected.

## Legacy Quest Manager CLI
Use the legacy quest tool to explore old mission data.

```bash
python -m src.data.legacy_quest_manager --list
python -m src.data.legacy_quest_manager --search Corellia
python -m src.data.legacy_quest_manager --npc "Rebel Trainer"
python -m src.data.legacy_quest_manager --list --planet Naboo
python -m src.data.legacy_quest_manager --list --status completed
```
