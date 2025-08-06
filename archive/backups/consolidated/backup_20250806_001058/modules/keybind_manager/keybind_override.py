"""
MS11 Batch 066 - Keybind Override System

Provides editable override functionality via CLI/JSON for keybind configurations.
Allows users to manually specify keybinds when automatic detection fails.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from .keybind_parser import Keybind, KeybindCategory


@dataclass
class KeybindOverride:
    """Represents a manual keybind override."""
    name: str
    key: str
    category: str
    description: str
    required: bool = False
    source: str = "manual_override"


class KeybindOverrideManager:
    """Manages manual keybind overrides."""
    
    def __init__(self, override_file: str = "data/keybind_overrides.json"):
        """Initialize the override manager.
        
        Args:
            override_file: Path to override configuration file
        """
        self.override_file = override_file
        self.overrides: Dict[str, KeybindOverride] = {}
        self._load_overrides()
    
    def _load_overrides(self) -> None:
        """Load overrides from file."""
        try:
            if os.path.exists(self.override_file):
                with open(self.override_file, 'r') as f:
                    data = json.load(f)
                
                for name, override_data in data.items():
                    self.overrides[name] = KeybindOverride(
                        name=name,
                        key=override_data.get('key', ''),
                        category=override_data.get('category', 'other'),
                        description=override_data.get('description', ''),
                        required=override_data.get('required', False),
                        source='manual_override'
                    )
        except Exception as e:
            print(f"Warning: Could not load overrides from {self.override_file}: {e}")
    
    def save_overrides(self) -> None:
        """Save overrides to file."""
        try:
            os.makedirs(os.path.dirname(self.override_file), exist_ok=True)
            
            data = {}
            for name, override in self.overrides.items():
                data[name] = asdict(override)
                # Remove source from saved data
                del data[name]['source']
            
            with open(self.override_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving overrides to {self.override_file}: {e}")
    
    def add_override(self, name: str, key: str, category: str = "other", 
                    description: str = "", required: bool = False) -> bool:
        """Add a manual override.
        
        Args:
            name: Keybind name
            key: Key to bind
            category: Keybind category
            description: Description of the keybind
            required: Whether this keybind is required
            
        Returns:
            True if override was added successfully
        """
        try:
            override = KeybindOverride(
                name=name,
                key=key.upper(),
                category=category,
                description=description,
                required=required
            )
            
            self.overrides[name] = override
            self.save_overrides()
            return True
            
        except Exception as e:
            print(f"Error adding override: {e}")
            return False
    
    def remove_override(self, name: str) -> bool:
        """Remove a manual override.
        
        Args:
            name: Keybind name to remove
            
        Returns:
            True if override was removed successfully
        """
        if name in self.overrides:
            del self.overrides[name]
            self.save_overrides()
            return True
        return False
    
    def get_override(self, name: str) -> Optional[KeybindOverride]:
        """Get a specific override.
        
        Args:
            name: Keybind name
            
        Returns:
            KeybindOverride if found, None otherwise
        """
        return self.overrides.get(name)
    
    def list_overrides(self) -> List[KeybindOverride]:
        """List all overrides.
        
        Returns:
            List of all KeybindOverride objects
        """
        return list(self.overrides.values())
    
    def apply_overrides_to_keybinds(self, keybinds: Dict[str, Keybind]) -> Dict[str, Keybind]:
        """Apply manual overrides to detected keybinds.
        
        Args:
            keybinds: Dictionary of detected keybinds
            
        Returns:
            Updated keybinds dictionary with overrides applied
        """
        updated_keybinds = keybinds.copy()
        
        for name, override in self.overrides.items():
            if name in updated_keybinds:
                # Update existing keybind
                keybind = updated_keybinds[name]
                keybind.key = override.key
                keybind.description = override.description
            else:
                # Create new keybind from override
                category_enum = self._get_category_enum(override.category)
                keybind = Keybind(
                    name=override.name,
                    key=override.key,
                    category=category_enum,
                    description=override.description,
                    required=override.required
                )
                updated_keybinds[name] = keybind
        
        return updated_keybinds
    
    def _get_category_enum(self, category_str: str) -> KeybindCategory:
        """Convert category string to enum."""
        category_map = {
            'combat': KeybindCategory.COMBAT,
            'healing': KeybindCategory.HEALING,
            'navigation': KeybindCategory.NAVIGATION,
            'inventory': KeybindCategory.INVENTORY,
            'movement': KeybindCategory.MOVEMENT,
            'chat': KeybindCategory.CHAT,
            'camera': KeybindCategory.CAMERA,
            'utility': KeybindCategory.UTILITY,
            'other': KeybindCategory.OTHER
        }
        return category_map.get(category_str.lower(), KeybindCategory.OTHER)
    
    def create_template(self) -> Dict[str, Dict]:
        """Create a template for manual overrides.
        
        Returns:
            Dictionary template for manual overrides
        """
        template = {
            "attack": {
                "key": "F1",
                "category": "combat",
                "description": "Attack/Combat action",
                "required": True
            },
            "use": {
                "key": "Enter",
                "category": "utility",
                "description": "Use/Interact with objects",
                "required": True
            },
            "inventory": {
                "key": "I",
                "category": "inventory",
                "description": "Open inventory",
                "required": True
            },
            "map": {
                "key": "M",
                "category": "navigation",
                "description": "Open map",
                "required": True
            },
            "chat": {
                "key": "Enter",
                "category": "chat",
                "description": "Open chat window",
                "required": True
            },
            "target": {
                "key": "Tab",
                "category": "combat",
                "description": "Target selection",
                "required": True
            },
            "heal": {
                "key": "H",
                "category": "healing",
                "description": "Heal action",
                "required": False
            },
            "follow": {
                "key": "F",
                "category": "movement",
                "description": "Follow target",
                "required": False
            },
            "stop": {
                "key": "Escape",
                "category": "movement",
                "description": "Stop current action",
                "required": False
            },
            "loot": {
                "key": "L",
                "category": "utility",
                "description": "Loot corpses",
                "required": False
            }
        }
        
        return template
    
    def save_template(self, filepath: str) -> bool:
        """Save override template to file.
        
        Args:
            filepath: Path to save template
            
        Returns:
            True if template was saved successfully
        """
        try:
            template = self.create_template()
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(template, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving template to {filepath}: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """Load overrides from a file.
        
        Args:
            filepath: Path to override file
            
        Returns:
            True if overrides were loaded successfully
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Clear existing overrides
            self.overrides.clear()
            
            # Load new overrides
            for name, override_data in data.items():
                self.overrides[name] = KeybindOverride(
                    name=name,
                    key=override_data.get('key', ''),
                    category=override_data.get('category', 'other'),
                    description=override_data.get('description', ''),
                    required=override_data.get('required', False)
                )
            
            self.save_overrides()
            return True
            
        except Exception as e:
            print(f"Error loading overrides from {filepath}: {e}")
            return False 