# MS11 Batch 079 Implementation Summary
## Heroics Instance Entry + Group Coordination Logic

**Date:** January 27, 2025  
**Status:** Complete  
**Scope:** Heroic instance detection, group coordination, role assignment, and Discord integration

---

## Overview

Batch 079 implements a comprehensive heroics coordination system that enables MS11 to detect available heroic instances, form groups, assign roles based on profession and level, execute entry sequences, and coordinate with other bots via Discord integration.

### Key Features Implemented

1. **Heroic Instance Detection** - Parse `/heroiclock` command output
2. **Group Formation & Management** - Create and manage heroic groups
3. **Role Assignment** - Intelligent role assignment based on profession/level
4. **Entry Sequence Execution** - Automated entry sequences (Axkva Min example)
5. **Role-Based Behaviors** - DPS, Healer, Tank, Support behaviors
6. **Discord Integration** - Multi-bot coordination via Discord

---

## Core Components

### 1. HeroicDetector (`core/heroics/heroic_detector.py`)

**Purpose:** Detect and parse available heroic instances from `/heroiclock` command output.

**Key Features:**
- Parse `/heroiclock` command text to identify available heroics
- Load heroic instance data from YAML files
- Check prerequisites and lockout status
- Generate entry sequences for specific heroics
- Cache lockout information

**Data Structures:**
```python
@dataclass
class HeroicInstance:
    heroic_id: str
    name: str
    planet: str
    location: str
    coordinates: List[int]
    difficulty_tiers: List[str]
    level_requirement: int
    group_size: str
    status: str
    lockout_timer: int
    reset_time: str
    prerequisites: Dict[str, Any]
    bosses: List[Dict[str, Any]]
    special_mechanics: List[Dict[str, Any]]

@dataclass
class HeroicLockout:
    heroic_id: str
    difficulty: str
    lockout_start: str
    lockout_end: str
    is_locked: bool
    time_remaining: int

@dataclass
class HeroicEntryStatus:
    heroic_id: str
    can_enter: bool
    missing_prerequisites: List[str]
    lockout_status: Optional[HeroicLockout]
    group_ready: bool
    recommended_group_size: int
    current_players: int
```

**Methods:**
- `parse_heroiclock_command()` - Parse command output
- `detect_available_heroics()` - Get available heroics
- `get_heroic_entry_sequence()` - Get entry sequence
- `get_heroic_info()` - Get detailed heroic info
- `update_lockout_cache()` - Update lockout status

### 2. HeroicCoordinator (`core/heroics/heroic_coordinator.py`)

**Purpose:** Manage group formation, role assignment, and entry sequence execution.

**Key Features:**
- Create and manage group formations
- Intelligent role assignment based on profession/level
- Add/remove group members
- Execute entry sequences
- Track group status and readiness

**Data Structures:**
```python
@dataclass
class GroupMember:
    player_name: str
    role: str
    level: int
    profession: str
    is_leader: bool = False
    is_ready: bool = False
    discord_id: Optional[str] = None

@dataclass
class GroupFormation:
    group_id: str
    heroic_id: str
    difficulty: str
    members: List[GroupMember]
    status: str  # forming, ready, in_progress, completed
    formation_time: str
    target_size: int
    current_size: int

@dataclass
class RoleAssignment:
    player_name: str
    assigned_role: str
    preferred_role: str
    confidence: float
    reasoning: str
```

**Methods:**
- `create_group_formation()` - Create new group
- `assign_role()` - Assign role to player
- `add_member_to_group()` - Add member to group
- `get_entry_sequence()` - Get entry sequence
- `execute_entry_sequence()` - Execute entry sequence
- `get_group_status()` - Get group status
- `disband_group()` - Disband group

### 3. RoleBehaviorManager (`core/heroics/role_behaviors.py`)

**Purpose:** Define and execute role-based behaviors for different professions.

**Key Features:**
- Role-specific combat actions and priorities
- Game state-based action selection
- Profession-based role scoring
- Health threshold management
- Cooldown management

**Data Structures:**
```python
@dataclass
class CombatAction:
    action_id: str
    name: str
    keybind: str
    cooldown: float
    priority: int
    conditions: Dict[str, Any]
    target_type: str

@dataclass
class RoleBehavior:
    role: str
    description: str
    priorities: List[str]
    combat_actions: List[CombatAction]
    targeting_rules: Dict[str, Any]
    health_thresholds: Dict[str, float]
    cooldown_management: Dict[str, Any]
```

**Methods:**
- `execute_dps_behavior()` - DPS role behavior
- `execute_healer_behavior()` - Healer role behavior
- `execute_tank_behavior()` - Tank role behavior
- `execute_support_behavior()` - Support role behavior
- `get_next_action()` - Get next action for role
- `get_role_priorities()` - Get role priorities

### 4. DiscordIntegration (`core/heroics/discord_integration.py`)

**Purpose:** Enable multi-bot coordination via Discord.

**Key Features:**
- Discord bot for group coordination
- Real-time group formation
- Role assignment and switching
- Status synchronization
- Group ready checks

