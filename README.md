# Android MS11
Version: 0.1.0
Android MS11 is an advanced interface assistant for long-session open-world automation maintained by **Project Galactic Beholder**.

The original MS11-Core implementation has been archived under `archive/ms11-core` to preserve legacy code.

## Features
- 🧭 Legacy Quest Dashboard: View progress with `--show-legacy-status`
- 🎡 Theme Park Dashboard: View progress with `--show-themepark-status`
- 🖥️ Unified Dashboard CLI: view both dashboards with `--show-dashboard`, switch
  tables with `--dashboard-mode`, toggle `--summary`/`--detailed`, and filter
  quest rows using `--filter-status`
- ✅ Smart Retry Logic: automatically retries failed quest steps up to 3 times, writing details to `logs/retry_log.txt`
- 📊 Quest Step Enrichment (Completed / Failed / In Progress / Unknown)
- 🔗 Dashboard Utils for grouping quests and summary counts
- ✅ Modular Quest Loader and Executor
- ✅ Screenshot-based Logging
- ✅ Batch-based Development System

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
```python
from core import profile_loader
from core.state_tracker import update_state, get_state

profile = profile_loader.load_profile("demo")
update_state(mode=profile.get("default_mode"))
print(get_state())
```
The modules under `src/` offer simple building blocks that you can integrate into larger systems.
Utilities for planning professions and trainer routes live under `profession_logic/`.

## Working with Quests

Three lightweight helpers provide a basic quest pipeline:

- `quest_selector.select_quest` picks the next mission for a character.
- `execution.quest_executor.QuestExecutor` runs quests step-by-step.
- `core.quest_loader.load_quest_steps` reads quest JSON files.
- `utils.source_verifier.verify_source` checks that the data you loaded is trustworthy.

```python
from src.quest_selector import select_quest
from src.execution.quest_executor import QuestExecutor
from core.quest_loader import load_quest_steps
from utils.source_verifier import verify_source

path = "quests/tutorial.json"
quest = select_quest("Ezra") or load_quest_steps(path)
if verify_source(quest):
    QuestExecutor(path).run()
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

## Quest State Detection

Use `core.quest_state.is_step_completed(log_text, step_text)` to check whether a
quest objective appears in captured log text.  The helper works with raw strings
or can scan files using `scan_log_file_for_step()`.  For screenshot workflows,
`extract_quest_log_from_screenshot()` first runs OCR so the text can be passed to
`is_step_completed`.

## 🛠️ Smart Retry Logic

Use `execute_with_retry(step, max_retries=3)` whenever a quest step might
intermittently fail. The helper calls `execute_quest_step(step)` until it
returns ``True`` or the retry limit is reached. By default the step is tried
three times. If every attempt fails, the function returns ``False`` (or invokes
the optional ``fallback`` callback when provided).

All retry attempts are logged to `logs/retry_log.txt` in CSV format. Each line
records the timestamp, step id, attempt number and error message:

```
2023-01-01T00:00:00, open_door, 1, false result
```

Review this file to identify repeated failures and refine your fallback
strategies.

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
   python src/main.py --mode quest --max_loops 3 --train
   ```

   You can also run the CLI runner directly and select a mode:

   ```bash
   python -m src.runner --mode quest
   ```


These steps should give you a working copy of Android MS11 and confidence
that the provided modules function as expected.

## ⚙️ Configuration

### Logging Behavior
`start_log()` writes messages to the `logs/` directory. The file name begins
with the value of the `BOT_INSTANCE_NAME` environment variable. Use this to
separate logs when running multiple instances:

```bash
BOT_INSTANCE_NAME=MS11_Alpha python src/main.py --mode quest
# creates logs/MS11_Alpha.log
```
All log levels, including warnings, are written to this file.

Set `LOG_LEVEL` to control how verbose the output is. Levels follow the
standard Python logging values such as `DEBUG` or `INFO` (the default):

```bash
LOG_LEVEL=DEBUG python src/main.py --mode quest
```

Set `LOG_RETENTION_DAYS` to configure how many days to retain timestamped log files. Old files are removed whenever `configure_logger()` runs.

