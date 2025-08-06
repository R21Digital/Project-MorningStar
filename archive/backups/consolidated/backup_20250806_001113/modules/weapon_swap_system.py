"""Weapon Swap + Loadout Handling System

This module provides dynamic weapon switching based on:
- Enemy type and resistances
- Combat distance and range
- Weapon condition and ammo
- Manual override options
- Weapon effectiveness tracking
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from android_ms11.utils.logging_utils import log_event


class WeaponType(Enum):
    """Enumeration of weapon types."""
    RIFLE = "rifle"
    CARBINE = "carbine"
    PISTOL = "pistol"
    MELEE = "melee"
    HEAVY = "heavy"
    SPECIAL = "special"


class DamageType(Enum):
    """Enumeration of damage types."""
    KINETIC = "kinetic"
    ENERGY = "energy"
    EXPLOSIVE = "explosive"
    MELEE = "melee"
    SPECIAL = "special"


@dataclass
class WeaponStats:
    """Represents weapon statistics and capabilities."""
    name: str
    weapon_type: WeaponType
    damage_type: DamageType
    base_damage: int
    range: int
    accuracy: float
    fire_rate: float
    ammo_capacity: int
    reload_time: float
    condition: float = 100.0  # Percentage
    current_ammo: int = 0
    last_used: Optional[str] = None


@dataclass
class EnemyResistance:
    """Represents enemy resistance to different damage types."""
    enemy_type: str
    kinetic_resistance: float = 0.0
    energy_resistance: float = 0.0
    explosive_resistance: float = 0.0
    melee_resistance: float = 0.0
    special_resistance: float = 0.0


@dataclass
class WeaponLoadout:
    """Represents a complete weapon loadout."""
    name: str
    description: str
    primary_weapon: str
    secondary_weapon: str
    melee_weapon: Optional[str] = None
    special_weapon: Optional[str] = None
    auto_swap_enabled: bool = True
    priority_rules: Dict[str, Any] = None


@dataclass
class WeaponSwapEvent:
    """Represents a weapon swap event for logging."""
    timestamp: str
    from_weapon: str
    to_weapon: str
    reason: str
    combat_context: Dict[str, Any]
    effectiveness_score: float


class WeaponSwapSystem:
    """Handles dynamic weapon switching based on combat conditions."""
    
    def __init__(self, config_path: str = "config/weapon_config.json"):
        """Initialize the weapon swap system.
        
        Parameters
        ----------
        config_path : str
            Path to weapon configuration file
        """
        self.config_path = Path(config_path)
        self.weapons: Dict[str, WeaponStats] = {}
        self.loadouts: Dict[str, WeaponLoadout] = {}
        self.enemy_resistances: Dict[str, EnemyResistance] = {}
        self.current_loadout: Optional[str] = None
        self.current_weapon: Optional[str] = None
        
        # Weapon history and effectiveness tracking
        self.weapon_history: List[WeaponSwapEvent] = []
        self.weapon_effectiveness: Dict[str, Dict[str, float]] = {}
        
        # Combat context
        self.combat_context = {
            "enemy_type": None,
            "distance": None,
            "enemy_health": None,
            "player_health": None,
            "ammo_status": {},
            "weapon_conditions": {}
        }
        
        # Load configuration
        self._load_weapon_config()
        self._load_enemy_resistances()
        
        log_event("[WEAPON_SWAP] Weapon swap system initialized")
    
    def _load_weapon_config(self):
        """Load weapon configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                # Load weapons
                weapons_data = config.get("weapons", {})
                for name, weapon_data in weapons_data.items():
                    self.weapons[name] = WeaponStats(
                        name=name,
                        weapon_type=WeaponType(weapon_data.get("weapon_type", "rifle")),
                        damage_type=DamageType(weapon_data.get("damage_type", "kinetic")),
                        base_damage=weapon_data.get("base_damage", 10),
                        range=weapon_data.get("range", 50),
                        accuracy=weapon_data.get("accuracy", 0.8),
                        fire_rate=weapon_data.get("fire_rate", 1.0),
                        ammo_capacity=weapon_data.get("ammo_capacity", 30),
                        reload_time=weapon_data.get("reload_time", 2.0),
                        condition=weapon_data.get("condition", 100.0),
                        current_ammo=weapon_data.get("current_ammo", 30)
                    )
                
                # Load loadouts
                loadouts_data = config.get("loadouts", {})
                for name, loadout_data in loadouts_data.items():
                    self.loadouts[name] = WeaponLoadout(
                        name=name,
                        description=loadout_data.get("description", ""),
                        primary_weapon=loadout_data.get("primary_weapon"),
                        secondary_weapon=loadout_data.get("secondary_weapon"),
                        melee_weapon=loadout_data.get("melee_weapon"),
                        special_weapon=loadout_data.get("special_weapon"),
                        auto_swap_enabled=loadout_data.get("auto_swap_enabled", True),
                        priority_rules=loadout_data.get("priority_rules", {})
                    )
                
                log_event(f"[WEAPON_SWAP] Loaded {len(self.weapons)} weapons and {len(self.loadouts)} loadouts")
            else:
                log_event("[WEAPON_SWAP] No weapon config file found, creating default")
                self._create_default_config()
                
        except Exception as e:
            log_event(f"[WEAPON_SWAP] Error loading weapon config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create a default weapon configuration."""
        default_config = {
            "weapons": {
                "rifle_standard": {
                    "weapon_type": "rifle",
                    "damage_type": "kinetic",
                    "base_damage": 25,
                    "range": 100,
                    "accuracy": 0.85,
                    "fire_rate": 1.0,
                    "ammo_capacity": 30,
                    "reload_time": 2.5,
                    "condition": 100.0,
                    "current_ammo": 30
                },
                "carbine_rapid": {
                    "weapon_type": "carbine",
                    "damage_type": "kinetic",
                    "base_damage": 18,
                    "range": 60,
                    "accuracy": 0.75,
                    "fire_rate": 1.5,
                    "ammo_capacity": 25,
                    "reload_time": 2.0,
                    "condition": 100.0,
                    "current_ammo": 25
                },
                "pistol_backup": {
                    "weapon_type": "pistol",
                    "damage_type": "kinetic",
                    "base_damage": 12,
                    "range": 30,
                    "accuracy": 0.8,
                    "fire_rate": 0.8,
                    "ammo_capacity": 15,
                    "reload_time": 1.5,
                    "condition": 100.0,
                    "current_ammo": 15
                },
                "energy_rifle": {
                    "weapon_type": "rifle",
                    "damage_type": "energy",
                    "base_damage": 30,
                    "range": 80,
                    "accuracy": 0.9,
                    "fire_rate": 0.7,
                    "ammo_capacity": 20,
                    "reload_time": 3.0,
                    "condition": 100.0,
                    "current_ammo": 20
                }
            },
            "loadouts": {
                "rifleman_standard": {
                    "description": "Standard rifleman loadout with rifle and carbine",
                    "primary_weapon": "rifle_standard",
                    "secondary_weapon": "carbine_rapid",
                    "auto_swap_enabled": True,
                    "priority_rules": {
                        "distance_based": True,
                        "enemy_resistance": True,
                        "ammo_management": True
                    }
                },
                "energy_specialist": {
                    "description": "Energy weapon specialist loadout",
                    "primary_weapon": "energy_rifle",
                    "secondary_weapon": "pistol_backup",
                    "auto_swap_enabled": True,
                    "priority_rules": {
                        "distance_based": True,
                        "enemy_resistance": True,
                        "ammo_management": True
                    }
                }
            }
        }
        
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        log_event(f"[WEAPON_SWAP] Created default config at {self.config_path}")
    
    def _load_enemy_resistances(self):
        """Load enemy resistance data."""
        # Default enemy resistances
        self.enemy_resistances = {
            "stormtrooper": EnemyResistance(
                enemy_type="stormtrooper",
                kinetic_resistance=0.1,
                energy_resistance=0.3,
                explosive_resistance=0.2,
                melee_resistance=0.0
            ),
            "droid": EnemyResistance(
                enemy_type="droid",
                kinetic_resistance=0.2,
                energy_resistance=0.1,
                explosive_resistance=0.4,
                melee_resistance=0.3
            ),
            "beast": EnemyResistance(
                enemy_type="beast",
                kinetic_resistance=0.0,
                energy_resistance=0.1,
                explosive_resistance=0.3,
                melee_resistance=0.2
            ),
            "boss": EnemyResistance(
                enemy_type="boss",
                kinetic_resistance=0.3,
                energy_resistance=0.2,
                explosive_resistance=0.1,
                melee_resistance=0.4
            )
        }
    
    def set_combat_context(self, enemy_type: str = None, distance: float = None, 
                          enemy_health: int = None, player_health: int = None,
                          ammo_status: Dict[str, int] = None, weapon_conditions: Dict[str, float] = None):
        """Update the current combat context.
        
        Parameters
        ----------
        enemy_type : str, optional
            Type of enemy being fought
        distance : float, optional
            Distance to enemy in meters
        enemy_health : int, optional
            Current enemy health percentage
        player_health : int, optional
            Current player health percentage
        ammo_status : dict, optional
            Current ammo counts for weapons
        weapon_conditions : dict, optional
            Current condition percentages for weapons
        """
        if enemy_type is not None:
            self.combat_context["enemy_type"] = enemy_type
        if distance is not None:
            self.combat_context["distance"] = distance
        if enemy_health is not None:
            self.combat_context["enemy_health"] = enemy_health
        if player_health is not None:
            self.combat_context["player_health"] = player_health
        if ammo_status is not None:
            self.combat_context["ammo_status"] = ammo_status
        if weapon_conditions is not None:
            self.combat_context["weapon_conditions"] = weapon_conditions
    
    def load_loadout(self, loadout_name: str) -> bool:
        """Load a specific weapon loadout.
        
        Parameters
        ----------
        loadout_name : str
            Name of the loadout to load
            
        Returns
        -------
        bool
            True if loadout loaded successfully, False otherwise
        """
        if loadout_name not in self.loadouts:
            log_event(f"[WEAPON_SWAP] Loadout not found: {loadout_name}")
            return False
        
        self.current_loadout = loadout_name
        loadout = self.loadouts[loadout_name]
        self.current_weapon = loadout.primary_weapon
        
        log_event(f"[WEAPON_SWAP] Loaded loadout: {loadout_name}")
        log_event(f"[WEAPON_SWAP] Primary weapon: {loadout.primary_weapon}")
        log_event(f"[WEAPON_SWAP] Secondary weapon: {loadout.secondary_weapon}")
        
        return True
    
    def get_available_weapons(self) -> List[str]:
        """Get list of available weapons in current loadout."""
        if not self.current_loadout:
            return []
        
        loadout = self.loadouts[self.current_loadout]
        weapons = [loadout.primary_weapon, loadout.secondary_weapon]
        if loadout.melee_weapon:
            weapons.append(loadout.melee_weapon)
        if loadout.special_weapon:
            weapons.append(loadout.special_weapon)
        
        return [w for w in weapons if w in self.weapons]
    
    def calculate_weapon_effectiveness(self, weapon_name: str, enemy_type: str = None, 
                                     distance: float = None) -> float:
        """Calculate weapon effectiveness against current enemy and conditions.
        
        Parameters
        ----------
        weapon_name : str
            Name of the weapon to evaluate
        enemy_type : str, optional
            Type of enemy (uses current context if not provided)
        distance : float, optional
            Distance to enemy (uses current context if not provided)
            
        Returns
        -------
        float
            Effectiveness score (0.0 to 1.0)
        """
        if weapon_name not in self.weapons:
            return 0.0
        
        weapon = self.weapons[weapon_name]
        enemy_type = enemy_type or self.combat_context.get("enemy_type", "unknown")
        distance = distance or self.combat_context.get("distance", 50.0)
        
        # Base effectiveness
        effectiveness = 1.0
        
        # Range effectiveness
        if distance > weapon.range:
            effectiveness *= 0.3  # Out of range penalty
        elif distance < weapon.range * 0.3:
            effectiveness *= 0.8  # Too close penalty for ranged weapons
        
        # Enemy resistance
        if enemy_type in self.enemy_resistances:
            resistance = self.enemy_resistances[enemy_type]
            damage_type = weapon.damage_type.value
            
            if damage_type == "kinetic":
                effectiveness *= (1.0 - resistance.kinetic_resistance)
            elif damage_type == "energy":
                effectiveness *= (1.0 - resistance.energy_resistance)
            elif damage_type == "explosive":
                effectiveness *= (1.0 - resistance.explosive_resistance)
            elif damage_type == "melee":
                effectiveness *= (1.0 - resistance.melee_resistance)
        
        # Weapon condition
        effectiveness *= (weapon.condition / 100.0)
        
        # Ammo availability
        if weapon.current_ammo == 0:
            effectiveness *= 0.1  # No ammo penalty
        
        return max(0.0, min(1.0, effectiveness))
    
    def get_best_weapon(self, enemy_type: str = None, distance: float = None) -> Optional[str]:
        """Get the best weapon for current combat conditions.
        
        Parameters
        ----------
        enemy_type : str, optional
            Type of enemy (uses current context if not provided)
        distance : float, optional
            Distance to enemy (uses current context if not provided)
            
        Returns
        -------
        str or None
            Name of the best weapon, or None if no suitable weapon
        """
        available_weapons = self.get_available_weapons()
        if not available_weapons:
            return None
        
        best_weapon = None
        best_score = 0.0
        
        for weapon_name in available_weapons:
            score = self.calculate_weapon_effectiveness(weapon_name, enemy_type, distance)
            if score > best_score:
                best_score = score
                best_weapon = weapon_name
        
        return best_weapon
    
    def should_swap_weapon(self, enemy_type: str = None, distance: float = None, 
                          min_improvement: float = 0.2) -> Tuple[bool, Optional[str]]:
        """Determine if weapon should be swapped based on current conditions.
        
        Parameters
        ----------
        enemy_type : str, optional
            Type of enemy (uses current context if not provided)
        distance : float, optional
            Distance to enemy (uses current context if not provided)
        min_improvement : float
            Minimum effectiveness improvement required to swap
            
        Returns
        -------
        tuple
            (should_swap, best_weapon_name)
        """
        if not self.current_weapon:
            return False, None
        
        # Check if auto-swap is enabled
        if self.current_loadout and not self.loadouts[self.current_loadout].auto_swap_enabled:
            return False, None
        
        # Calculate current weapon effectiveness
        current_effectiveness = self.calculate_weapon_effectiveness(
            self.current_weapon, enemy_type, distance
        )
        
        # Find best weapon
        best_weapon = self.get_best_weapon(enemy_type, distance)
        if not best_weapon or best_weapon == self.current_weapon:
            return False, None
        
        # Calculate best weapon effectiveness
        best_effectiveness = self.calculate_weapon_effectiveness(
            best_weapon, enemy_type, distance
        )
        
        # Check if improvement is significant enough
        improvement = best_effectiveness - current_effectiveness
        should_swap = improvement >= min_improvement
        
        return should_swap, best_weapon
    
    def swap_weapon(self, weapon_name: str, reason: str = "manual") -> bool:
        """Swap to a specific weapon.
        
        Parameters
        ----------
        weapon_name : str
            Name of the weapon to swap to
        reason : str
            Reason for the swap (manual, auto, emergency, etc.)
            
        Returns
        -------
        bool
            True if swap successful, False otherwise
        """
        if weapon_name not in self.weapons:
            log_event(f"[WEAPON_SWAP] Weapon not found: {weapon_name}")
            return False
        
        if weapon_name not in self.get_available_weapons():
            log_event(f"[WEAPON_SWAP] Weapon not available in current loadout: {weapon_name}")
            return False
        
        old_weapon = self.current_weapon
        self.current_weapon = weapon_name
        
        # Log the swap event
        swap_event = WeaponSwapEvent(
            timestamp=datetime.now().isoformat(),
            from_weapon=old_weapon or "none",
            to_weapon=weapon_name,
            reason=reason,
            combat_context=self.combat_context.copy(),
            effectiveness_score=self.calculate_weapon_effectiveness(weapon_name)
        )
        self.weapon_history.append(swap_event)
        
        log_event(f"[WEAPON_SWAP] Swapped from {old_weapon} to {weapon_name} ({reason})")
        
        return True
    
    def auto_swap_weapon(self, enemy_type: str = None, distance: float = None) -> bool:
        """Automatically swap to the best weapon for current conditions.
        
        Parameters
        ----------
        enemy_type : str, optional
            Type of enemy (uses current context if not provided)
        distance : float, optional
            Distance to enemy (uses current context if not provided)
            
        Returns
        -------
        bool
            True if weapon was swapped, False otherwise
        """
        should_swap, best_weapon = self.should_swap_weapon(enemy_type, distance)
        
        if should_swap and best_weapon:
            return self.swap_weapon(best_weapon, "auto")
        
        return False
    
    def get_weapon_stats(self, weapon_name: str) -> Optional[WeaponStats]:
        """Get weapon statistics.
        
        Parameters
        ----------
        weapon_name : str
            Name of the weapon
            
        Returns
        -------
        WeaponStats or None
            Weapon statistics if found
        """
        return self.weapons.get(weapon_name)
    
    def update_weapon_ammo(self, weapon_name: str, ammo_count: int):
        """Update weapon ammo count.
        
        Parameters
        ----------
        weapon_name : str
            Name of the weapon
        ammo_count : int
            New ammo count
        """
        if weapon_name in self.weapons:
            self.weapons[weapon_name].current_ammo = max(0, ammo_count)
            log_event(f"[WEAPON_SWAP] Updated {weapon_name} ammo: {ammo_count}")
    
    def update_weapon_condition(self, weapon_name: str, condition: float):
        """Update weapon condition.
        
        Parameters
        ----------
        weapon_name : str
            Name of the weapon
        condition : float
            New condition percentage (0-100)
        """
        if weapon_name in self.weapons:
            self.weapons[weapon_name].condition = max(0.0, min(100.0, condition))
            log_event(f"[WEAPON_SWAP] Updated {weapon_name} condition: {condition}%")
    
    def get_weapon_history(self, limit: int = 10) -> List[WeaponSwapEvent]:
        """Get recent weapon swap history.
        
        Parameters
        ----------
        limit : int
            Maximum number of events to return
            
        Returns
        -------
        list
            List of recent weapon swap events
        """
        return self.weapon_history[-limit:] if self.weapon_history else []
    
    def get_weapon_effectiveness_stats(self) -> Dict[str, Dict[str, float]]:
        """Get weapon effectiveness statistics.
        
        Returns
        -------
        dict
            Weapon effectiveness statistics by weapon and enemy type
        """
        stats = {}
        
        for weapon_name in self.weapons:
            stats[weapon_name] = {}
            for enemy_type in self.enemy_resistances:
                effectiveness = self.calculate_weapon_effectiveness(weapon_name, enemy_type)
                stats[weapon_name][enemy_type] = effectiveness
        
        return stats
    
    def export_weapon_data(self, filepath: str = None) -> str:
        """Export weapon data to JSON file.
        
        Parameters
        ----------
        filepath : str, optional
            Path to save the export file
            
        Returns
        -------
        str
            Path to the exported file
        """
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"logs/weapon_data_{timestamp}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "current_loadout": self.current_loadout,
            "current_weapon": self.current_weapon,
            "weapons": {name: asdict(weapon) for name, weapon in self.weapons.items()},
            "loadouts": {name: asdict(loadout) for name, loadout in self.loadouts.items()},
            "enemy_resistances": {name: asdict(resistance) for name, resistance in self.enemy_resistances.items()},
            "weapon_history": [asdict(event) for event in self.weapon_history],
            "effectiveness_stats": self.get_weapon_effectiveness_stats(),
            "combat_context": self.combat_context
        }
        
        Path(filepath).parent.mkdir(exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        log_event(f"[WEAPON_SWAP] Exported weapon data to {filepath}")
        return filepath 