**Data Structures:**
```python
@dataclass
class DiscordBotInfo:
    bot_id: str
    bot_name: str
    character_name: str
    role: str
    is_available: bool
    last_seen: str

@dataclass
class DiscordGroupMessage:
    message_id: str
    sender_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str
```

**Discord Commands:**
- `!heroic available` - Show available heroics
- `!heroic form <heroic> <difficulty>` - Form group
- `!heroic join <group_id>` - Join group
- `!group status` - Show group status
- `!group ready <group_id>` - Mark ready
- `!role request <role>` - Request role
- `!status <health> <energy> <location> <target>` - Update status
- `!heartbeat <character>` - Send heartbeat

---

## Configuration

### Group Profiles (`config/group_profiles/group_heroics.json`)

**Structure:**
```json
{
  "group_coordination": {
    "enabled": true,
    "discord_integration": {
      "enabled": false,
      "webhook_url": "",
      "channel_id": "",
      "bot_token": ""
    },
    "auto_role_assignment": true,
    "role_priority": ["healer", "tank", "dps", "support"]
  },
  "roles": {
    "dps": {
      "description": "Damage dealer role",
      "priorities": ["maximize_damage_output"],
      "combat_profile": "dps_heroic",
      "keybinds": {
        "primary_attack": "1",
        "secondary_attack": "2",
        "damage_cooldown": "3"
      },
      "targeting_rules": {
        "primary_target": "boss",
        "secondary_target": "elite_minions"
      }
    },
    "healer": {
      "description": "Healing and support role",
      "priorities": ["maintain_group_health"],
      "combat_profile": "healer_heroic",
      "keybinds": {
        "primary_heal": "1",
        "group_heal": "2",
        "cleanse": "3"
      },
      "healing_rules": {
        "tank_health_threshold": 0.8,
        "group_health_threshold": 0.6,
        "emergency_heal_threshold": 0.3
      }
    }
  },
  "heroic_instances": {
    "axkva_min": {
      "recommended_group_size": {
        "normal": 6,
        "hard": 8
      },
      "role_distribution": {
        "normal": {
          "tank": 1,
          "healer": 2,
          "dps": 2,
          "support": 1
        }
      },
      "special_mechanics": {
        "dark_side_corruption": {
          "affected_roles": ["all"],
          "mitigation": "cleanse_abilities",
          "priority": "high"
        }
      }
    }
  }
}
```

### Heroic Data (`data/heroics/`)

**Files:**
- `heroics_index.yml` - Index of all heroics
- `axkva_min.yml` - Axkva Min heroic details
- `ancient_jedi_temple.yml` - Ancient Jedi Temple details
- `sith_academy.yml` - Sith Academy details
- `mandalorian_bunker.yml` - Mandalorian Bunker details
- `imperial_fortress.yml` - Imperial Fortress details

---

## Role Assignment Logic

### Profession-Based Scoring

**Scoring Matrix:**
```python
profession_roles = {
    "medic": {"healer": 0.9, "support": 0.7, "dps": 0.3, "tank": 0.2},
    "commando": {"dps": 0.9, "tank": 0.6, "support": 0.4, "healer": 0.2},
    "rifleman": {"dps": 0.9, "support": 0.5, "tank": 0.3, "healer": 0.1},
    "pistoleer": {"dps": 0.8, "support": 0.6, "tank": 0.3, "healer": 0.2},
    "carbineer": {"dps": 0.8, "support": 0.5, "tank": 0.4, "healer": 0.2},
    "brawler": {"tank": 0.8, "dps": 0.6, "support": 0.4, "healer": 0.2},
    "entertainer": {"support": 0.9, "healer": 0.6, "dps": 0.3, "tank": 0.2},
    "artisan": {"support": 0.7, "dps": 0.4, "healer": 0.3, "tank": 0.2}
}
```

**Level Adjustments:**
- Level 90+: +0.1 to all roles
- Level < 70: -0.2 from all roles
- Preferred role: +0.2 bonus

---

## Entry Sequences

### Axkva Min Example

**Sequence Steps:**
1. **Travel to Location** - Travel to Dantooine Ruins (5000, -3000)
2. **Find Entrance** - Locate ancient temple entrance
3. **Use Key Fragments** - Use ancient key fragments (3 required)
4. **Enter Instance** - Enter Axkva Min heroic instance
5. **Navigate Corridors** - Navigate through temple corridors
6. **Reach Boss Room** - Reach main chamber where Axkva Min awaits

**Special Mechanics:**
- Dark Side Corruption - Reduces healing effectiveness
- Force Storm - Periodic area damage
- Mind Control - Random player becomes hostile

---

## Role Behaviors

### DPS Role
**Priorities:**
1. Maximize damage output
2. Target priority bosses
3. Avoid aggro management
4. Use damage cooldowns

**Actions:**
- Primary Attack (keybind: 1)
- Secondary Attack (keybind: 2)
- Damage Cooldown (keybind: 3)

### Healer Role
**Priorities:**
1. Maintain group health
2. Prioritize tank healing
3. Use healing cooldowns
4. Cleanse debuffs

