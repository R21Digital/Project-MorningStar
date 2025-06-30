# Terminal Farming Mode

`TerminalFarmer` parses mission terminals and logs accepted bounties. The module reads a simple JSON profile and exposes an `execute_run()` method to process the on-screen text.

## Configuration Options

The default profile lives at `config/farming_profile.json` and supports the keys below:

- `preferred_terminal` – name of the terminal to use for missions.
- `preferred_direction` – cardinal direction your character should face before scanning.
- `mob_priority` – ordered list of mob names to prioritize when multiple matches are found.
- `distance_limit` – only accept missions within this distance in meters.
- `blacklist_mobs` – list of mobs to always ignore.

## Expected Output

`execute_run(board_text=None)` returns a list of missions sorted from the parsed screen text. Each mission is a dictionary with at least:

- `name` – mission or mob name.
- `coords` – `(x, y)` tuple of mission coordinates.
- `distance` – distance to the target in meters.
- `credits` – optional credit reward if present on the board.

Accepted missions are logged via `core.session_tracker.log_farming_result`, updating `session_state.json` with the total credits and counts.

## Usage Example

```python
from modules.farming import TerminalFarmer

farmer = TerminalFarmer()
missions = farmer.execute_run()
for mission in missions:
    print(mission)
```

For unit testing you can pass pre-captured text to `execute_run()`:

```python
sample = """
Bandit Camp 100,200 300m 500c
Rebel Hideout -50,-75 500m
"""
farmer = TerminalFarmer()
farmer.profile["distance_limit"] = 400
accepted = farmer.execute_run(board_text=sample)
```

The tests in `tests/farming/test_terminal_farm.py` demonstrate the expected parsing behavior.
