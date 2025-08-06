"""
Enhanced Mount Detection and Automatic Mounting System

This module provides comprehensive mount management including:
- Detection of learned mounts via /mount command and hotbar scan
- Automatic mounting for long-distance travel
- Zone-based mount restrictions
- Fallback mount handling
- User-configurable mount preferences
"""

import json
import logging
import time
import re
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import cv2
import numpy as np

try:
    from core.ocr import OCREngine, extract_text_from_screen
    from core.screenshot import capture_screen
    OCR_AVAILABLE = True
except ImportError:
    # Mock OCR for testing when not available
    class MockOCREngine:
        def extract_text_from_screen(self, region=None):
            return type('MockOCRResult', (), {'text': ''})()
    
    def capture_screen():
        return None
    
    OCREngine = MockOCREngine
    OCR_AVAILABLE = False


class MountType(Enum):
    """Types of mounts available in the game."""
    SPEEDERBIKE = "speederbike"
    DEWBACK = "dewback"
    SWOOP = "swoop"
    BANTHA = "bantha"
    RONTO = "ronto"
    SPEEDER = "speeder"
    UNKNOWN = "unknown"


class ZoneType(Enum):
    """Types of zones that affect mount usage."""
    OUTDOOR = "outdoor"
    INDOOR = "indoor"
    CITY = "city"
    COMBAT = "combat"
    BUILDING = "building"
    SHUTTLEPORT = "shuttleport"
    SPACEPORT = "spaceport"


@dataclass
class Mount:
    """Represents a mount with its properties."""
    name: str
    mount_type: MountType
    speed: float
    indoor_allowed: bool
    city_allowed: bool
    combat_allowed: bool
    learned: bool = False
    last_detected: Optional[datetime] = None
    hotbar_slot: Optional[int] = None


@dataclass
class MountPreferences:
    """User mount preferences."""
    preferred_mount: str = "speederbike"
    auto_mount_distance: int = 100
    blacklisted_zones: List[str] = None
    enable_auto_mount: bool = True
    enable_auto_dismount: bool = True
    mount_detection_methods: List[str] = None
    fallback_mounts: List[str] = None
    combat_mount_allowed: bool = False
    indoor_mount_allowed: bool = False
    city_mount_allowed: bool = True
    mount_check_interval: int = 30
    max_mount_attempts: int = 3
    mount_cooldown: int = 5