**Actions:**
- Primary Heal (keybind: 1)
- Group Heal (keybind: 2)
- Cleanse (keybind: 3)

**Health Thresholds:**
- Tank health: 80%
- Group health: 60%
- Emergency heal: 30%

### Tank Role
**Priorities:**
1. Maintain aggro on boss
2. Position boss correctly
3. Use defensive cooldowns
4. Protect group members

**Actions:**
- Taunt (keybind: 1)
- Defensive Cooldown (keybind: 2)

### Support Role
**Priorities:**
1. Maintain group buffs
2. Debuff enemy targets
3. Provide utility abilities
4. Assist with healing

**Actions:**
- Group Buff (keybind: 1)
- Debuff Target (keybind: 2)

---

## Discord Integration

### Bot Commands

**Group Management:**
```bash
!heroic available                    # Show available heroics
!heroic form axkva_min normal       # Form group for Axkva Min
!heroic join group_123              # Join existing group
!heroic leave group_123             # Leave group
```

**Group Status:**
```bash
!group status                       # Show all groups
!group ready group_123              # Mark as ready
!group start group_123              # Start heroic
```

**Role Management:**
```bash
!role request dps                   # Request DPS role
!role assign bot_123 healer         # Assign role to bot
!role switch tank                   # Switch to tank role
```

**Status Updates:**
```bash
!status 0.8 0.9 dantooine axkva_min    # Update status
!heartbeat DemoCharacter                # Send heartbeat
```

### Multi-Bot Coordination

**Features:**
- Real-time group formation
- Automatic role assignment
- Status synchronization
- Group ready checks
- Heroic instance coordination

---

## Testing

### Test Coverage

**Test Classes:**
- `TestHeroicDetector` - Heroic detection and parsing
- `TestHeroicCoordinator` - Group formation and management
- `TestRoleBehaviorManager` - Role behaviors and actions
- `TestDiscordIntegration` - Discord integration functionality
- `TestIntegration` - Complete workflow testing

**Test Scenarios:**
- Heroic instance detection from `/heroiclock`
- Group formation and member management
- Role assignment for different professions/levels
- Entry sequence execution
- Role behavior execution
- Discord command parsing

### Demo Script

**Features Demonstrated:**
1. Heroic instance detection
2. Group formation for Axkva Min
3. Role assignment for group members
4. Entry sequence execution
5. Role-based behaviors
6. Discord integration capabilities

---

## Dependencies

### Required Packages
```python
# Core dependencies
import json
import yaml
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

# Discord integration
import discord
from discord.ext import commands
import aiohttp

# Android MS11 utilities
from android_ms11.utils.logging_utils import log_event
```

### External Dependencies
- `discord.py` - Discord bot functionality
- `aiohttp` - Async HTTP client for webhooks
- `pyyaml` - YAML file parsing
- `dataclasses` - Data structure definitions

---

## Future Enhancements

### Planned Features
1. **Advanced Combat AI** - Machine learning for combat optimization
2. **Dynamic Role Switching** - Automatic role switching based on group needs
3. **Voice Integration** - Voice commands for Discord coordination
4. **Advanced Analytics** - Performance tracking and optimization
5. **Cross-Server Coordination** - Multi-server heroic coordination

### Integration Points
1. **Combat System** - Integrate with existing combat modules
2. **Navigation System** - Integrate with travel/navigation modules
3. **Inventory System** - Check required items for heroics
4. **Quest System** - Track prerequisite quest completion
5. **Session Management** - Track heroic completion status

---

## Performance Considerations

### Optimization Strategies
1. **Caching** - Cache lockout status and heroic data
2. **Async Operations** - Use async for Discord and web operations
3. **Memory Management** - Clean up unused groups and data
4. **Error Handling** - Robust error handling for network operations

### Scalability
1. **Multiple Groups** - Support multiple concurrent groups
2. **Cross-Instance** - Coordinate across different heroic instances
3. **Load Balancing** - Distribute bots across different heroics
4. **Fault Tolerance** - Handle bot disconnections gracefully

---

## Security Considerations

### Discord Integration
1. **Token Security** - Secure storage of Discord bot tokens
2. **Permission Management** - Proper Discord bot permissions
3. **Rate Limiting** - Respect Discord API rate limits
4. **Error Handling** - Handle Discord API errors gracefully

### Data Protection
1. **Player Privacy** - Protect player information in Discord
2. **Group Security** - Secure group formation and management
3. **Logging** - Secure logging of coordination activities

---

## Conclusion

Batch 079 successfully implements a comprehensive heroics coordination system that enables MS11 to:

✅ **Detect available heroics** from `/heroiclock` command output  
✅ **Form and manage groups** with intelligent role assignment  
✅ **Execute entry sequences** for specific heroics (Axkva Min example)  
✅ **Implement role-based behaviors** for DPS, Healer, Tank, Support  
✅ **Coordinate with other bots** via Discord integration  
✅ **Support multiple heroics** with configurable difficulty tiers  

The system provides a solid foundation for automated heroic instance participation while maintaining flexibility for future enhancements and integrations. 