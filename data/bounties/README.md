# Bounty Hunter Missions Data

This directory contains JSON files for bounty hunter missions and enemy patterns.

## File Structure

Each bounty mission file should contain:

```json
{
  "mission_id": "unique_mission_identifier",
  "target_name": "NPC or PC target name",
  "target_type": "npc|pc",
  "location": {
    "planet": "planet_name",
    "city": "city_name", 
    "coordinates": [x, y],
    "zone": "zone_name"
  },
  "difficulty": "easy|medium|hard|elite",
  "reward_credits": 1000,
  "reward_faction": "imperial|rebel|neutral",
  "time_limit": 3600,
  "requirements": {
    "level_min": 10,
    "level_max": 50,
    "profession": "bounty_hunter",
    "faction": "imperial"
  },
  "combat_profile": "aggressive|defensive|tactical",
  "escape_chance": 0.1,
  "backup_targets": ["npc1", "npc2"],
  "notes": "Additional mission details"
}
```

## Mission Types

- **NPC Bounties**: Standard NPC targets (Phase 1)
- **PC Bounties**: Player character targets (Future Phase)
- **Elite Bounties**: High-value, high-risk targets
- **Faction Bounties**: Targets with specific faction requirements

## Usage

The bounty hunter mode will load these files to:
1. Accept missions from BH terminals
2. Travel to target locations
3. Engage targets with appropriate combat strategies
4. Complete missions and collect rewards 