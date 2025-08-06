#!/usr/bin/env python3
"""
Stat Extractor for Character Attributes

This module provides functionality to extract character stats and attributes
from game panels using OCR and macro commands.
"""

import re
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

import cv2
import numpy as np
from PIL import Image

from core.ocr import OCREngine, extract_text_from_screen
from core.screenshot import capture_screen
from utils.logging_utils import log_event


class StatType(Enum):
    """Types of character stats."""
    HEALTH = "health"
    ACTION = "action"
    MIND = "mind"
    LUCK = "luck"
    RESIST_ENERGY = "resist_energy"
    RESIST_BLAST = "resist_blast"
    RESIST_KINETIC = "resist_kinetic"
    RESIST_HEAT = "resist_heat"
    RESIST_COLD = "resist_cold"
    RESIST_ELECTRICITY = "resist_electricity"
    RESIST_ACID = "resist_acid"
    RESIST_STUN = "resist_stun"
    TAPE_ENERGY = "tape_energy"
    TAPE_BLAST = "tape_blast"
    TAPE_KINETIC = "tape_kinetic"
    TAPE_HEAT = "tape_heat"
    TAPE_COLD = "tape_cold"
    TAPE_ELECTRICITY = "tape_electricity"
    TAPE_ACID = "tape_acid"
    TAPE_STUN = "tape_stun"


@dataclass
class CharacterStat:
    """Individual character stat."""
    stat_type: StatType
    current_value: int
    max_value: int
    percentage: float
    confidence: float
    source: str  # "stats_panel", "armor_panel", "macro"
    timestamp: float = field(default_factory=time.time)


@dataclass
class CharacterProfile:
    """Complete character profile with all stats."""
    character_name: str
    profession: str
    level: int
    stats: Dict[StatType, CharacterStat]
    armor_stats: Dict[str, Dict[str, int]]
    resistances: Dict[str, int]
    tapes: Dict[str, int]
    scan_timestamp: float = field(default_factory=time.time)
    scan_method: str = "ocr"
    confidence_score: float = 0.0


