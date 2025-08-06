"""Detect space events via logs and OCR."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from src.vision.ocr import screen_text, capture_screen
from utils.logging_utils import log_event


@dataclass
class SpaceEvent:
    """Represents a detected space event."""
    event_type: str  # "space", "ship_entry", "ship_exit", "mission_available"
    timestamp: str
    location: str
    details: Dict[str, Any]
    confidence: float


@dataclass
class SpaceTerminal:
    """Represents a detected space terminal."""
    x: int
    y: int
    width: int
    height: int
    terminal_type: str  # "mission", "ship", "trade", "repair"
    confidence: float
    detected_text: str


class SpaceEventDetector:
    """Detect space events and terminals using logs and OCR."""

    def __init__(self, config_path: str = "config/session_config.json"):
        """Initialize the space event detector.

        Parameters
        ----------
        config_path : str
            Path to session configuration file
        """
        self.config = self._load_config(config_path)
        self.space_config = self.config.get("space_mode", {})
        
        # Space event keywords
        self.space_keywords = [
            "/space", "space", "ship", "mission", "terminal",
            "patrol", "escort", "kill", "target", "station"
        ]
        
        # Terminal detection keywords
        self.terminal_keywords = [
            "mission terminal", "ship terminal", "trade terminal",
            "repair terminal", "space terminal"
        ]
        
        # Log monitoring
        self.last_log_check = time.time()
        self.log_check_interval = 5.0  # Check logs every 5 seconds

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load session configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        return {}

    def detect_space_events(self) -> List[SpaceEvent]:
        """Detect space events from logs and screen.

        Returns
        -------
        List[SpaceEvent]
            List of detected space events
        """
        events = []
        
        # Check if auto-detect is enabled
        if not self.space_config.get("auto_detect_space_events", True):
            return events

        # Detect from logs
        log_events = self._detect_from_logs()
        events.extend(log_events)

        # Detect from screen
        screen_events = self._detect_from_screen()
        events.extend(screen_events)

        if events:
            log_event(f"[SPACE] Detected {len(events)} space events")
            
        return events

    def _detect_from_logs(self) -> List[SpaceEvent]:
        """Detect space events from log files.

        Returns
        -------
        List[SpaceEvent]
            Space events detected from logs
        """
        events = []
        
        # Check recent log files
        log_dir = Path("logs")
        if not log_dir.exists():
            return events

        # Look for recent log files
        current_time = time.time()
        for log_file in log_dir.glob("*.log"):
            if current_time - log_file.stat().st_mtime < 300:  # Last 5 minutes
                events.extend(self._parse_log_file(log_file))

        return events

    def _parse_log_file(self, log_file: Path) -> List[SpaceEvent]:
        """Parse a log file for space events.

        Parameters
        ----------
        log_file : Path
            Path to log file

        Returns
        -------
        List[SpaceEvent]
            Space events found in log file
        """
        events = []
        
        try:
            with log_file.open("r", encoding="utf-8") as fh:
                for line in fh:
                    event = self._parse_log_line(line)
                    if event:
                        events.append(event)
        except Exception as e:
            log_event(f"[SPACE] Error parsing log file {log_file}: {e}")

        return events

    def _parse_log_line(self, line: str) -> Optional[SpaceEvent]:
        """Parse a single log line for space events.

        Parameters
        ----------
        line : str
            Log line to parse

        Returns
        -------
        SpaceEvent or None
            Detected space event
        """
        # Look for /space command
        if "/space" in line.lower():
            return self._create_space_event("space_command", line)
        
        # Look for ship entry/exit
        if any(keyword in line.lower() for keyword in ["ship", "enter", "exit", "board"]):
            if "enter" in line.lower() or "board" in line.lower():
                return self._create_space_event("ship_entry", line)
            elif "exit" in line.lower() or "leave" in line.lower():
                return self._create_space_event("ship_exit", line)
        
        # Look for mission-related text
        mission_keywords = ["mission", "patrol", "escort", "kill", "target"]
        if any(keyword in line.lower() for keyword in mission_keywords):
            return self._create_space_event("mission_available", line)
        
        # Look for terminal interaction
        if "terminal" in line.lower():
            return self._create_space_event("terminal_interaction", line)

        return None

    def _create_space_event(self, event_type: str, line: str) -> SpaceEvent:
        """Create a space event from log line.

        Parameters
        ----------
        event_type : str
            Type of space event
        line : str
            Log line containing the event

        Returns
        -------
        SpaceEvent
            Created space event
        """
        # Extract timestamp if present
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        timestamp = timestamp_match.group(1) if timestamp_match else datetime.now().isoformat()
        
        # Extract location if present
        location_match = re.search(r'at\s+([^\s]+)', line)
        location = location_match.group(1) if location_match else "unknown"
        
        # Extract details
        details = {
            "raw_line": line.strip(),
            "event_type": event_type,
            "confidence": 0.8
        }
        
        return SpaceEvent(
            event_type=event_type,
            timestamp=timestamp,
            location=location,
            details=details,
            confidence=0.8
        )

    def _detect_from_screen(self) -> List[SpaceEvent]:
        """Detect space events from screen content.

        Returns
        -------
        List[SpaceEvent]
            Space events detected from screen
        """
        events = []
        
        try:
            # Capture screen and extract text
            screen_image = capture_screen()
            text = screen_text()
            
            # Look for space-related keywords
            for keyword in self.space_keywords:
                if keyword.lower() in text.lower():
                    event = self._create_screen_event(keyword, text, screen_image)
                    if event:
                        events.append(event)
                        
        except Exception as e:
            log_event(f"[SPACE] Error detecting from screen: {e}")
            
        return events

    def _create_screen_event(self, keyword: str, text: str, 
                           screen_image) -> Optional[SpaceEvent]:
        """Create a space event from screen content.

        Parameters
        ----------
        keyword : str
            Keyword that triggered detection
        text : str
            Screen text
        screen_image
            Screen image

        Returns
        -------
        SpaceEvent or None
            Created space event
        """
        # Determine event type based on keyword
        if keyword == "/space":
            event_type = "space_command"
        elif keyword in ["ship", "enter", "board"]:
            event_type = "ship_entry"
        elif keyword in ["exit", "leave"]:
            event_type = "ship_exit"
        elif keyword in ["mission", "patrol", "escort", "kill", "target"]:
            event_type = "mission_available"
        elif keyword == "terminal":
            event_type = "terminal_interaction"
        else:
            event_type = "space_detected"
        
        details = {
            "keyword": keyword,
            "screen_text": text[:200],  # First 200 chars
            "confidence": 0.7
        }
        
        return SpaceEvent(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            location="screen",
            details=details,
            confidence=0.7
        )

    def detect_space_terminals(self, screen_image=None) -> List[SpaceTerminal]:
        """Detect space terminals on screen.

        Parameters
        ----------
        screen_image
            Screenshot to analyze. If None, captures current screen.

        Returns
        -------
        List[SpaceTerminal]
            List of detected space terminals
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

        log_event(f"[SPACE] Detected {len(terminals)} space terminals")
        return terminals

    def _find_terminal_region(self, image, keyword: str) -> Optional[SpaceTerminal]:
        """Find the region containing a terminal keyword.

        Parameters
        ----------
        image
            Screenshot to analyze
        keyword : str
            Keyword to search for

        Returns
        -------
        SpaceTerminal or None
            Detected terminal region
        """
        # This is a simplified implementation
        # In practice, you'd use more sophisticated image processing
        
        # For now, return a default terminal if keyword is found
        import cv2
        import numpy as np
        
        height, width = image.shape[:2]
        
        # Return a default terminal position
        return SpaceTerminal(
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
        
        if "mission" in keyword_lower:
            return "mission"
        elif "ship" in keyword_lower:
            return "ship"
        elif "trade" in keyword_lower:
            return "trade"
        elif "repair" in keyword_lower:
            return "repair"
        else:
            return "space"  # Default

    def is_space_screen(self, screen_image=None) -> bool:
        """Check if current screen shows a space interface.

        Parameters
        ----------
        screen_image
            Screenshot to analyze. If None, captures current screen.

        Returns
        -------
        bool
            True if space interface is detected
        """
        if screen_image is None:
            screen_image = capture_screen()

        # Check for space-related text
        text = screen_text()
        space_indicators = ["space", "ship", "mission", "terminal", "station"]
        
        return any(indicator in text.lower() for indicator in space_indicators) 