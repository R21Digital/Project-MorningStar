"""Ship upgrade manager for tiered ship progression system."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from utils.logging_utils import log_event


class ShipTier(Enum):
    """Ship tier levels."""
    TIER_1 = "tier_1"  # Basic ships
    TIER_2 = "tier_2"  # Improved ships
    TIER_3 = "tier_3"  # Advanced ships
    TIER_4 = "tier_4"  # Elite ships
    TIER_5 = "tier_5"  # Legendary ships


class UpgradeType(Enum):
    """Types of ship upgrades."""
    WEAPONS = "weapons"
    SHIELDS = "shields"
    ENGINES = "engines"
    HULL = "hull"
    SYSTEMS = "systems"
    SPECIAL = "special"


class UpgradeRarity(Enum):
    """Upgrade rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class ShipUpgrade:
    """Represents a ship upgrade."""
    upgrade_id: str
    name: str
    upgrade_type: UpgradeType
    rarity: UpgradeRarity
    tier: ShipTier
    description: str
    stats: Dict[str, float]
    requirements: Dict[str, Any]
    cost: Dict[str, int]
    unlock_conditions: Dict[str, Any]
    is_unlocked: bool = False
    is_installed: bool = False


@dataclass
class ShipClass:
    """Represents a ship class with upgrade slots."""
    name: str
    ship_type: str
    base_tier: ShipTier
    max_tier: ShipTier
    upgrade_slots: Dict[UpgradeType, int]
    base_stats: Dict[str, float]
    current_stats: Dict[str, float]
    installed_upgrades: Dict[str, str]  # slot_id -> upgrade_id
    unlock_requirements: Dict[str, Any]
    is_unlocked: bool = False


@dataclass
class UpgradeProgress:
    """Tracks upgrade progress for a ship."""
    ship_name: str
    current_tier: ShipTier
    upgrade_points: int
    max_upgrade_points: int
    completed_upgrades: List[str]
    available_upgrades: List[str]
    next_tier_requirements: Dict[str, Any]


