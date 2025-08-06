# ai.combat

`ai.combat` packages a minimal combat decision helper and a runtime wrapper.

## `evaluate_state`

```python
from ai.combat import evaluate_state
```

-Return a suggested action string from two dictionaries:

- **`player_state`** – recognizes `hp`, `healing_items`, and `buffed`.
  Missing keys default to `hp=100`, `healing_items=0`, `buffed=False`.
- **`target_state`** – only the `hp` key is consulted and defaults to `100`.
- **`difficulty`** – optional string: "easy", "normal" (default), or "hard".
- **`behavior`** – optional string: "aggressive", "defensive", or "tactical" (default).

Possible results:

- `"heal"` – low HP with a heal item available.
- `"retreat"` – low HP and no heal item.
- `"attack"` – target still has HP.
- `"buff"` – target defeated but player lacks a buff.
- `"idle"` – target defeated and player already buffed.

### Example

```python
from ai.combat import evaluate_state

action = evaluate_state({"hp": 25, "healing_items": 1}, {"hp": 50})
print(action)  # "heal"

# Enable debug logging to understand why a choice was made
action = evaluate_state({"hp": 25, "healing_items": 1}, {"hp": 50}, debug=True)
# Difficulty can be tuned as well
hard_action = evaluate_state({"hp": 25, "healing_items": 0}, {"hp": 50}, difficulty="hard")
# Behavior can be adjusted as well
aggressive_action = evaluate_state({"hp": 45, "healing_items": 1}, {"hp": 50}, behavior="aggressive")
# Prints "Decision: heal ..." to stdout
```

## `CombatRunner`

```python
from ai.combat import CombatRunner
```

A thin wrapper exposing `tick(player_state, target_state)` and storing the
last returned action on `last_action`. The runner keeps a short memory of
recent actions to prevent repeating the same command.

### Usage Example

```python
from ai.combat import evaluate_state, CombatRunner

runner = CombatRunner(memory_size=3)  # memory_size controls action history length
player = {"hp": 80, "buffed": True}
target = {"hp": 40}

action = runner.tick(player, target)
print(action)  # "attack"
```
