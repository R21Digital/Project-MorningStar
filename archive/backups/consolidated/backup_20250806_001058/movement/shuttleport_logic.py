"""
Shuttleport Travel Logic for MS11

This module provides logic to:
- Read current city from UI or config
- Route to nearest shuttleport using mini-map estimation
- Select travel destination via OCR/template matching
- Simulate shuttle travel loop
- Mount up if possible for travel segments
"""

import json
import logging
import time
import math
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import pyautogui
import cv2
import numpy as np

from core.database import get_database
from core.navigation.navigation_engine import NavigationEngine, Coordinate, navigate_to_coordinates
from core.dialogue_handler import DialogueHandler, detect_dialogue_box, extract_dialogue_text
from core.screenshot import capture_screen
from core.ocr import extract_text_from_screen


class ShuttleStatus(Enum):
    """Shuttle travel status."""
    IDLE = "idle"
    TRAVELING = "traveling"
    ARRIVED = "arrived"
    FAILED = "failed"
    TIMEOUT = "timeout"
    NO_SHUTTLE = "no_shuttle"
    DESTINATION_SELECTED = "destination_selected"


class MountStatus(Enum):
    """Mount status."""
    UNMOUNTED = "unmounted"
    MOUNTED = "mounted"
    MOUNTING = "mounting"
    DISMOUNTING = "dismounting"
    NO_MOUNT = "no_mount"


@dataclass
class ShuttleportLocation:
    """Represents a shuttleport location."""
    planet: str
    city: str
    coordinates: Tuple[int, int]
    npc_name: str
    destinations: List[Dict[str, str]]
    is_active: bool = True
    distance: Optional[float] = None


@dataclass
class TravelDestination:
    """Represents a travel destination."""
    planet: str
    city: str
    coordinates: Tuple[int, int]
    travel_time: float  # seconds
    cost: int
    is_available: bool = True


@dataclass
class TravelSession:
    """Represents a travel session."""
    origin: ShuttleportLocation
    destination: TravelDestination
    status: ShuttleStatus
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    mount_used: Optional[str] = None


