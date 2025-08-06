"""
Planetary Travel Manager

This module provides comprehensive planetary travel functionality including:
- Shuttleport and starport detection
- Ship travel support
- OCR-based travel dialog recognition
- Route planning and fallback handling
- Travel preference management
"""

import json
import logging
import time
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
from travel.locations import TravelLocation, TravelTerminal


class TravelType(Enum):
    """Types of travel available."""
    SHUTTLEPORT = "shuttleport"
    STARPORT = "starport"
    SHIP = "ship"
    UNKNOWN = "unknown"


class TravelStatus(Enum):
    """Status of travel operations."""
    IDLE = "idle"
    PLANNING = "planning"
    MOVING_TO_TERMINAL = "moving_to_terminal"
    INTERACTING = "interacting"
    SELECTING_DESTINATION = "selecting_destination"
    TRAVELING = "traveling"
    ARRIVED = "arrived"
    FAILED = "failed"


@dataclass
class TravelRoute:
    """Represents a travel route between locations."""
    start_planet: str
    start_city: str
    dest_planet: str
    dest_city: str
    travel_type: TravelType
    terminal: TravelTerminal
    estimated_time: int  # minutes
    cost: int  # credits
    fallback_cities: List[str] = None


@dataclass
class TravelPreferences:
    """User travel preferences."""
    preferred_travel_type: TravelType = TravelType.SHUTTLEPORT
    use_ship: bool = False
    max_cost: int = 1000
    max_travel_time: int = 30  # minutes
    prefer_direct_routes: bool = True
    fallback_enabled: bool = True


