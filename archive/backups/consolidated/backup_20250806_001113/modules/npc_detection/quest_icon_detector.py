#!/usr/bin/env python3
"""Quest Icon Detection Module for Batch 043.

This module provides functionality to detect quest icons above NPCs using
OCR and image detection techniques.
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from PIL import Image
import pytesseract
from dataclasses import dataclass
import time

from vision.capture_screen import capture_screen
from vision.ocr_engine import run_ocr


@dataclass
class QuestIcon:
    """Represents a detected quest icon."""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    icon_type: str  # 'quest', 'repeatable', 'daily', 'weekly'
    npc_name: Optional[str] = None
    npc_coordinates: Optional[Tuple[int, int]] = None


@dataclass
class NPCDetection:
    """Represents a detected NPC with quest icon."""
    name: str
    coordinates: Tuple[int, int]
    quest_icon: QuestIcon
    confidence: float
    detected_time: float


class QuestIconDetector:
    """Detects quest icons above NPCs using computer vision and OCR."""
    
    def __init__(self):
        """Initialize the quest icon detector."""
        self.logger = logging.getLogger(__name__)
        
        # Quest icon templates and patterns
        self.quest_icons = {
            'quest': {
                'color_ranges': [
                    # Yellow quest icon color range
                    ([20, 100, 100], [30, 255, 255]),  # HSV
                    ([200, 200, 0], [255, 255, 100])   # BGR
                ],
                'min_size': (20, 20),
                'max_size': (50, 50)
            },
            'repeatable': {
                'color_ranges': [
                    # Blue repeatable quest color range
                    ([100, 100, 100], [130, 255, 255]),  # HSV
                    ([100, 0, 0], [255, 100, 100])      # BGR
                ],
                'min_size': (15, 15),
                'max_size': (40, 40)
            },
            'daily': {
                'color_ranges': [
                    # Green daily quest color range
                    ([40, 100, 100], [80, 255, 255]),   # HSV
                    ([0, 100, 0], [100, 255, 100])      # BGR
                ],
                'min_size': (15, 15),
                'max_size': (40, 40)
            }
        }
        
        # OCR configuration for NPC names
        self.npc_name_config = '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz -'
        
        # Detection regions (relative to screen)
        self.detection_regions = [
            # Upper portion of screen where NPC names appear
            (0, 0, 0.8, 0.3),  # Top 30% of screen, left 80%
            (0.2, 0, 1.0, 0.4),  # Top 40% of screen, right 80%
        ]
    
    def detect_quest_icons(self, screen_region: Optional[Tuple[int, int, int, int]] = None) -> List[QuestIcon]:
        """Detect quest icons in the given screen region."""
        self.logger.info("Starting quest icon detection")
        
        try:
            # Capture screen
            screenshot = capture_screen(region=screen_region)
            if screenshot is None:
                self.logger.error("Failed to capture screen")
                return []
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            detected_icons = []
            
            # Detect each type of quest icon
            for icon_type, config in self.quest_icons.items():
                icons = self._detect_icon_type(cv_image, icon_type, config)
                detected_icons.extend(icons)
            
            self.logger.info(f"Detected {len(detected_icons)} quest icons")
            return detected_icons
            
        except Exception as e:
            self.logger.error(f"Error detecting quest icons: {e}")
            return []
    
    def _detect_icon_type(self, image: np.ndarray, icon_type: str, config: Dict[str, Any]) -> List[QuestIcon]:
        """Detect a specific type of quest icon."""
        icons = []
        
        for color_range in config['color_ranges']:
            # Create mask for color range
            if len(color_range[0]) == 3:  # HSV
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                lower = np.array(color_range[0])
                upper = np.array(color_range[1])
                mask = cv2.inRange(hsv, lower, upper)
            else:  # BGR
                lower = np.array(color_range[0])
                upper = np.array(color_range[1])
                mask = cv2.inRange(image, lower, upper)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Check size constraints
                x, y, w, h = cv2.boundingRect(contour)
                min_w, min_h = config['min_size']
                max_w, max_h = config['max_size']
                
                if min_w <= w <= max_w and min_h <= h <= max_h:
                    # Calculate confidence based on contour area and shape
                    area = cv2.contourArea(contour)
                    expected_area = w * h
                    confidence = min(area / expected_area, 1.0)
                    
                    if confidence > 0.3:  # Minimum confidence threshold
                        icon = QuestIcon(
                            x=x, y=y, width=w, height=h,
                            confidence=confidence,
                            icon_type=icon_type
                        )
                        icons.append(icon)
        
        return icons
    
    def scan_npc_names(self, quest_icons: List[QuestIcon]) -> List[NPCDetection]:
        """Scan for NPC names near detected quest icons."""
        self.logger.info(f"Scanning for NPC names near {len(quest_icons)} quest icons")
        
        npc_detections = []
        
        try:
            # Capture full screen for OCR
            screenshot = capture_screen()
            if screenshot is None:
                self.logger.error("Failed to capture screen for NPC name scanning")
                return []
            
            for icon in quest_icons:
                npc_name = self._extract_npc_name(screenshot, icon)
                if npc_name:
                    # Estimate NPC coordinates (below the quest icon)
                    npc_x = icon.x + icon.width // 2
                    npc_y = icon.y + icon.height + 20  # 20 pixels below icon
                    
                    detection = NPCDetection(
                        name=npc_name,
                        coordinates=(npc_x, npc_y),
                        quest_icon=icon,
                        confidence=icon.confidence,
                        detected_time=time.time()
                    )
                    npc_detections.append(detection)
                    self.logger.info(f"Detected NPC: {npc_name} at ({npc_x}, {npc_y})")
        
        except Exception as e:
            self.logger.error(f"Error scanning NPC names: {e}")
        
        self.logger.info(f"Found {len(npc_detections)} NPCs with quest icons")
        return npc_detections
    
    def _extract_npc_name(self, screenshot: Image.Image, quest_icon: QuestIcon) -> Optional[str]:
        """Extract NPC name from the area below the quest icon."""
        try:
            # Define region below quest icon where NPC name should be
            icon_center_x = quest_icon.x + quest_icon.width // 2
            icon_center_y = quest_icon.y + quest_icon.height
            
            # Region for NPC name (centered below icon)
            name_region_width = 200
            name_region_height = 30
            
            name_x = max(0, icon_center_x - name_region_width // 2)
            name_y = icon_center_y + 5  # 5 pixels below icon
            
            # Crop the region
            name_region = screenshot.crop((
                name_x, name_y,
                name_x + name_region_width,
                name_y + name_region_height
            ))
            
            # Run OCR on the region
            npc_text = run_ocr(name_region, lang='eng')
            
            # Clean up the text
            if npc_text:
                npc_name = self._clean_npc_name(npc_text)
                if npc_name:
                    return npc_name
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting NPC name: {e}")
            return None
    
    def _clean_npc_name(self, text: str) -> Optional[str]:
        """Clean and validate NPC name from OCR text."""
        # Remove common OCR artifacts
        text = text.strip()
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())  # Normalize whitespace
        
        # Remove common non-name characters
        text = text.replace('|', ' ').replace('_', ' ').replace('-', ' ')
        
        # Basic validation
        if len(text) < 2 or len(text) > 50:
            return None
        
        # Check if text contains mostly letters and spaces
        letter_count = sum(1 for c in text if c.isalpha() or c.isspace())
        if letter_count / len(text) < 0.7:
            return None
        
        return text
    
    def get_detection_regions(self) -> List[Tuple[int, int, int, int]]:
        """Get screen regions to scan for quest icons."""
        # This would be customized based on game UI layout
        screen_width = 1920  # Default screen width
        screen_height = 1080  # Default screen height
        
        regions = []
        for rel_x, rel_y, rel_w, rel_h in self.detection_regions:
            x = int(rel_x * screen_width)
            y = int(rel_y * screen_height)
            w = int(rel_w * screen_width)
            h = int(rel_h * screen_height)
            regions.append((x, y, w, h))
        
        return regions


def detect_quest_icons(screen_region: Optional[Tuple[int, int, int, int]] = None) -> List[QuestIcon]:
    """Detect quest icons in the given screen region."""
    detector = QuestIconDetector()
    return detector.detect_quest_icons(screen_region)


def scan_npc_names(quest_icons: List[QuestIcon]) -> List[NPCDetection]:
    """Scan for NPC names near detected quest icons."""
    detector = QuestIconDetector()
    return detector.scan_npc_names(quest_icons) 