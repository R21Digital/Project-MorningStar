# android_ms11

The **android_ms11** package bundles minimal mode stubs used by the demo
application. Each module under `android_ms11.modes` exposes a `run()`
function which is selected by `src.main` based on the chosen mode.

## Available modes

- `combat_assist_mode` – placeholder for assisting in combat situations.
- `crafting_mode` – stub for crafting and resource management loops.
- `dancer_mode` – provides entertainer routines such as dancing.
- `medic_mode` – basic healing behavior and support abilities.
- `profession_mode` – handles profession training tasks.
- `quest_mode` – runs quest step sequences.
- `whisper_mode` – monitors and relays whispers.

## Running a mode

Start a session with `src.main` and specify a mode:

```bash
python src/main.py --mode medic
```

You can also launch a mode through the lightweight CLI:

```bash
python -m src.runner --mode quest
```

Both approaches use the same mode mapping defined in `src.main`.
