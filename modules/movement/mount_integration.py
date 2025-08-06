#!/usr/bin/env python3
"""
Batch 111 - Mount Integration Module

This module integrates the mount manager with the existing movement system,
providing intelligent mount handling during travel and navigation.

Author: SWG Bot Development Team
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from core.mount_manager import (
    MountManager, get_mount_manager, MountType, MountStatus, ZoneType,
    auto_mount_management, get_mount_status
)
from utils.logging_utils import log_event


@dataclass
class TravelContext:
    """Context information for travel decisions."""
    start_location: str
    destination: str
    distance: float
    terrain_type: str
    weather_conditions: str
    time_of_day: str
    faction: str
    urgency: str = "normal"  # normal, urgent, stealth
    combat_risk: float = 0.0  # 0.0 to 1.0


class MountIntegration:
    """Integrates mount management with movement system."""
    
    def __init__(self, profile_name: str = "default"):
        """Initialize mount integration.
        
        Parameters
        ----------
        profile_name : str
            Profile name for mount preferences
        """
        self.profile_name = profile_name
        self.mount_manager = get_mount_manager(profile_name)
        
        # Travel context tracking
        self.current_travel_context = None
        self.travel_history = []
        
        # Integration settings
        self.auto_mount_enabled = True
        self.smart_route_planning = True
        self.combat_avoidance = True
        
        log_event(f"[MOUNT_INTEGRATION] Mount integration initialized for profile: {profile_name}")
    
    def prepare_for_travel(self, start_location: str, destination: str, 
                          distance: float, **context_kwargs) -> bool:
        """Prepare mount for travel.
        
        Parameters
        ----------
        start_location : str
            Starting location
        destination : str
            Destination location
        distance : float
            Travel distance
        **context_kwargs
            Additional context information
            
        Returns
        -------
        bool
            True if mount preparation was successful
        """
        # Create travel context
        context = TravelContext(
            start_location=start_location,
            destination=destination,
            distance=distance,
            **context_kwargs
        )
        
        self.current_travel_context = context
        
        log_event(f"[MOUNT_INTEGRATION] Preparing for travel: {start_location} -> {destination} ({distance:.1f} units)")
        
        # Check if we should mount
        should_mount = self._should_mount_for_travel(context)
        
        if should_mount:
            # Select appropriate mount
            best_mount = self._select_mount_for_travel(context)
            if best_mount:
                success = self.mount_manager.summon_mount(best_mount)
                if success:
                    log_event(f"[MOUNT_INTEGRATION] Successfully mounted {best_mount.name} for travel")
                    return True
                else:
                    log_event(f"[MOUNT_INTEGRATION] Failed to mount {best_mount.name}")
        
        return False
    
    def handle_travel_completion(self, actual_distance: float = None):
        """Handle completion of travel.
        
        Parameters
        ----------
        actual_distance : float, optional
            Actual distance traveled
        """
        if not self.current_travel_context:
            return
        
        context = self.current_travel_context
        
        # Update travel history
        travel_record = {
            "start": context.start_location,
            "destination": context.destination,
            "planned_distance": context.distance,
            "actual_distance": actual_distance or context.distance,
            "mount_used": self.mount_manager.state.current_mount.name if self.mount_manager.state.current_mount else None,
            "timestamp": time.time()
        }
        
        self.travel_history.append(travel_record)
        
        # Check if we should dismount
        if self._should_dismount_after_travel(context):
            self.mount_manager.dismount()
            log_event(f"[MOUNT_INTEGRATION] Dismounted after travel completion")
        
        # Clear current context
        self.current_travel_context = None
        
        log_event(f"[MOUNT_INTEGRATION] Travel completed: {context.start_location} -> {context.destination}")
    
    def handle_combat_encounter(self):
        """Handle mount behavior during combat encounters."""
        if self.mount_manager.state.status == MountStatus.MOUNTED:
            log_event("[MOUNT_INTEGRATION] Combat detected, dismounting for safety")
            return self.mount_manager.emergency_dismount()
        return True
    
    def handle_zone_transition(self, new_zone: str, zone_type: ZoneType):
        """Handle mount behavior during zone transitions.
        
        Parameters
        ----------
        new_zone : str
            New zone name
        zone_type : ZoneType
            Type of zone entered
        """
        log_event(f"[MOUNT_INTEGRATION] Zone transition: {new_zone} (type: {zone_type.value})")
        
        # Check if we need to dismount for this zone
        if zone_type in [ZoneType.INDOORS, ZoneType.NO_MOUNT, ZoneType.COMBAT]:
            if self.mount_manager.state.status == MountStatus.MOUNTED:
                log_event(f"[MOUNT_INTEGRATION] Dismounting for zone type: {zone_type.value}")
                return self.mount_manager.dismount()
        
        return True
    
    def _should_mount_for_travel(self, context: TravelContext) -> bool:
        """Determine if we should mount for this travel."""
        # Check distance threshold
        if context.distance < self.mount_manager.preferences.auto_mount_distance:
            return False
        
        # Check for no-mount zones
        if self.mount_manager.is_no_mount_zone(context.start_location, context.destination):
            return False
        
        # Check combat risk
        if context.combat_risk > 0.7:
            return False
        
        # Check urgency (stealth mode might avoid mounts)
        if context.urgency == "stealth":
            return False
        
        return True
    
    def _select_mount_for_travel(self, context: TravelContext):
        """Select the best mount for this travel context."""
        available_mounts = self.mount_manager.get_available_mounts()
        
        if not available_mounts:
            return None
        
        # Filter mounts based on context
        suitable_mounts = []
        
        for mount in available_mounts:
            if self._is_mount_suitable_for_context(mount, context):
                suitable_mounts.append(mount)
        
        if not suitable_mounts:
            # Fall back to any available mount
            suitable_mounts = available_mounts
        
        # Sort by preference and speed
        suitable_mounts.sort(key=lambda m: (
            m.mount_type == self.mount_manager.preferences.preferred_mount_type,
            m.speed
        ), reverse=True)
        
        return suitable_mounts[0] if suitable_mounts else None
    
    def _is_mount_suitable_for_context(self, mount, context: TravelContext) -> bool:
        """Check if a mount is suitable for the travel context."""
        preferences = mount.preferences
        
        # Check terrain compatibility
        if "terrain" in preferences:
            if context.terrain_type not in preferences["terrain"] and "all" not in preferences["terrain"]:
                return False
        
        # Check weather compatibility
        if "weather" in preferences:
            if context.weather_conditions not in preferences["weather"]:
                return False
        
        # Check time of day compatibility
        if "time_of_day" in preferences:
            if context.time_of_day not in preferences["time_of_day"]:
                return False
        
        # Check faction compatibility
        if "faction" in preferences:
            if context.faction not in preferences["faction"]:
                return False
        
        return True
    
    def _should_dismount_after_travel(self, context: TravelContext) -> bool:
        """Determine if we should dismount after travel."""
        # Check destination zone type
        current_zone = self.mount_manager.detect_current_zone()
        
        if current_zone in [ZoneType.INDOORS, ZoneType.NO_MOUNT, ZoneType.COMBAT]:
            return True
        
        # Check if destination is a no-mount zone
        if self.mount_manager.is_no_mount_zone(context.destination, context.destination):
            return True
        
        return False
    
    def get_travel_statistics(self) -> Dict[str, Any]:
        """Get travel statistics.
        
        Returns
        -------
        dict
            Travel statistics
        """
        if not self.travel_history:
            return {}
        
        total_travels = len(self.travel_history)
        total_distance = sum(travel["actual_distance"] for travel in self.travel_history)
        mount_usage = {}
        
        for travel in self.travel_history:
            mount_name = travel["mount_used"] or "walking"
            if mount_name not in mount_usage:
                mount_usage[mount_name] = {"count": 0, "distance": 0}
            mount_usage[mount_name]["count"] += 1
            mount_usage[mount_name]["distance"] += travel["actual_distance"]
        
        return {
            "total_travels": total_travels,
            "total_distance": total_distance,
            "average_distance": total_distance / total_travels if total_travels > 0 else 0,
            "mount_usage": mount_usage,
            "most_used_mount": max(mount_usage.items(), key=lambda x: x[1]["count"])[0] if mount_usage else None
        }
    
    def update_integration_settings(self, **settings):
        """Update integration settings.
        
        Parameters
        ----------
        **settings
            Settings to update
        """
        for key, value in settings.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        log_event(f"[MOUNT_INTEGRATION] Updated settings: {settings}")


# Integration with existing movement system
def integrate_with_movement_system(movement_agent, start_location: str, 
                                 destination: str, distance: float,
                                 profile_name: str = "default") -> bool:
    """Integrate mount management with movement system.
    
    Parameters
    ----------
    movement_agent
        Movement agent instance
    start_location : str
        Starting location
    destination : str
        Destination location
    distance : float
        Travel distance
    profile_name : str
        Profile name for mount preferences
        
    Returns
    -------
    bool
        True if integration was successful
    """
    integration = MountIntegration(profile_name)
    
    # Prepare for travel
    mount_prepared = integration.prepare_for_travel(
        start_location=start_location,
        destination=destination,
        distance=distance,
        terrain_type="grassland",  # Default, could be detected
        weather_conditions="clear",  # Default, could be detected
        time_of_day="day",  # Default, could be detected
        faction="neutral"  # Default, could be detected
    )
    
    if mount_prepared:
        # Execute movement with mount
        movement_result = movement_agent.move_to()
        
        # Handle travel completion
        integration.handle_travel_completion(distance)
        
        return movement_result
    
    return False


def get_mount_travel_status(profile_name: str = "default") -> Dict[str, Any]:
    """Get mount travel status.
    
    Parameters
    ----------
    profile_name : str
        Profile name
        
    Returns
    -------
    dict
        Mount travel status
    """
    integration = MountIntegration(profile_name)
    mount_status = get_mount_status(profile_name)
    travel_stats = integration.get_travel_statistics()
    
    return {
        "mount_status": mount_status,
        "travel_statistics": travel_stats,
        "integration_settings": {
            "auto_mount_enabled": integration.auto_mount_enabled,
            "smart_route_planning": integration.smart_route_planning,
            "combat_avoidance": integration.combat_avoidance
        }
    }


# Convenience functions for direct integration
def auto_mount_for_travel(distance: float, start_location: str, destination: str,
                         profile_name: str = "default") -> bool:
    """Automatically mount for travel.
    
    Parameters
    ----------
    distance : float
        Travel distance
    start_location : str
        Starting location
    destination : str
        Destination location
    profile_name : str
        Profile name
        
    Returns
    -------
    bool
        True if mount action was taken
    """
    return auto_mount_management(distance, start_location, destination, profile_name)


def handle_combat_mount_behavior(profile_name: str = "default") -> bool:
    """Handle mount behavior during combat.
    
    Parameters
    ----------
    profile_name : str
        Profile name
        
    Returns
    -------
    bool
        True if mount action was taken
    """
    integration = MountIntegration(profile_name)
    return integration.handle_combat_encounter()


def handle_zone_mount_behavior(zone_name: str, zone_type: ZoneType,
                              profile_name: str = "default") -> bool:
    """Handle mount behavior during zone transitions.
    
    Parameters
    ----------
    zone_name : str
        Zone name
    zone_type : ZoneType
        Zone type
    profile_name : str
        Profile name
        
    Returns
    -------
    bool
        True if mount action was taken
    """
    integration = MountIntegration(profile_name)
    return integration.handle_zone_transition(zone_name, zone_type) 