"""
Personal Ship Travel System

This module provides functionality for traveling using personal ships,
including ship availability checking, cooldown management, and ship travel execution.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

try:
    from core.ocr import OCREngine, extract_text_from_screen
    from core.screenshot import capture_screen
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class ShipType(Enum):
    """Types of personal ships."""
    LIGHT_FREIGHTER = "light_freighter"
    HEAVY_FREIGHTER = "heavy_freighter"
    STARFIGHTER = "starfighter"
    TRANSPORT = "transport"
    UNKNOWN = "unknown"


class ShipStatus(Enum):
    """Status of ship travel operations."""
    IDLE = "idle"
    CHECKING_AVAILABILITY = "checking_availability"
    BOARDING_SHIP = "boarding_ship"
    PILOTING = "piloting"
    LANDING = "landing"
    ARRIVED = "arrived"
    FAILED = "failed"


@dataclass
class ShipInfo:
    """Information about a personal ship."""
    ship_type: ShipType
    ship_name: str
    unlocked: bool = False
    cooldown_remaining: int = 0  # seconds
    max_cooldown: int = 300  # 5 minutes default
    fuel_level: int = 100  # percentage
    last_used: float = 0.0


@dataclass
class ShipTravelResult:
    """Result of ship travel operation."""
    success: bool
    ship_used: Optional[str] = None
    travel_time: Optional[int] = None
    fuel_consumed: Optional[int] = None
    error_message: Optional[str] = None


class PersonalShipTravelSystem:
    """
    System for traveling using personal ships.
    
    Features:
    - Ship availability checking
    - Cooldown management
    - Auto-use personal ship when available
    - Ship travel execution
    - Success/failure rate tracking
    """
    
    def __init__(self, config_path: str = "data/ship_config.json"):
        """Initialize the personal ship travel system."""
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = OCREngine() if OCR_AVAILABLE else None
        self.current_status = ShipStatus.IDLE
        self.config_path = Path(config_path)
        
        # Ship information
        self.ships: Dict[str, ShipInfo] = {}
        self.travel_history: List[Dict[str, Any]] = []
        
        # Load ship configuration
        self._load_ship_config()
        
        # Ship detection keywords
        self.ship_keywords = {
            ShipType.LIGHT_FREIGHTER: ["light freighter", "x-wing", "y-wing"],
            ShipType.HEAVY_FREIGHTER: ["heavy freighter", "millennium falcon", "corellian"],
            ShipType.STARFIGHTER: ["starfighter", "tie fighter", "x-wing"],
            ShipType.TRANSPORT: ["transport", "shuttle", "passenger"]
        }
        
        # Ship travel patterns
        self.travel_patterns = {
            "ship_available": [
                r"ship available",
                r"ready for travel",
                r"ship unlocked"
            ],
            "cooldown_active": [
                r"cooldown: (\d+)",
                r"wait (\d+) seconds",
                r"ship recharging"
            ],
            "fuel_level": [
                r"fuel: (\d+)%",
                r"fuel level: (\d+)",
                r"(\d+)% fuel"
            ]
        }
    
    def _load_ship_config(self):
        """Load ship configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                for ship_name, ship_data in config.get("ships", {}).items():
                    ship_info = ShipInfo(
                        ship_type=ShipType(ship_data.get("type", "unknown")),
                        ship_name=ship_name,
                        unlocked=ship_data.get("unlocked", False),
                        cooldown_remaining=ship_data.get("cooldown_remaining", 0),
                        max_cooldown=ship_data.get("max_cooldown", 300),
                        fuel_level=ship_data.get("fuel_level", 100),
                        last_used=ship_data.get("last_used", 0.0)
                    )
                    self.ships[ship_name] = ship_info
                
                self.logger.info(f"Loaded {len(self.ships)} ship configurations")
            else:
                self._create_default_ship_config()
                
        except Exception as e:
            self.logger.error(f"Error loading ship config: {e}")
            self._create_default_ship_config()
    
    def _create_default_ship_config(self):
        """Create default ship configuration."""
        default_ships = {
            "x-wing": ShipInfo(
                ship_type=ShipType.STARFIGHTER,
                ship_name="X-Wing",
                unlocked=True,
                max_cooldown=180  # 3 minutes
            ),
            "millennium_falcon": ShipInfo(
                ship_type=ShipType.HEAVY_FREIGHTER,
                ship_name="Millennium Falcon",
                unlocked=False,
                max_cooldown=300  # 5 minutes
            ),
            "transport_shuttle": ShipInfo(
                ship_type=ShipType.TRANSPORT,
                ship_name="Transport Shuttle",
                unlocked=True,
                max_cooldown=120  # 2 minutes
            )
        }
        
        self.ships = default_ships
        self.logger.info("Created default ship configuration")
    
    def check_ship_availability(self, ship_name: str = None) -> Dict[str, Any]:
        """
        Check if a ship is available for travel.
        
        Parameters
        ----------
        ship_name : str, optional
            Specific ship to check. If None, checks all ships.
            
        Returns
        -------
        Dict[str, Any]
            Availability information
        """
        self.current_status = ShipStatus.CHECKING_AVAILABILITY
        self.logger.info(f"Checking ship availability: {ship_name or 'all'}")
        
        available_ships = []
        unavailable_ships = []
        
        ships_to_check = [ship_name] if ship_name else self.ships.keys()
        
        for ship_key in ships_to_check:
            if ship_key not in self.ships:
                continue
                
            ship = self.ships[ship_key]
            
            # Check if ship is unlocked
            if not ship.unlocked:
                unavailable_ships.append({
                    "name": ship.ship_name,
                    "reason": "not unlocked"
                })
                continue
            
            # Check cooldown
            current_time = time.time()
            time_since_last_use = current_time - ship.last_used
            cooldown_remaining = max(0, ship.max_cooldown - time_since_last_use)
            
            if cooldown_remaining > 0:
                unavailable_ships.append({
                    "name": ship.ship_name,
                    "reason": "cooldown active",
                    "cooldown_remaining": int(cooldown_remaining)
                })
                continue
            
            # Check fuel level
            if ship.fuel_level < 20:
                unavailable_ships.append({
                    "name": ship.ship_name,
                    "reason": "low fuel",
                    "fuel_level": ship.fuel_level
                })
                continue
            
            # Ship is available
            available_ships.append({
                "name": ship.ship_name,
                "type": ship.ship_type.value,
                "fuel_level": ship.fuel_level,
                "travel_time": self._estimate_travel_time(ship.ship_type)
            })
        
        result = {
            "available_ships": available_ships,
            "unavailable_ships": unavailable_ships,
            "total_available": len(available_ships),
            "total_unavailable": len(unavailable_ships)
        }
        
        self.logger.info(f"Ship availability: {len(available_ships)} available, {len(unavailable_ships)} unavailable")
        self.current_status = ShipStatus.IDLE
        
        return result
    
    def auto_use_personal_ship(self, destination: str) -> ShipTravelResult:
        """
        Automatically use personal ship if available and cooldown is ready.
        
        Parameters
        ----------
        destination : str
            Destination for travel
            
        Returns
        -------
        ShipTravelResult
            Result of ship travel attempt
        """
        self.logger.info(f"Attempting auto-use personal ship to {destination}")
        
        # Check ship availability
        availability = self.check_ship_availability()
        
        if not availability["available_ships"]:
            return ShipTravelResult(
                success=False,
                error_message="No ships available for travel"
            )
        
        # Select best available ship (prefer faster ships)
        best_ship = None
        for ship_info in availability["available_ships"]:
            if ship_info["type"] == "starfighter":
                best_ship = ship_info
                break
            elif ship_info["type"] == "light_freighter" and not best_ship:
                best_ship = ship_info
            elif not best_ship:
                best_ship = ship_info
        
        if not best_ship:
            return ShipTravelResult(
                success=False,
                error_message="No suitable ship found"
            )
        
        # Execute ship travel
        return self.execute_ship_travel(best_ship["name"], destination)
    
    def execute_ship_travel(self, ship_name: str, destination: str) -> ShipTravelResult:
        """
        Execute travel using a specific ship.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship to use
        destination : str
            Destination for travel
            
        Returns
        -------
        ShipTravelResult
            Result of ship travel
        """
        if ship_name not in self.ships:
            return ShipTravelResult(
                success=False,
                error_message=f"Ship {ship_name} not found"
            )
        
        ship = self.ships[ship_name]
        
        # Check if ship is available
        availability = self.check_ship_availability(ship_name)
        if not availability["available_ships"]:
            unavailable_reason = availability["unavailable_ships"][0]["reason"]
            return ShipTravelResult(
                success=False,
                error_message=f"Ship not available: {unavailable_reason}"
            )
        
        self.current_status = ShipStatus.BOARDING_SHIP
        self.logger.info(f"Boarding {ship.ship_name} for travel to {destination}")
        
        try:
            # Simulate boarding process
            time.sleep(0.1)
            
            # Simulate travel time
            travel_time = self._estimate_travel_time(ship.ship_type)
            self.current_status = ShipStatus.PILOTING
            
            self.logger.info(f"Traveling to {destination} (estimated {travel_time} seconds)")
            time.sleep(0.1)  # Simulate travel time
            
            # Simulate landing
            self.current_status = ShipStatus.LANDING
            time.sleep(0.1)
            
            # Update ship status
            current_time = time.time()
            ship.last_used = current_time
            ship.fuel_level = max(0, ship.fuel_level - 10)  # Consume fuel
            
            # Record travel
            travel_record = {
                "timestamp": current_time,
                "ship_name": ship.ship_name,
                "destination": destination,
                "travel_time": travel_time,
                "fuel_consumed": 10,
                "status": "success"
            }
            self.travel_history.append(travel_record)
            
            # Save updated ship configuration
            self._save_ship_config()
            
            self.current_status = ShipStatus.ARRIVED
            self.logger.info(f"Successfully traveled to {destination} using {ship.ship_name}")
            
            return ShipTravelResult(
                success=True,
                ship_used=ship.ship_name,
                travel_time=travel_time,
                fuel_consumed=10
            )
            
        except Exception as e:
            self.logger.error(f"Ship travel failed: {e}")
            self.current_status = ShipStatus.FAILED
            
            return ShipTravelResult(
                success=False,
                error_message=str(e)
            )
    
    def scan_for_ships(self) -> List[Dict[str, Any]]:
        """
        Scan for available ships using OCR.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of detected ships
        """
        if not OCR_AVAILABLE:
            return []
        
        detected_ships = []
        
        try:
            screenshot = capture_screen()
            if screenshot is None:
                return []
            
            # Define regions to scan for ship information
            scan_regions = [
                (100, 100, 400, 300),   # Top-left
                (500, 100, 400, 300),   # Top-right
                (100, 400, 400, 300),   # Bottom-left
            ]
            
            for region in scan_regions:
                ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, region)
                
                if ocr_result.confidence > 60:
                    text = ocr_result.text.lower()
                    
                    # Check for ship keywords
                    for ship_type, keywords in self.ship_keywords.items():
                        for keyword in keywords:
                            if keyword in text:
                                detected_ships.append({
                                    "type": ship_type.value,
                                    "confidence": ocr_result.confidence,
                                    "region": region,
                                    "text": text
                                })
                                break
                        
                        if any(keyword in text for keyword in keywords):
                            break
            
            self.logger.info(f"Ship scan completed: {len(detected_ships)} ships detected")
            
        except Exception as e:
            self.logger.error(f"Error during ship scanning: {e}")
        
        return detected_ships
    
    def _estimate_travel_time(self, ship_type: ShipType) -> int:
        """Estimate travel time for a ship type."""
        travel_times = {
            ShipType.STARFIGHTER: 30,      # 30 seconds
            ShipType.LIGHT_FREIGHTER: 45,   # 45 seconds
            ShipType.HEAVY_FREIGHTER: 60,   # 60 seconds
            ShipType.TRANSPORT: 90,         # 90 seconds
        }
        
        return travel_times.get(ship_type, 60)
    
    def _save_ship_config(self):
        """Save ship configuration to file."""
        try:
            config = {
                "ships": {}
            }
            
            for ship_name, ship_info in self.ships.items():
                config["ships"][ship_name] = {
                    "type": ship_info.ship_type.value,
                    "unlocked": ship_info.unlocked,
                    "cooldown_remaining": ship_info.cooldown_remaining,
                    "max_cooldown": ship_info.max_cooldown,
                    "fuel_level": ship_info.fuel_level,
                    "last_used": ship_info.last_used
                }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info("Ship configuration saved")
            
        except Exception as e:
            self.logger.error(f"Error saving ship config: {e}")
    
    def get_travel_statistics(self) -> Dict[str, Any]:
        """Get ship travel success/failure statistics."""
        if not self.travel_history:
            return {
                "total_travels": 0, 
                "successful_travels": 0,
                "success_rate": 0.0,
                "average_travel_time": 0.0,
                "recent_travels": []
            }
        
        total_travels = len(self.travel_history)
        successful_travels = len([
            record for record in self.travel_history 
            if record.get("status") == "success"
        ])
        
        success_rate = (successful_travels / total_travels) * 100 if total_travels > 0 else 0
        
        # Calculate average travel time
        travel_times = [
            record.get("travel_time", 0) 
            for record in self.travel_history 
            if record.get("travel_time")
        ]
        avg_travel_time = sum(travel_times) / len(travel_times) if travel_times else 0
        
        return {
            "total_travels": total_travels,
            "successful_travels": successful_travels,
            "success_rate": success_rate,
            "average_travel_time": avg_travel_time,
            "recent_travels": self.travel_history[-5:]  # Last 5 travels
        }
    
    def refuel_ship(self, ship_name: str) -> bool:
        """Refuel a ship."""
        if ship_name not in self.ships:
            return False
        
        ship = self.ships[ship_name]
        ship.fuel_level = 100
        self._save_ship_config()
        
        self.logger.info(f"Refueled {ship.ship_name}")
        return True
    
    def unlock_ship(self, ship_name: str) -> bool:
        """Unlock a ship."""
        if ship_name not in self.ships:
            return False
        
        ship = self.ships[ship_name]
        ship.unlocked = True
        self._save_ship_config()
        
        self.logger.info(f"Unlocked {ship.ship_name}")
        return True


# Global ship travel system instance
_ship_travel_system: Optional[PersonalShipTravelSystem] = None


def get_ship_travel_system() -> PersonalShipTravelSystem:
    """Get the global ship travel system instance."""
    global _ship_travel_system
    if _ship_travel_system is None:
        _ship_travel_system = PersonalShipTravelSystem()
    return _ship_travel_system


def check_ship_availability(ship_name: str = None) -> Dict[str, Any]:
    """Check if a ship is available for travel."""
    system = get_ship_travel_system()
    return system.check_ship_availability(ship_name)


def auto_use_personal_ship(destination: str) -> ShipTravelResult:
    """Automatically use personal ship if available and cooldown is ready."""
    system = get_ship_travel_system()
    return system.auto_use_personal_ship(destination)


def execute_ship_travel(ship_name: str, destination: str) -> ShipTravelResult:
    """Execute travel using a specific ship."""
    system = get_ship_travel_system()
    return system.execute_ship_travel(ship_name, destination)


def get_ship_travel_statistics() -> Dict[str, Any]:
    """Get ship travel success/failure statistics."""
    system = get_ship_travel_system()
    return system.get_travel_statistics() 