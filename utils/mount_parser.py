#!/usr/bin/env python3
"""
Mount Parser Utility

This module provides functionality to parse mount information from game output,
including /learn_mounts command results and OCR scanning of mount interfaces.
"""

import re
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from core.ocr import extract_text_from_screen
from core.screenshot import capture_screen
from utils.logging_utils import log_event


class MountSpeedTier(Enum):
    """Speed tiers for mounts."""
    SLOW = "slow"          # 5-8 speed units
    MEDIUM = "medium"      # 9-15 speed units
    FAST = "fast"          # 16-25 speed units
    VERY_FAST = "very_fast"  # 26+ speed units


@dataclass
class ParsedMount:
    """Parsed mount information."""
    name: str
    speed: float
    speed_tier: MountSpeedTier
    mount_type: str
    is_available: bool = True
    cooldown: float = 0.0
    summon_time: float = 2.0
    dismount_time: float = 1.0
    last_used: float = 0.0
    preferences: Dict[str, Any] = field(default_factory=dict)


class MountParser:
    """
    Parser for mount information from game output.
    
    Features:
    - Parse /learn_mounts command output
    - OCR scanning of mount interfaces
    - Speed tier classification
    - Mount availability detection
    - Preference-based ranking
    """
    
    def __init__(self):
        """Initialize the mount parser."""
        self.speed_tiers = {
            MountSpeedTier.SLOW: (5.0, 8.0),
            MountSpeedTier.MEDIUM: (9.0, 15.0),
            MountSpeedTier.FAST: (16.0, 25.0),
            MountSpeedTier.VERY_FAST: (26.0, 100.0)
        }
        
        # Known mount patterns for OCR detection
        self.mount_patterns = {
            "speeder": r"(speeder|landspeeder|swoop|jetpack)",
            "creature": r"(bantha|dewback|varactyl|rancor|tauntaun)",
            "vehicle": r"(landspeeder|speeder|swoop)",
            "flying": r"(jetpack|flying|hover)"
        }
        
        # Speed patterns for extraction
        self.speed_patterns = [
            r"speed[:\s]*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*speed",
            r"velocity[:\s]*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*velocity"
        ]
        
        # Mount name patterns
        self.mount_name_patterns = [
            r"([A-Za-z\s]+)\s+(?:Mount|Vehicle|Speeder)",
            r"([A-Za-z\s]+)\s+(?:Speed|Velocity)",
            r"([A-Za-z\s]+)\s+(?:Available|Ready)"
        ]
    
    def parse_learn_mounts_output(self, output: str) -> List[ParsedMount]:
        """
        Parse the output of /learn_mounts command.
        
        Parameters
        ----------
        output : str
            Raw output from /learn_mounts command
            
        Returns
        -------
        List[ParsedMount]
            List of parsed mount information
        """
        mounts = []
        
        # Split output into lines
        lines = output.strip().split('\n')
        
        for line in lines:
            mount = self._parse_mount_line(line)
            if mount:
                mounts.append(mount)
        
        log_event(f"[MOUNT_PARSER] Parsed {len(mounts)} mounts from /learn_mounts output")
        return mounts
    
    def _parse_mount_line(self, line: str) -> Optional[ParsedMount]:
        """Parse a single line of mount information."""
        line = line.strip()
        if not line:
            return None
        
        # Extract mount name
        mount_name = self._extract_mount_name(line)
        if not mount_name:
            return None
        
        # Extract speed
        speed = self._extract_speed(line)
        if speed is None:
            speed = self._get_default_speed(mount_name)
        
        # Determine speed tier
        speed_tier = self._classify_speed_tier(speed)
        
        # Determine mount type
        mount_type = self._classify_mount_type(mount_name)
        
        # Check availability
        is_available = self._check_availability(line)
        
        # Extract cooldown if present
        cooldown = self._extract_cooldown(line)
        
        return ParsedMount(
            name=mount_name,
            speed=speed,
            speed_tier=speed_tier,
            mount_type=mount_type,
            is_available=is_available,
            cooldown=cooldown
        )
    
    def _extract_mount_name(self, line: str) -> Optional[str]:
        """Extract mount name from line."""
        for pattern in self.mount_name_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up common prefixes/suffixes
                name = re.sub(r'^(a|an|the)\s+', '', name, flags=re.IGNORECASE)
                name = re.sub(r'\s+(mount|vehicle|speeder)$', '', name, flags=re.IGNORECASE)
                return name.title()
        
        # Fallback: look for capitalized words
        words = line.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Try to get a multi-word name
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    return f"{word} {words[i + 1]}"
                return word
        
        return None
    
    def _extract_speed(self, line: str) -> Optional[float]:
        """Extract speed value from line."""
        for pattern in self.speed_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _get_default_speed(self, mount_name: str) -> float:
        """Get default speed for mount based on name patterns."""
        mount_name_lower = mount_name.lower()
        
        # Very fast mounts
        if any(name in mount_name_lower for name in ["jetpack", "swoop", "landspeeder"]):
            return 25.0
        
        # Fast mounts
        if any(name in mount_name_lower for name in ["speeder", "bike", "hover"]):
            return 18.0
        
        # Medium mounts
        if any(name in mount_name_lower for name in ["dewback", "varactyl"]):
            return 12.0
        
        # Slow mounts
        if any(name in mount_name_lower for name in ["bantha", "rancor", "tauntaun"]):
            return 8.0
        
        # Default medium speed
        return 10.0
    
    def _classify_speed_tier(self, speed: float) -> MountSpeedTier:
        """Classify speed into tier."""
        for tier, (min_speed, max_speed) in self.speed_tiers.items():
            if min_speed <= speed <= max_speed:
                return tier
        
        # Default to medium if outside known ranges
        return MountSpeedTier.MEDIUM
    
    def _classify_mount_type(self, mount_name: str) -> str:
        """Classify mount type based on name."""
        mount_name_lower = mount_name.lower()
        
        for mount_type, pattern in self.mount_patterns.items():
            if re.search(pattern, mount_name_lower):
                return mount_type
        
        # Default classification based on name
        if any(word in mount_name_lower for word in ["speeder", "bike", "swoop"]):
            return "speeder"
        elif any(word in mount_name_lower for word in ["bantha", "dewback", "varactyl"]):
            return "creature"
        elif any(word in mount_name_lower for word in ["jetpack", "flying"]):
            return "flying"
        else:
            return "vehicle"
    
    def _check_availability(self, line: str) -> bool:
        """Check if mount is available based on line content."""
        line_lower = line.lower()
        
        # Check for unavailable indicators
        unavailable_indicators = [
            "unavailable", "not available", "cooldown", "disabled",
            "not ready", "in use", "busy", "locked"
        ]
        
        if any(indicator in line_lower for indicator in unavailable_indicators):
            return False
        
        # Check for available indicators
        available_indicators = [
            "available", "ready", "active", "summoned", "mounted"
        ]
        
        if any(indicator in line_lower for indicator in available_indicators):
            return True
        
        # Default to available if no clear indicators
        return True
    
    def _extract_cooldown(self, line: str) -> float:
        """Extract cooldown time from line."""
        cooldown_patterns = [
            r"cooldown[:\s]*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*seconds?\s*(?:cooldown|remaining)",
            r"(\d+(?:\.\d+)?)\s*sec\s*(?:cooldown|remaining)"
        ]
        
        for pattern in cooldown_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return 0.0
    
    def scan_mount_interface(self) -> List[ParsedMount]:
        """
        Scan mount interface using OCR.
        
        Returns
        -------
        List[ParsedMount]
            List of mounts detected via OCR
        """
        try:
            # Capture screen
            screen = capture_screen()
            
            # Extract text from screen
            screen_text = extract_text_from_screen(screen)
            if not screen_text:
                log_event("[MOUNT_PARSER] No text detected in screen capture")
                return []
            
            # Parse mounts from screen text
            mounts = self._parse_screen_text(screen_text)
            
            log_event(f"[MOUNT_PARSER] OCR detected {len(mounts)} mounts")
            return mounts
            
        except Exception as e:
            log_event(f"[MOUNT_PARSER] Error scanning mount interface: {e}")
            return []
    
    def _parse_screen_text(self, screen_text: str) -> List[ParsedMount]:
        """Parse mount information from screen text."""
        mounts = []
        
        # Split into lines and process each
        lines = screen_text.split('\n')
        
        for line in lines:
            mount = self._parse_mount_line(line)
            if mount:
                mounts.append(mount)
        
        return mounts
    
    def rank_mounts_by_speed(self, mounts: List[ParsedMount]) -> List[ParsedMount]:
        """
        Rank mounts by speed tier and speed value.
        
        Parameters
        ----------
        mounts : List[ParsedMount]
            List of mounts to rank
            
        Returns
        -------
        List[ParsedMount]
            Mounts ranked by speed (fastest first)
        """
        # Sort by speed tier first, then by actual speed
        def sort_key(mount):
            tier_order = {
                MountSpeedTier.VERY_FAST: 4,
                MountSpeedTier.FAST: 3,
                MountSpeedTier.MEDIUM: 2,
                MountSpeedTier.SLOW: 1
            }
            return (tier_order[mount.speed_tier], -mount.speed)
        
        ranked_mounts = sorted(mounts, key=sort_key, reverse=True)
        
        log_event(f"[MOUNT_PARSER] Ranked {len(ranked_mounts)} mounts by speed")
        return ranked_mounts
    
    def filter_mounts_by_preferences(self, mounts: List[ParsedMount], 
                                   preferences: Dict[str, Any]) -> List[ParsedMount]:
        """
        Filter mounts based on user preferences.
        
        Parameters
        ----------
        mounts : List[ParsedMount]
            List of mounts to filter
        preferences : Dict[str, Any]
            User mount preferences
            
        Returns
        -------
        List[ParsedMount]
            Filtered mounts based on preferences
        """
        filtered_mounts = []
        
        for mount in mounts:
            # Check if mount is banned
            if mount.name.lower() in [name.lower() for name in preferences.get('banned_mounts', [])]:
                continue
            
            # Check mount type preference
            preferred_type = preferences.get('preferred_mount_type', 'any')
            if preferred_type != 'any' and mount.mount_type != preferred_type:
                continue
            
            # Check availability
            if not mount.is_available:
                continue
            
            filtered_mounts.append(mount)
        
        log_event(f"[MOUNT_PARSER] Filtered to {len(filtered_mounts)} mounts based on preferences")
        return filtered_mounts
    
    def get_fastest_available_mount(self, mounts: List[ParsedMount]) -> Optional[ParsedMount]:
        """
        Get the fastest available mount.
        
        Parameters
        ----------
        mounts : List[ParsedMount]
            List of mounts to check
            
        Returns
        -------
        Optional[ParsedMount]
            Fastest available mount, or None if none available
        """
        available_mounts = [m for m in mounts if m.is_available]
        
        if not available_mounts:
            return None
        
        # Rank by speed and return fastest
        ranked_mounts = self.rank_mounts_by_speed(available_mounts)
        return ranked_mounts[0] if ranked_mounts else None
    
    def save_mount_data(self, mounts: List[ParsedMount], file_path: str = "data/parsed_mounts.json"):
        """Save parsed mount data to file."""
        try:
            mount_data = []
            for mount in mounts:
                mount_data.append({
                    "name": mount.name,
                    "speed": mount.speed,
                    "speed_tier": mount.speed_tier.value,
                    "mount_type": mount.mount_type,
                    "is_available": mount.is_available,
                    "cooldown": mount.cooldown,
                    "summon_time": mount.summon_time,
                    "dismount_time": mount.dismount_time,
                    "last_used": mount.last_used,
                    "preferences": mount.preferences
                })
            
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(mount_data, f, indent=2)
            
            log_event(f"[MOUNT_PARSER] Saved {len(mounts)} mounts to {file_path}")
            
        except Exception as e:
            log_event(f"[MOUNT_PARSER] Error saving mount data: {e}")
    
    def load_mount_data(self, file_path: str = "data/parsed_mounts.json") -> List[ParsedMount]:
        """Load parsed mount data from file."""
        try:
            if not Path(file_path).exists():
                return []
            
            with open(file_path, 'r') as f:
                mount_data = json.load(f)
            
            mounts = []
            for data in mount_data:
                mount = ParsedMount(
                    name=data["name"],
                    speed=data["speed"],
                    speed_tier=MountSpeedTier(data["speed_tier"]),
                    mount_type=data["mount_type"],
                    is_available=data["is_available"],
                    cooldown=data["cooldown"],
                    summon_time=data["summon_time"],
                    dismount_time=data["dismount_time"],
                    last_used=data["last_used"],
                    preferences=data["preferences"]
                )
                mounts.append(mount)
            
            log_event(f"[MOUNT_PARSER] Loaded {len(mounts)} mounts from {file_path}")
            return mounts
            
        except Exception as e:
            log_event(f"[MOUNT_PARSER] Error loading mount data: {e}")
            return []


