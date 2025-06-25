# Android MS11
Version: 0.1.0
Android MS11 is an advanced interface assistant for long-session open-world automation maintained by **Project Galactic Beholder**.

The original MS11-Core implementation has been archived under `archive/ms11-core` to preserve legacy code.

## Lore
In the world of **Argent**, legendary guilds compete to recover ancient relics. Adventurers take on perilous quests to gain favor with their faction and earn the power needed to reunite the shards. Android MS11 provides the tooling to script and observe these journeys, whether you are tracking combat victories or following a sprawling roleplay narrative.

## Basic Usage
Install the dependencies and then import the modules you need.
The `requirements.txt` file now includes `requests>=2.0`, `PyYAML`, and `pymongo>=3.0`:
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

## Monitoring On-Screen Events

`src/state/state_manager.py` provides a `StateManager` for general game state
tracking. It watches OCR text and triggers callbacks when phrases appear,
updating ``current_state`` to the matched key. Modules under
`src/execution` still expose a lightweight version for internal helpers. Use
the state module when you want to react to global game conditions and the
execution module when writing step-by-step automation.

Both classes share the same basic API. The version in `src/state` remembers
the last matched phrase through its ``current_state`` attribute, while the one
in `src/execution` omits this attribute to remain a minimal dependency.

```python
from src.state.state_manager import StateManager

def on_accept():
    print("Quest accepted!")

manager = StateManager({"quest accepted": on_accept}, interval=0.5)
manager.run(duration=10)
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
    The requirements file includes `requests>=2.0`, `PyYAML`, and `pymongo>=3.0`.

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
    # includes requests>=2.0, PyYAML, and pymongo>=3.0
   ```

These steps should give you a working copy of Android MS11 and confidence
that the provided modules function as expected.

## Automation Modes
Select a runtime mode when starting the automation. The ``--mode`` option
controls which behavior module is activated.

```bash
python src/main.py --mode questing
python src/main.py --mode medic
python src/main.py --mode grinding
```

## Legacy Quest Manager CLI
Use the legacy quest tool to explore old mission data.

```bash
python -m src.data.legacy_quest_manager --list
python -m src.data.legacy_quest_manager --search Corellia
python -m src.data.legacy_quest_manager --npc "Rebel Trainer"
python -m src.data.legacy_quest_manager --list --planet Naboo
python -m src.data.legacy_quest_manager --list --status completed
```

## Quest Selection CLI
Quickly pick the next quest for a character by running:

```bash
python scripts/cli/execute_quest.py --character "Ezra"
```

You can further control the selection with these options:

- `--planet PLANET` &ndash; filter quests by planet.
- `--type TYPE` &ndash; filter by quest type.
- `--random` &ndash; choose randomly among matches.
- `--debug` &ndash; show the full quest data instead of a summary.

Every run appends the chosen quest to `logs/quest_selections.log`.

## Trainer Lookup CLI
Locate the in-game coordinates for a profession trainer.

```bash
python scripts/cli/find_trainer.py artisan --planet tatooine --city mos_eisley
```

The `profession` argument is required. `--planet` and `--city` default to
`tatooine` and `mos_eisley`. When a matching entry is found in
`data/trainers.yaml`, the trainer's name and coordinates are printed; otherwise
a helpful message is shown.
The lookup uses `utils.get_trainer_location.get_trainer_location()` to read
locations from the YAML file. By default the file is loaded relative to the
project root, but you can override the location by setting the
`TRAINER_FILE` environment variable or passing a custom path to
`utils.load_trainers.load_trainers()`.
Trainer coordinates are currently curated manually. A future script may
automate populating `data/trainers.yaml` once reliable NPC extraction is
available.

Automating the visit is possible through `trainer_visit.visit_trainer()`. It
loads coordinates from the same YAML file and directs an agent to travel to the
trainer. Dialogue steps referencing "Trainer" trigger `train_with_npc()` to log
the interaction.

## Log Files
The application writes several logs under the `logs/` directory:

- `logs/app.log` &ndash; general runtime messages produced by `start_log()`.
- `logs/quest_selections.log` &ndash; history of quests chosen via the CLI.
- `logs/step_journal.log` &ndash; success/failure records from step validation.
- `logs/session_*.log` &ndash; detailed step traces for each session.
