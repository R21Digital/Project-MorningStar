"""
Terminal Travel System

This module provides specialized functionality for traveling via starports and shuttleports,
including OCR-based terminal detection, waypoint navigation, and destination selection.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

try:
    from core.ocr import OCREngine, extract_text_from_screen
    from core.screenshot import capture_screen
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from travel.locations import TravelTerminal, TerminalType


class TerminalStatus(Enum):
    """Status of terminal travel operations."""
    IDLE = "idle"
    SCANNING = "scanning"
    MOVING_TO_TERMINAL = "moving_to_terminal"
    INTERACTING = "interacting"
    SELECTING_DESTINATION = "selecting_destination"
    CONFIRMING_TRAVEL = "confirming_travel"
    TRAVELING = "traveling"
    ARRIVED = "arrived"
    FAILED = "failed"


@dataclass
class TerminalScanResult:
    """Result of terminal scanning operation."""
    terminal_found: bool
    terminal_type: Optional[TerminalType] = None
    terminal_name: Optional[str] = None
    confidence: float = 0.0
    coordinates: Optional[Tuple[int, int]] = None
    scan_time: float = 0.0


@dataclass
class TravelDialogResult:
    """Result of travel dialog interaction."""
    dialog_detected: bool
    destinations_available: List[str] = None
    selected_destination: Optional[str] = None
    confirmation_required: bool = False
    travel_cost: Optional[int] = None
    travel_time: Optional[int] = None


class TerminalTravelSystem:
    """
    Specialized system for traveling via starports and shuttleports.
    
    Features:
    - OCR-based terminal detection
    - Waypoint navigation to terminals
    - Travel dialog recognition and interaction
    - Destination selection and confirmation
    - Success/failure rate tracking
    """
    
    def __init__(self):
        """Initialize the terminal travel system."""
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = OCREngine() if OCR_AVAILABLE else None
        self.current_status = TerminalStatus.IDLE
        self.scan_results: List[TerminalScanResult] = []
        self.travel_history: List[Dict[str, Any]] = []
        
        # Terminal detection keywords
        self.terminal_keywords = {
            TerminalType.SHUTTLEPORT: [
                "shuttleport", "shuttle", "conductor", "attendant",
                "shuttle conductor", "shuttle attendant"
            ],
            TerminalType.STARPORT: [
                "starport", "star port", "starport attendant",
                "travel terminal", "spaceport"
            ]
        }
        
        # Travel dialog patterns
        self.dialog_patterns = {
            "destination_list": [
                r"travel to (.+)",
                r"destination: (.+)",
                r"select destination: (.+)"
            ],
            "confirmation": [
                r"confirm travel",
                r"proceed with travel",
                r"travel cost: (\d+)",
                r"travel time: (\d+)"
            ]
        }
    
    def scan_for_terminals(self, terminal_type: TerminalType = None) -> List[TerminalScanResult]:
        """
        Scan for travel terminals using OCR.
        
        Parameters
        ----------
        terminal_type : TerminalType, optional
            Specific terminal type to scan for
            
        Returns
        -------
        List[TerminalScanResult]
            List of detected terminals
        """
        self.current_status = TerminalStatus.SCANNING
        self.logger.info(f"Scanning for terminals: {terminal_type.value if terminal_type else 'all'}")
        
        scan_results = []
        start_time = time.time()
        
        try:
            # Capture screen for OCR analysis
            screenshot = capture_screen()
            if screenshot is None:
                self.logger.warning("Could not capture screen for terminal scanning")
                return []
            
            # Define screen regions to scan (common terminal locations)
            scan_regions = [
                (100, 100, 400, 300),   # Top-left
                (500, 100, 400, 300),   # Top-right
                (100, 400, 400, 300),   # Bottom-left
                (500, 400, 400, 300),   # Bottom-right
                (300, 250, 400, 200),   # Center
            ]
            
            for region in scan_regions:
                # Extract text from region
                ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, region)
                
                if ocr_result.confidence > 60:
                    text = ocr_result.text.lower()
                    
                    # Check for terminal keywords
                    for term_type, keywords in self.terminal_keywords.items():
                        if terminal_type and term_type != terminal_type:
                            continue
                            
                        for keyword in keywords:
                            if keyword in text:
                                # Calculate approximate coordinates from region
                                x = region[0] + (region[2] - region[0]) // 2
                                y = region[1] + (region[3] - region[1]) // 2
                                
                                result = TerminalScanResult(
                                    terminal_found=True,
                                    terminal_type=term_type,
                                    terminal_name=f"{term_type.value.title()} Terminal",
                                    confidence=ocr_result.confidence,
                                    coordinates=(x, y),
                                    scan_time=time.time() - start_time
                                )
                                
                                scan_results.append(result)
                                self.logger.info(f"Found {term_type.value} terminal at ({x}, {y})")
                                break
                        
                        # Check if any keywords were found for this terminal type
                        if any(keyword in text for keyword in keywords):
                            break
            
            self.scan_results.extend(scan_results)
            self.logger.info(f"Scan completed: {len(scan_results)} terminals found")
            
        except Exception as e:
            self.logger.error(f"Error during terminal scanning: {e}")
        
        self.current_status = TerminalStatus.IDLE
        return scan_results
    
    def navigate_to_terminal(self, terminal: TravelTerminal) -> bool:
        """
        Use waypoint navigation to reach a terminal.
        
        Parameters
        ----------
        terminal : TravelTerminal
            Terminal to navigate to
            
        Returns
        -------
        bool
            True if navigation successful
        """
        self.current_status = TerminalStatus.MOVING_TO_TERMINAL
        self.logger.info(f"Navigating to terminal: {terminal.name}")
        
        try:
            # This would integrate with the existing navigation system
            # For now, we'll simulate the navigation process
            
            # Simulate movement time based on distance
            distance = self._calculate_distance((0, 0), terminal.coordinates)
            movement_time = min(distance / 100, 30)  # Cap at 30 seconds
            
            self.logger.info(f"Estimated movement time: {movement_time:.1f} seconds")
            
            # Simulate successful navigation
            time.sleep(0.1)  # Brief pause for simulation
            
            self.logger.info(f"Successfully navigated to {terminal.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            self.current_status = TerminalStatus.FAILED
            return False
    
    def interact_with_terminal(self, terminal: TravelTerminal) -> bool:
        """
        Interact with a travel terminal.
        
        Parameters
        ----------
        terminal : TravelTerminal
            Terminal to interact with
            
        Returns
        -------
        bool
            True if interaction successful
        """
        self.current_status = TerminalStatus.INTERACTING
        self.logger.info(f"Interacting with terminal: {terminal.name}")
        
        try:
            # Simulate terminal interaction
            time.sleep(0.1)
            
            # Check if interaction was successful
            # This would typically involve clicking on the terminal or NPC
            interaction_successful = True  # Simulated success
            
            if interaction_successful:
                self.logger.info(f"Successfully interacted with {terminal.name}")
                return True
            else:
                self.logger.warning(f"Failed to interact with {terminal.name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Terminal interaction failed: {e}")
            self.current_status = TerminalStatus.FAILED
            return False
    
    def select_destination(self, route_info: Dict[str, Any]) -> TravelDialogResult:
        """
        Select correct destination from dialogue or UI.
        
        Parameters
        ----------
        route_info : Dict[str, Any]
            Information about the desired route
            
        Returns
        -------
        TravelDialogResult
            Result of destination selection
        """
        self.current_status = TerminalStatus.SELECTING_DESTINATION
        self.logger.info(f"Selecting destination: {route_info.get('dest_planet')} - {route_info.get('dest_city')}")
        
        try:
            # Capture screen to analyze travel dialog
            screenshot = capture_screen()
            if screenshot is None:
                return TravelDialogResult(dialog_detected=False)
            
            # Extract text from dialog region
            dialog_region = (300, 200, 600, 500)  # Approximate dialog location
            ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, dialog_region)
            
            if ocr_result.confidence < 50:
                return TravelDialogResult(dialog_detected=False)
            
            text = ocr_result.text.lower()
            self.logger.info(f"Dialog text: {text}")
            
            # Parse available destinations
            destinations = self._parse_destinations(text)
            
            # Find target destination
            target_planet = route_info.get('dest_planet', '').lower()
            target_city = route_info.get('dest_city', '').lower()
            
            selected_destination = None
            for dest in destinations:
                if target_planet in dest.lower() and target_city in dest.lower():
                    selected_destination = dest
                    break
            
            # Check for confirmation requirements
            confirmation_required = any(
                pattern in text for pattern in self.dialog_patterns["confirmation"]
            )
            
            # Extract travel cost and time if available
            travel_cost = self._extract_travel_cost(text)
            travel_time = self._extract_travel_time(text)
            
            result = TravelDialogResult(
                dialog_detected=True,
                destinations_available=destinations,
                selected_destination=selected_destination,
                confirmation_required=confirmation_required,
                travel_cost=travel_cost,
                travel_time=travel_time
            )
            
            self.logger.info(f"Destination selection result: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Destination selection failed: {e}")
            return TravelDialogResult(dialog_detected=False)
    
    def confirm_travel(self, dialog_result: TravelDialogResult) -> bool:
        """
        Confirm travel after destination selection.
        
        Parameters
        ----------
        dialog_result : TravelDialogResult
            Result from destination selection
            
        Returns
        -------
        bool
            True if travel confirmed successfully
        """
        self.current_status = TerminalStatus.CONFIRMING_TRAVEL
        self.logger.info("Confirming travel")
        
        try:
            if not dialog_result.selected_destination:
                self.logger.warning("No destination selected for confirmation")
                return False
            
            # Simulate travel confirmation
            time.sleep(0.1)
            
            # Record travel attempt
            travel_record = {
                "timestamp": time.time(),
                "destination": dialog_result.selected_destination,
                "cost": dialog_result.travel_cost,
                "time": dialog_result.travel_time,
                "status": "confirmed"
            }
            
            self.travel_history.append(travel_record)
            self.logger.info(f"Travel confirmed to {dialog_result.selected_destination}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Travel confirmation failed: {e}")
            return False
    
    def _parse_destinations(self, text: str) -> List[str]:
        """Parse available destinations from dialog text."""
        destinations = []
        
        # Look for destination patterns
        lines = text.split('\n')
        for line in lines:
            line = line.strip().lower()
            
            # Common destination patterns
            if any(keyword in line for keyword in ["travel to", "destination:", "select"]):
                # Extract destination name
                for pattern in self.dialog_patterns["destination_list"]:
                    import re
                    match = re.search(pattern, line)
                    if match:
                        destination = match.group(1).strip()
                        if destination and destination not in destinations:
                            destinations.append(destination)
        
        return destinations
    
    def _extract_travel_cost(self, text: str) -> Optional[int]:
        """Extract travel cost from dialog text."""
        import re
        
        # Look for cost patterns
        cost_patterns = [
            r"cost: (\d+)",
            r"travel cost: (\d+)",
            r"price: (\d+)",
            r"(\d+) credits"
        ]
        
        for pattern in cost_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_travel_time(self, text: str) -> Optional[int]:
        """Extract travel time from dialog text."""
        import re
        
        # Look for time patterns
        time_patterns = [
            r"time: (\d+)",
            r"travel time: (\d+)",
            r"duration: (\d+)",
            r"(\d+) minutes"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _calculate_distance(self, coords1: Tuple[int, int], coords2: Tuple[int, int]) -> float:
        """Calculate distance between two coordinate pairs."""
        import math
        return math.sqrt((coords2[0] - coords1[0])**2 + (coords2[1] - coords1[1])**2)
    
    def get_travel_statistics(self) -> Dict[str, Any]:
        """Get travel success/failure statistics."""
        if not self.travel_history:
            return {
                "total_travels": 0, 
                "successful_travels": 0,
                "success_rate": 0.0,
                "recent_travels": []
            }
        
        total_travels = len(self.travel_history)
        successful_travels = len([
            record for record in self.travel_history 
            if record.get("status") == "confirmed"
        ])
        
        success_rate = (successful_travels / total_travels) * 100 if total_travels > 0 else 0
        
        return {
            "total_travels": total_travels,
            "successful_travels": successful_travels,
            "success_rate": success_rate,
            "recent_travels": self.travel_history[-5:]  # Last 5 travels
        }


# Global terminal travel system instance
_terminal_travel_system: Optional[TerminalTravelSystem] = None


def get_terminal_travel_system() -> TerminalTravelSystem:
    """Get the global terminal travel system instance."""
    global _terminal_travel_system
    if _terminal_travel_system is None:
        _terminal_travel_system = TerminalTravelSystem()
    return _terminal_travel_system


def scan_for_terminals(terminal_type: TerminalType = None) -> List[TerminalScanResult]:
    """Scan for travel terminals using OCR."""
    system = get_terminal_travel_system()
    return system.scan_for_terminals(terminal_type)


def navigate_to_terminal(terminal: TravelTerminal) -> bool:
    """Navigate to a travel terminal."""
    system = get_terminal_travel_system()
    return system.navigate_to_terminal(terminal)


def select_destination(route_info: Dict[str, Any]) -> TravelDialogResult:
    """Select destination from travel dialog."""
    system = get_terminal_travel_system()
    return system.select_destination(route_info)


def get_travel_statistics() -> Dict[str, Any]:
    """Get travel success/failure statistics."""
    system = get_terminal_travel_system()
    return system.get_travel_statistics() 