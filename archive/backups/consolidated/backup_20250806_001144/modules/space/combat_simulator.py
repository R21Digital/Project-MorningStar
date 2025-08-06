"""Simulate space combat for Tansarii Point Station."""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

import pyautogui

from src.vision.ocr import screen_text, capture_screen
from utils.logging_utils import log_event


@dataclass
class CombatTarget:
    """Represents a combat target."""
    name: str
    target_type: str  # "enemy_ship", "asteroid", "space_debris"
    health: int
    max_health: int
    damage: int
    position: Tuple[int, int]
    status: str  # "active", "destroyed", "fleeing"


@dataclass
class CombatResult:
    """Represents a combat result."""
    target_name: str
    target_type: str
    damage_dealt: int
    damage_received: int
    target_destroyed: bool
    combat_duration: float
    credits_earned: int
    experience_earned: int


class SpaceCombatSimulator:
    """Simulate space combat for Tansarii Point Station."""

    def __init__(self, config_path: str = "config/session_config.json"):
        """Initialize the space combat simulator.

        Parameters
        ----------
        config_path : str
            Path to session configuration file
        """
        self.config = self._load_config(config_path)
        self.space_config = self.config.get("space_mode", {})
        
        # Combat configuration
        self.combat_enabled = self.space_config.get("combat_simulation", True)
        self.default_station = self.space_config.get("default_station", "Tansarii Point Station")
        
        # Combat targets for Tansarii Point Station
        self.combat_targets = {
            "patrol_targets": [
                {"name": "Pirate Fighter", "type": "enemy_ship", "health": 100, "damage": 15},
                {"name": "Smuggler Transport", "type": "enemy_ship", "health": 150, "damage": 10},
                {"name": "Asteroid Field", "type": "asteroid", "health": 50, "damage": 5}
            ],
            "escort_targets": [
                {"name": "Merchant Vessel", "type": "friendly_ship", "health": 200, "damage": 0},
                {"name": "Diplomatic Shuttle", "type": "friendly_ship", "health": 300, "damage": 0}
            ],
            "kill_targets": [
                {"name": "Bounty Target", "type": "enemy_ship", "health": 200, "damage": 25},
                {"name": "Wanted Criminal", "type": "enemy_ship", "health": 250, "damage": 30},
                {"name": "Rogue AI", "type": "enemy_ship", "health": 300, "damage": 35}
            ]
        }
        
        # Combat state
        self.current_combat: Optional[Dict[str, Any]] = None
        self.combat_history: List[CombatResult] = []

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load session configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        return {}

    def simulate_combat(self, mission_type: str, target_name: str = None) -> Optional[CombatResult]:
        """Simulate space combat for a mission.

        Parameters
        ----------
        mission_type : str
            Type of mission ("patrol", "escort", "kill_target")
        target_name : str, optional
            Specific target name

        Returns
        -------
        CombatResult or None
            Combat result
        """
        if not self.combat_enabled:
            log_event("[COMBAT] Combat simulation disabled")
            return None

        # Get appropriate targets for mission type
        targets = self.combat_targets.get(f"{mission_type}_targets", [])
        if not targets:
            log_event(f"[COMBAT] No targets found for mission type: {mission_type}")
            return None

        # Select target
        if target_name:
            target_data = next((t for t in targets if t["name"] == target_name), None)
        else:
            target_data = random.choice(targets)

        if not target_data:
            log_event(f"[COMBAT] Target {target_name} not found")
            return None

        # Create combat target
        target = CombatTarget(
            name=target_data["name"],
            target_type=target_data["type"],
            health=target_data["health"],
            max_health=target_data["health"],
            damage=target_data["damage"],
            position=(random.randint(100, 800), random.randint(100, 600)),
            status="active"
        )

        log_event(f"[COMBAT] Starting combat with {target.name}")
        
        # Simulate combat
        result = self._execute_combat(target, mission_type)
        
        if result:
            self.combat_history.append(result)
            log_event(f"[COMBAT] Combat completed: {result.target_name} - Damage: {result.damage_dealt}")
        
        return result

    def _execute_combat(self, target: CombatTarget, mission_type: str) -> CombatResult:
        """Execute combat simulation.

        Parameters
        ----------
        target : CombatTarget
            Combat target
        mission_type : str
            Type of mission

        Returns
        -------
        CombatResult
            Combat result
        """
        start_time = time.time()
        damage_dealt = 0
        damage_received = 0
        target_destroyed = False

        # Simulate combat rounds
        while target.health > 0 and damage_received < 100:  # Player health limit
            # Player attack
            player_damage = random.randint(20, 40)
            target.health -= player_damage
            damage_dealt += player_damage

            # Target attack (if still alive)
            if target.health > 0:
                target_damage = random.randint(5, target.damage)
                damage_received += target_damage

            # Small delay to simulate combat time
            time.sleep(0.1)

        # Determine result
        combat_duration = time.time() - start_time
        target_destroyed = target.health <= 0

        # Calculate rewards
        credits_earned = self._calculate_credits(target, target_destroyed, mission_type)
        experience_earned = self._calculate_experience(target, target_destroyed, mission_type)

        return CombatResult(
            target_name=target.name,
            target_type=target.target_type,
            damage_dealt=damage_dealt,
            damage_received=damage_received,
            target_destroyed=target_destroyed,
            combat_duration=combat_duration,
            credits_earned=credits_earned,
            experience_earned=experience_earned
        )

    def _calculate_credits(self, target: CombatTarget, destroyed: bool, mission_type: str) -> int:
        """Calculate credits earned from combat.

        Parameters
        ----------
        target : CombatTarget
            Combat target
        destroyed : bool
            Whether target was destroyed
        mission_type : str
            Type of mission

        Returns
        -------
        int
            Credits earned
        """
        base_credits = target.max_health * 2
        
        if not destroyed:
            base_credits = base_credits // 4  # Reduced reward if not destroyed
        
        # Mission type multipliers
        multipliers = {
            "patrol": 1.0,
            "escort": 1.5,
            "kill_target": 2.0
        }
        
        multiplier = multipliers.get(mission_type, 1.0)
        return int(base_credits * multiplier)

    def _calculate_experience(self, target: CombatTarget, destroyed: bool, mission_type: str) -> int:
        """Calculate experience earned from combat.

        Parameters
        ----------
        target : CombatTarget
            Combat target
        destroyed : bool
            Whether target was destroyed
        mission_type : str
            Type of mission

        Returns
        -------
        int
            Experience earned
        """
        base_exp = target.max_health
        
        if not destroyed:
            base_exp = base_exp // 2  # Reduced reward if not destroyed
        
        # Mission type multipliers
        multipliers = {
            "patrol": 1.0,
            "escort": 1.2,
            "kill_target": 1.5
        }
        
        multiplier = multipliers.get(mission_type, 1.0)
        return int(base_exp * multiplier)

    def detect_combat_interface(self, screen_image=None) -> bool:
        """Detect if combat interface is visible.

        Parameters
        ----------
        screen_image
            Screenshot to analyze. If None, captures current screen.

        Returns
        -------
        bool
            True if combat interface is detected
        """
        if screen_image is None:
            screen_image = capture_screen()

        text = screen_text()
        combat_indicators = ["combat", "weapons", "target", "fire", "attack", "defend"]
        
        return any(indicator in text.lower() for indicator in combat_indicators)

    def auto_combat(self, mission_type: str) -> List[CombatResult]:
        """Automatically engage in combat for a mission type.

        Parameters
        ----------
        mission_type : str
            Type of mission

        Returns
        -------
        List[CombatResult]
            Combat results
        """
        results = []
        
        # Get targets for mission type
        targets = self.combat_targets.get(f"{mission_type}_targets", [])
        
        for target_data in targets:
            result = self.simulate_combat(mission_type, target_data["name"])
            if result:
                results.append(result)
        
        log_event(f"[COMBAT] Auto combat completed: {len(results)} engagements")
        return results

    def get_combat_statistics(self) -> Dict[str, Any]:
        """Get combat statistics.

        Returns
        -------
        Dict[str, Any]
            Combat statistics
        """
        if not self.combat_history:
            return {
                "total_combats": 0,
                "targets_destroyed": 0,
                "total_damage_dealt": 0,
                "total_damage_received": 0,
                "total_credits_earned": 0,
                "total_experience_earned": 0
            }

        total_combats = len(self.combat_history)
        targets_destroyed = sum(1 for result in self.combat_history if result.target_destroyed)
        total_damage_dealt = sum(result.damage_dealt for result in self.combat_history)
        total_damage_received = sum(result.damage_received for result in self.combat_history)
        total_credits_earned = sum(result.credits_earned for result in self.combat_history)
        total_experience_earned = sum(result.experience_earned for result in self.combat_history)

        return {
            "total_combats": total_combats,
            "targets_destroyed": targets_destroyed,
            "total_damage_dealt": total_damage_dealt,
            "total_damage_received": total_damage_received,
            "total_credits_earned": total_credits_earned,
            "total_experience_earned": total_experience_earned,
            "success_rate": targets_destroyed / total_combats if total_combats > 0 else 0
        }

    def get_available_targets(self, mission_type: str) -> List[Dict[str, Any]]:
        """Get available targets for a mission type.

        Parameters
        ----------
        mission_type : str
            Type of mission

        Returns
        -------
        List[Dict[str, Any]]
            Available targets
        """
        targets = self.combat_targets.get(f"{mission_type}_targets", [])
        return targets.copy()

    def is_combat_active(self) -> bool:
        """Check if combat is currently active.

        Returns
        -------
        bool
            True if combat is active
        """
        return self.current_combat is not None

    def end_combat(self) -> None:
        """End current combat.

        Returns
        -------
        None
        """
        if self.current_combat:
            log_event("[COMBAT] Ending current combat")
            self.current_combat = None 