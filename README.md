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
sudo apt-get install tesseract-ocr libtesseract-dev
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
Utilities for planning professions and trainer routes live under `profession_logic/`.

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
   sudo apt-get install tesseract-ocr libtesseract-dev
   # then install Python packages
   pip install -r requirements.txt
   ```
    The requirements file includes `requests>=2.0`, `PyYAML`, `pymongo>=3.0`, and
    `discord.py` for the optional Discord relay bot.

4. **Configure runtime defaults**

   Edit `config/config.json` to set your character name, default mode,
   and whether the Discord relay is enabled. These values are not read
   from `config/session_config.json`, which only stores temporary session
   settings.

5. **Run the example application**

   Launch the main script to see the questing demo:

   ```bash
   python src/main.py
   ```

   You can also run the CLI runner directly and select a mode:

   ```bash
   python -m src.runner --mode quest
   ```

6. **Run the tests**

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
controls which behavior module is activated. Available modes include:

- ``quest``
- ``profession``
- ``combat``
- ``dancer``
- ``medic``
- ``crafting``
- ``whisper``
- ``support`` – follows leader, joins party, assists target, reacts to commands.

```bash
python src/main.py --mode medic
python src/main.py --mode quest
```

Runtime profiles stored in `profiles/runtime/` let you bundle these
settings together. Use the ``--profile`` option to load one:

```bash
python src/main.py --profile questing
```

The ``--mode`` flag overrides the ``default_mode`` defined in `config/config.json`.
Each runtime profile is a small JSON file describing the starting location,
objectives, and priority for a task. See below for an example profile.

An example runtime profile looks like this:

```json
{
  "mode": "medic",
  "location": "Naboo",
  "objectives": [
    "Heal players in Theed",
    "Restock medical supplies"
  ],
  "priority": 1
}
```

## Discord Relay Bot
The relay bot depends on the `discord.py` package. Enable it by editing
`config/config.json` (set `enable_discord_relay`) and
`config/discord_config.json`. The relay flag is only read from
`config/config.json`.

Example configuration:

```json
{
  "discord_token": "YOUR_BOT_TOKEN",
  "relay_mode": "manual",
  "target_user_id": 0,
  "reply_queue": []
}
```
If ``discord_token`` is empty in the JSON file, the bot will look for a
``DISCORD_TOKEN`` environment variable instead. This lets you keep the token out
of the repo when deploying or running locally.

`relay_mode` controls how whispers are delivered:

- `notify` – forward messages without replying.
- `manual` – wait for manual replies via DM.
- `auto` – auto-reply using placeholder AI logic.

Set `target_user_id` to specify the DM recipient.

Run the bot directly:

```bash
python relaybot/bot.py
```

To launch a bot that only uses direct messages, run:

```bash
python discord_dm_bot.py
```

Or start the demo with relay enabled:

```bash
python src/main.py --mode medic
```

## Credit and XP Tracking
Session logs are managed by `core.session_manager.SessionManager`. When a session starts, it records the starting credit balance and XP value. Calling `end_session()` writes a JSON report under `logs/` showing credits earned and XP gained.

You can track smaller actions with `XPManager`:

```python
from src.xp_manager import XPManager

xp = XPManager("Ezra")
xp.record_action("quest_complete")
xp.end_session()
```

Each action adds an entry to `logs/xp_tracking/` so you can review progress later.

## Whisper Relay Setup
The optional Discord relay forwards in-game whispers to a Discord DM. Enable it in `config/config.json` and configure credentials in `config/discord_config.json`.

When `relay_mode` is set to `auto` or `manual`, replies are sent back to the game via `game_bridge.GameBridge`. The helper `whisper_monitor.py` watches the screen and queues new whispers for dispatch.

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
`data/trainers.json`, the trainer's name and coordinates are printed; otherwise
the lookup uses `utils.get_trainer_location.get_trainer_location()` to read
locations from the JSON file. By default the file is loaded relative to the
project root, but you can override the location by setting the
`TRAINER_FILE` environment variable or passing a custom path to
`utils.load_trainers.load_trainers()`.
Trainer coordinates are currently curated manually. A future script may
automate populating `data/trainers.json` once reliable NPC extraction is
available.

Automating the visit is possible through `trainer_visit.visit_trainer()`. It
loads coordinates from the same JSON file and directs an agent to travel to the
trainer. Dialogue steps referencing "Trainer" trigger `train_with_npc()` to log
the interaction.

## Trainer Navigation CLI
Navigate and log a trainer visit in one step:

```bash
python cli/trainer/find_trainer.py --trainer "Master Combat Medic"
```

The command accepts the same `--planet` and `--city` options as the lookup
script, defaulting to `tatooine` and `mos_eisley`.

## Trainer Navigator Script
`scripts/logic/trainer_navigator.py` exposes helper functions for locating
nearby trainers and logging training sessions. Trainer locations are stored in
`data/trainers.json` using a list of entries per profession:

```json
{
  "artisan": [
    {"planet": "tatooine", "city": "mos_eisley", "name": "Artisan Trainer", "coords": [3432, -4795]}
  ]
}
```

Use the module interactively to list trainers near a position and record the
visit:

```bash
python - <<'EOF'
from scripts.logic import trainer_navigator as tn

