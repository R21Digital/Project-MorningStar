"""Detect vendor and bazaar terminals using OCR."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

import cv2
import numpy as np
import pyautogui

from src.vision.ocr import screen_text, capture_screen
from utils.logging_utils import log_event


@dataclass
class VendorTerminal:
    """Represents a detected vendor terminal."""
    x: int
    y: int
    width: int
    height: int
    terminal_type: str  # "vendor", "bazaar", "shop"
    confidence: float
    detected_text: str


@dataclass
class VendorInterface:
    """Represents vendor interface elements."""
    sell_button: Optional[Tuple[int, int]] = None
    buy_button: Optional[Tuple[int, int]] = None
    inventory_list: Optional[Tuple[int, int, int, int]] = None
    price_display: Optional[Tuple[int, int, int, int]] = None


class BazaarDetector:
    """Detect vendor terminals and interface elements using OCR."""
    
    def __init__(self, config_path: str = "config/bazaar_config.json"):
        """Initialize the bazaar detector.
        
        Parameters
        ----------
        config_path : str
            Path to bazaar configuration file
        """
        self.config = self._load_config(config_path)
        self.terminal_keywords = self.config.get("vendor_detection", {}).get("terminal_keywords", [])
        self.sell_keywords = self.config.get("vendor_detection", {}).get("sell_button_keywords", [])
        self.buy_keywords = self.config.get("vendor_detection", {}).get("buy_button_keywords", [])
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load bazaar configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        return {}
    
    def detect_vendor_terminals(self, screen_image: np.ndarray = None) -> List[VendorTerminal]:
        """Detect vendor terminals on screen.
        
        Parameters
        ----------
        screen_image : np.ndarray, optional
            Screenshot to analyze. If None, captures current screen.
            
        Returns
        -------
        List[VendorTerminal]
            List of detected vendor terminals
        """
        if screen_image is None:
            screen_image = capture_screen()
        
        terminals = []
        text = screen_text()
        
        # Look for terminal keywords in the text
        for keyword in self.terminal_keywords:
            if keyword.lower() in text.lower():
                # Try to find the region containing this keyword
                terminal = self._find_terminal_region(screen_image, keyword)
                if terminal:
                    terminals.append(terminal)
        
        log_event(f"[BAZAAR] Detected {len(terminals)} vendor terminals")
        return terminals
    
    def _find_terminal_region(self, image: np.ndarray, keyword: str) -> Optional[VendorTerminal]:
        """Find the region containing a terminal keyword.
        
        Parameters
        ----------
        image : np.ndarray
            Screenshot to analyze
        keyword : str
            Keyword to search for
            
        Returns
        -------
        VendorTerminal or None
            Detected terminal region
        """
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for bright rectangular areas that might be terminals
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:  # Minimum terminal size
                x, y, w, h = cv2.boundingRect(contour)
                
                # Extract text from this region
                region_image = image[y:y+h, x:x+w]
                region_text = screen_text(region=(x, y, w, h))
                
                if keyword.lower() in region_text.lower():
                    # Determine terminal type based on keywords
                    terminal_type = self._determine_terminal_type(region_text)
                    
                    return VendorTerminal(
                        x=x, y=y, width=w, height=h,
                        terminal_type=terminal_type,
                        confidence=0.8,
                        detected_text=region_text
                    )
        
        return None
    
    def _determine_terminal_type(self, text: str) -> str:
        """Determine the type of terminal based on text content.
        
        Parameters
        ----------
        text : str
            Text extracted from terminal region
            
        Returns
        -------
        str
            Terminal type ("vendor", "bazaar", "shop")
        """
        text_lower = text.lower()
        
        if "bazaar" in text_lower:
            return "bazaar"
        elif "vendor" in text_lower:
            return "vendor"
        elif "shop" in text_lower or "store" in text_lower:
            return "shop"
        else:
            return "vendor"  # Default
    
    def detect_vendor_interface(self, screen_image: np.ndarray = None) -> Optional[VendorInterface]:
        """Detect vendor interface elements (buttons, lists, etc.).
        
        Parameters
        ----------
        screen_image : np.ndarray, optional
            Screenshot to analyze. If None, captures current screen.
            
        Returns
        -------
        VendorInterface or None
            Detected interface elements
        """
        if screen_image is None:
            screen_image = capture_screen()
        
        text = screen_text()
        interface = VendorInterface()
        
        # Look for sell button
        for keyword in self.sell_keywords:
            if keyword.lower() in text.lower():
                button_pos = self._find_button_position(screen_image, keyword)
                if button_pos:
                    interface.sell_button = button_pos
                    break
        
        # Look for buy button
        for keyword in self.buy_keywords:
            if keyword.lower() in text.lower():
                button_pos = self._find_button_position(screen_image, keyword)
                if button_pos:
                    interface.buy_button = button_pos
                    break
        
        # Try to detect inventory list area
        interface.inventory_list = self._detect_inventory_area(screen_image)
        
        # Try to detect price display area
        interface.price_display = self._detect_price_area(screen_image)
        
        if interface.sell_button or interface.buy_button:
            log_event("[BAZAAR] Detected vendor interface elements")
            return interface
        
        return None
    
    def _find_button_position(self, image: np.ndarray, keyword: str) -> Optional[Tuple[int, int]]:
        """Find the position of a button containing the keyword.
        
        Parameters
        ----------
        image : np.ndarray
            Screenshot to analyze
        keyword : str
            Button text to search for
            
        Returns
        -------
        Tuple[int, int] or None
            Button coordinates (x, y)
        """
        # This is a simplified approach - in practice you'd use more sophisticated
        # button detection with template matching or OCR bounding boxes
        text = screen_text()
        
        # For now, return a default position if keyword is found
        if keyword.lower() in text.lower():
            # Return center of screen as placeholder
            height, width = image.shape[:2]
            return (width // 2, height // 2)
        
        return None
    
    def _detect_inventory_area(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect inventory list area.
        
        Parameters
        ----------
        image : np.ndarray
            Screenshot to analyze
            
        Returns
        -------
        Tuple[int, int, int, int] or None
            Inventory area coordinates (x, y, width, height)
        """
        # Simplified detection - look for areas with list-like patterns
        height, width = image.shape[:2]
        
        # Return a default inventory area (left side of screen)
        return (50, 100, width // 3, height - 200)
    
    def _detect_price_area(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect price display area.
        
        Parameters
        ----------
        image : np.ndarray
            Screenshot to analyze
            
        Returns
        -------
        Tuple[int, int, int, int] or None
            Price area coordinates (x, y, width, height)
        """
        # Simplified detection - look for areas with price-like patterns
        height, width = image.shape[:2]
        
        # Return a default price area (right side of screen)
        return (width * 2 // 3, 100, width // 3, height - 200)
    
    def is_vendor_screen(self, screen_image: np.ndarray = None) -> bool:
        """Check if current screen shows a vendor interface.
        
        Parameters
        ----------
        screen_image : np.ndarray, optional
            Screenshot to analyze. If None, captures current screen.
            
        Returns
        -------
        bool
            True if vendor interface is detected
        """
        if screen_image is None:
            screen_image = capture_screen()
        
        terminals = self.detect_vendor_terminals(screen_image)
        interface = self.detect_vendor_interface(screen_image)
        
        return len(terminals) > 0 or interface is not None 