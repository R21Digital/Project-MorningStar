"""Fallback Navigation System for Batch 040 - Planetary & Galactic Fallback Pathing.

This module provides default navigation logic for zones without quest profiles
by using generic waypoints and fallback loops. It enables exploration of
unexplored regions and sandbox grinding.
"""

import logging
import time
import yaml
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

import cv2
import numpy as np

from core.navigator import Navigator, Waypoint, get_navigator
from core.ocr import OCREngine
from core.screenshot import capture_screen
from core.state_tracker import update_state, get_state


class FallbackStatus(Enum):
    """Fallback navigation status enumeration."""
    IDLE = "idle"
    EXPLORING = "exploring"
    SCANNING = "scanning"
    INTERACTING = "interacting"
    COMBAT = "combat"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Hotspot:
    """Represents a navigation hotspot with scanning capabilities."""
    name: str
    x: int
    y: int
    description: str
    scan_radius: int
    scan_time: int
    
    def to_waypoint(self, planet: str, zone: str) -> Waypoint:
        """Convert hotspot to waypoint."""
        return Waypoint(
            x=self.x,
            y=self.y,
            name=self.name,
            planet=planet,
            zone=zone,
            description=self.description
        )


@dataclass
class ZoneProfile:
    """Represents a zone profile with hotspots and navigation loop."""
    name: str
    description: str
    hotspots: List[Hotspot]
    navigation_loop: List[str]
    scan_interval: int
    max_loop_iterations: int
    
    def get_hotspot_by_name(self, name: str) -> Optional[Hotspot]:
        """Get hotspot by name."""
        for hotspot in self.hotspots:
            if hotspot.name == name:
                return hotspot
        return None


@dataclass
class FallbackState:
    """Current fallback navigation state."""
    current_zone: Optional[ZoneProfile] = None
    current_hotspot: Optional[Hotspot] = None
    status: FallbackStatus = FallbackStatus.IDLE
    start_time: Optional[float] = None
    loop_iterations: int = 0
    hotspots_visited: List[str] = None
    quests_found: List[str] = None
    npcs_found: List[str] = None
    pois_found: List[str] = None
    
    def __post_init__(self):
        """Initialize lists if None."""
        if self.hotspots_visited is None:
            self.hotspots_visited = []
        if self.quests_found is None:
            self.quests_found = []
        if self.npcs_found is None:
            self.npcs_found = []
        if self.pois_found is None:
            self.pois_found = []