```bash
LOG_RETENTION_DAYS=7 python src/main.py
```

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
- ``support`` – enhanced support with a pre-buff routine, follows the leader, joins the party, assists the target, and reacts to commands.
- ``rls`` – rare loot scanner mode.

```bash
python src/main.py --mode medic
python src/main.py --mode quest
python src/main.py --mode support
python src/main.py --mode rls
```

### RLS Mode
Rare Loot Scanner mode monitors loot messages and records rare item drops. The number of scans is controlled by the ``iterations`` value in ``config/config.json``.

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

## Smart Mode Switching

Phase 5 adds a session monitor that watches XP per minute, loot collected and
fatigue. When the ``--smart`` flag is enabled these values are gathered by
``session_monitor.monitor_session`` in ``core/session_monitor.py`` and used to
determine if another mode would perform better.

```bash
python src/main.py --profile hero.json --smart
```

This command launches using the ``hero.json`` profile and automatically adjusts
behavior based on the tracked statistics.

## Mode Looping

Use the ``--loop`` flag to keep the runner active and rotate between modes. The
rotation order is defined by ``mode_sequence`` in a runtime profile. Each time
``session_monitor`` detects fatigue above the profile's threshold, the next mode
is selected via ``core.mode_scheduler.get_next_mode``.

```bash
python src/main.py --profile hero.json --loop
```

Example profile snippet:

```json
{
  "default_mode": "quest",
  "mode_sequence": ["quest", "crafting", "medic"],
  "fatigue_threshold": 50
}
```

This setup cycles through questing, crafting, and healing whenever fatigue rises
above 50 while ``--loop`` is active.

### 🔁 Repeat Mode

To continuously run a single mode (like entertainer or farming), use:

```bash
python src/main.py --mode entertainer --repeat
```

You can also set a rest interval (in seconds) between loops:

```bash
python src/main.py --mode entertainer --repeat --rest 30
```

You can limit how many times the selected mode runs by adding
`--max_loops N`. Combine this with `--train` to automatically visit
profession trainers between loops.

```bash
python src/main.py --mode entertainer --repeat --max_loops 5 --train
```

## Targeted Farming Setup

Use the `--farming_target` flag to define exactly where farming should occur.
The value is a JSON string with `planet`, `city`, and `hotspot` keys:

```bash
python src/main.py --mode bounty_farming \
  --farming_target '{"planet": "dantooine", "city": "imperial_outpost", "hotspot": "north_field"}'
```

Omit `--train` or set `"auto_train": false` in a runtime profile to skip
visiting trainers between loops.

## Terminal Farming

`TerminalFarmer` reads the on-screen mission board and accepts
bounties within your desired distance. Adjust the defaults in
`config/farming_profile.json` and call `execute_run()` to parse the
terminal:

For complete configuration details see [docs/modes/farming_mode.md](docs/modes/farming_mode.md).

```python
from modules.farming import TerminalFarmer

farmer = TerminalFarmer()
farmer.execute_run()
```

The farming profile uses a `distance_limit` key to restrict how far the
farmer will travel:

```json
{
  "distance_limit": 600
}
```

Run the farming tests individually with:

```bash
pytest tests/farming/test_terminal_farm.py
```

## State Tracking and Profiles

The `core.state_tracker` module persists simple game state between runs.
Calls to `update_state()` write values to `logs/state.json`, which is loaded
automatically on the next import. Use `get_state()` to inspect the stored data.

Profiles under `profiles/` capture long-term preferences. Load one with
`core.profile_loader.load_profile(name)` and combine it with the state tracker
to initialize a session.

Example profile:

```json
{
  "support_target": "Leader",
  "preferred_trainers": {"medic": "trainer"},
  "default_mode": "medic",
  "skip_modes": ["crafting"],
  "farming_targets": ["Bandit"],
  "farming_target": {
    "planet": "Naboo",
    "city": "Theed",
    "hotspot": "Cantina"
  },
  "skill_build": "basic",
  "auto_train": false
}
```

`skill_build` points to a JSON file under `profiles/builds/` describing the
skills for that character. The loader will raise an error if this build file is
missing or malformed.

`farming_target` defines the planet, city and hotspot for farming sessions.
The automation uses this information to travel back to the desired zone before
clearing mobs.  Setting `auto_train` to `true` will automatically check
trainers after each loop.
You can also enable this behavior at runtime with the `--train` flag.

