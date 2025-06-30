# Combat Module

This package bundles a minimal combat AI. The helper function
`evaluate_state` inspects a player dictionary and a target dictionary and
returns a recommended action string. `CombatRunner` provides a thin wrapper
that records the last suggested action.

## `evaluate_state`

### Parameters
- **`player_state`** – mapping describing the player. The keys `hp`,
  `has_heal`, and `is_buffed` are recognized. Missing values default to
  `hp=100`, `has_heal=False`, and `is_buffed=False`.
- **`target_state`** – mapping describing the target. Only the `hp` field is
  consulted and defaults to `100` if absent.

### Returns
One of the following strings:

- `"heal"` – player HP below 30 and a heal item is available.
- `"retreat"` – low HP with no heal available.
- `"attack"` – enemy still has HP remaining.
- `"buff"` – encounter over but the player lacks a buff.
- `"idle"` – nothing to do once buffed and the target is defeated.

## Example: `CombatRunner`

```python
from src.ai.combat import CombatRunner

runner = CombatRunner()
player = {"hp": 80}
target = {"hp": 40}

action = runner.tick(player, target)
print(action)  # "attack"
```
