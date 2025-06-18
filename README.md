# Project-MorningStar
Version: 0.1.0
Project MorningStar (formerly known as MS11-Core) is an advanced interface assistant for long-session open-world automation. Inspired by player realism, faction-based systems, and strategic progression loops.

The original MS11-Core implementation has been archived under `archive/ms11-core` to preserve legacy code.

## Lore
In the world of **Argent**, legendary guilds compete to recover the fragments of the star "Morning". Adventurers take on perilous quests to gain favor with their faction and earn the power needed to reunite the shards. MorningStar provides the tooling to script and observe these journeys, whether you are tracking combat victories or following a sprawling roleplay narrative.

## Basic Usage
Install the dependencies and then import the modules you need:
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

## Getting Started

This section walks through a fresh setup so you can try the project locally.

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourname/Project-MorningStar.git
   cd Project-MorningStar
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

   The repository contains a small test suite powered by `pytest`.
   Execute it with:

   ```bash
   pytest
   ```

These steps should give you a working copy of MorningStar and confidence
that the provided modules function as expected.
