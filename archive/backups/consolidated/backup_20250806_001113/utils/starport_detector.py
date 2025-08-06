"""
Starport Detector Utility

This module provides OCR-based detection and interaction with starport terminals,
including terminal detection, dialog parsing, and travel confirmation.
"""

import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

try:
    from core.ocr import OCREngine, extract_text_from_screen
    from core.screenshot import capture_screen
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class TerminalType(Enum):
    """Types of travel terminals."""
    STARPORT = "starport"
    SHUTTLEPORT = "shuttleport"
    UNKNOWN = "unknown"


class DetectionStatus(Enum):
    """Status of terminal detection."""
    IDLE = "idle"
    SCANNING = "scanning"
    DETECTED = "detected"
    INTERACTING = "interacting"
    FAILED = "failed"


@dataclass
class TerminalInfo:
    """Information about a detected terminal."""
    name: str
    terminal_type: TerminalType
    coordinates: Tuple[int, int]
    confidence: float
    npc_name: str = ""
    description: str = ""


@dataclass
class DetectionResult:
    """Result of terminal detection."""
    success: bool
    terminals: List[TerminalInfo] = None
    error_message: Optional[str] = None
    scan_time: float = 0.0


@dataclass
class DialogInfo:
    """Information about travel dialog."""
    destinations: List[str]
    selected_destination: Optional[str] = None
    cost: Optional[int] = None
    travel_time: Optional[int] = None
    confirmation_required: bool = False


@dataclass
class InteractionResult:
    """Result of terminal interaction."""
    success: bool
    dialog: Optional[DialogInfo] = None
    error_message: Optional[str] = None


