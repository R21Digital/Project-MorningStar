"""
MS11 Batch 066 - Keybind Parser

Handles parsing of SWG configuration files (options.cfg, inputmap.cfg)
and extracting keybind information for validation.
"""

import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set
from pathlib import Path


class KeybindCategory(Enum):
    """Categories for different types of keybinds."""
    COMBAT = "combat"
    HEALING = "healing"
    NAVIGATION = "navigation"
    INVENTORY = "inventory"
    MOVEMENT = "movement"
    CHAT = "chat"
    CAMERA = "camera"
    UTILITY = "utility"
    OTHER = "other"


class KeybindStatus(Enum):
    """Status of keybind validation."""
    VALID = "valid"
    MISSING = "missing"
    CONFLICT = "conflict"
    UNKNOWN = "unknown"


@dataclass
class Keybind:
    """Represents a single keybind configuration."""
    name: str
    key: str
    category: KeybindCategory
    description: str
    required: bool = False
    status: KeybindStatus = KeybindStatus.UNKNOWN
    suggestion: Optional[str] = None
    file_source: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class KeybindParseResult:
    """Result of parsing keybind configuration files."""
    keybinds: Dict[str, Keybind]
    config_files_found: List[str]
    parse_errors: List[str]
    swg_directory: str
    total_keybinds: int
    required_keybinds: Dict[str, Keybind]


