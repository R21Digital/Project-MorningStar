"""Weapon Swap Integration with Combat AI

This module integrates the weapon swap system with the existing combat AI
to provide dynamic weapon switching during combat encounters.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from modules.weapon_swap_system import WeaponSwapSystem
from src.ai.combat.evaluator import evaluate_state
from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)


class CombatWeaponSwapIntegration:
    """Integrates weapon swap system with combat AI."""
    
    def __init__(self, weapon_system: WeaponSwapSystem):
        """Initialize the combat weapon swap integration.
        
        Parameters
        ----------
        weapon_system : WeaponSwapSystem
            The weapon swap system to integrate
        """
        self.weapon_system = weapon_system
        self.last_swap_time = None
        self.swap_cooldown = 5.0  # Minimum seconds between swaps
        
        log_event("[COMBAT_WEAPON] Combat weapon swap integration initialized")
    
    def update_combat_context(self, player_state: Dict[str, Any], target_state: Dict[str, Any], 
                             enemy_type: str = None, distance: float = None):
        """Update combat context for weapon swap decisions.
        
        Parameters
        ----------
        player_state : dict
            Current player state (hp, buffs, etc.)
        target_state : dict
            Current target state (hp, etc.)
        enemy_type : str, optional
            Type of enemy being fought
        distance : float, optional
            Distance to enemy in meters
        """
        # Extract relevant information from player state
        player_health = player_state.get("hp", 100)
        ammo_status = player_state.get("ammo_status", {})
        weapon_conditions = player_state.get("weapon_conditions", {})
        
        # Extract target information
        enemy_health = target_state.get("hp", 100)
        
        # Update weapon system combat context
        self.weapon_system.set_combat_context(
            enemy_type=enemy_type,
            distance=distance,
            enemy_health=enemy_health,
            player_health=player_health,
            ammo_status=ammo_status,
            weapon_conditions=weapon_conditions
        )
        
        log_event(f"[COMBAT_WEAPON] Updated combat context - Enemy: {enemy_type}, Distance: {distance}, Player HP: {player_health}")
    
    def should_swap_weapon(self, player_state: Dict[str, Any], target_state: Dict[str, Any],
                          enemy_type: str = None, distance: float = None) -> Tuple[bool, Optional[str]]:
        """Determine if weapon should be swapped during combat.
        
        Parameters
        ----------
        player_state : dict
            Current player state
        target_state : dict
            Current target state
        enemy_type : str, optional
            Type of enemy
        distance : float, optional
            Distance to enemy
            
        Returns
        -------
        tuple
            (should_swap, best_weapon_name)
        """
        # Update combat context
        self.update_combat_context(player_state, target_state, enemy_type, distance)
        
        # Check if we're on cooldown
        if self.last_swap_time:
            time_since_swap = (datetime.now() - self.last_swap_time).total_seconds()
            if time_since_swap < self.swap_cooldown:
                return False, None
        
        # Check for emergency swap conditions
        emergency_swap, emergency_weapon = self._check_emergency_swap(player_state)
        if emergency_swap:
            return True, emergency_weapon
        
        # Check for normal swap conditions
        should_swap, best_weapon = self.weapon_system.should_swap_weapon(
            enemy_type=enemy_type,
            distance=distance
        )
        
        return should_swap, best_weapon
    
    def _check_emergency_swap(self, player_state: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for emergency weapon swap conditions.
        
        Parameters
        ----------
        player_state : dict
            Current player state
            
        Returns
        -------
        tuple
            (should_emergency_swap, emergency_weapon_name)
        """
        current_weapon = self.weapon_system.current_weapon
        if not current_weapon:
            return False, None
        
        weapon_stats = self.weapon_system.get_weapon_stats(current_weapon)
        if not weapon_stats:
            return False, None
        
        # Check for no ammo emergency
        if weapon_stats.current_ammo == 0:
            available_weapons = self.weapon_system.get_available_weapons()
            for weapon_name in available_weapons:
                weapon = self.weapon_system.get_weapon_stats(weapon_name)
                if weapon and weapon.current_ammo > 0:
                    log_event(f"[COMBAT_WEAPON] Emergency swap: {current_weapon} has no ammo, switching to {weapon_name}")
                    return True, weapon_name
        
        # Check for critical weapon condition
        if weapon_stats.condition < 20.0:
            available_weapons = self.weapon_system.get_available_weapons()
            for weapon_name in available_weapons:
                weapon = self.weapon_system.get_weapon_stats(weapon_name)
                if weapon and weapon.condition > 50.0:
                    log_event(f"[COMBAT_WEAPON] Emergency swap: {current_weapon} condition critical ({weapon_stats.condition}%), switching to {weapon_name}")
                    return True, weapon_name
        
        return False, None
    
    def execute_weapon_swap(self, weapon_name: str, reason: str = "combat_auto") -> bool:
        """Execute a weapon swap during combat.
        
        Parameters
        ----------
        weapon_name : str
            Name of the weapon to swap to
        reason : str
            Reason for the swap
            
        Returns
        -------
        bool
            True if swap successful, False otherwise
        """
        success = self.weapon_system.swap_weapon(weapon_name, reason)
        
        if success:
            self.last_swap_time = datetime.now()
            log_event(f"[COMBAT_WEAPON] Combat weapon swap executed: {weapon_name} ({reason})")
        
        return success
    
    def get_enhanced_combat_action(self, player_state: Dict[str, Any], target_state: Dict[str, Any],
                                  enemy_type: str = None, distance: float = None) -> str:
        """Get enhanced combat action that includes weapon swap logic.
        
        Parameters
        ----------
        player_state : dict
            Current player state
        target_state : dict
            Current target state
        enemy_type : str, optional
            Type of enemy
        distance : float, optional
            Distance to enemy
            
        Returns
        -------
        str
            Combat action (attack, heal, retreat, etc.)
        """
        # Check for weapon swap first
        should_swap, best_weapon = self.should_swap_weapon(
            player_state, target_state, enemy_type, distance
        )
        
        if should_swap and best_weapon:
            self.execute_weapon_swap(best_weapon, "combat_auto")
            # Return attack action after weapon swap
            return "attack"
        
        # Get normal combat action from AI
        action = evaluate_state(player_state, target_state)
        
        # Add weapon-specific logic
        if action == "attack":
            current_weapon = self.weapon_system.current_weapon
            if current_weapon:
                weapon_stats = self.weapon_system.get_weapon_stats(current_weapon)
                if weapon_stats and weapon_stats.current_ammo == 0:
                    # No ammo, try to reload or switch to melee
                    if "melee" in [w.weapon_type.value for w in self.weapon_system.weapons.values()]:
                        return "attack"  # Continue with melee
                    else:
                        return "retreat"  # No viable weapons
        
        return action
    
    def get_weapon_recommendation(self, enemy_type: str, distance: float) -> Dict[str, Any]:
        """Get weapon recommendation for specific enemy and distance.
        
        Parameters
        ----------
        enemy_type : str
            Type of enemy
        distance : float
            Distance to enemy
            
        Returns
        -------
        dict
            Weapon recommendation with effectiveness scores
        """
        available_weapons = self.weapon_system.get_available_weapons()
        recommendations = {}
        
        for weapon_name in available_weapons:
            effectiveness = self.weapon_system.calculate_weapon_effectiveness(
                weapon_name, enemy_type, distance
            )
            weapon_stats = self.weapon_system.get_weapon_stats(weapon_name)
            
            recommendations[weapon_name] = {
                "effectiveness": effectiveness,
                "damage_type": weapon_stats.damage_type.value if weapon_stats else "unknown",
                "range": weapon_stats.range if weapon_stats else 0,
                "current_ammo": weapon_stats.current_ammo if weapon_stats else 0,
                "condition": weapon_stats.condition if weapon_stats else 100.0
            }
        
        # Sort by effectiveness
        sorted_recommendations = sorted(
            recommendations.items(),
            key=lambda x: x[1]["effectiveness"],
            reverse=True
        )
        
        return {
            "recommendations": dict(sorted_recommendations),
            "best_weapon": sorted_recommendations[0][0] if sorted_recommendations else None,
            "enemy_type": enemy_type,
            "distance": distance
        }
    
    def get_combat_analytics(self) -> Dict[str, Any]:
        """Get combat analytics including weapon swap data.
        
        Returns
        -------
        dict
            Combat analytics data
        """
        weapon_history = self.weapon_system.get_weapon_history()
        effectiveness_stats = self.weapon_system.get_weapon_effectiveness_stats()
        
        analytics = {
            "total_swaps": len(weapon_history),
            "recent_swaps": len(weapon_history[-10:]) if weapon_history else 0,
            "current_weapon": self.weapon_system.current_weapon,
            "current_loadout": self.weapon_system.current_loadout,
            "weapon_effectiveness": effectiveness_stats,
            "swap_reasons": {}
        }
        
        # Analyze swap reasons
        for event in weapon_history:
            reason = event.reason
            analytics["swap_reasons"][reason] = analytics["swap_reasons"].get(reason, 0) + 1
        
        return analytics


def create_combat_weapon_integration(weapon_config_path: str = "config/weapon_config.json") -> CombatWeaponSwapIntegration:
    """Create a combat weapon swap integration instance.
    
    Parameters
    ----------
    weapon_config_path : str
        Path to weapon configuration file
        
    Returns
    -------
    CombatWeaponSwapIntegration
        Initialized combat weapon swap integration
    """
    weapon_system = WeaponSwapSystem(weapon_config_path)
    return CombatWeaponSwapIntegration(weapon_system) 