pos = (3400, -4800)
trainers = tn.find_nearby_trainers(pos, "tatooine", "mos_eisley", threshold=200)
for t in trainers:
    print(t)
    tn.log_training_event(t["profession"], t["name"], t["distance"])
EOF
```

Each call to `log_training_event` appends a timestamped entry to
`logs/training_log.txt`.

## Trainer Data Extraction
Generate trainer location entries from sample screenshots.

```bash
python scripts/data/extract_trainers.py
```

The script runs OCR on images under `docs/samples/` and writes structured
results to `data/trainers.json`.

### Migration Note
The JSON trainer data file has moved from `data/trainers/trainers.json` to
`data/trainers.json`. `utils.load_trainers` now looks for this new path by
default. Update any custom scripts referencing the old location or set the
`TRAINER_FILE` environment variable if needed.

## Trainer Profiles
`core.TravelManager` reads profession trainer information from
`profiles/trainers.json`. Each profession key maps to an object with the fields
below:

- `name` – in‑game NPC name of the trainer.
- `waypoint` – `[x, y]` waypoint coordinates.
- `expected_zone` – city or outpost where the trainer is found.
- `expected_skill` – skill expected to be available when visiting.

Coordinates may be stored under either `waypoint` or `coords` – both fields are
treated interchangeably.

An example file:

```json
{
  "artisan": {
    "name": "Artisan Trainer",
    "waypoint": [3432, -4795],
    "expected_zone": "mos_eisley",
    "expected_skill": "Novice Artisan"
  },
  "marksman": {
    "name": "Marksman Trainer",
    "waypoint": [-150, 60],
    "expected_zone": "coronet",
    "expected_skill": "Novice Marksman"
  }
}
```

Add new professions to `profiles/trainers.json` using the same fields. The
waypoint (or `coords`) can be stored as a list or as separate `x`/`y` values
&ndash; `core.TravelManager` accepts any of these forms.  `planet` and `city` are
optional but help navigation.

### Training with `TravelManager`

```python
from core import TravelManager

tm = TravelManager()  # loads profiles/trainers.json by default
skills = tm.train_profession("artisan")
print(skills)
```

### Profession Leveler

`core.ProfessionLeveler` can visit a sequence of trainers defined in
`profiles/profession_plan.json`.

```json
[
  "artisan",
  "marksman"
]
```

```python
from core import ProfessionLeveler

leveler = ProfessionLeveler()  # reads profession_plan.json by default
leveler.level_all_professions()
```

## Shuttle Travel Utilities
Shuttle locations and connections are defined in `data/shuttles.json`. Each
planet key contains a list of shuttles with NPC coordinates and destination
links. A minimal entry looks like:

```json
{
  "tatooine": [
    {
      "city": "mos_eisley",
      "npc": "Shuttle Conductor",
      "x": 3520,
      "y": -4800,
      "destinations": [
        {"planet": "corellia", "city": "coronet"}
      ]
    }
  ]
}
```

Utilities under `scripts/travel/` read this file to determine the nearest
shuttle and to plan multi-hop routes. After traveling, `navigate_to(city, agent)`
walks the agent from the shuttle to the destination coordinates.

## Log Files
The application writes several logs under the `logs/` directory:

- `logs/app.log` &ndash; general runtime messages produced by `start_log()`.
- `logs/quest_selections.log` &ndash; history of quests chosen via the CLI.
- `logs/step_journal.log` &ndash; success/failure records from step validation.
- `logs/session_*.json` &ndash; detailed step traces and summaries for each session.
- `logs/training_log.txt` &ndash; entries recorded by the trainer navigator.

Running the test suite also writes logs to this directory.

## Running Tests

Before executing the test suite, ensure all dependencies are installed.
You can run the helper script below or manually install the packages.

```bash
./scripts/setup_test_env.sh
```

If you prefer to install manually, install the system packages and
then the Python requirements:

```bash
sudo apt-get install tesseract-ocr libtesseract-dev
# then install Python packages
pip install -r requirements.txt -r requirements-test.txt
```

Once dependencies are installed you can run the tests directly with
`pytest` or use the convenience target:

```bash
make test
```
Note: When running tests in headless CI, `pyautogui` requires a virtual display such as Xvfb.

Launch the test suite with `xvfb-run -a pytest` or an equivalent wrapper.

## Wiki Content and Licensing

The file `data/raw/legacy.html` and the JSON files under `data/wiki_raw/` were
exported from the SWG Wiki hosted on Fandom. This material is licensed under
the Creative Commons Attribution-ShareAlike 3.0 license (CC-BY-SA 3.0). See
<https://www.fandom.com/licensing> for the official licensing terms. The
project uses these extracts solely to look up quest and item information and
includes references back to the original pages via `data/metadata_index.json`.

## Disclaimer
Android MS11 is an unofficial project, not affiliated with SWGR or LucasArts, and must be used in accordance with the game's terms of service.
