#!/usr/bin/env python3
"""OCR Damage Parser for Batch 046 - Licensing System + Combat Intelligence v1."""

import re
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import json

logger = logging.getLogger(__name__)


@dataclass
class DamageEvent:
    """Represents a detected damage event."""
    damage_amount: int
    damage_type: str
    timestamp: datetime
    confidence: float
    screen_region: Tuple[int, int, int, int]  # x, y, width, height
    raw_text: str
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'damage_amount': self.damage_amount,
            'damage_type': self.damage_type,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'screen_region': self.screen_region,
            'raw_text': self.raw_text,
            'processed': self.processed
        }


class OCRDamageParser:
    """OCR-based damage detection and parsing."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize OCR damage parser."""
        self.config = self._load_config(config_file)
        self.damage_patterns = self._compile_damage_patterns()
        self.damage_history: List[DamageEvent] = []
        self.last_processed_time: Optional[datetime] = None
        
        # OCR configuration
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789-+'
        
        logger.info("OCR Damage Parser initialized")
    
    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration."""
        default_config = {
            'damage_regions': [
                {'name': 'combat_log', 'coords': [100, 200, 400, 300]},
                {'name': 'damage_popup', 'coords': [300, 150, 500, 200]},
                {'name': 'health_bar', 'coords': [50, 100, 250, 150]}
            ],
            'damage_types': {
                'physical': ['red', 'orange'],
                'energy': ['blue', 'cyan'],
                'kinetic': ['yellow', 'white'],
                'heat': ['red', 'dark_red'],
                'cold': ['light_blue', 'white'],
                'electric': ['bright_blue', 'yellow'],
                'acid': ['green', 'dark_green']
            },
            'min_confidence': 0.6,
            'max_history_size': 100,
            'damage_threshold': 10  # Minimum damage to consider valid
        }
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config file: {e}")
        
        return default_config
    
    def _compile_damage_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for damage detection."""
        patterns = [
            r'(\d{1,4})',  # Basic damage numbers
            r'(\d{1,4})\s*damage',  # "damage" suffix
            r'(\d{1,4})\s*DMG',  # "DMG" suffix
            r'(\d{1,4})\s*pts?',  # "pts" or "pt" suffix
            r'(\d{1,4})\s*damage\s*dealt',  # "damage dealt" suffix
            r'(\d{1,4})\s*to\s*(\w+)',  # "X to target" format
            r'(\d{1,4})\s*\((\w+)\)',  # "X (type)" format
        ]
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        # Convert to PIL Image for processing
        pil_image = Image.fromarray(image)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(2.0)
        
        # Apply slight blur to reduce noise
        pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Convert back to numpy array
        processed_image = np.array(pil_image)
        
        # Convert to grayscale if needed
        if len(processed_image.shape) == 3:
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold to create binary image
        _, binary_image = cv2.threshold(processed_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary_image
    
    def extract_text_from_region(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> str:
        """Extract text from a specific region of the image."""
        x, y, width, height = region
        
        # Ensure coordinates are within image bounds
        img_height, img_width = image.shape[:2]
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        width = min(width, img_width - x)
        height = min(height, img_height - y)
        
        if width <= 0 or height <= 0:
            return ""
        
        # Extract region
        region_image = image[y:y+height, x:x+width]
        
        # Preprocess the region
        processed_region = self.preprocess_image(region_image)
        
        try:
            # Perform OCR
            text = pytesseract.image_to_string(
                processed_region,
                config=self.tesseract_config
            )
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""
    
    def parse_damage_from_text(self, text: str) -> List[Tuple[int, float]]:
        """Parse damage amounts from text."""
        damage_matches = []
        
        for pattern in self.damage_patterns:
            matches = pattern.findall(text)
            for match in matches:
                try:
                    # Extract the damage number
                    if isinstance(match, tuple):
                        damage_str = match[0]
                    else:
                        damage_str = match
                    
                    damage_amount = int(damage_str)
                    
                    # Validate damage amount
                    if damage_amount >= self.config['damage_threshold']:
                        # Calculate confidence based on pattern match
                        confidence = min(1.0, len(text) / 50.0)  # Simple confidence calculation
                        damage_matches.append((damage_amount, confidence))
                        
                except (ValueError, TypeError) as e:
                    logger.debug(f"Could not parse damage from '{match}': {e}")
                    continue
        
        return damage_matches
    
    def detect_damage_type_from_color(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> str:
        """Detect damage type based on color analysis."""
        x, y, width, height = region
        
        # Extract region
        region_image = image[y:y+height, x:x+width]
        
        if len(region_image.shape) == 3:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(region_image, cv2.COLOR_BGR2HSV)
            
            # Calculate average hue and saturation
            avg_hue = np.mean(hsv[:, :, 0])
            avg_sat = np.mean(hsv[:, :, 1])
            avg_val = np.mean(hsv[:, :, 2])
            
            # Simple color-based damage type detection
            if avg_hue < 10 or avg_hue > 170:  # Red range
                if avg_sat > 100:
                    return 'physical' if avg_val > 150 else 'heat'
                else:
                    return 'physical'
            elif 100 < avg_hue < 130:  # Blue range
                if avg_sat > 100:
                    return 'energy' if avg_val > 150 else 'cold'
                else:
                    return 'energy'
            elif 30 < avg_hue < 90:  # Green range
                return 'acid'
            elif 20 < avg_hue < 30:  # Yellow range
                return 'electric'
            else:
                return 'kinetic'  # Default for unknown colors
        
        return 'unknown'
    
    def scan_for_damage(self, image: np.ndarray) -> List[DamageEvent]:
        """Scan image for damage events."""
        damage_events = []
        current_time = datetime.now()
        
        # Scan each configured region
        for region_config in self.config['damage_regions']:
            region_name = region_config['name']
            region_coords = region_config['coords']
            
            # Extract text from region
            text = self.extract_text_from_region(image, region_coords)
            
            if text:
                # Parse damage from text
                damage_matches = self.parse_damage_from_text(text)
                
                for damage_amount, confidence in damage_matches:
                    if confidence >= self.config['min_confidence']:
                        # Detect damage type
                        damage_type = self.detect_damage_type_from_color(image, region_coords)
                        
                        # Create damage event
                        damage_event = DamageEvent(
                            damage_amount=damage_amount,
                            damage_type=damage_type,
                            timestamp=current_time,
                            confidence=confidence,
                            screen_region=region_coords,
                            raw_text=text
                        )
                        
                        damage_events.append(damage_event)
        
        # Add to history
        self.damage_history.extend(damage_events)
        
        # Trim history if too large
        if len(self.damage_history) > self.config['max_history_size']:
            self.damage_history = self.damage_history[-self.config['max_history_size']:]
        
        return damage_events
    
    def get_recent_damage_events(self, seconds: float = 5.0) -> List[DamageEvent]:
        """Get recent damage events within a time window."""
        cutoff_time = datetime.now() - timedelta(seconds=seconds)
        return [
            event for event in self.damage_history
            if event.timestamp > cutoff_time
        ]
    
    def get_damage_statistics(self, time_window: float = 300.0) -> Dict[str, Any]:
        """Get damage statistics for a time window."""
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        recent_events = [
            event for event in self.damage_history
            if event.timestamp > cutoff_time
        ]
        
        if not recent_events:
            return {
                'total_damage': 0,
                'event_count': 0,
                'average_damage': 0,
                'damage_by_type': {},
                'highest_damage': 0,
                'lowest_damage': 0
            }
        
        total_damage = sum(event.damage_amount for event in recent_events)
        damage_by_type = {}
        
        for event in recent_events:
            damage_type = event.damage_type
            if damage_type not in damage_by_type:
                damage_by_type[damage_type] = {
                    'total': 0,
                    'count': 0,
                    'average': 0
                }
            
            damage_by_type[damage_type]['total'] += event.damage_amount
            damage_by_type[damage_type]['count'] += 1
        
        # Calculate averages
        for damage_type, stats in damage_by_type.items():
            stats['average'] = stats['total'] / stats['count']
        
        damage_amounts = [event.damage_amount for event in recent_events]
        
        return {
            'total_damage': total_damage,
            'event_count': len(recent_events),
            'average_damage': total_damage / len(recent_events),
            'damage_by_type': damage_by_type,
            'highest_damage': max(damage_amounts),
            'lowest_damage': min(damage_amounts)
        }
    
    def clear_history(self) -> None:
        """Clear damage history."""
        self.damage_history.clear()
        logger.info("Cleared damage history")
    
    def export_damage_history(self, filename: str) -> bool:
        """Export damage history to file."""
        try:
            history_data = {
                'export_time': datetime.now().isoformat(),
                'events': [event.to_dict() for event in self.damage_history]
            }
            
            with open(filename, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            logger.info(f"Exported damage history to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting damage history: {e}")
            return False
    
    def import_damage_history(self, filename: str) -> bool:
        """Import damage history from file."""
        try:
            with open(filename, 'r') as f:
                history_data = json.load(f)
            
            imported_events = []
            for event_data in history_data.get('events', []):
                event = DamageEvent(
                    damage_amount=event_data['damage_amount'],
                    damage_type=event_data['damage_type'],
                    timestamp=datetime.fromisoformat(event_data['timestamp']),
                    confidence=event_data['confidence'],
                    screen_region=tuple(event_data['screen_region']),
                    raw_text=event_data['raw_text'],
                    processed=event_data.get('processed', False)
                )
                imported_events.append(event)
            
            self.damage_history.extend(imported_events)
            logger.info(f"Imported {len(imported_events)} damage events from {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing damage history: {e}")
            return False


def main():
    """Test the OCR damage parser."""
    parser = OCRDamageParser()
    
    # Create a test image with damage numbers
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Add some test text (simulating damage numbers)
    cv2.putText(test_image, "183", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
    cv2.putText(test_image, "400 damage", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(test_image, "255 pts", (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Scan for damage
    damage_events = parser.scan_for_damage(test_image)
    
    print(f"Found {len(damage_events)} damage events:")
    for event in damage_events:
        print(f"  {event.damage_amount} {event.damage_type} damage (confidence: {event.confidence:.2f})")
    
    # Get statistics
    stats = parser.get_damage_statistics()
    print(f"Damage statistics: {stats}")


if __name__ == "__main__":
    main() 