class PlanetaryTravelManager:
    """Manages planetary travel via shuttleports, starports, and ships."""
    
    def __init__(self, config_path: str = "data/planetary_routes.json"):
        """Initialize the planetary travel manager.
        
        Parameters
        ----------
        config_path : str
            Path to planetary routes configuration
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = OCREngine()
        
        # Travel data
        self.planetary_routes: Dict[str, List[str]] = {}
        self.travel_preferences: TravelPreferences = TravelPreferences()
        self.current_location: Optional[TravelLocation] = None
        self.current_route: Optional[TravelRoute] = None
        
        # State tracking
        self.travel_status = TravelStatus.IDLE
        self.last_travel_attempt = None
        self.travel_history: List[Dict[str, Any]] = []
        
        # Load configuration
        self._load_planetary_routes()
        self._load_travel_preferences()
        
        # Initialize travel terminals
        self._initialize_terminals()
        
        # Test mode flag
        self._test_mode = False
    
    def _load_planetary_routes(self):
        """Load planetary routes from configuration file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.planetary_routes = json.load(f)
                
                self.logger.info(f"Loaded {len(self.planetary_routes)} planetary routes")
                
            except Exception as e:
                self.logger.error(f"Failed to load planetary routes: {e}")
        else:
            self.logger.info("No planetary routes found, using defaults")
            self._create_default_routes()
    
    def _create_default_routes(self):
        """Create default planetary routes."""
        self.planetary_routes = {
            "corellia": ["tyrena", "kor_vella"],
            "naboo": ["theed", "kaadara"],
            "tatooine": ["mos_eisley", "bestine"],
            "dantooine": ["khoonda", "dantooine_mining_outpost"],
            "lok": ["nyms_stronghold", "lok_imperial_outpost"],
            "rori": ["narmle", "restuss"],
            "talus": ["dearic", "nashal"],
            "yavin4": ["labor_outpost", "mining_outpost"]
        }
    
    def _load_travel_preferences(self):
        """Load travel preferences from file."""
        prefs_file = Path("profiles/travel_preferences.json")
        if prefs_file.exists():
            try:
                with open(prefs_file, 'r') as f:
                    prefs_data = json.load(f)
                
                # Handle the case where preferred_travel_type might be "starport" instead of TravelType
                preferred_type_str = prefs_data.get("preferred_travel_type", "shuttleport")
                try:
                    preferred_travel_type = TravelType(preferred_type_str)
                except ValueError:
                    # If the string doesn't match enum values, default to shuttleport
                    preferred_travel_type = TravelType.SHUTTLEPORT
                
                self.travel_preferences = TravelPreferences(
                    preferred_travel_type=preferred_travel_type,
                    use_ship=prefs_data.get("use_ship", False),
                    max_cost=prefs_data.get("max_cost", 1000),
                    max_travel_time=prefs_data.get("max_travel_time", 30),
                    prefer_direct_routes=prefs_data.get("prefer_direct_routes", True),
                    fallback_enabled=prefs_data.get("fallback_enabled", True)
                )
                
                self.logger.info("Loaded travel preferences")
                
            except Exception as e:
                self.logger.error(f"Failed to load travel preferences: {e}")
                # Use defaults if loading fails
                self.travel_preferences = TravelPreferences()
        else:
            self.logger.info("No travel preferences found, using defaults")
            self.travel_preferences = TravelPreferences()
    
    def _initialize_terminals(self):
        """Initialize travel terminals with known locations."""
        # Import terminals from locations module
        from travel.locations import KNOWN_TERMINALS
        
        self.terminals = {}
        for terminal_id, terminal in KNOWN_TERMINALS.items():
            # Convert TerminalType to TravelType
            travel_type = TravelType(terminal.terminal_type.value)
            self.terminals[terminal_id] = TravelTerminal(
                name=terminal.name,
                city=terminal.city,
                planet=terminal.planet,
                terminal_type=travel_type,
                coordinates=terminal.coordinates,
                npc=terminal.npc,
                description=terminal.description,
                available_destinations=terminal.available_destinations
            )
        
        self.logger.info(f"Initialized {len(self.terminals)} travel terminals")
    
    def find_closest_terminal(self, current_location: TravelLocation, 
                            travel_type: TravelType = None) -> Optional[TravelTerminal]:
        """Find the closest travel terminal to current location.
        
        Parameters
        ----------
        current_location : TravelLocation
            Current location
        travel_type : TravelType, optional
            Preferred travel type
            
        Returns
        -------
        Optional[TravelTerminal]
            Closest terminal, or None if not found
        """
        if travel_type is None:
            travel_type = self.travel_preferences.preferred_travel_type
        
        closest_terminal = None
        min_distance = float('inf')
        
        for terminal in self.terminals.values():
            if terminal.terminal_type == travel_type:
                distance = self._calculate_distance(
                    current_location.coordinates,
                    terminal.coordinates
                )
                
                if distance < min_distance:
                    min_distance = distance
                    closest_terminal = terminal
        
        if closest_terminal:
            self.logger.info(f"Found closest {travel_type.value}: {closest_terminal.name}")
        
        return closest_terminal
    
    def _calculate_distance(self, coords1: Tuple[int, int], 
                          coords2: Tuple[int, int]) -> float:
        """Calculate distance between two coordinate pairs."""
        x1, y1 = coords1
        x2, y2 = coords2
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    def plan_travel_route(self, dest_planet: str, dest_city: str,
                         start_location: TravelLocation = None) -> Optional[TravelRoute]:
        """Plan a travel route to destination.
        
        Parameters
        ----------
        dest_planet : str
            Destination planet
        dest_city : str
            Destination city
        start_location : TravelLocation, optional
            Starting location. If None, uses current location.
            
        Returns
        -------
        Optional[TravelRoute]
            Planned travel route, or None if no route found
        """
        if start_location is None:
            start_location = self.current_location
        
        if not start_location:
            self.logger.error("No starting location available")
            return None
        
        # Check if destination is valid
        if dest_planet not in self.planetary_routes:
            self.logger.error(f"Unknown destination planet: {dest_planet}")
            return None
        
        available_cities = self.planetary_routes[dest_planet]
        if dest_city not in available_cities:
            if self.travel_preferences.fallback_enabled:
                dest_city = available_cities[0]
                self.logger.info(f"Using fallback city: {dest_city}")
            else:
                self.logger.error(f"Unknown destination city: {dest_city}")
                return None
        
        # Find closest terminal
        terminal = self.find_closest_terminal(start_location)
        if not terminal:
            self.logger.error("No suitable travel terminal found")
            return None
        
        # Create travel route
        route = TravelRoute(
            start_planet=start_location.planet,
            start_city=start_location.city,
            dest_planet=dest_planet,
            dest_city=dest_city,
            travel_type=terminal.terminal_type,
            terminal=terminal,
            estimated_time=self._estimate_travel_time(terminal.terminal_type),
            cost=self._estimate_travel_cost(terminal.terminal_type),
            fallback_cities=available_cities
        )
        
        self.logger.info(f"Planned route: {start_location.city} -> {dest_city}")
        return route
    
    def _estimate_travel_time(self, travel_type: TravelType) -> int:
        """Estimate travel time in minutes."""
        time_estimates = {
            TravelType.SHUTTLEPORT: 5,
            TravelType.STARPORT: 10,
            TravelType.SHIP: 15
        }
        return time_estimates.get(travel_type, 10)
    
    def _estimate_travel_cost(self, travel_type: TravelType) -> int:
        """Estimate travel cost in credits."""
        cost_estimates = {
            TravelType.SHUTTLEPORT: 50,
            TravelType.STARPORT: 200,
            TravelType.SHIP: 500
        }
        return cost_estimates.get(travel_type, 100)
    
    def execute_travel(self, route: TravelRoute) -> bool:
        """Execute a travel route.
        
        Parameters
        ----------
        route : TravelRoute
            Travel route to execute
            
        Returns
        -------
        bool
            True if travel was successful
        """
        self.travel_status = TravelStatus.PLANNING
        self.current_route = route
        
        try:
            self.logger.info(f"Starting travel: {route.start_city} -> {route.dest_city}")
            
            # Step 1: Move to terminal
            if not self._move_to_terminal(route.terminal):
                self.travel_status = TravelStatus.FAILED
                return False
            
            # Step 2: Interact with terminal
            if not self._interact_with_terminal(route.terminal):
                self.travel_status = TravelStatus.FAILED
                return False
            
            # Step 3: Select destination
            if not self._select_destination(route):
                self.travel_status = TravelStatus.FAILED
                return False
            
            # Step 4: Confirm travel
            if not self._confirm_travel():
                self.travel_status = TravelStatus.FAILED
                return False
            
            # Step 5: Wait for travel completion
            self.travel_status = TravelStatus.TRAVELING
            
            # For testing, use shorter wait times
            if hasattr(self, '_test_mode') and self._test_mode:
                wait_time = min(route.estimated_time, 1)  # Max 1 second in test mode
            else:
                wait_time = route.estimated_time * 60  # Convert to seconds
            
            time.sleep(wait_time)
            
            # Step 6: Update location
            self._update_location_after_travel(route)
            
            self.travel_status = TravelStatus.ARRIVED
            self.logger.info(f"Successfully traveled to {route.dest_city}")
            
            # Record travel history
            self._record_travel_history(route)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Travel execution failed: {e}")
            self.travel_status = TravelStatus.FAILED
            return False
    
    def _move_to_terminal(self, terminal: TravelTerminal) -> bool:
        """Move to travel terminal location."""
        self.travel_status = TravelStatus.MOVING_TO_TERMINAL
        
        self.logger.info(f"Moving to terminal: {terminal.name}")
        
        # In a real implementation, this would use navigation system
        # For now, simulate movement
        time.sleep(2.0)  # Simulate travel time
        
        return True
    
    def _interact_with_terminal(self, terminal: TravelTerminal) -> bool:
        """Interact with travel terminal."""
        self.travel_status = TravelStatus.INTERACTING
        
        self.logger.info(f"Interacting with {terminal.name}")
        
        # Simulate terminal interaction
        time.sleep(1.0)
        
        return True
    
    def _select_destination(self, route: TravelRoute) -> bool:
        """Select destination from travel dialog."""
        self.travel_status = TravelStatus.SELECTING_DESTINATION
        
        try:
            # Capture screen and look for travel dialog
            screen_image = capture_screen()
            
            # Define regions where travel dialog might appear
            dialog_regions = [
                (300, 200, 400, 300),  # Center dialog
                (200, 150, 500, 350),  # Large dialog
                (100, 100, 600, 400)   # Full dialog
            ]
            
            for region in dialog_regions:
                ocr_result = self.ocr_engine.extract_text_from_screen(region)
                
                if ocr_result.text:
                    # Look for destination options
                    if self._find_destination_in_text(ocr_result.text, route.dest_planet, route.dest_city):
                        self.logger.info(f"Found destination: {route.dest_planet} - {route.dest_city}")
                        return True
            
            # If OCR doesn't find destination, try fallback cities
            if route.fallback_cities:
                for fallback_city in route.fallback_cities:
                    if fallback_city != route.dest_city:
                        self.logger.info(f"Trying fallback city: {fallback_city}")
                        # Try to select fallback city
                        if self._select_fallback_destination(route.dest_planet, fallback_city):
                            route.dest_city = fallback_city
                            return True
            
            self.logger.error("Could not find destination in travel dialog")
            return False
            
        except Exception as e:
            self.logger.error(f"Error selecting destination: {e}")
            return False
    
    def _find_destination_in_text(self, text: str, planet: str, city: str) -> bool:
        """Find destination in OCR text."""
        text_lower = text.lower()
        planet_lower = planet.lower()
        city_lower = city.lower()
        
        # Look for planet and city names
        if planet_lower in text_lower and city_lower in text_lower:
            return True
        
        # Look for common variations
        city_variations = {
            "mos_eisley": ["mos eisley", "mos eisley", "mos eisley"],
            "theed": ["theed", "theed palace"],
            "coronet": ["coronet", "coronet city"],
            "tyrena": ["tyrena", "tyrena city"]
        }
        
        if city_lower in city_variations:
            for variation in city_variations[city_lower]:
                if variation in text_lower:
                    return True
        
        return False
    
    def _select_fallback_destination(self, planet: str, city: str) -> bool:
        """Select fallback destination."""
        self.logger.info(f"Selecting fallback destination: {planet} - {city}")
        
        # Simulate fallback selection
        time.sleep(1.0)
        
        return True
    
    def _confirm_travel(self) -> bool:
        """Confirm travel selection."""
        self.logger.info("Confirming travel selection")
        
        # Simulate confirmation
        time.sleep(0.5)
        
        return True
    
    def _update_location_after_travel(self, route: TravelRoute):
        """Update current location after successful travel."""
        self.current_location = TravelLocation(
            city=route.dest_city,
            planet=route.dest_planet,
            coordinates=(0, 0),  # Would be updated with actual coordinates
            zone="travel_destination"
        )
        
        self.logger.info(f"Updated location: {route.dest_city}, {route.dest_planet}")
    
    def _record_travel_history(self, route: TravelRoute):
        """Record travel in history."""
        travel_record = {
            "timestamp": datetime.now().isoformat(),
            "start_planet": route.start_planet,
            "start_city": route.start_city,
            "dest_planet": route.dest_planet,
            "dest_city": route.dest_city,
            "travel_type": route.travel_type.value,
            "cost": route.cost,
            "estimated_time": route.estimated_time,
            "status": "completed"
        }
        
        self.travel_history.append(travel_record)
        
        # Keep only last 50 travel records
        if len(self.travel_history) > 50:
            self.travel_history = self.travel_history[-50:]
    
    def travel_to_planet(self, dest_planet: str, dest_city: str = None) -> bool:
        """Travel to a specific planet and city.
        
        Parameters
        ----------
        dest_planet : str
            Destination planet
        dest_city : str, optional
            Destination city. If None, uses first available city.
            
        Returns
        -------
        bool
            True if travel was successful
        """
        # Plan route
        route = self.plan_travel_route(dest_planet, dest_city or "")
        if not route:
            return False
        
        # Execute travel
        return self.execute_travel(route)
    
    def get_travel_status(self) -> Dict[str, Any]:
        """Get current travel status.
        
        Returns
        -------
        Dict[str, Any]
            Current travel status information
        """
        return {
            "status": self.travel_status.value,
            "current_location": asdict(self.current_location) if self.current_location else None,
            "current_route": asdict(self.current_route) if self.current_route else None,
            "travel_preferences": asdict(self.travel_preferences),
            "travel_history": self.travel_history[-10:],  # Last 10 travels
            "available_planets": list(self.planetary_routes.keys())
        }
    
    def update_current_location(self, location: TravelLocation):
        """Update current location."""
        self.current_location = location
        self.logger.info(f"Updated current location: {location.city}, {location.planet}")
    
    def enable_test_mode(self):
        """Enable test mode for faster execution."""
        self._test_mode = True
        self.logger.info("Test mode enabled")
    
    def save_travel_preferences(self):
        """Save travel preferences to file."""
        prefs_file = Path("profiles/travel_preferences.json")
        prefs_file.parent.mkdir(exist_ok=True)
        
        # Convert enum to string for JSON serialization
        prefs_dict = asdict(self.travel_preferences)
        prefs_dict["preferred_travel_type"] = prefs_dict["preferred_travel_type"].value
        
        with open(prefs_file, 'w') as f:
            json.dump(prefs_dict, f, indent=2)
        
        self.logger.info("Saved travel preferences")


# Global instance
_planetary_travel_manager: Optional[PlanetaryTravelManager] = None


def get_planetary_travel_manager() -> PlanetaryTravelManager:
    """Get the global planetary travel manager instance."""
    global _planetary_travel_manager
    if _planetary_travel_manager is None:
        _planetary_travel_manager = PlanetaryTravelManager()
    return _planetary_travel_manager


def travel_to_planet(dest_planet: str, dest_city: str = None) -> bool:
    """Travel to a specific planet."""
    manager = get_planetary_travel_manager()
    return manager.travel_to_planet(dest_planet, dest_city)


def get_travel_status() -> Dict[str, Any]:
    """Get current travel status."""
    manager = get_planetary_travel_manager()
    return manager.get_travel_status()


def update_current_location(city: str, planet: str, coordinates: Tuple[int, int] = (0, 0)):
    """Update current location."""
    manager = get_planetary_travel_manager()
    location = TravelLocation(city=city, planet=planet, coordinates=coordinates)
    manager.update_current_location(location) 