```python
from core import profile_loader
from core.state_tracker import update_state

profile = profile_loader.load_profile("demo")
update_state(mode=profile.get("default_mode"))
```

Session progress defaults to ``runtime/session_state.json``. Set the
``SESSION_FILE_PATH`` environment variable to use a different location.

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
python src/main.py --mode medic --train --max_loops 5
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

Launch the legacy quest loop directly or just display progress with:

```bash
python main.py --legacy
python main.py --show-legacy-status
python main.py --show-themepark-status
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

## Unified Dashboard CLI
Display quest progress from both legacy and theme park quests. By default the
tables are shown in a split-pane layout:

```bash
python main.py --show-dashboard
```

Limit the output to one table with `--dashboard-mode`. Combine it with `--summary`
or `--detailed` to control verbosity:

```bash
python main.py --show-dashboard --dashboard-mode legacy --summary
python main.py --show-dashboard --dashboard-mode themepark --detailed
```

Filter rows by status emoji with `--filter-status`:

```bash
python main.py --show-dashboard --filter-status ✅
```
Summary mode displays total quest counts per category when filtering.

The split layout places the legacy table above the theme park table using Rich's
`Layout` class.

### Status Emoji Legend
The dashboards use a small set of emoji to represent quest state:

- ✅ ``completed``
- ❌ ``failed``
- ⏳ ``in_progress``
- 🕒 ``not_started``
- ❓ ``unknown``

Quest summaries group legacy steps by their ``category`` key with all theme park
quests collected under **Theme Parks**. Each category row shows a progress bar
and the total quest count when ``--summary`` is enabled.

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

### Trainer Travel

`core.trainer_travel` provides helpers for creating waypoint macros and
outlining the steps needed to reach a profession trainer. Use
`get_travel_macro()` to build the `/waypoint` string, or call
`start_travel_to_trainer()` to log and print it for manual execution.  When the
trainer is on another planet, `plan_travel_to_trainer()` lists the shuttle hops
and final waypoint.

```python
from core import plan_travel_to_trainer, start_travel_to_trainer

trainer = {
    "name": "Marksman Trainer",
    "coords": [1234, -567],
    "planet": "tatooine",
}

steps = plan_travel_to_trainer(trainer)
print(steps)

start_travel_to_trainer(trainer)
```

## Log Files
The application writes several logs under the `logs/` directory:

- `logs/<instance>.log` &ndash; general runtime messages produced by `start_log()`.
- Warnings are included in the main log.
- `logs/quest_selections.log` &ndash; history of quests chosen via the CLI.
- `logs/step_journal.log` &ndash; success/failure records from step validation.
- `logs/session_*.json` &ndash; detailed step traces and summaries for each session.
- `logs/training_log.txt` &ndash; entries recorded by the trainer navigator.

Running the test suite also writes logs to this directory. See the
⚙️ Configuration section for how to control the log filename and verbosity.

## Running Tests

Install the test requirements and run the suite with:

```bash
pip install -r requirements.txt -r requirements-test.txt
pytest
```

### Makefile Commands

The repository includes a small `Makefile` for running development tasks.
Use the `validate-batch-044` target to execute the Codex batch validation
script:

```bash
make validate-batch-044
```

Use the `validate-batch-045` target to run the next batch's validation script:

```bash
make validate-batch-045
```

## License Hooks

Several entry points are decorated with ``@requires_license`` from
``utils.license_hooks``. When the ``ANDROID_MS11_LICENSE`` environment variable
is absent the decorator issues a warning and continues execution. Future
releases will replace this placeholder with real license validation.

## Wiki Content and Licensing

The file `data/raw/legacy.html` and the JSON files under `data/wiki_raw/` were
exported from the SWG Wiki hosted on Fandom. This material is licensed under
the Creative Commons Attribution-ShareAlike 3.0 license (CC-BY-SA 3.0). See
<https://www.fandom.com/licensing> for the official licensing terms. The
project uses these extracts solely to look up quest and item information and
includes references back to the original pages via `data/metadata_index.json`.

## Disclaimer
Android MS11 is an unofficial project, not affiliated with SWGR or LucasArts, and must be used in accordance with the game's terms of service.
