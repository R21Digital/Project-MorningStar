"""
Default Combat Profile

This module provides a sample combat profile for Rifleman or Brawler
with basic attack sequences and emergency abilities.
"""

import json
from pathlib import Path
from typing import Dict, Any


def create_default_rifleman_profile() -> Dict[str, Any]:
    """Create a default Rifleman combat profile."""
    return {
        "name": "default_rifleman",
        "description": "Default Rifleman combat profile with basic attack rotation",
        "build_type": "rifleman",
        "abilities": [
            "Rifle Shot",
            "Burst Shot",
            "Full Auto",
            "Precise Shot",
            "Suppressive Fire",
            "Reload"
        ],
        "ability_rotation": [
            "Rifle Shot",
            "Burst Shot",
            "Rifle Shot",
            "Precise Shot",
            "Full Auto"
        ],
        "emergency_abilities": {
            "reload": "Reload",
            "suppression": "Suppressive Fire"
        },
        "combat_priorities": {
            "player_health_threshold": 50,
            "target_health_threshold": 20,
            "ammo_threshold": 10
        },
        "cooldowns": {
            "Rifle Shot": 0,
            "Burst Shot": 5,
            "Full Auto": 15,
            "Precise Shot": 8,
            "Suppressive Fire": 12,
            "Reload": 0
        },
        "targeting": {
            "primary_target": "nearest_hostile",
            "max_range": 50,
            "switch_target_threshold": 20
        }
    }


def create_default_brawler_profile() -> Dict[str, Any]:
    """Create a default Brawler combat profile."""
    return {
        "name": "default_brawler",
        "description": "Default Brawler combat profile with melee attack rotation",
        "build_type": "brawler",
        "abilities": [
            "Punch",
            "Kick",
            "Uppercut",
            "Body Slam",
            "Dodge",
            "Block"
        ],
        "ability_rotation": [
            "Punch",
            "Kick",
            "Punch",
            "Uppercut",
            "Body Slam"
        ],
        "emergency_abilities": {
            "dodge": "Dodge",
            "block": "Block"
        },
        "combat_priorities": {
            "player_health_threshold": 40,
            "target_health_threshold": 15,
            "stamina_threshold": 20
        },
        "cooldowns": {
            "Punch": 0,
            "Kick": 3,
            "Uppercut": 8,
            "Body Slam": 12,
            "Dodge": 5,
            "Block": 2
        },
        "targeting": {
            "primary_target": "nearest_hostile",
            "max_range": 5,
            "switch_target_threshold": 25
        }
    }


def create_default_hybrid_profile() -> Dict[str, Any]:
    """Create a default hybrid combat profile (Rifleman + Medic)."""
    return {
        "name": "default_hybrid",
        "description": "Default hybrid combat profile with rifle and healing abilities",
        "build_type": "hybrid",
        "abilities": [
            "Rifle Shot",
            "Burst Shot",
            "Heal Self",
            "Heal Other",
            "Cure Poison",
            "Stim Pack"
        ],
        "ability_rotation": [
            "Rifle Shot",
            "Burst Shot",
            "Rifle Shot"
        ],
        "emergency_abilities": {
            "critical_heal": "Heal Self",
            "emergency_stim": "Stim Pack",
            "poison_cure": "Cure Poison"
        },
        "combat_priorities": {
            "player_health_threshold": 30,
            "target_health_threshold": 20,
            "heal_other_threshold": 50
        },
        "cooldowns": {
            "Rifle Shot": 0,
            "Burst Shot": 5,
            "Heal Self": 30,
            "Heal Other": 45,
            "Cure Poison": 60,
            "Stim Pack": 120
        },
        "targeting": {
            "primary_target": "nearest_hostile",
            "heal_target": "lowest_health_ally",
            "max_range": 50
        }
    }


def save_profile(profile_data: Dict[str, Any], filename: str):
    """Save a combat profile to JSON file."""
    try:
        profiles_dir = Path("profiles/combat")
        profiles_dir.mkdir(parents=True, exist_ok=True)
        
        profile_file = profiles_dir / f"{filename}.json"
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
        
        print(f"✅ Saved combat profile: {filename}")
        
    except Exception as e:
        print(f"❌ Error saving profile {filename}: {e}")


def create_all_default_profiles():
    """Create all default combat profiles."""
    profiles = [
        ("default_rifleman", create_default_rifleman_profile()),
        ("default_brawler", create_default_brawler_profile()),
        ("default_hybrid", create_default_hybrid_profile())
    ]
    
    for filename, profile_data in profiles:
        save_profile(profile_data, filename)
    
    print("✅ Created all default combat profiles")


if __name__ == "__main__":
    create_all_default_profiles() 