class KeybindParser:
    """Parser for SWG keybind configuration files."""
    
    def __init__(self, swg_directory: Optional[str] = None):
        """Initialize the keybind parser.
        
        Args:
            swg_directory: Path to SWG installation directory
        """
        self.swg_directory = swg_directory or self._find_swg_directory()
        self.keybinds: Dict[str, Keybind] = {}
        self.required_keybinds = self._get_required_keybinds()
        self.parse_errors: List[str] = []
        
    def _find_swg_directory(self) -> str:
        """Attempt to find SWG installation directory."""
        # Common SWG installation paths
        possible_paths = [
            "C:\\Program Files (x86)\\Sony\\Star Wars Galaxies",
            "C:\\Program Files\\Sony\\Star Wars Galaxies", 
            "D:\\Star Wars Galaxies",
            "E:\\Star Wars Galaxies",
            os.path.expanduser("~/Star Wars Galaxies")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # Default to current directory if not found
        return os.getcwd()
    
    def _get_required_keybinds(self) -> Dict[str, Keybind]:
        """Define required keybinds for MS11 compatibility."""
        return {
            "attack": Keybind(
                name="attack",
                key="",
                category=KeybindCategory.COMBAT,
                description="Attack/Combat action",
                required=True,
                suggestion="F1"
            ),
            "use": Keybind(
                name="use", 
                key="",
                category=KeybindCategory.UTILITY,
                description="Use/Interact with objects",
                required=True,
                suggestion="Enter"
            ),
            "inventory": Keybind(
                name="inventory",
                key="",
                category=KeybindCategory.INVENTORY,
                description="Open inventory",
                required=True,
                suggestion="I"
            ),
            "map": Keybind(
                name="map",
                key="",
                category=KeybindCategory.NAVIGATION,
                description="Open map",
                required=True,
                suggestion="M"
            ),
            "chat": Keybind(
                name="chat",
                key="",
                category=KeybindCategory.CHAT,
                description="Open chat window",
                required=True,
                suggestion="Enter"
            ),
            "target": Keybind(
                name="target",
                key="",
                category=KeybindCategory.COMBAT,
                description="Target selection",
                required=True,
                suggestion="Tab"
            ),
            "heal": Keybind(
                name="heal",
                key="",
                category=KeybindCategory.HEALING,
                description="Heal action",
                required=False,
                suggestion="H"
            ),
            "follow": Keybind(
                name="follow",
                key="",
                category=KeybindCategory.MOVEMENT,
                description="Follow target",
                required=False,
                suggestion="F"
            ),
            "stop": Keybind(
                name="stop",
                key="",
                category=KeybindCategory.MOVEMENT,
                description="Stop current action",
                required=False,
                suggestion="Escape"
            ),
            "loot": Keybind(
                name="loot",
                key="",
                category=KeybindCategory.UTILITY,
                description="Loot corpses",
                required=False,
                suggestion="L"
            )
        }
    
    def parse_config_files(self) -> KeybindParseResult:
        """Parse all SWG configuration files for keybinds."""
        config_files = self._find_config_files()
        self.keybinds.clear()
        self.parse_errors.clear()
        
        for filepath in config_files:
            self._parse_config_file(filepath)
        
        return KeybindParseResult(
            keybinds=self.keybinds,
            config_files_found=config_files,
            parse_errors=self.parse_errors,
            swg_directory=self.swg_directory,
            total_keybinds=len(self.keybinds),
            required_keybinds=self.required_keybinds
        )
    
    def _find_config_files(self) -> List[str]:
        """Find SWG configuration files."""
        config_files = []
        
        # Look for options.cfg and inputmap.cfg
        possible_files = [
            os.path.join(self.swg_directory, "options.cfg"),
            os.path.join(self.swg_directory, "inputmap.cfg"),
            os.path.join(self.swg_directory, "user.cfg"),
            os.path.join(self.swg_directory, "swg.cfg")
        ]
        
        for filepath in possible_files:
            if os.path.exists(filepath):
                config_files.append(filepath)
        
        return config_files
    
    def _parse_config_file(self, filepath: str) -> None:
        """Parse a single configuration file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                self._parse_keybind_line(line.strip(), filepath, line_num)
                
        except Exception as e:
            self.parse_errors.append(f"Error parsing {filepath}: {e}")
    
    def _parse_keybind_line(self, line: str, filepath: str, line_number: int) -> None:
        """Parse a single line for keybind information."""
        if not line or line.startswith('#'):
            return
        
        # Try different keybind line formats
        patterns = [
            r'Keybind\s+(\w+)\s+(\S+)',  # Keybind attack F1
            r'input\s+(\w+)\s+(\S+)',    # input map M
            r'(\w+)\s*=\s*(\S+)',        # attack=F1
            r'(\w+)\s+(\S+)',            # attack F1
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                name = match.group(1).lower()
                key = match.group(2).upper()
                
                # Map common variations
                mapped_name = self._map_keybind_name(name)
                if mapped_name:
                    self._add_detected_keybind(mapped_name, key, filepath, line_number)
                break
    
    def _map_keybind_name(self, name: str) -> Optional[str]:
        """Map detected keybind names to standard names."""
        name_mappings = {
            # Combat variations
            'combat': 'attack',
            'fight': 'attack',
            'hit': 'attack',
            'strike': 'attack',
            
            # Interaction variations
            'interact': 'use',
            'action': 'use',
            'activate': 'use',
            
            # Inventory variations
            'inv': 'inventory',
            'bag': 'inventory',
            'items': 'inventory',
            
            # Navigation variations
            'worldmap': 'map',
            'world_map': 'map',
            'navigator': 'map',
            
            # Movement variations
            'halt': 'stop',
            'cancel': 'stop',
            'abort': 'stop',
            
            # Healing variations
            'cure': 'heal',
            'medic': 'heal',
            'healing': 'heal',
            
            # Utility variations
            'corpse': 'loot',
            'harvest': 'loot',
            'collect': 'loot'
        }
        
        return name_mappings.get(name, name)
    
    def _add_detected_keybind(self, name: str, key: str, filepath: str, line_number: int) -> None:
        """Add a detected keybind to the collection."""
        if name in self.required_keybinds:
            # Update the required keybind with detected key
            keybind = self.required_keybinds[name]
            keybind.key = key
            keybind.file_source = filepath
            keybind.line_number = line_number
            self.keybinds[name] = keybind
        else:
            # Create new keybind for non-required actions
            category = self._categorize_keybind(name)
            keybind = Keybind(
                name=name,
                key=key,
                category=category,
                description=f"Custom keybind: {name}",
                file_source=filepath,
                line_number=line_number
            )
            self.keybinds[name] = keybind
    
    def _categorize_keybind(self, name: str) -> KeybindCategory:
        """Categorize a keybind based on its name."""
        category_patterns = {
            KeybindCategory.COMBAT: ['attack', 'defend', 'flee', 'combat'],
            KeybindCategory.HEALING: ['heal', 'cure', 'medic', 'healing'],
            KeybindCategory.NAVIGATION: ['map', 'waypoint', 'travel', 'goto'],
            KeybindCategory.INVENTORY: ['inventory', 'bag', 'items', 'equipment'],
            KeybindCategory.MOVEMENT: ['follow', 'stop', 'move', 'run'],
            KeybindCategory.CHAT: ['chat', 'say', 'tell', 'group'],
            KeybindCategory.CAMERA: ['camera', 'zoom', 'rotate', 'pan'],
            KeybindCategory.UTILITY: ['use', 'loot', 'harvest', 'craft']
        }
        
        for category, patterns in category_patterns.items():
            if any(pattern in name.lower() for pattern in patterns):
                return category
        
        return KeybindCategory.OTHER 