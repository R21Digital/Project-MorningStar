"""Handle ship entry and exit functionality."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

import pyautogui

from src.vision.ocr import screen_text, capture_screen
from utils.logging_utils import log_event


@dataclass
class Ship:
    """Represents a ship."""
    name: str
    ship_type: str  # "starfighter", "heavy_freighter", "transport"
    unlocked: bool
    cooldown_remaining: int
    max_cooldown: int
    fuel_level: int
    last_used: float
    location: str


@dataclass
class ShipTerminal:
    """Represents a ship terminal."""
    x: int
    y: int
    width: int
    height: int
    terminal_type: str  # "ship", "hangar", "dock"
    confidence: float
    detected_text: str


class ShipHandler:
    """Handle ship entry and exit functionality."""

    def __init__(self, config_path: str = "config/session_config.json"):
        """Initialize the ship handler.

        Parameters
        ----------
        config_path : str
            Path to session configuration file
        """
        self.config = self._load_config(config_path)
        self.space_config = self.config.get("space_mode", {})
        
        # Ship configuration
        self.ship_config = self._load_ship_config()
        self.current_ship: Optional[Ship] = None
        self.in_ship = False
        
        # Terminal detection keywords
        self.ship_terminal_keywords = [
            "ship terminal", "hangar", "dock", "shipyard",
            "enter ship", "exit ship", "board ship"
        ]

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load session configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        return {}

    def _load_ship_config(self) -> Dict[str, Any]:
        """Load ship configuration."""
        ship_config_file = Path("data/ship_config.json")
        if ship_config_file.exists():
            try:
                with ship_config_file.open("r", encoding="utf-8") as fh:
                    return json.load(fh)
            except Exception as e:
                log_event(f"[SHIP] Error loading ship config: {e}")
        
        return {}

    def detect_ship_terminals(self, screen_image=None) -> List[ShipTerminal]:
        """Detect ship terminals on screen.

        Parameters
        ----------
        screen_image
            Screenshot to analyze. If None, captures current screen.

        Returns
        -------
        List[ShipTerminal]
            List of detected ship terminals
        """
        if screen_image is None:
            screen_image = capture_screen()

        terminals = []
        text = screen_text()

        # Look for ship terminal keywords in the text
        for keyword in self.ship_terminal_keywords:
            if keyword.lower() in text.lower():
                # Try to find the region containing this keyword
                terminal = self._find_terminal_region(screen_image, keyword)
                if terminal:
                    terminals.append(terminal)

        log_event(f"[SHIP] Detected {len(terminals)} ship terminals")
        return terminals

    def _find_terminal_region(self, image, keyword: str) -> Optional[ShipTerminal]:
        """Find the region containing a ship terminal keyword.

        Parameters
        ----------
        image
            Screenshot to analyze
        keyword : str
            Keyword to search for

        Returns
        -------
        ShipTerminal or None
            Detected terminal region
        """
        # This is a simplified implementation
        # In practice, you'd use more sophisticated image processing
        
        # For now, return a default terminal if keyword is found
        import cv2
        import numpy as np
        
        height, width = image.shape[:2]
        
        # Return a default terminal position
        return ShipTerminal(
            x=width // 4,
            y=height // 4,
            width=width // 2,
            height=height // 2,
            terminal_type=self._determine_terminal_type(keyword),
            confidence=0.8,
            detected_text=keyword
        )

    def _determine_terminal_type(self, keyword: str) -> str:
        """Determine the type of terminal based on keyword.

        Parameters
        ----------
        keyword : str
            Terminal keyword

        Returns
        -------
        str
            Terminal type
        """
        keyword_lower = keyword.lower()
        
        if "hangar" in keyword_lower:
            return "hangar"
        elif "dock" in keyword_lower:
            return "dock"
        elif "shipyard" in keyword_lower:
            return "shipyard"
        else:
            return "ship"  # Default

    def get_available_ships(self) -> List[Ship]:
        """Get available ships.

        Returns
        -------
        List[Ship]
            Available ships
        """
        ships = []
        
        for ship_name, ship_data in self.ship_config.get("ships", {}).items():
            ship = Ship(
                name=ship_name,
                ship_type=ship_data.get("type", "unknown"),
                unlocked=ship_data.get("unlocked", False),
                cooldown_remaining=ship_data.get("cooldown_remaining", 0),
                max_cooldown=ship_data.get("max_cooldown", 0),
                fuel_level=ship_data.get("fuel_level", 0),
                last_used=ship_data.get("last_used", 0.0),
                location="hangar"  # Default location
            )
            ships.append(ship)
        
        log_event(f"[SHIP] Found {len(ships)} available ships")
        return ships

    def enter_ship(self, ship_name: str) -> bool:
        """Enter a ship.

        Parameters
        ----------
        ship_name : str
            Name of ship to enter

        Returns
        -------
        bool
            True if ship entry was successful
        """
        if self.in_ship:
            log_event("[SHIP] Already in a ship")
            return False

        # Find the ship
        available_ships = self.get_available_ships()
        ship = next((s for s in available_ships if s.name == ship_name), None)
        
        if not ship:
            log_event(f"[SHIP] Ship {ship_name} not found")
            return False

        if not ship.unlocked:
            log_event(f"[SHIP] Ship {ship_name} is not unlocked")
            return False

        if ship.cooldown_remaining > 0:
            log_event(f"[SHIP] Ship {ship_name} is on cooldown")
            return False

        if ship.fuel_level <= 0:
            log_event(f"[SHIP] Ship {ship_name} has no fuel")
            return False

        # Detect ship terminal
        terminals = self.detect_ship_terminals()
        if not terminals:
            log_event("[SHIP] No ship terminals detected")
            return False

        # Click on ship terminal
        terminal = terminals[0]
        center_x = terminal.x + terminal.width // 2
        center_y = terminal.y + terminal.height // 2

        log_event(f"[SHIP] Interacting with {terminal.terminal_type} terminal")
        pyautogui.click(center_x, center_y)
        time.sleep(1)  # Wait for interface to load

        # Check if ship interface is now visible
        if self._is_ship_interface_visible():
            self.current_ship = ship
            self.in_ship = True
            
            # Update ship usage
            self._update_ship_usage(ship_name)
            
            log_event(f"[SHIP] Successfully entered {ship_name}")
            return True
        else:
            log_event("[SHIP] Failed to enter ship")
            return False

    def exit_ship(self) -> bool:
        """Exit current ship.

        Returns
        -------
        bool
            True if ship exit was successful
        """
        if not self.in_ship or not self.current_ship:
            log_event("[SHIP] Not in a ship")
            return False

        # Look for exit button or command
        text = screen_text()
        exit_keywords = ["exit", "leave", "disembark", "return"]
        
        if any(keyword in text.lower() for keyword in exit_keywords):
            # Click exit button (simplified)
            height, width = capture_screen().shape[:2]
            pyautogui.click(width // 2, height // 2)  # Center of screen
            time.sleep(1)
            
            self.in_ship = False
            self.current_ship = None
            
            log_event(f"[SHIP] Successfully exited ship")
            return True
        else:
            log_event("[SHIP] No exit option found")
            return False

    def _is_ship_interface_visible(self) -> bool:
        """Check if ship interface is visible.

        Returns
        -------
        bool
            True if ship interface is detected
        """
        text = screen_text()
        ship_indicators = ["ship", "cockpit", "controls", "navigation", "weapons"]
        
        return any(indicator in text.lower() for indicator in ship_indicators)

    def _update_ship_usage(self, ship_name: str) -> None:
        """Update ship usage statistics.

        Parameters
        ----------
        ship_name : str
            Name of ship used
        """
        if ship_name in self.ship_config.get("ships", {}):
            self.ship_config["ships"][ship_name]["last_used"] = time.time()
            self.ship_config["ships"][ship_name]["cooldown_remaining"] = \
                self.ship_config["ships"][ship_name]["max_cooldown"]
            
            # Save updated config
            self._save_ship_config()

    def _save_ship_config(self) -> None:
        """Save ship configuration."""
        ship_config_file = Path("data/ship_config.json")
        try:
            with ship_config_file.open("w", encoding="utf-8") as fh:
                json.dump(self.ship_config, fh, indent=2)
        except Exception as e:
            log_event(f"[SHIP] Error saving ship config: {e}")

    def get_current_ship(self) -> Optional[Ship]:
        """Get current ship.

        Returns
        -------
        Ship or None
            Current ship
        """
        return self.current_ship

    def is_in_ship(self) -> bool:
        """Check if currently in a ship.

        Returns
        -------
        bool
            True if in a ship
        """
        return self.in_ship

    def get_ship_status(self) -> Dict[str, Any]:
        """Get current ship status.

        Returns
        -------
        Dict[str, Any]
            Ship status information
        """
        status = {
            "in_ship": self.in_ship,
            "current_ship": None,
            "available_ships": len(self.get_available_ships()),
            "unlocked_ships": len([s for s in self.get_available_ships() if s.unlocked])
        }
        
        if self.current_ship:
            status["current_ship"] = {
                "name": self.current_ship.name,
                "type": self.current_ship.ship_type,
                "fuel_level": self.current_ship.fuel_level,
                "cooldown_remaining": self.current_ship.cooldown_remaining
            }
        
        return status

    def refuel_ship(self, ship_name: str) -> bool:
        """Refuel a ship.

        Parameters
        ----------
        ship_name : str
            Name of ship to refuel

        Returns
        -------
        bool
            True if refuel was successful
        """
        if ship_name not in self.ship_config.get("ships", {}):
            log_event(f"[SHIP] Ship {ship_name} not found")
            return False

        # Simulate refueling
        self.ship_config["ships"][ship_name]["fuel_level"] = 100
        self._save_ship_config()
        
        log_event(f"[SHIP] Refueled {ship_name}")
        return True

    def repair_ship(self, ship_name: str) -> bool:
        """Repair a ship.

        Parameters
        ----------
        ship_name : str
            Name of ship to repair

        Returns
        -------
        bool
            True if repair was successful
        """
        if ship_name not in self.ship_config.get("ships", {}):
            log_event(f"[SHIP] Ship {ship_name} not found")
            return False

        # Simulate repair
        self.ship_config["ships"][ship_name]["cooldown_remaining"] = 0
        self._save_ship_config()
        
        log_event(f"[SHIP] Repaired {ship_name}")
        return True 