class ShuttleportLogic:
    """
    Shuttleport travel and routing system.
    
    Features:
    - Read current city from UI or config
    - Route to nearest shuttleport
    - Select travel destination via OCR
    - Handle shuttle travel simulation
    - Manage mount usage for travel
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize shuttleport logic.
        
        Args:
            data_dir: Path to data directory
        """
        self.logger = logging.getLogger("shuttleport_logic")
        self.data_dir = Path(data_dir)
        self.database = get_database()
        self.navigation_engine = NavigationEngine()
        self.dialogue_handler = DialogueHandler()
        
        # Current location state
        self.current_planet: str = "tatooine"
        self.current_city: str = "mos_eisley"
        self.current_coordinates: Optional[Coordinate] = None
        
        # Travel session tracking
        self.active_travel_session: Optional[TravelSession] = None
        self.recent_destinations: List[str] = []
        self.mount_status: MountStatus = MountStatus.UNMOUNTED
        self.available_mounts: List[str] = []
        
        # Configuration
        self.auto_mount_enabled = True
        self.travel_timeout = 60.0  # seconds
        self.mount_travel_threshold = 100.0  # meters - use mount for travel > this distance
        
        self._setup_logging()
        self._load_shuttle_data()
        self._load_mount_data()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _load_shuttle_data(self):
        """Load shuttle data from database."""
        try:
            shuttle_file = self.data_dir / "shuttles.json"
            if shuttle_file.exists():
                with open(shuttle_file, 'r') as f:
                    self.shuttle_data = json.load(f)
            else:
                self.logger.warning("Shuttle data file not found, using empty data")
                self.shuttle_data = {}
        except Exception as e:
            self.logger.error(f"Error loading shuttle data: {e}")
            self.shuttle_data = {}
    
    def _load_mount_data(self):
        """Load mount data (stub implementation)."""
        # In a real implementation, this would read from game state or config
        self.available_mounts = ["speeder_bike", "dewback", "bantha"]
        self.logger.info(f"Loaded {len(self.available_mounts)} available mounts")
    
    def read_current_city(self) -> str:
        """Read current city from UI or config.
        
        Returns:
            Current city name
        """
        try:
            # Try to read from UI first (stub implementation)
            # In a real implementation, this would use OCR to read city name from UI
            screen = capture_screen()
            if screen is not None:
                # Extract text from screen and look for city indicators
                text = extract_text_from_screen(screen)
                if text:
                    # Look for city names in the extracted text
                    city_indicators = ["Mos Eisley", "Anchorhead", "Coronet", "Theed"]
                    for indicator in city_indicators:
                        if indicator.lower() in text.lower():
                            self.current_city = indicator.lower().replace(" ", "_")
                            self.logger.info(f"Detected current city: {self.current_city}")
                            return self.current_city
            
            # Fallback to config or default
            self.logger.info(f"Using default city: {self.current_city}")
            return self.current_city
            
        except Exception as e:
            self.logger.error(f"Error reading current city: {e}")
            return self.current_city
    
    def find_nearest_shuttleport(self, planet: Optional[str] = None) -> Optional[ShuttleportLocation]:
        """Find the nearest shuttleport to current location.
        
        Args:
            planet: Optional planet filter (defaults to current planet)
            
        Returns:
            Nearest shuttleport location or None
        """
        try:
            target_planet = planet or self.current_planet
            current_city = self.read_current_city()
            
            if target_planet not in self.shuttle_data:
                self.logger.warning(f"No shuttle data for planet {target_planet}")
                return None
            
            shuttleports = []
            for city_data in self.shuttle_data[target_planet]:
                shuttleport = ShuttleportLocation(
                    planet=target_planet,
                    city=city_data["city"],
                    coordinates=(city_data["x"], city_data["y"]),
                    npc_name=city_data["npc"],
                    destinations=city_data["destinations"],
                    is_active=True
                )
                
                # Calculate distance if we have current coordinates
                if self.current_coordinates:
                    shuttle_coord = Coordinate(
                        x=shuttleport.coordinates[0],
                        y=shuttleport.coordinates[1],
                        zone=shuttleport.city,
                        planet=shuttleport.planet
                    )
                    shuttleport.distance = self.current_coordinates.distance_to(shuttle_coord)
                
                shuttleports.append(shuttleport)
            
            # Sort by distance (nearest first)
            shuttleports.sort(key=lambda s: s.distance or float('inf'))
            
            if shuttleports:
                nearest = shuttleports[0]
                self.logger.info(f"Found nearest shuttleport: {nearest.city} at {nearest.coordinates}")
                return nearest
            else:
                self.logger.warning(f"No shuttleports found on {target_planet}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error finding nearest shuttleport: {e}")
            return None
    
    def route_to_shuttleport(self, shuttleport: ShuttleportLocation) -> bool:
        """Route to a shuttleport location.
        
        Args:
            shuttleport: Shuttleport to route to
            
        Returns:
            True if routing was successful
        """
        try:
            # Check if we need to mount up for long travel
            if (self.auto_mount_enabled and 
                shuttleport.distance and 
                shuttleport.distance > self.mount_travel_threshold):
                self.mount_up()
            
            # Navigate to shuttleport coordinates
            success = navigate_to_coordinates(
                target_x=shuttleport.coordinates[0],
                target_y=shuttleport.coordinates[1],
                current_x=self.current_coordinates.x if self.current_coordinates else None,
                current_y=self.current_coordinates.y if self.current_coordinates else None,
                zone=shuttleport.city,
                planet=shuttleport.planet
            )
            
            if success:
                self.logger.info(f"Successfully routed to shuttleport in {shuttleport.city}")
                return True
            else:
                self.logger.error(f"Failed to route to shuttleport in {shuttleport.city}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error routing to shuttleport: {e}")
            return False
    
    def select_travel_destination(self, shuttleport: ShuttleportLocation, 
                                target_planet: str, target_city: str) -> Optional[TravelDestination]:
        """Select travel destination via OCR/template matching.
        
        Args:
            shuttleport: Current shuttleport
            target_planet: Target planet
            target_city: Target city
            
        Returns:
            Travel destination or None
        """
        try:
            # Look for destination in shuttleport destinations
            target_destination = None
            for dest in shuttleport.destinations:
                if (dest["planet"].lower() == target_planet.lower() and 
                    dest["city"].lower() == target_city.lower()):
                    target_destination = dest
                    break
            
            if not target_destination:
                self.logger.warning(f"Destination {target_city} on {target_planet} not available from {shuttleport.city}")
                return None
            
            # Simulate destination selection via OCR/template matching
            # In a real implementation, this would:
            # 1. Detect dialogue window with destination options
            # 2. Extract available destinations via OCR
            # 3. Click on the target destination
            
            # Stub implementation - simulate successful selection
            destination = TravelDestination(
                planet=target_destination["planet"],
                city=target_destination["city"],
                coordinates=(0, 0),  # Will be set when arriving
                travel_time=30.0,  # 30 seconds travel time
                cost=50,  # 50 credits
                is_available=True
            )
            
            self.logger.info(f"Selected destination: {destination.city} on {destination.planet}")
            return destination
            
        except Exception as e:
            self.logger.error(f"Error selecting travel destination: {e}")
            return None
    
    def simulate_shuttle_travel(self, destination: TravelDestination) -> bool:
        """Simulate shuttle travel loop.
        
        Args:
            destination: Travel destination
            
        Returns:
            True if travel was successful
        """
        try:
            import time
            
            # Start travel session
            self.active_travel_session = TravelSession(
                origin=None,  # Will be set by caller
                destination=destination,
                status=ShuttleStatus.TRAVELING,
                start_time=time.time()
            )
            
            self.logger.info(f"Starting shuttle travel to {destination.city} on {destination.planet}")
            
            # Simulate travel time
            time.sleep(min(destination.travel_time, 5.0))  # Cap at 5 seconds for testing
            
            # Update current location
            self.current_planet = destination.planet
            self.current_city = destination.city
            self.current_coordinates = Coordinate(
                x=destination.coordinates[0],
                y=destination.coordinates[1],
                zone=destination.city,
                planet=destination.planet
            )
            
            # Complete travel session
            if self.active_travel_session:
                self.active_travel_session.completion_time = time.time()
                self.active_travel_session.status = ShuttleStatus.ARRIVED
            
            self.logger.info(f"Arrived at {destination.city} on {destination.planet}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shuttle travel: {e}")
            if self.active_travel_session:
                self.active_travel_session.status = ShuttleStatus.FAILED
            return False
    
    def mount_up(self, mount_name: Optional[str] = None) -> bool:
        """Mount up if possible for travel segments.
        
        Args:
            mount_name: Specific mount to use (optional)
            
        Returns:
            True if mounting was successful
        """
        try:
            if self.mount_status == MountStatus.MOUNTED:
                self.logger.info("Already mounted")
                return True
            
            # Select mount
            if not mount_name and self.available_mounts:
                mount_name = self.available_mounts[0]  # Use first available mount
            
            if not mount_name:
                self.logger.warning("No mount available")
                return False
            
            # Simulate mounting (stub implementation)
            # In a real implementation, this would:
            # 1. Open mount menu
            # 2. Select mount
            # 3. Click mount button
            
            self.mount_status = MountStatus.MOUNTING
            time.sleep(1.0)  # Simulate mounting time
            self.mount_status = MountStatus.MOUNTED
            
            self.logger.info(f"Mounted {mount_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error mounting up: {e}")
            self.mount_status = MountStatus.UNMOUNTED
            return False
    
    def dismount(self) -> bool:
        """Dismount from current mount.
        
        Returns:
            True if dismounting was successful
        """
        try:
            if self.mount_status == MountStatus.UNMOUNTED:
                self.logger.info("Already unmounted")
                return True
            
            # Simulate dismounting (stub implementation)
            self.mount_status = MountStatus.DISMOUNTING
            time.sleep(1.0)  # Simulate dismounting time
            self.mount_status = MountStatus.UNMOUNTED
            
            self.logger.info("Dismounted")
            return True
            
        except Exception as e:
            self.logger.error(f"Error dismounting: {e}")
            return False
    
    def travel_to_destination(self, target_planet: str, target_city: str) -> bool:
        """Complete travel to a destination.
        
        Args:
            target_planet: Target planet
            target_city: Target city
            
        Returns:
            True if travel was successful
        """
        try:
            # Find nearest shuttleport
            shuttleport = self.find_nearest_shuttleport()
            if not shuttleport:
                self.logger.error("No shuttleport found")
                return False
            
            # Route to shuttleport
            if not self.route_to_shuttleport(shuttleport):
                self.logger.error("Failed to route to shuttleport")
                return False
            
            # Select destination
            destination = self.select_travel_destination(shuttleport, target_planet, target_city)
            if not destination:
                self.logger.error("Failed to select travel destination")
                return False
            
            # Simulate shuttle travel
            if not self.simulate_shuttle_travel(destination):
                self.logger.error("Failed to complete shuttle travel")
                return False
            
            # Dismount if we mounted for travel
            if self.mount_status == MountStatus.MOUNTED:
                self.dismount()
            
            self.logger.info(f"Successfully traveled to {target_city} on {target_planet}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during travel: {e}")
            return False
    
    def get_travel_summary(self) -> Dict[str, Any]:
        """Get travel summary.
        
        Returns:
            Dictionary with travel summary
        """
        return {
            "current_planet": self.current_planet,
            "current_city": self.current_city,
            "current_coordinates": str(self.current_coordinates) if self.current_coordinates else None,
            "mount_status": self.mount_status.name,
            "available_mounts": self.available_mounts,
            "active_travel_session": self.active_travel_session.destination.city if self.active_travel_session else None,
            "recent_destinations": self.recent_destinations
        }


# Global convenience functions
def get_shuttleport_logic() -> ShuttleportLogic:
    """Get the global shuttleport logic instance."""
    return ShuttleportLogic()


def find_nearest_shuttleport(planet: Optional[str] = None) -> Optional[ShuttleportLocation]:
    """Find the nearest shuttleport."""
    logic = get_shuttleport_logic()
    return logic.find_nearest_shuttleport(planet)


def route_to_shuttleport(shuttleport: ShuttleportLocation) -> bool:
    """Route to a shuttleport."""
    logic = get_shuttleport_logic()
    return logic.route_to_shuttleport(shuttleport)


def travel_to_destination(target_planet: str, target_city: str) -> bool:
    """Travel to a destination."""
    logic = get_shuttleport_logic()
    return logic.travel_to_destination(target_planet, target_city)


def mount_up(mount_name: Optional[str] = None) -> bool:
    """Mount up for travel."""
    logic = get_shuttleport_logic()
    return logic.mount_up(mount_name)


def get_travel_summary() -> Dict[str, Any]:
    """Get travel summary."""
    logic = get_shuttleport_logic()
    return logic.get_travel_summary() 