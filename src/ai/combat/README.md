# ai.combat

`ai.combat` packages a minimal combat decision helper and a runtime wrapper.

## `evaluate_state`

```python
from ai.combat import evaluate_state
```

Return a suggested action string from two dictionaries:

- **`player_state`** – recognizes `hp`, `has_heal`, and `is_buffed`.
  Missing keys default to `hp=100`, `has_heal=False`, `is_buffed=False`.
- **`target_state`** – only the `hp` key is consulted and defaults to `100`.
- **`difficulty`** – optional string: "easy", "normal" (default), or "hard".

Possible results:

- `"heal"` – low HP with a heal item available.
- `"retreat"` – low HP and no heal item.
- `"attack"` – target still has HP.
- `"buff"` – target defeated but player lacks a buff.
- `"idle"` – target defeated and player already buffed.

### Example

```python
from ai.combat import evaluate_state

action = evaluate_state({"hp": 25, "has_heal": True}, {"hp": 50})
print(action)  # "heal"

# Enable debug logging to understand why a choice was made
action = evaluate_state({"hp": 25, "has_heal": True}, {"hp": 50}, debug=True)
# Difficulty can be tuned as well
hard_action = evaluate_state({"hp": 25, "has_heal": False}, {"hp": 50}, difficulty="hard")
# Prints "Decision: heal ..." to stdout
```

## `CombatRunner`

```python
from ai.combat import CombatRunner
```

A thin wrapper exposing `tick(player_state, target_state)` and storing the
last returned action on `last_action`.

### Usage Example

```python
from ai.combat import evaluate_state, CombatRunner

runner = CombatRunner()
player = {"hp": 80}
target = {"hp": 40}

action = runner.tick(player, target)
print(action)  # "attack"
```
