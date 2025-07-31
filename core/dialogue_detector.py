"""OCR-based dialogue detection and interaction system.

This module provides automated detection and interaction with NPC dialogue windows
using OCR text recognition and pattern matching for quest automation.
"""

from __future__ import annotations

import re
import time
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

import cv2
import numpy as np
import pyautogui
import pytesseract

from src.vision.ocr import capture_screen, extract_text
from core.logging_config import configure_logger

# Configure logger for dialogue system
logger = configure_logger("dialogue_detector", "logs/dialogue/dialogue.log")

# Dialogue detection regions (relative to screen dimensions)
DIALOGUE_REGIONS = {
    "full_screen": None,  # Capture entire screen
    "dialogue_box": (0.2, 0.6, 0.6, 0.3),  # Center-bottom region
    "quest_window": (0.1, 0.1, 0.8, 0.8),  # Most of screen
}

# Common dialogue patterns for different types of interactions
DIALOGUE_PATTERNS = {
    "quest_offer": [
        r"would you.*help",
        r"task.*for you",
        r"quest.*available",
        r"mission.*urgent",
        r"need.*assistance",
    ],
    "quest_acceptance": [
        r"accept.*quest",
        r"take.*mission",
        r"yes.*help",
        r"i'll.*do it",
        r"count me in",
    ],
    "quest_completion": [
        r"completed.*task",
        r"finished.*mission",
        r"quest.*complete",
        r"well done",
        r"excellent work",
    ],
    "trainer_dialogue": [
        r"train.*skills",
        r"teach.*abilities",
        r"learn.*from me",
        r"instruction.*available",
        r"master.*profession",
    ],
    "vendor_dialogue": [
        r"buy.*sell",
        r"items.*for sale",
        r"purchase.*goods",
        r"trading.*post",
        r"merchant.*wares",
    ],
    "continue_prompt": [
        r"press.*continue",
        r"click.*proceed",
        r"next.*dialogue",
        r"more.*to say",
    ],
}

# Response mappings for different dialogue types
RESPONSE_ACTIONS = {
    "quest_offer": {"key": "1", "description": "Accept quest"},
    "quest_acceptance": {"key": "enter", "description": "Confirm acceptance"},
    "quest_completion": {"key": "enter", "description": "Acknowledge completion"},
    "trainer_dialogue": {"key": "1", "description": "Begin training"},
    "vendor_dialogue": {"key": "1", "description": "Browse items"},
    "continue_prompt": {"key": "enter", "description": "Continue dialogue"},
}


@dataclass
class DialogueDetection:
    """Represents a detected dialogue interaction."""
    dialogue_type: str
    text_content: str
    confidence: float
    timestamp: datetime
    response_action: Optional[Dict[str, str]] = None
    region_used: str = "full_screen"


