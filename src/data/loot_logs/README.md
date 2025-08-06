# Heroic Loot Logs Directory

This directory contains parsed loot data from heroic instances, extracted from MS11 bot session logs.

## File Structure

```
loot_logs/
├── heroic_loot_logs_YYYYMMDD_HHMMSS.json - Parsed loot data files
├── raw_sessions/                          - Original session logs (optional backup)
└── README.md                             - This file
```

## Data Format

Each `heroic_loot_logs_*.json` file contains:

```json
{
  "metadata": {
    "generated_at": "2025-01-27T12:00:00Z",
    "version": "1.0",
    "total_entries": 150,
    "heroic_instances": ["axkva_min", "ig_88", "geonosian_queen"],
    "date_range": {
      "start": "2025-01-26T10:00:00Z",
      "end": "2025-01-27T12:00:00Z"
    }
  },
  "loot_entries": [
    {
      "timestamp": "2025-01-27T11:30:00Z",
      "player_name": "PlayerName",
      "heroic_instance": "axkva_min",
      "boss_name": "Axkva Min",
      "item_name": "Axkva Min's Lightsaber",
      "item_type": "weapon",
      "rarity": "legendary",
      "quantity": 1,
      "stats": {
        "damage": "150-200",
        "force_power": 50
      },
      "source_log": "session_20250127.log",
      "completion_status": "completed",
      "difficulty": "heroic",
      "group_size": 8,
      "session_id": "session_abc123",
      "raw_log_line": "[11:30:00] You have received Axkva Min's Lightsaber from Axkva Min"
    }
  ]
}
```

## Field Descriptions

### Metadata
- `generated_at`: When this file was created
- `version`: Data format version
- `total_entries`: Number of loot entries in this file
- `heroic_instances`: List of heroic instances covered
- `date_range`: Time span of the loot data

### Loot Entry
- `timestamp`: When the loot was received (ISO 8601)
- `player_name`: Character who received the loot
- `heroic_instance`: Which heroic instance (axkva_min, ig_88, etc.)
- `boss_name`: Specific boss that dropped the loot
- `item_name`: Name of the loot item
- `item_type`: Category (weapon, armor, material, etc.)
- `rarity`: Item rarity (common, uncommon, rare, epic, legendary)
- `quantity`: Number of items received
- `stats`: Item statistics if available
- `source_log`: Original log file name
- `completion_status`: Instance completion status
- `difficulty`: Difficulty level (normal, heroic)
- `group_size`: Number of players in group
- `session_id`: Unique session identifier
- `raw_log_line`: Original log line for debugging

## Usage

This data is used by:
1. The Heroics Loot API (`/api/heroics/loot`)
2. SWGDB web interface for loot tables
3. MS11 bot for loot tracking and statistics
4. Community tools and analysis

## Data Retention

- Files older than 30 days are automatically archived
- Duplicate entries are filtered during processing
- Invalid or corrupted entries are logged but excluded