class FallbackNavigator:
    """Fallback navigation system for zones without quest profiles."""
    
    def __init__(self, fallback_paths_file: str = "data/fallback_paths.yaml"):
        """Initialize the fallback navigator.
        
        Parameters
        ----------
        fallback_paths_file : str
            Path to YAML file containing fallback path definitions
        """
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = OCREngine()
        self.navigator = get_navigator()
        
        # Load fallback paths
        self.fallback_data = self._load_fallback_paths(fallback_paths_file)
        self.state = FallbackState()
        
        # Scanning settings
        self.scanning_config = self.fallback_data.get("scanning", {})
        self.settings = self.fallback_data.get("settings", {})
        
        # Dynamic detection settings
        self.npc_detection = self.scanning_config.get("npc_detection", {})
        self.quest_detection = self.scanning_config.get("quest_detection", {})
        self.poi_detection = self.scanning_config.get("poi_detection", {})
    
    def _load_fallback_paths(self, path: str) -> Dict[str, Any]:
        """Load fallback paths from YAML file.
        
        Parameters
        ----------
        path : str
            Path to fallback paths file
            
        Returns
        -------
        dict
            Loaded fallback paths data
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            self.logger.info(f"Loaded fallback paths from {path}")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load fallback paths from {path}: {e}")
            return {}
    
    def get_zone_profile(self, planet: str, zone: str) -> Optional[ZoneProfile]:
        """Get zone profile for a specific planet and zone.
        
        Parameters
        ----------
        planet : str
            Planet name
        zone : str
            Zone name
            
        Returns
        -------
        ZoneProfile or None
            Zone profile if found, None otherwise
        """
        try:
            planets = self.fallback_data.get("planets", {})
            planet_data = planets.get(planet.lower())
            
            if not planet_data:
                self.logger.warning(f"No fallback data for planet: {planet}")
                return None
            
            zones = planet_data.get("zones", {})
            zone_data = zones.get(zone.lower())
            
            if not zone_data:
                self.logger.warning(f"No fallback data for zone: {zone} on {planet}")
                return None
            
            # Create hotspots
            hotspots = []
            for hotspot_data in zone_data.get("hotspots", []):
                hotspot = Hotspot(
                    name=hotspot_data["name"],
                    x=hotspot_data["x"],
                    y=hotspot_data["y"],
                    description=hotspot_data["description"],
                    scan_radius=hotspot_data.get("scan_radius", 50),
                    scan_time=hotspot_data.get("scan_time", 5)
                )
                hotspots.append(hotspot)
            
            # Create zone profile
            profile = ZoneProfile(
                name=zone_data["name"],
                description=zone_data["description"],
                hotspots=hotspots,
                navigation_loop=zone_data.get("navigation_loop", []),
                scan_interval=zone_data.get("scan_interval", 45),
                max_loop_iterations=zone_data.get("max_loop_iterations", 3)
            )
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error getting zone profile for {planet}/{zone}: {e}")
            return None
    
    def get_generic_pattern(self, pattern_name: str) -> Optional[ZoneProfile]:
        """Get generic exploration pattern.
        
        Parameters
        ----------
        pattern_name : str
            Name of the pattern to use
            
        Returns
        -------
        ZoneProfile or None
            Generic pattern if found, None otherwise
        """
        try:
            patterns = self.fallback_data.get("patterns", {})
            pattern_data = patterns.get(pattern_name)
            
            if not pattern_data:
                self.logger.warning(f"No generic pattern found: {pattern_name}")
                return None
            
            # Create hotspots from pattern
            hotspots = []
            for hotspot_data in pattern_data.get("hotspots", []):
                hotspot = Hotspot(
                    name=hotspot_data["name"],
                    x=0,  # Generic patterns don't have specific coordinates
                    y=0,
                    description=hotspot_data["description"],
                    scan_radius=hotspot_data.get("scan_radius", 50),
                    scan_time=hotspot_data.get("scan_time", 5)
                )
                hotspots.append(hotspot)
            
            # Create zone profile
            profile = ZoneProfile(
                name=pattern_data["name"],
                description=pattern_data["description"],
                hotspots=hotspots,
                navigation_loop=pattern_data.get("navigation_loop", []),
                scan_interval=pattern_data.get("scan_interval", 45),
                max_loop_iterations=pattern_data.get("max_loop_iterations", 3)
            )
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error getting generic pattern {pattern_name}: {e}")
            return None
    
    def start_fallback_navigation(self, planet: str, zone: str, 
                                pattern_name: str = "standard_exploration") -> bool:
        """Start fallback navigation for a zone.
        
        Parameters
        ----------
        planet : str
            Planet name
        zone : str
            Zone name
        pattern_name : str
            Generic pattern to use if no zone profile found
            
        Returns
        -------
        bool
            True if fallback navigation started successfully
        """
        try:
            self.logger.info(f"Starting fallback navigation for {planet}/{zone}")
            
            # Get zone profile
            zone_profile = self.get_zone_profile(planet, zone)
            
            if not zone_profile:
                self.logger.info(f"No zone profile found, using generic pattern: {pattern_name}")
                zone_profile = self.get_generic_pattern(pattern_name)
                
                if not zone_profile:
                    self.logger.error(f"No fallback navigation available for {planet}/{zone}")
                    return False
            
            # Initialize state
            self.state = FallbackState(
                current_zone=zone_profile,
                status=FallbackStatus.EXPLORING,
                start_time=time.time()
            )
            
            # Update state tracker
            self._update_fallback_state()
            
            self.logger.info(f"Fallback navigation started for {zone_profile.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start fallback navigation: {e}")
            return False
    
    def execute_navigation_loop(self) -> bool:
        """Execute the navigation loop for the current zone.
        
        Returns
        -------
        bool
            True if navigation loop completed successfully
        """
        try:
            if not self.state.current_zone:
                self.logger.error("No current zone profile")
                return False
            
            zone_profile = self.state.current_zone
            
            # Check if we've exceeded max iterations
            if self.state.loop_iterations >= zone_profile.max_loop_iterations:
                self.logger.info(f"Reached max loop iterations ({zone_profile.max_loop_iterations})")
                self.state.status = FallbackStatus.COMPLETED
                return True
            
            self.logger.info(f"Executing navigation loop iteration {self.state.loop_iterations + 1}")
            
            # Navigate through hotspots in the loop
            for hotspot_name in zone_profile.navigation_loop:
                if self.state.status == FallbackStatus.COMPLETED:
                    break
                
                # Get hotspot
                hotspot = zone_profile.get_hotspot_by_name(hotspot_name)
                if not hotspot:
                    self.logger.warning(f"Hotspot not found: {hotspot_name}")
                    continue
                
                # Navigate to hotspot
                success = self._navigate_to_hotspot(hotspot)
                if not success:
                    self.logger.warning(f"Failed to navigate to hotspot: {hotspot_name}")
                    continue
                
                # Scan at hotspot
                self._scan_at_hotspot(hotspot)
                
                # Check for quests/NPCs/POIs
                self._check_for_interactions(hotspot)
                
                # Wait at hotspot
                self._wait_at_hotspot(hotspot)
            
            # Increment loop counter
            self.state.loop_iterations += 1
            
            # Update state tracker
            self._update_fallback_state()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Navigation loop execution failed: {e}")
            self.state.status = FallbackStatus.FAILED
            return False
    
    def _navigate_to_hotspot(self, hotspot: Hotspot) -> bool:
        """Navigate to a specific hotspot.
        
        Parameters
        ----------
        hotspot : Hotspot
            Hotspot to navigate to
            
        Returns
        -------
        bool
            True if navigation was successful
        """
        try:
            self.logger.info(f"Navigating to hotspot: {hotspot.name}")
            
            # Convert hotspot to waypoint
            waypoint = hotspot.to_waypoint("unknown", "unknown")
            
            # Navigate using the navigator
            success = self.navigator.navigate_to_waypoint(waypoint.name)
            
            if success:
                self.state.current_hotspot = hotspot
                self.state.hotspots_visited.append(hotspot.name)
                self.logger.info(f"Successfully navigated to {hotspot.name}")
            else:
                self.logger.warning(f"Failed to navigate to {hotspot.name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error navigating to hotspot {hotspot.name}: {e}")
            return False
    
    def _scan_at_hotspot(self, hotspot: Hotspot) -> None:
        """Perform scanning at a hotspot.
        
        Parameters
        ----------
        hotspot : Hotspot
            Hotspot to scan at
        """
        try:
            self.logger.info(f"Scanning at {hotspot.name} (radius: {hotspot.scan_radius})")
            
            # Capture screen for scanning
            image = capture_screen()
            
            # Perform OCR scan
            scan_result = self.ocr_engine.extract_text(image, method="standard")
            
            if scan_result.text:
                self.logger.info(f"Scan results at {hotspot.name}: {scan_result.text[:100]}...")
                
                # Check for quest indicators
                if self.quest_detection.get("enabled", True):
                    self._check_for_quests(scan_result.text, hotspot)
                
                # Check for NPCs
                if self.npc_detection.get("enabled", True):
                    self._check_for_npcs(scan_result.text, hotspot)
                
                # Check for POIs
                if self.poi_detection.get("enabled", True):
                    self._check_for_pois(scan_result.text, hotspot)
            
            # Wait for scan time
            time.sleep(hotspot.scan_time)
            
        except Exception as e:
            self.logger.error(f"Error scanning at hotspot {hotspot.name}: {e}")
    
    def _check_for_quests(self, text: str, hotspot: Hotspot) -> None:
        """Check for quest indicators in scanned text.
        
        Parameters
        ----------
        text : str
            Scanned text to analyze
        hotspot : Hotspot
            Hotspot where scanning occurred
        """
        try:
            quest_indicators = self.quest_detection.get("quest_indicators", [])
            text_lower = text.lower()
            
            for indicator in quest_indicators:
                if indicator.lower() in text_lower:
                    quest_id = f"{hotspot.name}_quest_{len(self.state.quests_found)}"
                    self.state.quests_found.append(quest_id)
                    self.logger.info(f"Quest detected at {hotspot.name}: {indicator}")
                    
                    # Update state tracker
                    update_state(
                        fallback_quests_found=self.state.quests_found,
                        last_quest_location=hotspot.name
                    )
                    
        except Exception as e:
            self.logger.error(f"Error checking for quests: {e}")
    
    def _check_for_npcs(self, text: str, hotspot: Hotspot) -> None:
        """Check for NPCs in scanned text.
        
        Parameters
        ----------
        text : str
            Scanned text to analyze
        hotspot : Hotspot
            Hotspot where scanning occurred
        """
        try:
            npc_types = self.npc_detection.get("npc_types", [])
            text_lower = text.lower()
            
            for npc_type in npc_types:
                if npc_type.lower() in text_lower:
                    npc_id = f"{hotspot.name}_{npc_type}_{len(self.state.npcs_found)}"
                    self.state.npcs_found.append(npc_id)
                    self.logger.info(f"NPC detected at {hotspot.name}: {npc_type}")
                    
                    # Update state tracker
                    update_state(
                        fallback_npcs_found=self.state.npcs_found,
                        last_npc_location=hotspot.name
                    )
                    
        except Exception as e:
            self.logger.error(f"Error checking for NPCs: {e}")
    
    def _check_for_pois(self, text: str, hotspot: Hotspot) -> None:
        """Check for Points of Interest in scanned text.
        
        Parameters
        ----------
        text : str
            Scanned text to analyze
        hotspot : Hotspot
            Hotspot where scanning occurred
        """
        try:
            poi_types = self.poi_detection.get("poi_types", [])
            text_lower = text.lower()
            
            for poi_type in poi_types:
                if poi_type.lower() in text_lower:
                    poi_id = f"{hotspot.name}_{poi_type}_{len(self.state.pois_found)}"
                    self.state.pois_found.append(poi_id)
                    self.logger.info(f"POI detected at {hotspot.name}: {poi_type}")
                    
                    # Update state tracker
                    update_state(
                        fallback_pois_found=self.state.pois_found,
                        last_poi_location=hotspot.name
                    )
                    
        except Exception as e:
            self.logger.error(f"Error checking for POIs: {e}")
    
    def _check_for_interactions(self, hotspot: Hotspot) -> None:
        """Check for interactive elements at hotspot.
        
        Parameters
        ----------
        hotspot : Hotspot
            Hotspot to check for interactions
        """
        try:
            # Check if NPC interaction is enabled
            if self.settings.get("enable_npc_interaction", True):
                self._attempt_npc_interaction(hotspot)
            
            # Check if combat is enabled
            if self.settings.get("enable_combat", True):
                self._check_for_combat(hotspot)
            
            # Check if resource gathering is enabled
            if self.settings.get("enable_resource_gathering", True):
                self._check_for_resources(hotspot)
                
        except Exception as e:
            self.logger.error(f"Error checking for interactions at {hotspot.name}: {e}")
    
    def _attempt_npc_interaction(self, hotspot: Hotspot) -> None:
        """Attempt to interact with NPCs at hotspot.
        
        Parameters
        ----------
        hotspot : Hotspot
            Hotspot to attempt NPC interaction
        """
        try:
            # Simulate NPC interaction attempt
            self.logger.info(f"Attempting NPC interaction at {hotspot.name}")
            
            # This would integrate with existing NPC interaction systems
            # For now, just log the attempt
            
        except Exception as e:
            self.logger.error(f"Error attempting NPC interaction: {e}")
    
    def _check_for_combat(self, hotspot: Hotspot) -> None:
        """Check for combat opportunities at hotspot.
        
        Parameters
        ----------
        hotspot : Hotspot
            Hotspot to check for combat
        """
        try:
            # Simulate combat detection
            self.logger.info(f"Checking for combat opportunities at {hotspot.name}")
            
            # This would integrate with existing combat systems
            # For now, just log the check
            
        except Exception as e:
            self.logger.error(f"Error checking for combat: {e}")
    
    def _check_for_resources(self, hotspot: Hotspot) -> None:
        """Check for resources at hotspot.
        
        Parameters
        ----------
        hotspot : Hotspot
            Hotspot to check for resources
        """
        try:
            # Simulate resource detection
            self.logger.info(f"Checking for resources at {hotspot.name}")
            
            # This would integrate with existing resource gathering systems
            # For now, just log the check
            
        except Exception as e:
            self.logger.error(f"Error checking for resources: {e}")
    
    def _wait_at_hotspot(self, hotspot: Hotspot) -> None:
        """Wait at hotspot for specified time.
        
        Parameters
        ----------
        hotspot : Hotspot
            Hotspot to wait at
        """
        try:
            min_time = self.settings.get("min_hotspot_time", 30)
            max_time = self.settings.get("max_hotspot_time", 120)
            
            # Random wait time between min and max
            import random
            wait_time = random.randint(min_time, max_time)
            
            self.logger.info(f"Waiting at {hotspot.name} for {wait_time} seconds")
            time.sleep(wait_time)
            
        except Exception as e:
            self.logger.error(f"Error waiting at hotspot {hotspot.name}: {e}")
    
    def _update_fallback_state(self) -> None:
        """Update the state tracker with current fallback state."""
        try:
            state_updates = {
                "fallback_status": self.state.status.value,
                "fallback_zone": self.state.current_zone.name if self.state.current_zone else None,
                "fallback_hotspot": self.state.current_hotspot.name if self.state.current_hotspot else None,
                "fallback_start_time": self.state.start_time,
                "fallback_loop_iterations": self.state.loop_iterations,
                "fallback_hotspots_visited": self.state.hotspots_visited,
                "fallback_quests_found": self.state.quests_found,
                "fallback_npcs_found": self.state.npcs_found,
                "fallback_pois_found": self.state.pois_found
            }
            update_state(**state_updates)
        except Exception as e:
            self.logger.error(f"Failed to update fallback state: {e}")
    
    def get_fallback_status(self) -> Dict[str, Any]:
        """Get current fallback navigation status.
        
        Returns
        -------
        dict
            Current fallback status information
        """
        return {
            "status": self.state.status.value,
            "zone": self.state.current_zone.name if self.state.current_zone else None,
            "hotspot": self.state.current_hotspot.name if self.state.current_hotspot else None,
            "start_time": self.state.start_time,
            "loop_iterations": self.state.loop_iterations,
            "hotspots_visited": len(self.state.hotspots_visited),
            "quests_found": len(self.state.quests_found),
            "npcs_found": len(self.state.npcs_found),
            "pois_found": len(self.state.pois_found)
        }


# Global fallback navigator instance
_fallback_navigator = None

def get_fallback_navigator() -> FallbackNavigator:
    """Get global fallback navigator instance."""
    global _fallback_navigator
    if _fallback_navigator is None:
        _fallback_navigator = FallbackNavigator()
    return _fallback_navigator

def start_fallback_navigation(planet: str, zone: str, 
                            pattern_name: str = "standard_exploration") -> bool:
    """Start fallback navigation for a zone.
    
    Parameters
    ----------
    planet : str
        Planet name
    zone : str
        Zone name
    pattern_name : str
        Generic pattern to use if no zone profile found
        
    Returns
    -------
    bool
        True if fallback navigation started successfully
    """
    navigator = get_fallback_navigator()
    return navigator.start_fallback_navigation(planet, zone, pattern_name)

def execute_navigation_loop() -> bool:
    """Execute the navigation loop for the current zone.
    
    Returns
    -------
    bool
        True if navigation loop completed successfully
    """
    navigator = get_fallback_navigator()
    return navigator.execute_navigation_loop()

def get_fallback_status() -> Dict[str, Any]:
    """Get current fallback navigation status.
    
    Returns
    -------
    dict
        Current fallback status information
    """
    navigator = get_fallback_navigator()
    return navigator.get_fallback_status()

def get_zone_profile(planet: str, zone: str) -> Optional[ZoneProfile]:
    """Get zone profile for a specific planet and zone.
    
    Parameters
    ----------
    planet : str
        Planet name
    zone : str
        Zone name
        
    Returns
    -------
    ZoneProfile or None
        Zone profile if found, None otherwise
    """
    navigator = get_fallback_navigator()
    return navigator.get_zone_profile(planet, zone) 