class DialoguePreprocessor:
    """Handles image preprocessing for better OCR accuracy."""

    @staticmethod
    def enhance_for_ocr(image: np.ndarray) -> np.ndarray:
        """Enhance image for better OCR text recognition."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned

    @staticmethod
    def extract_dialogue_region(image: np.ndarray, region_key: str) -> np.ndarray:
        """Extract specific region from image based on dialogue region definition."""
        if region_key == "full_screen" or region_key not in DIALOGUE_REGIONS:
            return image
            
        h, w = image.shape[:2]
        region = DIALOGUE_REGIONS[region_key]
        
        # Convert relative coordinates to absolute
        x = int(region[0] * w)
        y = int(region[1] * h)
        width = int(region[2] * w)
        height = int(region[3] * h)
        
        return image[y:y+height, x:x+width]


class DialogueTextAnalyzer:
    """Analyzes extracted text to identify dialogue types and content."""

    def __init__(self):
        self.patterns = DIALOGUE_PATTERNS

    def analyze_text(self, text: str) -> Tuple[Optional[str], float]:
        """Analyze text and return dialogue type with confidence score."""
        text_lower = text.lower()
        best_match = None
        best_confidence = 0.0

        for dialogue_type, patterns in self.patterns.items():
            confidence = self._calculate_confidence(text_lower, patterns)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = dialogue_type

        # Require minimum confidence threshold
        if best_confidence < 0.3:
            return None, 0.0

        return best_match, best_confidence

    def _calculate_confidence(self, text: str, patterns: List[str]) -> float:
        """Calculate confidence score based on pattern matches."""
        matches = 0
        total_patterns = len(patterns)

        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1

        # Basic confidence calculation
        confidence = matches / total_patterns if total_patterns > 0 else 0.0
        
        # Bonus for multiple matches
        if matches > 1:
            confidence *= 1.2
            
        return min(confidence, 1.0)


class DialogueActionExecutor:
    """Executes appropriate actions based on detected dialogue types."""

    def __init__(self):
        self.actions = RESPONSE_ACTIONS

    def execute_response(self, dialogue_type: str) -> bool:
        """Execute the appropriate response action for the dialogue type."""
        if dialogue_type not in self.actions:
            logger.warning(f"No action defined for dialogue type: {dialogue_type}")
            return False

        action_info = self.actions[dialogue_type]
        key = action_info["key"]
        description = action_info["description"]

        logger.info(f"Executing action: {description} (key: {key})")

        try:
            # Add human-like delay
            delay = random.uniform(0.8, 2.0)
            time.sleep(delay)

            # Execute the key press
            if key == "enter":
                pyautogui.press("enter")
            else:
                pyautogui.press(key)

            # Additional delay after action
            time.sleep(random.uniform(0.5, 1.0))
            
            logger.info(f"Successfully executed action: {description}")
            return True

        except Exception as e:
            logger.error(f"Failed to execute action {description}: {e}")
            return False


class DialogueLogger:
    """Handles logging of dialogue interactions to files."""

    def __init__(self):
        self.log_dir = Path("logs/dialogue")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_log = self.log_dir / "session_dialogue.log"
        self.detailed_log = self.log_dir / "detailed_dialogue.json"

    def log_detection(self, detection: DialogueDetection) -> None:
        """Log a dialogue detection event."""
        # Simple text log
        with open(self.session_log, "a", encoding="utf-8") as f:
            timestamp = detection.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {detection.dialogue_type} (conf: {detection.confidence:.2f})\n")

        # Detailed JSON log
        self._append_json_log(detection)

    def _append_json_log(self, detection: DialogueDetection) -> None:
        """Append detection to detailed JSON log."""
        log_entry = {
            "timestamp": detection.timestamp.isoformat(),
            "dialogue_type": detection.dialogue_type,
            "confidence": detection.confidence,
            "text_content": detection.text_content[:500],  # Truncate for storage
            "response_action": detection.response_action,
            "region_used": detection.region_used,
        }

        # Read existing logs
        try:
            with open(self.detailed_log, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []

        # Append new log
        logs.append(log_entry)

        # Keep only last 1000 entries
        if len(logs) > 1000:
            logs = logs[-1000:]

        # Write back
        with open(self.detailed_log, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)


class DialogueDetector:
    """Main dialogue detection and interaction system."""

    def __init__(self):
        self.preprocessor = DialoguePreprocessor()
        self.analyzer = DialogueTextAnalyzer()
        self.executor = DialogueActionExecutor()
        self.dialogue_logger = DialogueLogger()
        
        logger.info("DialogueDetector initialized")

    def detect_and_handle_dialogue(
        self, 
        auto_respond: bool = True,
        region: str = "dialogue_box"
    ) -> Optional[DialogueDetection]:
        """Detect dialogue and optionally respond automatically."""
        try:
            # Capture screen
            image = capture_screen()
            
            # Extract dialogue region
            dialogue_region = self.preprocessor.extract_dialogue_region(image, region)
            
            # Enhance for OCR
            enhanced = self.preprocessor.enhance_for_ocr(dialogue_region)
            
            # Extract text
            text = pytesseract.image_to_string(enhanced)
            
            if not text.strip():
                return None

            logger.debug(f"Extracted text: {text[:100]}...")

            # Analyze text for dialogue type
            dialogue_type, confidence = self.analyzer.analyze_text(text)
            
            if not dialogue_type:
                return None

            # Create detection object
            detection = DialogueDetection(
                dialogue_type=dialogue_type,
                text_content=text,
                confidence=confidence,
                timestamp=datetime.now(),
                region_used=region
            )

            # Add response action info
            if dialogue_type in RESPONSE_ACTIONS:
                detection.response_action = RESPONSE_ACTIONS[dialogue_type]

            # Log the detection
            self.dialogue_logger.log_detection(detection)
            
            logger.info(f"Detected dialogue: {dialogue_type} (confidence: {confidence:.2f})")

            # Execute response if auto-respond is enabled
            if auto_respond and detection.response_action:
                success = self.executor.execute_response(dialogue_type)
                if success:
                    logger.info(f"Auto-responded to {dialogue_type}")
                else:
                    logger.warning(f"Failed to auto-respond to {dialogue_type}")

            return detection

        except Exception as e:
            logger.error(f"Error in dialogue detection: {e}")
            return None

    def scan_for_dialogues(
        self, 
        duration: float = 10.0, 
        interval: float = 2.0,
        auto_respond: bool = True
    ) -> List[DialogueDetection]:
        """Continuously scan for dialogues for a specified duration."""
        detections = []
        start_time = time.time()
        
        logger.info(f"Starting dialogue scan for {duration}s (interval: {interval}s)")

        while time.time() - start_time < duration:
            detection = self.detect_and_handle_dialogue(auto_respond=auto_respond)
            if detection:
                detections.append(detection)

            time.sleep(interval)

        logger.info(f"Dialogue scan completed. Found {len(detections)} dialogues")
        return detections

    def get_dialogue_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent dialogue history from logs."""
        try:
            with open(self.dialogue_logger.detailed_log, "r", encoding="utf-8") as f:
                logs = json.load(f)
            return logs[-limit:] if len(logs) > limit else logs
        except (FileNotFoundError, json.JSONDecodeError):
            return []


# Convenience functions for integration with existing systems
def detect_dialogue(auto_respond: bool = True) -> Optional[DialogueDetection]:
    """Convenience function to detect a single dialogue interaction."""
    detector = DialogueDetector()
    return detector.detect_and_handle_dialogue(auto_respond=auto_respond)


def scan_dialogues(duration: float = 10.0, auto_respond: bool = True) -> List[DialogueDetection]:
    """Convenience function to scan for dialogues over time."""
    detector = DialogueDetector()
    return detector.scan_for_dialogues(duration=duration, auto_respond=auto_respond)


def register_custom_dialogue_pattern(dialogue_type: str, patterns: List[str], action: Dict[str, str]) -> None:
    """Register a custom dialogue pattern and response action."""
    DIALOGUE_PATTERNS[dialogue_type] = patterns
    RESPONSE_ACTIONS[dialogue_type] = action
    logger.info(f"Registered custom dialogue pattern: {dialogue_type}")


__all__ = [
    "DialogueDetector",
    "DialogueDetection", 
    "detect_dialogue",
    "scan_dialogues",
    "register_custom_dialogue_pattern",
]