# Combat Profiles

This folder stores JSON configuration files used by the combat system.
Each profile is a dictionary defining how to engage a particular enemy
or scenario. Files are loaded with
`modules.combat.profiles.load_combat_profile(name)`, which reads
`<name>.json` from this directory and returns the parsed data. Missing
files yield an empty dictionary.

Profiles typically include at least an `enemy` and `strategy` key:

```json
{
  "enemy": "stormtrooper",
  "strategy": "burst"
}
```

CombatAI reads these values and adjusts its actions accordingly. You may
extend the format with optional fields such as `abilities` or cooldown
settings to further refine behaviors.

Sample profile names include:

- `default.json`
- `rifleman_medic.json`
- `brawler_tank.json`

Add your own profiles here and load them by name when starting a
combat routine.