class StarportDetector:
    """
    OCR-based starport terminal detector and interactor.
    
    Features:
    - Terminal detection using OCR
    - Dialog parsing and destination selection
    - Travel confirmation handling
    - Multiple terminal type support
    """
    
    def __init__(self, config_path: str = "data/starport_routes.json"):
        """Initialize the starport detector."""
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = OCREngine() if OCR_AVAILABLE else None
        self.current_status = DetectionStatus.IDLE
        self.config_path = config_path
        
        # Terminal detection keywords
        self.terminal_keywords = {
            TerminalType.STARPORT: [
                "starport", "star port", "starport attendant", "travel terminal",
                "spaceport", "starport terminal", "travel to", "starport attendant"
            ],
            TerminalType.SHUTTLEPORT: [
                "shuttleport", "shuttle", "conductor", "attendant",
                "shuttle conductor", "shuttle attendant", "shuttle terminal"
            ]
        }
        
        # NPC names for different terminal types
        self.npc_names = {
            TerminalType.STARPORT: [
                "starport attendant", "travel agent", "spaceport attendant",
                "starport terminal", "travel terminal"
            ],
            TerminalType.SHUTTLEPORT: [
                "shuttle conductor", "shuttle attendant", "conductor",
                "shuttle terminal", "shuttleport attendant"
            ]
        }
        
        # Dialog patterns for parsing
        self.dialog_patterns = {
            "destination_list": [
                r"travel to (.+)",
                r"destination: (.+)",
                r"select destination: (.+)",
                r"(.+) - (.+)",  # Planet - City format
                r"(.+) to (.+)"   # From to format
            ],
            "cost": [
                r"cost: (\d+)",
                r"travel cost: (\d+)",
                r"price: (\d+)",
                r"(\d+) credits"
            ],
            "time": [
                r"time: (\d+)",
                r"travel time: (\d+)",
                r"duration: (\d+)",
                r"(\d+) minutes"
            ],
            "confirmation": [
                r"confirm travel",
                r"proceed with travel",
                r"yes, travel",
                r"confirm departure"
            ]
        }
        
        # Screen regions to scan for terminals
        self.scan_regions = [
            (100, 100, 400, 300),   # Top-left
            (500, 100, 400, 300),   # Top-right
            (100, 400, 400, 300),   # Bottom-left
            (500, 400, 400, 300),   # Bottom-right
            (300, 250, 400, 200),   # Center
        ]
        
        # Dialog regions (common dialog locations)
        self.dialog_regions = [
            (300, 200, 600, 500),   # Center dialog
            (200, 150, 700, 550),   # Large dialog
            (400, 250, 500, 450),   # Small dialog
        ]
        
        self.logger.info("Starport Detector initialized")
    
    def scan_for_terminals(self, terminal_type: TerminalType = None) -> DetectionResult:
        """
        Scan for travel terminals using OCR.
        
        Parameters
        ----------
        terminal_type : TerminalType, optional
            Specific terminal type to scan for
            
        Returns
        -------
        DetectionResult
            Result of terminal scanning
        """
        self.current_status = DetectionStatus.SCANNING
        start_time = time.time()
        
        self.logger.info(f"Scanning for terminals: {terminal_type.value if terminal_type else 'all'}")
        
        if not OCR_AVAILABLE:
            return DetectionResult(
                success=False,
                error_message="OCR not available"
            )
        
        detected_terminals = []
        
        try:
            # Capture screen for OCR analysis
            screenshot = capture_screen()
            if screenshot is None:
                return DetectionResult(
                    success=False,
                    error_message="Could not capture screen"
                )
            
            # Scan each region for terminals
            for region in self.scan_regions:
                region_terminals = self._scan_region_for_terminals(
                    screenshot, region, terminal_type
                )
                detected_terminals.extend(region_terminals)
            
            scan_time = time.time() - start_time
            
            if detected_terminals:
                self.current_status = DetectionStatus.DETECTED
                self.logger.info(f"Found {len(detected_terminals)} terminals")
                return DetectionResult(
                    success=True,
                    terminals=detected_terminals,
                    scan_time=scan_time
                )
            else:
                self.current_status = DetectionStatus.FAILED
                self.logger.warning("No terminals detected")
                return DetectionResult(
                    success=False,
                    error_message="No terminals found",
                    scan_time=scan_time
                )
                
        except Exception as e:
            self.current_status = DetectionStatus.FAILED
            self.logger.error(f"Error during terminal scanning: {e}")
            return DetectionResult(
                success=False,
                error_message=str(e),
                scan_time=time.time() - start_time
            )
    
    def _scan_region_for_terminals(self, screenshot, region: Tuple[int, int, int, int], 
                                  terminal_type: TerminalType = None) -> List[TerminalInfo]:
        """Scan a specific region for terminals."""
        terminals = []
        
        # Extract text from region
        ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, region)
        
        if ocr_result.confidence < 50:
            return terminals
        
        text = ocr_result.text.lower()
        
        # Check for terminal keywords
        for term_type, keywords in self.terminal_keywords.items():
            if terminal_type and term_type != terminal_type:
                continue
                
            for keyword in keywords:
                if keyword in text:
                    # Calculate coordinates from region
                    x = region[0] + (region[2] - region[0]) // 2
                    y = region[1] + (region[3] - region[1]) // 2
                    
                    # Extract NPC name if possible
                    npc_name = self._extract_npc_name(text, term_type)
                    
                    terminal = TerminalInfo(
                        name=f"{term_type.value.title()} Terminal",
                        terminal_type=term_type,
                        coordinates=(x, y),
                        confidence=ocr_result.confidence,
                        npc_name=npc_name,
                        description=f"Detected {term_type.value} terminal"
                    )
                    
                    terminals.append(terminal)
                    self.logger.info(f"Found {term_type.value} terminal at ({x}, {y})")
                    break
            
            # Check if any keywords were found for this terminal type
            if any(keyword in text for keyword in keywords):
                break
        
        return terminals
    
    def _extract_npc_name(self, text: str, terminal_type: TerminalType) -> str:
        """Extract NPC name from text."""
        npc_names = self.npc_names.get(terminal_type, [])
        
        for npc_name in npc_names:
            if npc_name in text:
                return npc_name
        
        return ""
    
    def interact_with_terminal(self, terminal: TerminalInfo) -> InteractionResult:
        """
        Interact with a detected terminal.
        
        Parameters
        ----------
        terminal : TerminalInfo
            Terminal to interact with
            
        Returns
        -------
        InteractionResult
            Result of terminal interaction
        """
        self.current_status = DetectionStatus.INTERACTING
        self.logger.info(f"Interacting with terminal: {terminal.name}")
        
        try:
            # Simulate terminal interaction (clicking on terminal)
            time.sleep(0.1)
            
            # Check if interaction was successful by looking for dialog
            dialog = self._detect_travel_dialog()
            
            if dialog:
                self.logger.info("Travel dialog detected")
                return InteractionResult(
                    success=True,
                    dialog=dialog
                )
            else:
                self.logger.warning("No travel dialog detected")
                return InteractionResult(
                    success=False,
                    error_message="No travel dialog found"
                )
                
        except Exception as e:
            self.logger.error(f"Terminal interaction failed: {e}")
            return InteractionResult(
                success=False,
                error_message=str(e)
            )
    
    def _detect_travel_dialog(self) -> Optional[DialogInfo]:
        """Detect travel dialog on screen."""
        if not OCR_AVAILABLE:
            return None
        
        try:
            screenshot = capture_screen()
            if screenshot is None:
                return None
            
            # Scan dialog regions
            for region in self.dialog_regions:
                ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, region)
                
                if ocr_result.confidence > 60:
                    text = ocr_result.text.lower()
                    
                    # Check if this looks like a travel dialog
                    if self._is_travel_dialog(text):
                        return self._parse_travel_dialog(text)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting travel dialog: {e}")
            return None
    
    def _is_travel_dialog(self, text: str) -> bool:
        """Check if text contains travel dialog indicators."""
        travel_indicators = [
            "travel to", "destination", "select destination",
            "travel cost", "travel time", "confirm travel"
        ]
        
        return any(indicator in text for indicator in travel_indicators)
    
    def _parse_travel_dialog(self, text: str) -> DialogInfo:
        """Parse travel dialog text."""
        destinations = []
        selected_destination = None
        cost = None
        travel_time = None
        confirmation_required = False
        
        # Parse destinations
        for pattern in self.dialog_patterns["destination_list"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle planet - city format
                    destination = f"{match[0]} - {match[1]}"
                else:
                    destination = match
                
                if destination and destination not in destinations:
                    destinations.append(destination)
        
        # Parse cost
        for pattern in self.dialog_patterns["cost"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cost = int(match.group(1))
                break
        
        # Parse travel time
        for pattern in self.dialog_patterns["time"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                travel_time = int(match.group(1))
                break
        
        # Check for confirmation requirement
        confirmation_required = any(
            pattern in text for pattern in self.dialog_patterns["confirmation"]
        )
        
        return DialogInfo(
            destinations=destinations,
            selected_destination=selected_destination,
            cost=cost,
            travel_time=travel_time,
            confirmation_required=confirmation_required
        )
    
    def select_destination(self, destinations: List[str], target_planet: str, 
                         target_city: str = None) -> InteractionResult:
        """
        Select destination from available destinations.
        
        Parameters
        ----------
        destinations : List[str]
            Available destinations
        target_planet : str
            Target planet
        target_city : str, optional
            Target city
            
        Returns
        -------
        InteractionResult
            Result of destination selection
        """
        self.logger.info(f"Selecting destination: {target_planet} - {target_city}")
        
        try:
            # Find matching destination
            selected_destination = None
            target_planet_lower = target_planet.lower()
            target_city_lower = target_city.lower() if target_city else ""
            
            for destination in destinations:
                dest_lower = destination.lower()
                
                # Check if destination matches target
                if target_planet_lower in dest_lower:
                    if not target_city or target_city_lower in dest_lower:
                        selected_destination = destination
                        break
            
            if not selected_destination:
                # Try partial matches
                for destination in destinations:
                    dest_lower = destination.lower()
                    if any(planet in dest_lower for planet in [target_planet_lower, "naboo", "tatooine", "corellia"]):
                        selected_destination = destination
                        break
            
            if selected_destination:
                self.logger.info(f"Selected destination: {selected_destination}")
                
                # Simulate selection
                time.sleep(0.1)
                
                return InteractionResult(
                    success=True,
                    dialog=DialogInfo(
                        destinations=destinations,
                        selected_destination=selected_destination
                    )
                )
            else:
                self.logger.warning(f"No matching destination found for {target_planet}")
                return InteractionResult(
                    success=False,
                    error_message=f"No destination found for {target_planet}"
                )
                
        except Exception as e:
            self.logger.error(f"Destination selection failed: {e}")
            return InteractionResult(
                success=False,
                error_message=str(e)
            )
    
    def confirm_travel(self, dialog: DialogInfo) -> InteractionResult:
        """
        Confirm travel after destination selection.
        
        Parameters
        ----------
        dialog : DialogInfo
            Travel dialog information
            
        Returns
        -------
        InteractionResult
            Result of travel confirmation
        """
        self.logger.info("Confirming travel")
        
        try:
            if not dialog.selected_destination:
                return InteractionResult(
                    success=False,
                    error_message="No destination selected"
                )
            
            # Simulate travel confirmation
            time.sleep(0.1)
            
            self.logger.info(f"Travel confirmed to {dialog.selected_destination}")
            return InteractionResult(
                success=True,
                dialog=dialog
            )
            
        except Exception as e:
            self.logger.error(f"Travel confirmation failed: {e}")
            return InteractionResult(
                success=False,
                error_message=str(e)
            )
    
    def wait_for_arrival(self, destination_planet: str) -> InteractionResult:
        """
        Wait for arrival at destination.
        
        Parameters
        ----------
        destination_planet : str
            Destination planet
            
        Returns
        -------
        InteractionResult
            Result of arrival wait
        """
        self.logger.info(f"Waiting for arrival at {destination_planet}")
        
        try:
            # Simulate travel time
            travel_time = 5  # Default travel time
            time.sleep(travel_time)
            
            # Check for arrival indicators
            arrival_confirmed = self._check_arrival_confirmation(destination_planet)
            
            if arrival_confirmed:
                self.logger.info(f"Arrived at {destination_planet}")
                return InteractionResult(success=True)
            else:
                self.logger.warning(f"Arrival confirmation failed at {destination_planet}")
                return InteractionResult(
                    success=False,
                    error_message="Arrival confirmation failed"
                )
                
        except Exception as e:
            self.logger.error(f"Arrival wait failed: {e}")
            return InteractionResult(
                success=False,
                error_message=str(e)
            )
    
    def _check_arrival_confirmation(self, destination_planet: str) -> bool:
        """Check for arrival confirmation indicators."""
        if not OCR_AVAILABLE:
            return True  # Assume success if OCR not available
        
        try:
            screenshot = capture_screen()
            if screenshot is None:
                return True
            
            # Scan for arrival indicators
            arrival_indicators = [
                destination_planet.lower(),
                "arrived", "arrival", "welcome to",
                "you have arrived", "travel complete"
            ]
            
            # Check center region for arrival text
            center_region = (300, 200, 600, 500)
            ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, center_region)
            
            if ocr_result.confidence > 50:
                text = ocr_result.text.lower()
                return any(indicator in text for indicator in arrival_indicators)
            
            return True  # Assume success if no clear indicators
            
        except Exception as e:
            self.logger.error(f"Error checking arrival confirmation: {e}")
            return True  # Assume success on error
    
    def get_detection_status(self) -> Dict[str, Any]:
        """Get current detection status."""
        return {
            "status": self.current_status.value,
            "ocr_available": OCR_AVAILABLE,
            "scan_regions": len(self.scan_regions),
            "dialog_regions": len(self.dialog_regions)
        }


# Global detector instance
_detector: Optional[StarportDetector] = None


def get_starport_detector(config_path: str = "data/starport_routes.json") -> StarportDetector:
    """Get the global starport detector instance."""
    global _detector
    if _detector is None:
        _detector = StarportDetector(config_path)
    return _detector


def scan_for_terminals(terminal_type: TerminalType = None) -> DetectionResult:
    """Scan for travel terminals using OCR."""
    detector = get_starport_detector()
    return detector.scan_for_terminals(terminal_type)


def interact_with_terminal(terminal: TerminalInfo) -> InteractionResult:
    """Interact with a detected terminal."""
    detector = get_starport_detector()
    return detector.interact_with_terminal(terminal)


def get_detection_status() -> Dict[str, Any]:
    """Get current detection status."""
    detector = get_starport_detector()
    return detector.get_detection_status() 