class StatExtractor:
    """
    Extracts character stats using OCR and macro commands.
    
    Features:
    - OCR-based stat extraction from game panels
    - Macro command execution for stat reading
    - Stat normalization and validation
    - Confidence scoring for extracted data
    - Support for multiple stat types
    """
    
    def __init__(self):
        """Initialize the stat extractor."""
        self.ocr_engine = OCREngine()
        self.logger = logging.getLogger(__name__)
        
        # Stat patterns for OCR recognition
        self.stat_patterns = {
            StatType.HEALTH: [
                r"health[:\s]*(\d+)/(\d+)",
                r"hp[:\s]*(\d+)/(\d+)",
                r"(\d+)/(\d+)\s*health"
            ],
            StatType.ACTION: [
                r"action[:\s]*(\d+)/(\d+)",
                r"ap[:\s]*(\d+)/(\d+)",
                r"(\d+)/(\d+)\s*action"
            ],
            StatType.MIND: [
                r"mind[:\s]*(\d+)/(\d+)",
                r"mp[:\s]*(\d+)/(\d+)",
                r"(\d+)/(\d+)\s*mind"
            ],
            StatType.LUCK: [
                r"luck[:\s]*(\d+)",
                r"(\d+)\s*luck"
            ]
        }
        
        # Resistance patterns
        self.resistance_patterns = {
            StatType.RESIST_ENERGY: [
                r"energy[:\s]*(\d+)",
                r"energy\s*resistance[:\s]*(\d+)"
            ],
            StatType.RESIST_BLAST: [
                r"blast[:\s]*(\d+)",
                r"blast\s*resistance[:\s]*(\d+)"
            ],
            StatType.RESIST_KINETIC: [
                r"kinetic[:\s]*(\d+)",
                r"kinetic\s*resistance[:\s]*(\d+)"
            ],
            StatType.RESIST_HEAT: [
                r"heat[:\s]*(\d+)",
                r"heat\s*resistance[:\s]*(\d+)"
            ],
            StatType.RESIST_COLD: [
                r"cold[:\s]*(\d+)",
                r"cold\s*resistance[:\s]*(\d+)"
            ],
            StatType.RESIST_ELECTRICITY: [
                r"electricity[:\s]*(\d+)",
                r"electricity\s*resistance[:\s]*(\d+)"
            ],
            StatType.RESIST_ACID: [
                r"acid[:\s]*(\d+)",
                r"acid\s*resistance[:\s]*(\d+)"
            ],
            StatType.RESIST_STUN: [
                r"stun[:\s]*(\d+)",
                r"stun\s*resistance[:\s]*(\d+)"
            ]
        }
        
        # Tape patterns
        self.tape_patterns = {
            StatType.TAPE_ENERGY: [
                r"energy\s*tape[:\s]*(\d+)",
                r"tape\s*energy[:\s]*(\d+)"
            ],
            StatType.TAPE_BLAST: [
                r"blast\s*tape[:\s]*(\d+)",
                r"tape\s*blast[:\s]*(\d+)"
            ],
            StatType.TAPE_KINETIC: [
                r"kinetic\s*tape[:\s]*(\d+)",
                r"tape\s*kinetic[:\s]*(\d+)"
            ],
            StatType.TAPE_HEAT: [
                r"heat\s*tape[:\s]*(\d+)",
                r"tape\s*heat[:\s]*(\d+)"
            ],
            StatType.TAPE_COLD: [
                r"cold\s*tape[:\s]*(\d+)",
                r"tape\s*cold[:\s]*(\d+)"
            ],
            StatType.TAPE_ELECTRICITY: [
                r"electricity\s*tape[:\s]*(\d+)",
                r"tape\s*electricity[:\s]*(\d+)"
            ],
            StatType.TAPE_ACID: [
                r"acid\s*tape[:\s]*(\d+)",
                r"tape\s*acid[:\s]*(\d+)"
            ],
            StatType.TAPE_STUN: [
                r"stun\s*tape[:\s]*(\d+)",
                r"tape\s*stun[:\s]*(\d+)"
            ]
        }
        
        # Panel regions for different stat types
        self.panel_regions = {
            "stats_panel": (100, 100, 400, 300),  # Example coordinates
            "armor_panel": (500, 100, 400, 300),   # Example coordinates
            "character_sheet": (200, 200, 600, 400) # Example coordinates
        }
    
    def extract_stats_from_panel(self, panel_type: str = "stats_panel") -> Dict[StatType, CharacterStat]:
        """
        Extract stats from a specific game panel.
        
        Parameters
        ----------
        panel_type : str
            Type of panel to scan ("stats_panel", "armor_panel", "character_sheet")
            
        Returns
        -------
        Dict[StatType, CharacterStat]
            Extracted stats with confidence scores
        """
        stats = {}
        
        try:
            # Get panel region
            region = self.panel_regions.get(panel_type)
            if not region:
                log_event(f"[STAT_EXTRACTOR] Unknown panel type: {panel_type}")
                return stats
            
            # Extract text from panel
            ocr_result = extract_text_from_screen(region, method="standard")
            
            if not ocr_result or not ocr_result.text:
                log_event(f"[STAT_EXTRACTOR] No text extracted from {panel_type}")
                return stats
            
            # Parse stats from text
            stats.update(self._parse_stats_from_text(ocr_result.text, panel_type, ocr_result.confidence))
            
            log_event(f"[STAT_EXTRACTOR] Extracted {len(stats)} stats from {panel_type}")
            
        except Exception as e:
            log_event(f"[STAT_EXTRACTOR] Error extracting stats from {panel_type}: {e}")
        
        return stats
    
    def _parse_stats_from_text(self, text: str, source: str, base_confidence: float) -> Dict[StatType, CharacterStat]:
        """Parse stats from OCR text."""
        stats = {}
        
        # Parse basic stats (Health, Action, Mind, Luck)
        for stat_type, patterns in self.stat_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        if len(match) == 2:  # Current/Max format
                            current, maximum = int(match[0]), int(match[1])
                            percentage = (current / maximum * 100) if maximum > 0 else 0
                        else:  # Single value format
                            current = int(match[0])
                            maximum = current  # Assume max equals current for single values
                            percentage = 100.0
                        
                        stat = CharacterStat(
                            stat_type=stat_type,
                            current_value=current,
                            max_value=maximum,
                            percentage=percentage,
                            confidence=base_confidence,
                            source=source
                        )
                        stats[stat_type] = stat
                        break  # Use first match for each stat type
                        
                    except (ValueError, IndexError) as e:
                        log_event(f"[STAT_EXTRACTOR] Error parsing {stat_type.value}: {e}")
                        continue
        
        # Parse resistances
        for stat_type, patterns in self.resistance_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = int(match)
                        stat = CharacterStat(
                            stat_type=stat_type,
                            current_value=value,
                            max_value=value,
                            percentage=100.0,
                            confidence=base_confidence,
                            source=source
                        )
                        stats[stat_type] = stat
                        break
                        
                    except (ValueError, IndexError) as e:
                        log_event(f"[STAT_EXTRACTOR] Error parsing resistance {stat_type.value}: {e}")
                        continue
        
        # Parse tapes
        for stat_type, patterns in self.tape_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = int(match)
                        stat = CharacterStat(
                            stat_type=stat_type,
                            current_value=value,
                            max_value=value,
                            percentage=100.0,
                            confidence=base_confidence,
                            source=source
                        )
                        stats[stat_type] = stat
                        break
                        
                    except (ValueError, IndexError) as e:
                        log_event(f"[STAT_EXTRACTOR] Error parsing tape {stat_type.value}: {e}")
                        continue
        
        return stats
    
    def extract_stats_via_macro(self) -> Dict[StatType, CharacterStat]:
        """
        Extract stats using macro commands.
        
        Returns
        -------
        Dict[StatType, CharacterStat]
            Stats extracted via macro commands
        """
        stats = {}
        
        try:
            # Execute /stats command
            stats_text = self._execute_stats_macro()
            if stats_text:
                stats.update(self._parse_stats_from_text(stats_text, "macro", 90.0))
            
            # Execute /armor command
            armor_text = self._execute_armor_macro()
            if armor_text:
                stats.update(self._parse_stats_from_text(armor_text, "macro", 90.0))
            
            log_event(f"[STAT_EXTRACTOR] Extracted {len(stats)} stats via macro")
            
        except Exception as e:
            log_event(f"[STAT_EXTRACTOR] Error extracting stats via macro: {e}")
        
        return stats
    
    def _execute_stats_macro(self) -> Optional[str]:
        """Execute /stats macro and capture output."""
        try:
            # This would execute the /stats command in-game
            # For now, return sample data
            return """
            Character Stats:
            Health: 1500/1500
            Action: 800/800
            Mind: 600/600
            Luck: 25
            """
        except Exception as e:
            log_event(f"[STAT_EXTRACTOR] Error executing stats macro: {e}")
            return None
    
    def _execute_armor_macro(self) -> Optional[str]:
        """Execute /armor macro and capture output."""
        try:
            # This would execute the /armor command in-game
            # For now, return sample data
            return """
            Armor Stats:
            Energy Resistance: 45
            Blast Resistance: 30
            Kinetic Resistance: 25
            Heat Resistance: 20
            Cold Resistance: 15
            Electricity Resistance: 10
            Acid Resistance: 5
            Stun Resistance: 0
            
            Tapes:
            Energy Tape: 15
            Blast Tape: 10
            Kinetic Tape: 8
            Heat Tape: 5
            Cold Tape: 3
            Electricity Tape: 2
            Acid Tape: 1
            Stun Tape: 0
            """
        except Exception as e:
            log_event(f"[STAT_EXTRACTOR] Error executing armor macro: {e}")
            return None
    
    def create_character_profile(self, character_name: str, profession: str = "", level: int = 0) -> CharacterProfile:
        """
        Create a complete character profile by scanning all available sources.
        
        Parameters
        ----------
        character_name : str
            Name of the character
        profession : str
            Character profession
        level : int
            Character level
            
        Returns
        -------
        CharacterProfile
            Complete character profile with all stats
        """
        all_stats = {}
        confidence_scores = []
        
        # Extract from different sources
        sources = [
            ("stats_panel", self.extract_stats_from_panel("stats_panel")),
            ("armor_panel", self.extract_stats_from_panel("armor_panel")),
            ("character_sheet", self.extract_stats_from_panel("character_sheet")),
            ("macro", self.extract_stats_via_macro())
        ]
        
        # Combine stats from all sources
        for source_name, source_stats in sources:
            for stat_type, stat in source_stats.items():
                if stat_type not in all_stats or stat.confidence > all_stats[stat_type].confidence:
                    all_stats[stat_type] = stat
                    confidence_scores.append(stat.confidence)
        
        # Calculate overall confidence
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        # Organize stats by category
        resistances = {stat_type.value: stat.current_value 
                      for stat_type, stat in all_stats.items() 
                      if stat_type.value.startswith("resist_")}
        
        tapes = {stat_type.value: stat.current_value 
                for stat_type, stat in all_stats.items() 
                if stat_type.value.startswith("tape_")}
        
        # Create character profile
        profile = CharacterProfile(
            character_name=character_name,
            profession=profession,
            level=level,
            stats=all_stats,
            armor_stats={},  # Would be populated from armor panel
            resistances=resistances,
            tapes=tapes,
            scan_timestamp=time.time(),
            scan_method="ocr_macro_combined",
            confidence_score=overall_confidence
        )
        
        log_event(f"[STAT_EXTRACTOR] Created profile for {character_name} with {len(all_stats)} stats")
        return profile
    
    def validate_stat_data(self, profile: CharacterProfile) -> Dict[str, Any]:
        """
        Validate extracted stat data for consistency.
        
        Parameters
        ----------
        profile : CharacterProfile
            Character profile to validate
            
        Returns
        -------
        Dict[str, Any]
            Validation results
        """
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "confidence_score": profile.confidence_score
        }
        
        # Check for required stats
        required_stats = [StatType.HEALTH, StatType.ACTION, StatType.MIND]
        for stat_type in required_stats:
            if stat_type not in profile.stats:
                validation_results["warnings"].append(f"Missing required stat: {stat_type.value}")
                validation_results["valid"] = False
        
        # Check for reasonable stat values
        for stat_type, stat in profile.stats.items():
            if stat.current_value < 0:
                validation_results["errors"].append(f"Invalid {stat_type.value}: negative value")
                validation_results["valid"] = False
            
            if stat.max_value > 0 and stat.current_value > stat.max_value:
                validation_results["warnings"].append(f"Current {stat_type.value} exceeds maximum")
        
        # Check confidence thresholds
        if profile.confidence_score < 50.0:
            validation_results["warnings"].append("Low confidence score - data may be unreliable")
        
        return validation_results
    
    def save_character_profile(self, profile: CharacterProfile, file_path: str = None) -> bool:
        """
        Save character profile to file.
        
        Parameters
        ----------
        profile : CharacterProfile
            Character profile to save
        file_path : str, optional
            Custom file path, defaults to data/character_stats/{name}.json
            
        Returns
        -------
        bool
            True if saved successfully
        """
        try:
            if not file_path:
                # Ensure directory exists
                stats_dir = Path("data/character_stats")
                stats_dir.mkdir(parents=True, exist_ok=True)
                file_path = stats_dir / f"{profile.character_name}.json"
            
            # Convert profile to dictionary
            profile_data = {
                "character_name": profile.character_name,
                "profession": profile.profession,
                "level": profile.level,
                "scan_timestamp": profile.scan_timestamp,
                "scan_method": profile.scan_method,
                "confidence_score": profile.confidence_score,
                "stats": {},
                "resistances": profile.resistances,
                "tapes": profile.tapes
            }
            
            # Convert stats to dictionary format
            for stat_type, stat in profile.stats.items():
                profile_data["stats"][stat_type.value] = {
                    "current_value": stat.current_value,
                    "max_value": stat.max_value,
                    "percentage": stat.percentage,
                    "confidence": stat.confidence,
                    "source": stat.source,
                    "timestamp": stat.timestamp
                }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            log_event(f"[STAT_EXTRACTOR] Saved character profile: {file_path}")
            return True
            
        except Exception as e:
            log_event(f"[STAT_EXTRACTOR] Error saving character profile: {e}")
            return False
    
    def load_character_profile(self, character_name: str) -> Optional[CharacterProfile]:
        """
        Load character profile from file.
        
        Parameters
        ----------
        character_name : str
            Name of the character
            
        Returns
        -------
        CharacterProfile or None
            Loaded character profile
        """
        try:
            file_path = Path("data/character_stats") / f"{character_name}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                profile_data = json.load(f)
            
            # Reconstruct stats
            stats = {}
            for stat_name, stat_data in profile_data.get("stats", {}).items():
                stat_type = StatType(stat_name)
                stat = CharacterStat(
                    stat_type=stat_type,
                    current_value=stat_data["current_value"],
                    max_value=stat_data["max_value"],
                    percentage=stat_data["percentage"],
                    confidence=stat_data["confidence"],
                    source=stat_data["source"],
                    timestamp=stat_data["timestamp"]
                )
                stats[stat_type] = stat
            
            # Create profile
            profile = CharacterProfile(
                character_name=profile_data["character_name"],
                profession=profile_data["profession"],
                level=profile_data["level"],
                stats=stats,
                armor_stats={},
                resistances=profile_data.get("resistances", {}),
                tapes=profile_data.get("tapes", {}),
                scan_timestamp=profile_data["scan_timestamp"],
                scan_method=profile_data["scan_method"],
                confidence_score=profile_data["confidence_score"]
            )
            
            log_event(f"[STAT_EXTRACTOR] Loaded character profile: {character_name}")
            return profile
            
        except Exception as e:
            log_event(f"[STAT_EXTRACTOR] Error loading character profile: {e}")
            return None


