"""
Smart NPC Detection via Quest Giver Icons and OCR (Batch 054)

- Uses OpenCV template matching to identify quest icons (!) and (?)
- Captures surrounding NPC names using OCR
- Cross-checks NPC names with quest_sources.json
- Provides CLI debug mode with confidence ratings
"""

import cv2
import numpy as np
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from PIL import Image

# Import existing vision utilities
from .capture_screen import capture_screen
from .ocr_engine import run_ocr

@dataclass
class QuestNPC:
    """Represents a detected quest-giving NPC."""
    name: str
    icon_type: str  # "!" or "?"
    confidence: float
    coordinates: Tuple[int, int]
    quest_data: Optional[Dict[str, Any]] = None
    screen_region: Optional[Tuple[int, int, int, int]] = None

@dataclass
class QuestIcon:
    """Represents a detected quest icon."""
    icon_type: str  # "!" or "?"
    confidence: float
    coordinates: Tuple[int, int]
    size: Tuple[int, int]

class QuestIconDetector:
    """Detects quest icons using OpenCV template matching."""
    
    def __init__(self):
        """Initialize the quest icon detector."""
        self.logger = logging.getLogger(__name__)
        
        # Create templates directory if it doesn't exist
        self.templates_dir = Path("assets/quest_icons")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Quest icon templates (these would be actual image files in practice)
        self.icon_templates = {
            "quest_available": "quest_available.png",  # Yellow (!)
            "quest_complete": "quest_complete.png",    # Yellow (?)
        }
        
        # Detection thresholds
        self.confidence_threshold = 0.7
        self.min_icon_size = (16, 16)
        self.max_icon_size = (32, 32)
        
        # Icon search regions (relative to screen)
        self.search_regions = [
            (0, 0, 1920, 1080),  # Full screen
            (400, 200, 1120, 680),  # Center region
            (300, 100, 1320, 880),  # Extended center
        ]
    
    def create_quest_icon_templates(self):
        """Create sample quest icon templates for testing."""
        try:
            # Create a simple yellow exclamation mark template
            exclamation_template = np.zeros((24, 24, 3), dtype=np.uint8)
            # Draw a simple yellow exclamation mark
            cv2.putText(exclamation_template, "!", (8, 18), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # Create a simple yellow question mark template
            question_template = np.zeros((24, 24, 3), dtype=np.uint8)
            # Draw a simple yellow question mark
            cv2.putText(question_template, "?", (8, 18), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # Save templates
            cv2.imwrite(str(self.templates_dir / "quest_available.png"), exclamation_template)
            cv2.imwrite(str(self.templates_dir / "quest_complete.png"), question_template)
            
            self.logger.info("Created quest icon templates")
            
        except Exception as e:
            self.logger.warning(f"Could not create templates: {e}")
    
    def detect_quest_icons(self, image: np.ndarray) -> List[QuestIcon]:
        """
        Detect quest icons in the given image.
        
        Parameters
        ----------
        image : np.ndarray
            Screenshot to analyze
            
        Returns
        -------
        List[QuestIcon]
            List of detected quest icons
        """
        detected_icons = []
        
        try:
            # Convert to BGR if needed (OpenCV format)
            if len(image.shape) == 3 and image.shape[2] == 3:
                # Already in BGR format
                pass
            else:
                # Convert from RGB to BGR
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Try to load templates
            for icon_type, template_name in self.icon_templates.items():
                template_path = self.templates_dir / template_name
                
                if not template_path.exists():
                    # Create templates if they don't exist
                    self.create_quest_icon_templates()
                
                if template_path.exists():
                    template = cv2.imread(str(template_path))
                    if template is not None:
                        # Perform template matching
                        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
                        
                        # Find locations where confidence exceeds threshold
                        locations = np.where(result >= self.confidence_threshold)
                        
                        for pt in zip(*locations[::-1]):  # Switch columns and rows
                            confidence = result[pt[1], pt[0]]
                            
                            # Get template size
                            h, w = template.shape[:2]
                            
                            # Check if size is reasonable
                            if (self.min_icon_size[0] <= w <= self.max_icon_size[0] and
                                self.min_icon_size[1] <= h <= self.max_icon_size[1]):
                                
                                icon = QuestIcon(
                                    icon_type="!" if "available" in icon_type else "?",
                                    confidence=float(confidence),
                                    coordinates=(pt[0], pt[1]),
                                    size=(w, h)
                                )
                                detected_icons.append(icon)
                                
                                self.logger.debug(f"Detected {icon.icon_type} icon at {pt} with confidence {confidence:.2f}")
            
            # Remove duplicates (icons detected multiple times)
            unique_icons = self._remove_duplicate_icons(detected_icons)
            
            return unique_icons
            
        except Exception as e:
            self.logger.error(f"Error detecting quest icons: {e}")
            return []
    
    def _remove_duplicate_icons(self, icons: List[QuestIcon]) -> List[QuestIcon]:
        """Remove duplicate icons that are too close to each other."""
        if not icons:
            return []
        
        # Sort by confidence (highest first)
        sorted_icons = sorted(icons, key=lambda x: x.confidence, reverse=True)
        unique_icons = []
        
        for icon in sorted_icons:
            # Check if this icon is too close to any already accepted icon
            is_duplicate = False
            for unique_icon in unique_icons:
                distance = np.sqrt((icon.coordinates[0] - unique_icon.coordinates[0])**2 + 
                                 (icon.coordinates[1] - unique_icon.coordinates[1])**2)
                if distance < 20:  # 20 pixel threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_icons.append(icon)
        
        return unique_icons

class NPCDetector:
    """Main NPC detector that combines icon detection and OCR."""
    
    def __init__(self, quest_sources_file: str = "data/quest_sources.json"):
        """Initialize the NPC detector."""
        self.logger = logging.getLogger(__name__)
        self.icon_detector = QuestIconDetector()
        self.quest_sources_file = Path(quest_sources_file)
        self.quest_sources = self._load_quest_sources()
        
        # OCR settings
        self.npc_name_region_size = (200, 50)  # Width, height for NPC name region
        self.min_npc_name_length = 3
        self.max_npc_name_length = 50
        
        # Detection settings
        self.min_confidence = 0.6
        self.debug_mode = False
    
    def _load_quest_sources(self) -> Dict[str, Any]:
        """Load quest sources from JSON file."""
        try:
            if self.quest_sources_file.exists():
                with open(self.quest_sources_file, 'r') as f:
                    data = json.load(f)
                    self.logger.info(f"Loaded {len(data.get('quest_sources', {}))} quest sources")
                    return data
            else:
                self.logger.warning(f"Quest sources file not found: {self.quest_sources_file}")
                return {"quest_sources": {}}
        except Exception as e:
            self.logger.error(f"Error loading quest sources: {e}")
            return {"quest_sources": {}}
    
    def detect_quest_npcs(self, image: np.ndarray = None) -> List[QuestNPC]:
        """
        Detect quest-giving NPCs in the given image.
        
        Parameters
        ----------
        image : np.ndarray, optional
            Screenshot to analyze. If None, captures current screen.
            
        Returns
        -------
        List[QuestNPC]
            List of detected quest-giving NPCs
        """
        if image is None:
            # Capture current screen
            pil_image = capture_screen()
            if pil_image is None:
                self.logger.error("Failed to capture screen")
                return []
            
            # Convert PIL to numpy array
            image = np.array(pil_image)
        
        detected_npcs = []
        
        try:
            # Detect quest icons
            quest_icons = self.icon_detector.detect_quest_icons(image)
            
            if self.debug_mode:
                self.logger.info(f"Detected {len(quest_icons)} quest icons")
            
            # For each detected icon, try to extract NPC name
            for icon in quest_icons:
                npc_name = self._extract_npc_name(image, icon)
                
                if npc_name:
                    # Cross-check with quest sources
                    quest_data = self._find_quest_data(npc_name)
                    
                    npc = QuestNPC(
                        name=npc_name,
                        icon_type=icon.icon_type,
                        confidence=icon.confidence,
                        coordinates=icon.coordinates,
                        quest_data=quest_data,
                        screen_region=self._get_npc_region(icon)
                    )
                    
                    detected_npcs.append(npc)
                    
                    if self.debug_mode:
                        self.logger.info(f"Detected NPC: {npc_name} ({icon.icon_type}) - Confidence: {icon.confidence:.2f}")
        
        except Exception as e:
            self.logger.error(f"Error detecting quest NPCs: {e}")
        
        return detected_npcs
    
    def _extract_npc_name(self, image: np.ndarray, icon: QuestIcon) -> Optional[str]:
        """
        Extract NPC name from the region around the quest icon.
        
        Parameters
        ----------
        image : np.ndarray
            Screenshot image
        icon : QuestIcon
            Detected quest icon
            
        Returns
        -------
        str or None
            Extracted NPC name, or None if not found
        """
        try:
            # Define region around the icon to look for NPC name
            # Quest icons are typically above NPC names
            x, y = icon.coordinates
            w, h = icon.size
            
            # Region below the icon (where NPC name typically appears)
            region_x = max(0, x - self.npc_name_region_size[0] // 2)
            region_y = min(image.shape[0] - self.npc_name_region_size[1], y + h + 5)
            region_w = min(self.npc_name_region_size[0], image.shape[1] - region_x)
            region_h = min(self.npc_name_region_size[1], image.shape[0] - region_y)
            
            # Extract region
            npc_region = image[region_y:region_y + region_h, region_x:region_x + region_w]
            
            if npc_region.size == 0:
                return None
            
            # Convert to PIL Image for OCR
            pil_region = Image.fromarray(npc_region)
            
            # Run OCR on the region
            ocr_text = run_ocr(pil_region)
            
            if ocr_text:
                # Clean up the text
                cleaned_text = self._clean_npc_name(ocr_text)
                
                if self._is_valid_npc_name(cleaned_text):
                    return cleaned_text
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting NPC name: {e}")
            return None
    
    def _clean_npc_name(self, text: str) -> str:
        """Clean and normalize NPC name text."""
        if not text:
            return ""
        
        # Remove common OCR artifacts
        cleaned = text.strip()
        cleaned = cleaned.replace('\n', ' ')
        cleaned = cleaned.replace('\r', ' ')
        cleaned = ' '.join(cleaned.split())  # Remove extra whitespace
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['NPC:', 'Name:', 'Target:']
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        return cleaned
    
    def _is_valid_npc_name(self, name: str) -> bool:
        """Check if the extracted text is a valid NPC name."""
        if not name:
            return False
        
        # Check length
        if len(name) < self.min_npc_name_length or len(name) > self.max_npc_name_length:
            return False
        
        # Check for common invalid patterns
        invalid_patterns = [
            'level', 'health', 'damage', 'armor', 'shield',
            'quest', 'mission', 'task', 'objective',
            'accept', 'decline', 'complete', 'turn in'
        ]
        
        name_lower = name.lower()
        for pattern in invalid_patterns:
            if pattern in name_lower:
                return False
        
        # Must contain at least one letter
        if not any(c.isalpha() for c in name):
            return False
        
        return True
    
    def _get_npc_region(self, icon: QuestIcon) -> Tuple[int, int, int, int]:
        """Get the screen region around the NPC."""
        x, y = icon.coordinates
        w, h = icon.size
        
        region_x = max(0, x - self.npc_name_region_size[0] // 2)
        region_y = max(0, y - 10)  # Slightly above the icon
        region_w = self.npc_name_region_size[0]
        region_h = h + 10 + self.npc_name_region_size[1]  # Icon + gap + name region
        
        return (region_x, region_y, region_w, region_h)
    
    def _find_quest_data(self, npc_name: str) -> Optional[Dict[str, Any]]:
        """
        Find quest data for the given NPC name.
        
        Parameters
        ----------
        npc_name : str
            Name of the NPC
            
        Returns
        -------
        dict or None
            Quest data if found, None otherwise
        """
        quest_sources = self.quest_sources.get("quest_sources", {})
        
        # Try exact match first
        if npc_name in quest_sources:
            return quest_sources[npc_name]
        
        # Try partial matches
        npc_name_lower = npc_name.lower()
        for source_name, source_data in quest_sources.items():
            if npc_name_lower in source_name.lower() or source_name.lower() in npc_name_lower:
                return source_data
        
        return None
    
    def set_debug_mode(self, enabled: bool = True):
        """Enable or disable debug mode."""
        self.debug_mode = enabled
        self.logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")
    
    def get_available_quests_nearby(self) -> List[Dict[str, Any]]:
        """
        Get list of available quests nearby with confidence ratings.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of available quests with details
        """
        # Capture current screen
        pil_image = capture_screen()
        if pil_image is None:
            return []
        
        image = np.array(pil_image)
        detected_npcs = self.detect_quest_npcs(image)
        
        available_quests = []
        
        for npc in detected_npcs:
            quest_info = {
                "npc_name": npc.name,
                "icon_type": npc.icon_type,
                "confidence": npc.confidence,
                "coordinates": npc.coordinates,
                "quests": []
            }
            
            if npc.quest_data:
                quest_info["quests"] = npc.quest_data.get("quests", [])
                quest_info["planet"] = npc.quest_data.get("planet", "Unknown")
                quest_info["city"] = npc.quest_data.get("city", "Unknown")
            
            available_quests.append(quest_info)
        
        return available_quests

# Global detector instance
_npc_detector: Optional[NPCDetector] = None

def get_npc_detector() -> NPCDetector:
    """Get the global NPC detector instance."""
    global _npc_detector
    if _npc_detector is None:
        _npc_detector = NPCDetector()
    return _npc_detector

def detect_quest_npcs(image: np.ndarray = None) -> List[QuestNPC]:
    """Convenience function to detect quest NPCs."""
    return get_npc_detector().detect_quest_npcs(image)

def get_available_quests_nearby() -> List[Dict[str, Any]]:
    """Convenience function to get available quests nearby."""
    return get_npc_detector().get_available_quests_nearby()

def set_debug_mode(enabled: bool = True):
    """Convenience function to set debug mode."""
    get_npc_detector().set_debug_mode(enabled) 