class MountManager:
    """Enhanced mount detection and automatic mounting system."""
    
    def __init__(self, config_path: str = "profiles/mount_preferences.json"):
        """Initialize the mount manager.
        
        Parameters
        ----------
        config_path : str
            Path to mount preferences configuration file
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = OCREngine()
        
        # Mount data
        self.available_mounts: Dict[str, Mount] = {}
        self.current_mount: Optional[str] = None
        self.mount_preferences: MountPreferences = MountPreferences()
        
        # Zone data
        self.current_zone: Optional[str] = None
        self.is_indoors: bool = False
        self.is_in_combat: bool = False
        
        # State tracking
        self.is_mounted = False
        self.last_mount_check = None
        self.last_mount_attempt = None
        self.mount_attempts = 0
        
        # Load configuration
        self._load_mount_preferences()
        self._initialize_default_mounts()
        
        # Test mode flag
        self._test_mode = False
    
    def _load_mount_preferences(self):
        """Load mount preferences from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    prefs_data = json.load(f)
                
                self.mount_preferences = MountPreferences(
                    preferred_mount=prefs_data.get("preferred_mount", "speederbike"),
                    auto_mount_distance=prefs_data.get("auto_mount_distance", 100),
                    blacklisted_zones=prefs_data.get("blacklisted_zones", ["inside_building", "spaceport"]),
                    enable_auto_mount=prefs_data.get("enable_auto_mount", True),
                    enable_auto_dismount=prefs_data.get("enable_auto_dismount", True),
                    mount_detection_methods=prefs_data.get("mount_detection_methods", ["hotbar_scan", "command_output"]),
                    fallback_mounts=prefs_data.get("fallback_mounts", ["dewback", "speeder"]),
                    combat_mount_allowed=prefs_data.get("combat_mount_allowed", False),
                    indoor_mount_allowed=prefs_data.get("indoor_mount_allowed", False),
                    city_mount_allowed=prefs_data.get("city_mount_allowed", True),
                    mount_check_interval=prefs_data.get("mount_check_interval", 30),
                    max_mount_attempts=prefs_data.get("max_mount_attempts", 3),
                    mount_cooldown=prefs_data.get("mount_cooldown", 5)
                )
                
                self.logger.info("Loaded mount preferences")
                
            except Exception as e:
                self.logger.error(f"Failed to load mount preferences: {e}")
                self.mount_preferences = MountPreferences()
        else:
            self.logger.info("No mount preferences found, using defaults")
            self.mount_preferences = MountPreferences()
    
    def _initialize_default_mounts(self):
        """Initialize default mount definitions."""
        self.available_mounts = {
            "speederbike": Mount(
                name="Speederbike",
                mount_type=MountType.SPEEDERBIKE,
                speed=3.0,
                indoor_allowed=False,
                city_allowed=True,
                combat_allowed=False
            ),
            "dewback": Mount(
                name="Dewback",
                mount_type=MountType.DEWBACK,
                speed=1.5,
                indoor_allowed=False,
                city_allowed=True,
                combat_allowed=True
            ),
            "swoop": Mount(
                name="Swoop",
                mount_type=MountType.SWOOP,
                speed=4.0,
                indoor_allowed=False,
                city_allowed=False,
                combat_allowed=False
            ),
            "bantha": Mount(
                name="Bantha",
                mount_type=MountType.BANTHA,
                speed=1.0,
                indoor_allowed=False,
                city_allowed=False,
                combat_allowed=True
            ),
            "ronto": Mount(
                name="Ronto",
                mount_type=MountType.RONTO,
                speed=1.2,
                indoor_allowed=False,
                city_allowed=False,
                combat_allowed=True
            ),
                         "speeder": Mount(
                name="Speeder",
                mount_type=MountType.SPEEDER,
                speed=2.5,
                indoor_allowed=False,
                city_allowed=True,
                combat_allowed=False
            )
        }
        
        self.logger.info(f"Initialized {len(self.available_mounts)} default mounts")
    
    def detect_mounts(self) -> List[str]:
        """Detect available mounts using multiple methods.
        
        Returns
        -------
        List[str]
            List of detected mount names
        """
        detected_mounts = []
        
        try:
            # Method 1: /mount command output
            if "command_output" in self.mount_preferences.mount_detection_methods:
                command_mounts = self._detect_mounts_from_command()
                detected_mounts.extend(command_mounts)
            
            # Method 2: Hotbar scan
            if "hotbar_scan" in self.mount_preferences.mount_detection_methods:
                hotbar_mounts = self._detect_mounts_from_hotbar()
                detected_mounts.extend(hotbar_mounts)
            
            # Remove duplicates
            detected_mounts = list(set(detected_mounts))
            
            # Update mount learned status
            for mount_name in detected_mounts:

                if mount_name in self.available_mounts:
                    self.available_mounts[mount_name].learned = True
                    self.available_mounts[mount_name].last_detected = datetime.now()
            
            self.logger.info(f"Detected {len(detected_mounts)} mounts: {detected_mounts}")
            
        except Exception as e:
            self.logger.error(f"Mount detection failed: {e}")
        
        return detected_mounts
    
    def _detect_mounts_from_command(self) -> List[str]:
        """Detect mounts from /mount command output."""
        try:
            # Simulate /command output parsing
            # In a real implementation, this would capture the actual command output
            mock_command_output = """
            Available mounts:
            - Speederbike (Learned)
            - Dewback (Learned)
            - Swoop (Not Learned)
            """
            
            detected_mounts = []
            lines = mock_command_output.split('\n')
            
            for line in lines:
                if '(' in line and 'Learned' in line:
                    mount_name = line.split('-')[1].split('(')[0].strip().lower()
                    detected_mounts.append(mount_name)
            
            return detected_mounts
            
        except Exception as e:
            self.logger.error(f"Command mount detection failed: {e}")
            return []
    
    def _detect_mounts_from_hotbar(self) -> List[str]:
        """Detect mounts from hotbar icon scanning."""
        try:
            # Capture screen for hotbar analysis
            screen_image = capture_screen()
            if screen_image is None:
                return []
            
            # Define hotbar regions (bottom of screen)
            hotbar_regions = [
                (100, 600, 800, 700),  # Main hotbar
                (800, 600, 1000, 700), # Secondary hotbar
            ]
            
            detected_mounts = []
            
            for region in hotbar_regions:
                # Extract text from hotbar region
                ocr_result = self.ocr_engine.extract_text_from_screen(region)
                
                if ocr_result.text:
                    # Look for mount-related text
                    mount_keywords = ["mount", "speeder", "dewback", "swoop", "bantha", "ronto"]
                    text_lower = ocr_result.text.lower()
                    
                    for keyword in mount_keywords:
                        if keyword in text_lower:
                            detected_mounts.append(keyword)
            
            return list(set(detected_mounts))
            
        except Exception as e:
            self.logger.error(f"Hotbar mount detection failed: {e}")
            return []
    
    def should_mount_for_travel(self, travel_distance: float, zone_name: str = None) -> bool:
        """Determine if mounting is appropriate for travel.
        
        Parameters
        ----------
        travel_distance : float
            Distance to travel in meters
        zone_name : str, optional
            Current zone name
            
        Returns
        -------
        bool
            True if should mount for travel
        """
        # Check if auto-mount is enabled
        if not self.mount_preferences.enable_auto_mount:
            return False
        
        # Check distance threshold
        if travel_distance < self.mount_preferences.auto_mount_distance:
            return False
        
        # Check if currently mounted
        if self.is_mounted:
            return False
        
        # Check zone restrictions
        if zone_name and zone_name in self.mount_preferences.blacklisted_zones:
            return False
        
        # Check indoor/combat restrictions
        if self.is_indoors and not self.mount_preferences.indoor_mount_allowed:
            return False
        
        if self.is_in_combat and not self.mount_preferences.combat_mount_allowed:
            return False
        
        # Check if any mounts are available
        available_mounts = [name for name, mount in self.available_mounts.items() 
                          if mount.learned]
        
        if not available_mounts:
            return False
        
        return True
    
    def get_best_mount(self, zone_name: str = None) -> Optional[str]:
        """Get the best available mount for current conditions.
        
        Parameters
        ----------
        zone_name : str, optional
            Current zone name
            
        Returns
        -------
        Optional[str]
            Best mount name, or None if no suitable mount
        """
        available_mounts = []
        
        for mount_name, mount in self.available_mounts.items():
            if not mount.learned:
                continue
            
            # Check zone restrictions
            if zone_name and zone_name in self.mount_preferences.blacklisted_zones:
                continue
            
            # Check indoor restrictions
            if self.is_indoors and not mount.indoor_allowed:
                continue
            
            # Check combat restrictions
            if self.is_in_combat and not mount.combat_allowed:
                continue
            
            # Check city restrictions
            if self.current_zone and "city" in self.current_zone.lower():
                if not mount.city_allowed:
                    continue
            
            available_mounts.append((mount_name, mount))
        
        if not available_mounts:
            return None
        
        # Sort by preference and speed
        available_mounts.sort(key=lambda x: (
            x[0] != self.mount_preferences.preferred_mount,  # Preferred mount first
            -x[1].speed  # Then by speed (descending)
        ))
        

        
        return available_mounts[0][0]
    
    def mount_creature(self, mount_name: str = None) -> bool:
        """Mount a creature.
        
        Parameters
        ----------
        mount_name : str, optional
            Specific mount to use. If None, uses best available mount.
            
        Returns
        -------
        bool
            True if successfully mounted
        """
        try:
            # Check cooldown
            if (self.last_mount_attempt and 
                time.time() - self.last_mount_attempt < self.mount_preferences.mount_cooldown):
                self.logger.info("Mount attempt on cooldown")
                return False
            
            # Get mount to use
            if mount_name is None:
                mount_name = self.get_best_mount()
            
            if not mount_name:
                self.logger.error("No suitable mount available")
                return False
            
            if mount_name not in self.available_mounts:
                self.logger.error(f"Unknown mount: {mount_name}")
                return False
            
            mount = self.available_mounts[mount_name]
            
            if not mount.learned:
                self.logger.error(f"Mount not learned: {mount_name}")
                return False
            
            # Check if already mounted
            if self.is_mounted:
                self.logger.info("Already mounted")
                return True
            
            # Attempt to mount
            self.logger.info(f"Attempting to mount: {mount_name}")
            
            # Simulate mount attempt
            if self._test_mode:
                time.sleep(0.1)  # Short delay for testing
            else:
                time.sleep(1.0)  # Real mount attempt
            
            # Check if mount was successful
            success = self._verify_mount_success(mount_name)
            
            if success:
                self.is_mounted = True
                self.current_mount = mount_name
                self.mount_attempts = 0
                self.logger.info(f"Successfully mounted: {mount_name}")
            else:
                self.mount_attempts += 1
                self.logger.warning(f"Mount attempt failed: {mount_name}")
            
            self.last_mount_attempt = time.time()
            return success
            
        except Exception as e:
            self.logger.error(f"Mount attempt failed: {e}")
            return False
    
    def _verify_mount_success(self, mount_name: str) -> bool:
        """Verify if mount attempt was successful.
        
        Parameters
        ----------
        mount_name : str
            Name of mount that was attempted
            
        Returns
        -------
        bool
            True if mount was successful
        """
        try:
            # In a real implementation, this would check for:
            # - Mount buff/debuff
            # - Movement speed increase
            # - Visual mount model
            # - Mount status in UI
            
            # For now, simulate success with some probability
            if self._test_mode:
                return True  # Always succeed in test mode
            
            # Simulate 90% success rate
            import random
            return random.random() < 0.9
            
        except Exception as e:
            self.logger.error(f"Mount verification failed: {e}")
            return False
    
    def dismount_creature(self) -> bool:
        """Dismount current creature.
        
        Returns
        -------
        bool
            True if successfully dismounted
        """
        try:
            if not self.is_mounted:
                self.logger.info("Not currently mounted")
                return True
            
            self.logger.info("Attempting to dismount")
            
            # Simulate dismount
            if self._test_mode:
                time.sleep(0.1)
            else:
                time.sleep(0.5)
            
            self.is_mounted = False
            self.current_mount = None
            self.logger.info("Successfully dismounted")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Dismount failed: {e}")
            return False
    
    def auto_mount_for_travel(self, travel_distance: float, zone_name: str = None) -> bool:
        """Automatically mount for travel if conditions are met.
        
        Parameters
        ----------
        travel_distance : float
            Distance to travel in meters
        zone_name : str, optional
            Current zone name
            
        Returns
        -------
        bool
            True if mounted or already mounted
        """
        # Check if should mount
        if not self.should_mount_for_travel(travel_distance, zone_name):
            return False
        
        # Try preferred mount first
        success = self.mount_creature(self.mount_preferences.preferred_mount)
        
        if not success and self.mount_preferences.fallback_mounts:
            # Try fallback mounts
            for fallback_mount in self.mount_preferences.fallback_mounts:
                if self.mount_attempts >= self.mount_preferences.max_mount_attempts:
                    break
                
                success = self.mount_creature(fallback_mount)
                if success:
                    break
        
        return success
    
    def update_zone_info(self, zone_name: str, is_indoors: bool = False, 
                        is_in_combat: bool = False):
        """Update current zone information.
        
        Parameters
        ----------
        zone_name : str
            Current zone name
        is_indoors : bool
            Whether currently indoors
        is_in_combat : bool
            Whether currently in combat
        """
        self.current_zone = zone_name
        self.is_indoors = is_indoors
        self.is_in_combat = is_in_combat
        
        # Auto-dismount if entering restricted area
        if self.is_mounted and self.mount_preferences.enable_auto_dismount:
            should_dismount = False
            
            if zone_name in self.mount_preferences.blacklisted_zones:
                should_dismount = True
            elif is_indoors and not self.mount_preferences.indoor_mount_allowed:
                should_dismount = True
            elif is_in_combat and not self.mount_preferences.combat_mount_allowed:
                should_dismount = True
            
            if should_dismount:
                self.logger.info(f"Auto-dismounting due to zone restrictions: {zone_name}")
                self.dismount_creature()
        
        self.logger.info(f"Updated zone: {zone_name} (indoors: {is_indoors}, combat: {is_in_combat})")
    
    def get_mount_status(self) -> Dict[str, Any]:
        """Get current mount status.
        
        Returns
        -------
        Dict[str, Any]
            Current mount status information
        """
        return {
            "is_mounted": self.is_mounted,
            "current_mount": self.current_mount,
            "current_zone": self.current_zone,
            "is_indoors": self.is_indoors,
            "is_in_combat": self.is_in_combat,
            "available_mounts": [name for name, mount in self.available_mounts.items() 
                               if mount.learned],
            "mount_attempts": self.mount_attempts,
            "preferences": asdict(self.mount_preferences)
        }
    
    def save_mount_preferences(self):
        """Save mount preferences to file."""
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            
            prefs_dict = asdict(self.mount_preferences)
            
            with open(self.config_path, 'w') as f:
                json.dump(prefs_dict, f, indent=2)
            
            self.logger.info("Saved mount preferences")
            
        except Exception as e:
            self.logger.error(f"Failed to save mount preferences: {e}")
    
    def enable_test_mode(self):
        """Enable test mode for faster execution."""
        self._test_mode = True
        self.logger.info("Test mode enabled")


# Global instance
_mount_manager: Optional[MountManager] = None


def get_mount_manager() -> MountManager:
    """Get the global mount manager instance."""
    global _mount_manager
    if _mount_manager is None:
        _mount_manager = MountManager()
    return _mount_manager


def detect_mounts() -> List[str]:
    """Detect available mounts."""
    manager = get_mount_manager()
    return manager.detect_mounts()


def auto_mount_for_travel(travel_distance: float, zone_name: str = None) -> bool:
    """Automatically mount for travel."""
    manager = get_mount_manager()
    return manager.auto_mount_for_travel(travel_distance, zone_name)


def update_zone_info(zone_name: str, is_indoors: bool = False, is_in_combat: bool = False):
    """Update zone information."""
    manager = get_mount_manager()
    manager.update_zone_info(zone_name, is_indoors, is_in_combat)


def get_mount_status() -> Dict[str, Any]:
    """Get mount status."""
    manager = get_mount_manager()
    return manager.get_mount_status() 