def get_stat_extractor() -> StatExtractor:
    """Get a stat extractor instance."""
    return StatExtractor()


def extract_character_stats(character_name: str, profession: str = "", level: int = 0) -> Optional[CharacterProfile]:
    """Extract character stats and create profile."""
    extractor = get_stat_extractor()
    return extractor.create_character_profile(character_name, profession, level)


def save_character_stats(profile: CharacterProfile) -> bool:
    """Save character stats to file."""
    extractor = get_stat_extractor()
    return extractor.save_character_profile(profile)


def load_character_stats(character_name: str) -> Optional[CharacterProfile]:
    """Load character stats from file."""
    extractor = get_stat_extractor()
    return extractor.load_character_profile(character_name)


if __name__ == "__main__":
    # Test the stat extractor
    extractor = get_stat_extractor()
    
    # Test with sample character
    profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)
    
    print(f"Character: {profile.character_name}")
    print(f"Profession: {profile.profession}")
    print(f"Level: {profile.level}")
    print(f"Stats found: {len(profile.stats)}")
    print(f"Confidence: {profile.confidence_score:.1f}%")
    
    # Save profile
    extractor.save_character_profile(profile)
    
    # Load profile
    loaded_profile = extractor.load_character_profile("TestCharacter")
    if loaded_profile:
        print(f"Loaded profile for: {loaded_profile.character_name}") 