def get_mount_parser() -> MountParser:
    """Get a mount parser instance."""
    return MountParser()


def parse_learn_mounts_output(output: str) -> List[ParsedMount]:
    """Parse /learn_mounts command output."""
    parser = get_mount_parser()
    return parser.parse_learn_mounts_output(output)


def scan_mount_interface() -> List[ParsedMount]:
    """Scan mount interface using OCR."""
    parser = get_mount_parser()
    return parser.scan_mount_interface()


def get_fastest_mount(mounts: List[ParsedMount]) -> Optional[ParsedMount]:
    """Get the fastest available mount."""
    parser = get_mount_parser()
    return parser.get_fastest_available_mount(mounts)


if __name__ == "__main__":
    # Test the mount parser
    parser = get_mount_parser()
    
    # Test with sample /learn_mounts output
    sample_output = """
    Available Mounts:
    Speeder Bike - Speed: 15.0 (Available)
    Landspeeder - Speed: 20.0 (Available)
    Bantha - Speed: 8.0 (Cooldown: 30 seconds)
    Dewback - Speed: 10.0 (Available)
    Swoop Bike - Speed: 25.0 (Not Available)
    Jetpack - Speed: 30.0 (Available)
    """
    
    mounts = parser.parse_learn_mounts_output(sample_output)
    print(f"Parsed {len(mounts)} mounts:")
    
    for mount in mounts:
        print(f"  {mount.name}: {mount.speed} speed ({mount.speed_tier.value}) - {mount.mount_type}")
    
    # Test ranking
    ranked_mounts = parser.rank_mounts_by_speed(mounts)
    print(f"\nRanked mounts (fastest first):")
    for mount in ranked_mounts:
        print(f"  {mount.name}: {mount.speed} speed")
    
    # Test fastest mount
    fastest = parser.get_fastest_available_mount(mounts)
    if fastest:
        print(f"\nFastest available mount: {fastest.name} ({fastest.speed} speed)")
    else:
        print("\nNo available mounts found") 