class ShipUpgradeManager:
    """Manage ship upgrades and tiered progression."""
    
    def __init__(self, config_path: str = "config/space_config.json"):
        """Initialize the ship upgrade manager.
        
        Parameters
        ----------
        config_path : str
            Path to space configuration file
        """
        self.config = self._load_config(config_path)
        self.ship_classes: Dict[str, ShipClass] = {}
        self.upgrades: Dict[str, ShipUpgrade] = {}
        self.upgrade_progress: Dict[str, UpgradeProgress] = {}
        
        # Load upgrade data
        self._load_upgrade_data()
        self._initialize_ship_classes()
        self._initialize_upgrades()
        
        # Upgrade tracking
        self.upgrade_history: List[Dict[str, Any]] = []
        self.last_upgrade_check = time.time()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load space configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _load_upgrade_data(self) -> None:
        """Load ship upgrade data."""
        data_file = Path("data/space_quests/ship_upgrades.json")
        if data_file.exists():
            try:
                with data_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._parse_upgrade_data(data)
            except Exception as e:
                log_event(f"[SHIP_UPGRADES] Error loading upgrade data: {e}")
    
    def _parse_upgrade_data(self, data: Dict[str, Any]) -> None:
        """Parse ship upgrade data from JSON."""
        # Parse ship classes
        for ship_data in data.get("ship_classes", []):
            ship_class = ShipClass(
                name=ship_data["name"],
                ship_type=ship_data["ship_type"],
                base_tier=ShipTier(ship_data["base_tier"]),
                max_tier=ShipTier(ship_data["max_tier"]),
                upgrade_slots={UpgradeType(k): v for k, v in ship_data["upgrade_slots"].items()},
                base_stats=ship_data["base_stats"],
                current_stats=ship_data["base_stats"].copy(),
                installed_upgrades=ship_data.get("installed_upgrades", {}),
                unlock_requirements=ship_data.get("unlock_requirements", {}),
                is_unlocked=ship_data.get("is_unlocked", False)
            )
            self.ship_classes[ship_class.name] = ship_class
        
        # Parse upgrades
        for upgrade_data in data.get("upgrades", []):
            upgrade = ShipUpgrade(
                upgrade_id=upgrade_data["upgrade_id"],
                name=upgrade_data["name"],
                upgrade_type=UpgradeType(upgrade_data["upgrade_type"]),
                rarity=UpgradeRarity(upgrade_data["rarity"]),
                tier=ShipTier(upgrade_data["tier"]),
                description=upgrade_data["description"],
                stats=upgrade_data["stats"],
                requirements=upgrade_data["requirements"],
                cost=upgrade_data["cost"],
                unlock_conditions=upgrade_data.get("unlock_conditions", {}),
                is_unlocked=upgrade_data.get("is_unlocked", False),
                is_installed=upgrade_data.get("is_installed", False)
            )
            self.upgrades[upgrade.upgrade_id] = upgrade
    
    def _initialize_ship_classes(self) -> None:
        """Initialize default ship classes."""
        # Tier 1 - Basic Ships
        basic_fighter = ShipClass(
            name="Basic Fighter",
            ship_type="fighter",
            base_tier=ShipTier.TIER_1,
            max_tier=ShipTier.TIER_3,
            upgrade_slots={
                UpgradeType.WEAPONS: 2,
                UpgradeType.SHIELDS: 1,
                UpgradeType.ENGINES: 1,
                UpgradeType.HULL: 1,
                UpgradeType.SYSTEMS: 1
            },
            base_stats={
                "health": 100,
                "shield": 50,
                "damage": 25,
                "speed": 100,
                "maneuverability": 80,
                "cargo_capacity": 50
            },
            current_stats={
                "health": 100,
                "shield": 50,
                "damage": 25,
                "speed": 100,
                "maneuverability": 80,
                "cargo_capacity": 50
            },
            installed_upgrades={},
            unlock_requirements={"level": 1, "credits": 1000},
            is_unlocked=True
        )
        self.ship_classes["Basic Fighter"] = basic_fighter
        
        # Tier 2 - Improved Ships
        advanced_fighter = ShipClass(
            name="Advanced Fighter",
            ship_type="fighter",
            base_tier=ShipTier.TIER_2,
            max_tier=ShipTier.TIER_4,
            upgrade_slots={
                UpgradeType.WEAPONS: 3,
                UpgradeType.SHIELDS: 2,
                UpgradeType.ENGINES: 2,
                UpgradeType.HULL: 2,
                UpgradeType.SYSTEMS: 2,
                UpgradeType.SPECIAL: 1
            },
            base_stats={
                "health": 150,
                "shield": 75,
                "damage": 40,
                "speed": 120,
                "maneuverability": 90,
                "cargo_capacity": 75
            },
            current_stats={
                "health": 150,
                "shield": 75,
                "damage": 40,
                "speed": 120,
                "maneuverability": 90,
                "cargo_capacity": 75
            },
            installed_upgrades={},
            unlock_requirements={"level": 10, "credits": 5000, "reputation": 100},
            is_unlocked=False
        )
        self.ship_classes["Advanced Fighter"] = advanced_fighter
        
        # Tier 3 - Advanced Ships
        elite_fighter = ShipClass(
            name="Elite Fighter",
            ship_type="fighter",
            base_tier=ShipTier.TIER_3,
            max_tier=ShipTier.TIER_5,
            upgrade_slots={
                UpgradeType.WEAPONS: 4,
                UpgradeType.SHIELDS: 3,
                UpgradeType.ENGINES: 3,
                UpgradeType.HULL: 3,
                UpgradeType.SYSTEMS: 3,
                UpgradeType.SPECIAL: 2
            },
            base_stats={
                "health": 200,
                "shield": 100,
                "damage": 60,
                "speed": 140,
                "maneuverability": 100,
                "cargo_capacity": 100
            },
            current_stats={
                "health": 200,
                "shield": 100,
                "damage": 60,
                "speed": 140,
                "maneuverability": 100,
                "cargo_capacity": 100
            },
            installed_upgrades={},
            unlock_requirements={"level": 25, "credits": 15000, "reputation": 500},
            is_unlocked=False
        )
        self.ship_classes["Elite Fighter"] = elite_fighter
    
    def _initialize_upgrades(self) -> None:
        """Initialize default ship upgrades."""
        # Tier 1 Upgrades
        tier1_upgrades = [
            {
                "upgrade_id": "basic_weapon_001",
                "name": "Basic Weapon Array",
                "upgrade_type": UpgradeType.WEAPONS,
                "rarity": UpgradeRarity.COMMON,
                "tier": ShipTier.TIER_1,
                "description": "Standard weapon system for basic combat",
                "stats": {"damage": 10},
                "requirements": {"ship_tier": ShipTier.TIER_1},
                "cost": {"credits": 500},
                "unlock_conditions": {"level": 1}
            },
            {
                "upgrade_id": "basic_shield_001",
                "name": "Basic Shield Generator",
                "upgrade_type": UpgradeType.SHIELDS,
                "rarity": UpgradeRarity.COMMON,
                "tier": ShipTier.TIER_1,
                "description": "Standard shield system for basic protection",
                "stats": {"shield": 15},
                "requirements": {"ship_tier": ShipTier.TIER_1},
                "cost": {"credits": 400},
                "unlock_conditions": {"level": 1}
            },
            {
                "upgrade_id": "basic_engine_001",
                "name": "Basic Engine Array",
                "upgrade_type": UpgradeType.ENGINES,
                "rarity": UpgradeRarity.COMMON,
                "tier": ShipTier.TIER_1,
                "description": "Standard engine system for basic mobility",
                "stats": {"speed": 15, "maneuverability": 10},
                "requirements": {"ship_tier": ShipTier.TIER_1},
                "cost": {"credits": 300},
                "unlock_conditions": {"level": 1}
            }
        ]
        
        # Tier 2 Upgrades
        tier2_upgrades = [
            {
                "upgrade_id": "advanced_weapon_001",
                "name": "Advanced Weapon Array",
                "upgrade_type": UpgradeType.WEAPONS,
                "rarity": UpgradeRarity.UNCOMMON,
                "tier": ShipTier.TIER_2,
                "description": "Enhanced weapon system for improved combat",
                "stats": {"damage": 20},
                "requirements": {"ship_tier": ShipTier.TIER_2},
                "cost": {"credits": 1000},
                "unlock_conditions": {"level": 10}
            },
            {
                "upgrade_id": "advanced_shield_001",
                "name": "Advanced Shield Generator",
                "upgrade_type": UpgradeType.SHIELDS,
                "rarity": UpgradeRarity.UNCOMMON,
                "tier": ShipTier.TIER_2,
                "description": "Enhanced shield system for improved protection",
                "stats": {"shield": 30},
                "requirements": {"ship_tier": ShipTier.TIER_2},
                "cost": {"credits": 800},
                "unlock_conditions": {"level": 10}
            },
            {
                "upgrade_id": "advanced_engine_001",
                "name": "Advanced Engine Array",
                "upgrade_type": UpgradeType.ENGINES,
                "rarity": UpgradeRarity.UNCOMMON,
                "tier": ShipTier.TIER_2,
                "description": "Enhanced engine system for improved mobility",
                "stats": {"speed": 25, "maneuverability": 20},
                "requirements": {"ship_tier": ShipTier.TIER_2},
                "cost": {"credits": 600},
                "unlock_conditions": {"level": 10}
            }
        ]
        
        # Tier 3 Upgrades
        tier3_upgrades = [
            {
                "upgrade_id": "elite_weapon_001",
                "name": "Elite Weapon Array",
                "upgrade_type": UpgradeType.WEAPONS,
                "rarity": UpgradeRarity.RARE,
                "tier": ShipTier.TIER_3,
                "description": "Elite weapon system for superior combat",
                "stats": {"damage": 35},
                "requirements": {"ship_tier": ShipTier.TIER_3},
                "cost": {"credits": 2000},
                "unlock_conditions": {"level": 25}
            },
            {
                "upgrade_id": "elite_shield_001",
                "name": "Elite Shield Generator",
                "upgrade_type": UpgradeType.SHIELDS,
                "rarity": UpgradeRarity.RARE,
                "tier": ShipTier.TIER_3,
                "description": "Elite shield system for superior protection",
                "stats": {"shield": 50},
                "requirements": {"ship_tier": ShipTier.TIER_3},
                "cost": {"credits": 1500},
                "unlock_conditions": {"level": 25}
            },
            {
                "upgrade_id": "elite_engine_001",
                "name": "Elite Engine Array",
                "upgrade_type": UpgradeType.ENGINES,
                "rarity": UpgradeRarity.RARE,
                "tier": ShipTier.TIER_3,
                "description": "Elite engine system for superior mobility",
                "stats": {"speed": 40, "maneuverability": 30},
                "requirements": {"ship_tier": ShipTier.TIER_3},
                "cost": {"credits": 1200},
                "unlock_conditions": {"level": 25}
            }
        ]
        
        # Special Upgrades
        special_upgrades = [
            {
                "upgrade_id": "stealth_system_001",
                "name": "Stealth System",
                "upgrade_type": UpgradeType.SPECIAL,
                "rarity": UpgradeRarity.EPIC,
                "tier": ShipTier.TIER_2,
                "description": "Advanced stealth system for covert operations",
                "stats": {"stealth": 50, "maneuverability": 15},
                "requirements": {"ship_tier": ShipTier.TIER_2, "reputation": 200},
                "cost": {"credits": 3000},
                "unlock_conditions": {"level": 15, "reputation": 200}
            },
            {
                "upgrade_id": "advanced_targeting_001",
                "name": "Advanced Targeting System",
                "upgrade_type": UpgradeType.SPECIAL,
                "rarity": UpgradeRarity.EPIC,
                "tier": ShipTier.TIER_3,
                "description": "Advanced targeting system for improved accuracy",
                "stats": {"accuracy": 25, "damage": 10},
                "requirements": {"ship_tier": ShipTier.TIER_3, "combat_rating": 3},
                "cost": {"credits": 4000},
                "unlock_conditions": {"level": 30, "combat_rating": 3}
            }
        ]
        
        # Create all upgrades
        all_upgrades = tier1_upgrades + tier2_upgrades + tier3_upgrades + special_upgrades
        
        for upgrade_data in all_upgrades:
            upgrade = ShipUpgrade(**upgrade_data)
            self.upgrades[upgrade.upgrade_id] = upgrade
    
    def get_ship_class(self, ship_name: str) -> Optional[ShipClass]:
        """Get a specific ship class.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship class
            
        Returns
        -------
        ShipClass, optional
            Ship class or None if not found
        """
        return self.ship_classes.get(ship_name)
    
    def get_available_ships(self) -> List[ShipClass]:
        """Get all available ship classes.
        
        Returns
        -------
        List[ShipClass]
            List of all available ship classes
        """
        return list(self.ship_classes.values())
    
    def get_unlocked_ships(self) -> List[ShipClass]:
        """Get all unlocked ship classes.
        
        Returns
        -------
        List[ShipClass]
            List of unlocked ship classes
        """
        return [ship for ship in self.ship_classes.values() if ship.is_unlocked]
    
    def unlock_ship(self, ship_name: str, player_stats: Dict[str, Any]) -> bool:
        """Attempt to unlock a ship class.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship to unlock
        player_stats : Dict[str, Any]
            Player statistics for requirement checking
            
        Returns
        -------
        bool
            True if ship was unlocked successfully
        """
        if ship_name not in self.ship_classes:
            return False
        
        ship = self.ship_classes[ship_name]
        
        if ship.is_unlocked:
            return True
        
        # Check unlock requirements
        if self._check_unlock_requirements(ship.unlock_requirements, player_stats):
            ship.is_unlocked = True
            log_event(f"[SHIP_UPGRADES] Unlocked ship: {ship_name}")
            return True
        
        return False
    
    def _check_unlock_requirements(self, requirements: Dict[str, Any], player_stats: Dict[str, Any]) -> bool:
        """Check if unlock requirements are met.
        
        Parameters
        ----------
        requirements : Dict[str, Any]
            Requirements to check
        player_stats : Dict[str, Any]
            Player statistics
            
        Returns
        -------
        bool
            True if requirements are met
        """
        for req_key, req_value in requirements.items():
            if req_key not in player_stats:
                return False
            
            if player_stats[req_key] < req_value:
                return False
        
        return True
    
    def get_available_upgrades(self, ship_name: str) -> List[ShipUpgrade]:
        """Get available upgrades for a ship.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship
            
        Returns
        -------
        List[ShipUpgrade]
            List of available upgrades
        """
        if ship_name not in self.ship_classes:
            return []
        
        ship = self.ship_classes[ship_name]
        available_upgrades = []
        
        for upgrade in self.upgrades.values():
            if self._can_install_upgrade(upgrade, ship):
                available_upgrades.append(upgrade)
        
        return available_upgrades
    
    def _can_install_upgrade(self, upgrade: ShipUpgrade, ship: ShipClass) -> bool:
        """Check if an upgrade can be installed on a ship.
        
        Parameters
        ----------
        upgrade : ShipUpgrade
            Upgrade to check
        ship : ShipClass
            Ship to check compatibility with
            
        Returns
        -------
        bool
            True if upgrade can be installed
        """
        # Check ship tier requirement
        if upgrade.requirements.get("ship_tier") and ship.base_tier.value < upgrade.requirements["ship_tier"].value:
            return False
        
        # Check if upgrade type has available slots
        upgrade_type = upgrade.upgrade_type
        if upgrade_type not in ship.upgrade_slots:
            return False
        
        # Count installed upgrades of this type
        installed_count = sum(1 for slot_id, upgrade_id in ship.installed_upgrades.items() 
                            if slot_id.startswith(upgrade_type.value))
        
        if installed_count >= ship.upgrade_slots[upgrade_type]:
            return False
        
        return True
    
    def install_upgrade(self, ship_name: str, upgrade_id: str, slot_id: str) -> Dict[str, Any]:
        """Install an upgrade on a ship.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship
        upgrade_id : str
            ID of the upgrade to install
        slot_id : str
            ID of the slot to install in
            
        Returns
        -------
        Dict[str, Any]
            Installation result
        """
        if ship_name not in self.ship_classes:
            return {"error": "Ship not found"}
        
        if upgrade_id not in self.upgrades:
            return {"error": "Upgrade not found"}
        
        ship = self.ship_classes[ship_name]
        upgrade = self.upgrades[upgrade_id]
        
        # Check if upgrade can be installed
        if not self._can_install_upgrade(upgrade, ship):
            return {"error": "Upgrade cannot be installed on this ship"}
        
        # Check if slot is available
        if slot_id in ship.installed_upgrades:
            return {"error": "Slot already occupied"}
        
        # Install the upgrade
        ship.installed_upgrades[slot_id] = upgrade_id
        upgrade.is_installed = True
        
        # Update ship stats
        self._update_ship_stats(ship, upgrade, True)
        
        # Record upgrade
        self.upgrade_history.append({
            "timestamp": time.time(),
            "ship_name": ship_name,
            "upgrade_id": upgrade_id,
            "slot_id": slot_id,
            "action": "install"
        })
        
        log_event(f"[SHIP_UPGRADES] Installed upgrade {upgrade_id} on {ship_name}")
        
        return {
            "success": True,
            "ship_name": ship_name,
            "upgrade_id": upgrade_id,
            "slot_id": slot_id,
            "new_stats": ship.current_stats
        }
    
    def remove_upgrade(self, ship_name: str, slot_id: str) -> Dict[str, Any]:
        """Remove an upgrade from a ship.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship
        slot_id : str
            ID of the slot to remove upgrade from
            
        Returns
        -------
        Dict[str, Any]
            Removal result
        """
        if ship_name not in self.ship_classes:
            return {"error": "Ship not found"}
        
        ship = self.ship_classes[ship_name]
        
        if slot_id not in ship.installed_upgrades:
            return {"error": "No upgrade in this slot"}
        
        upgrade_id = ship.installed_upgrades[slot_id]
        upgrade = self.upgrades[upgrade_id]
        
        # Remove the upgrade
        del ship.installed_upgrades[slot_id]
        upgrade.is_installed = False
        
        # Update ship stats
        self._update_ship_stats(ship, upgrade, False)
        
        # Record removal
        self.upgrade_history.append({
            "timestamp": time.time(),
            "ship_name": ship_name,
            "upgrade_id": upgrade_id,
            "slot_id": slot_id,
            "action": "remove"
        })
        
        log_event(f"[SHIP_UPGRADES] Removed upgrade {upgrade_id} from {ship_name}")
        
        return {
            "success": True,
            "ship_name": ship_name,
            "upgrade_id": upgrade_id,
            "slot_id": slot_id,
            "new_stats": ship.current_stats
        }
    
    def _update_ship_stats(self, ship: ShipClass, upgrade: ShipUpgrade, installing: bool) -> None:
        """Update ship stats when installing or removing an upgrade.
        
        Parameters
        ----------
        ship : ShipClass
            Ship to update stats for
        upgrade : ShipUpgrade
            Upgrade being installed or removed
        installing : bool
            True if installing, False if removing
        """
        multiplier = 1 if installing else -1
        
        for stat_name, stat_value in upgrade.stats.items():
            if stat_name in ship.current_stats:
                ship.current_stats[stat_name] += stat_value * multiplier
    
    def get_ship_stats(self, ship_name: str) -> Dict[str, Any]:
        """Get current stats for a ship.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship
            
        Returns
        -------
        Dict[str, Any]
            Ship statistics
        """
        if ship_name not in self.ship_classes:
            return {}
        
        ship = self.ship_classes[ship_name]
        
        return {
            "name": ship.name,
            "ship_type": ship.ship_type,
            "base_tier": ship.base_tier.value,
            "max_tier": ship.max_tier.value,
            "base_stats": ship.base_stats,
            "current_stats": ship.current_stats,
            "installed_upgrades": ship.installed_upgrades,
            "upgrade_slots": {slot_type.value: count for slot_type, count in ship.upgrade_slots.items()},
            "is_unlocked": ship.is_unlocked
        }
    
    def get_upgrade_progress(self, ship_name: str) -> Optional[UpgradeProgress]:
        """Get upgrade progress for a ship.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship
            
        Returns
        -------
        UpgradeProgress, optional
            Upgrade progress or None if not found
        """
        if ship_name not in self.upgrade_progress:
            # Create default progress
            ship = self.ship_classes.get(ship_name)
            if ship:
                progress = UpgradeProgress(
                    ship_name=ship_name,
                    current_tier=ship.base_tier,
                    upgrade_points=0,
                    max_upgrade_points=100,
                    completed_upgrades=[],
                    available_upgrades=[],
                    next_tier_requirements={}
                )
                self.upgrade_progress[ship_name] = progress
        
        return self.upgrade_progress.get(ship_name)
    
    def add_upgrade_points(self, ship_name: str, points: int) -> bool:
        """Add upgrade points to a ship.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship
        points : int
            Points to add
            
        Returns
        -------
        bool
            True if points were added successfully
        """
        progress = self.get_upgrade_progress(ship_name)
        if not progress:
            return False
        
        progress.upgrade_points = min(progress.upgrade_points + points, progress.max_upgrade_points)
        
        # Check for tier advancement
        self._check_tier_advancement(ship_name)
        
        return True
    
    def _check_tier_advancement(self, ship_name: str) -> None:
        """Check if ship can advance to next tier.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship to check
        """
        progress = self.get_upgrade_progress(ship_name)
        ship = self.ship_classes.get(ship_name)
        
        if not progress or not ship:
            return
        
        # Simple tier advancement based on upgrade points
        tier_requirements = {
            ShipTier.TIER_1: 0,
            ShipTier.TIER_2: 50,
            ShipTier.TIER_3: 100,
            ShipTier.TIER_4: 200,
            ShipTier.TIER_5: 400
        }
        
        next_tier_points = tier_requirements.get(progress.current_tier, 0)
        
        if progress.upgrade_points >= next_tier_points:
            # Advance to next tier
            current_tier_value = progress.current_tier.value
            next_tier_value = f"tier_{int(current_tier_value.split('_')[1]) + 1}"
            
            try:
                progress.current_tier = ShipTier(next_tier_value)
                log_event(f"[SHIP_UPGRADES] Ship {ship_name} advanced to {progress.current_tier.value}")
            except ValueError:
                # Already at max tier
                pass
    
    def get_upgrade_statistics(self) -> Dict[str, Any]:
        """Get statistics for ship upgrades.
        
        Returns
        -------
        Dict[str, Any]
            Upgrade statistics
        """
        stats = {
            "total_ships": len(self.ship_classes),
            "unlocked_ships": len(self.get_unlocked_ships()),
            "total_upgrades": len(self.upgrades),
            "installed_upgrades": sum(1 for upgrade in self.upgrades.values() if upgrade.is_installed),
            "upgrades_by_tier": {},
            "upgrades_by_type": {},
            "upgrades_by_rarity": {}
        }
        
        # Count upgrades by tier
        for upgrade in self.upgrades.values():
            tier = upgrade.tier.value
            if tier not in stats["upgrades_by_tier"]:
                stats["upgrades_by_tier"][tier] = 0
            stats["upgrades_by_tier"][tier] += 1
        
        # Count upgrades by type
        for upgrade in self.upgrades.values():
            upgrade_type = upgrade.upgrade_type.value
            if upgrade_type not in stats["upgrades_by_type"]:
                stats["upgrades_by_type"][upgrade_type] = 0
            stats["upgrades_by_type"][upgrade_type] += 1
        
        # Count upgrades by rarity
        for upgrade in self.upgrades.values():
            rarity = upgrade.rarity.value
            if rarity not in stats["upgrades_by_rarity"]:
                stats["upgrades_by_rarity"][rarity] = 0
            stats["upgrades_by_rarity"][rarity] += 1
        
        return stats 