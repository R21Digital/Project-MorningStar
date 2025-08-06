"""Shortcut Helper for providing macro shortcuts and organization features.

This module provides intelligent shortcut suggestions, macro organization,
and quick access to commonly used macros and aliases.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

@dataclass
class Shortcut:
    """Data class for representing a shortcut."""
    name: str
    command: str
    category: str
    hotkey: Optional[str] = None
    description: str = ""
    usage_count: int = 0
    last_used: Optional[datetime] = None
    is_favorite: bool = False

@dataclass
class ShortcutCategory:
    """Data class for shortcut categories."""
    name: str
    shortcuts: List[Shortcut]
    total_usage: int
    most_used: Optional[Shortcut] = None

@dataclass
class ShortcutAnalysis:
    """Data class for shortcut analysis results."""
    total_shortcuts: int
    categories: Dict[str, ShortcutCategory]
    most_used_shortcuts: List[Tuple[str, int]]
    unused_shortcuts: List[str]
    favorite_shortcuts: List[str]
    suggestions: List[str]

class ShortcutHelper:
    """Helper for managing shortcuts and quick access to macros."""
    
    def __init__(self, shortcuts_file: str = "data/shortcuts.json", create_defaults: bool = True):
        """Initialize the shortcut helper.
        
        Parameters
        ----------
        shortcuts_file : str
            Path to shortcuts configuration file
        create_defaults : bool
            Whether to create default shortcuts if file doesn't exist
        """
        self.shortcuts_file = shortcuts_file
        self.shortcuts = {}
        self.categories = defaultdict(list)
        self.favorites = set()
        self.usage_stats = defaultdict(int)
        self.create_defaults = create_defaults
        
        # Common shortcut categories
        self.category_definitions = {
            "combat": {
                "description": "Combat-related shortcuts",
                "color": "red",
                "icon": "⚔️"
            },
            "travel": {
                "description": "Travel and movement shortcuts",
                "color": "blue", 
                "icon": "🚀"
            },
            "crafting": {
                "description": "Crafting and resource shortcuts",
                "color": "green",
                "icon": "🛠️"
            },
            "social": {
                "description": "Social interaction shortcuts",
                "color": "yellow",
                "icon": "💬"
            },
            "utility": {
                "description": "Utility and system shortcuts",
                "color": "gray",
                "icon": "🔧"
            },
            "profession": {
                "description": "Profession-specific shortcuts",
                "color": "purple",
                "icon": "🎯"
            }
        }
        
        # Load shortcuts
        self._load_shortcuts()
        
        log_event(f"[SHORTCUT_HELPER] Initialized with {len(self.shortcuts)} shortcuts")
    
    def _load_shortcuts(self) -> None:
        """Load shortcuts from configuration file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.shortcuts_file), exist_ok=True)
            
            if os.path.exists(self.shortcuts_file):
                with open(self.shortcuts_file, 'r') as f:
                    data = json.load(f)
                    
                # Load shortcuts
                for shortcut_data in data.get("shortcuts", []):
                    shortcut = Shortcut(**shortcut_data)
                    self.shortcuts[shortcut.name] = shortcut
                    self.categories[shortcut.category].append(shortcut)
                    
                    if shortcut.is_favorite:
                        self.favorites.add(shortcut.name)
                    
                    self.usage_stats[shortcut.name] = shortcut.usage_count
                    
            else:
                # Create default shortcuts only if enabled
                if self.create_defaults:
                    self._create_default_shortcuts()
                    self._save_shortcuts()
                
        except Exception as e:
            log_event(f"[SHORTCUT_HELPER] Error loading shortcuts: {e}")
            if self.create_defaults:
                self._create_default_shortcuts()
    
    def _create_default_shortcuts(self) -> None:
        """Create default shortcuts."""
        default_shortcuts = [
            Shortcut("heal", "/heal {target}", "combat", "F1", "Heal target", 0),
            Shortcut("buff", "/buff {target}", "combat", "F2", "Buff target", 0),
            Shortcut("attack", "/attack {target}", "combat", "F3", "Attack target", 0),
            Shortcut("defend", "/defend", "combat", "F4", "Defend", 0),
            Shortcut("flee", "/flee", "combat", "F5", "Flee from combat", 0),
            Shortcut("travel", "/travel {destination}", "travel", "F6", "Travel to destination", 0),
            Shortcut("follow", "/follow {target}", "travel", "F7", "Follow target", 0),
            Shortcut("craft", "/craft {item}", "crafting", "F8", "Craft item", 0),
            Shortcut("loot", "/loot", "utility", "F9", "Loot items", 0),
            Shortcut("status", "/status", "utility", "F10", "Show status", 0),
            Shortcut("say", "/say {message}", "social", "F11", "Say message", 0),
            Shortcut("tell", "/tell {player} {message}", "social", "F12", "Tell player", 0)
        ]
        
        for shortcut in default_shortcuts:
            self.shortcuts[shortcut.name] = shortcut
            self.categories[shortcut.category].append(shortcut)
    
    def _save_shortcuts(self) -> None:
        """Save shortcuts to configuration file."""
        try:
            shortcuts_data = {
                "shortcuts": [asdict(shortcut) for shortcut in self.shortcuts.values()],
                "categories": dict(self.categories),
                "favorites": list(self.favorites),
                "usage_stats": dict(self.usage_stats),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.shortcuts_file, 'w') as f:
                json.dump(shortcuts_data, f, indent=2, default=str)
            
            log_event(f"[SHORTCUT_HELPER] Saved shortcuts to {self.shortcuts_file}")
        except Exception as e:
            log_event(f"[SHORTCUT_HELPER] Error saving shortcuts: {e}")
    
    def add_shortcut(self, name: str, command: str, category: str = "utility",
                     hotkey: str = None, description: str = "") -> bool:
        """Add a new shortcut.
        
        Parameters
        ----------
        name : str
            Shortcut name
        command : str
            Command to execute
        category : str
            Category for the shortcut
        hotkey : str, optional
            Hotkey binding
        description : str
            Description of the shortcut
            
        Returns
        -------
        bool
            True if added successfully
        """
        if name in self.shortcuts:
            log_event(f"[SHORTCUT_HELPER] Shortcut '{name}' already exists")
            return False
        
        shortcut = Shortcut(
            name=name,
            command=command,
            category=category,
            hotkey=hotkey,
            description=description
        )
        
        self.shortcuts[name] = shortcut
        self.categories[category].append(shortcut)
        self._save_shortcuts()
        
        log_event(f"[SHORTCUT_HELPER] Added shortcut: {name}")
        return True
    
    def remove_shortcut(self, name: str) -> bool:
        """Remove a shortcut.
        
        Parameters
        ----------
        name : str
            Name of shortcut to remove
            
        Returns
        -------
        bool
            True if removed successfully
        """
        if name not in self.shortcuts:
            return False
        
        shortcut = self.shortcuts[name]
        self.categories[shortcut.category].remove(shortcut)
        del self.shortcuts[name]
        
        if name in self.favorites:
            self.favorites.remove(name)
        
        if name in self.usage_stats:
            del self.usage_stats[name]
        
        self._save_shortcuts()
        
        log_event(f"[SHORTCUT_HELPER] Removed shortcut: {name}")
        return True
    
    def update_shortcut_usage(self, name: str) -> None:
        """Update usage statistics for a shortcut.
        
        Parameters
        ----------
        name : str
            Name of the shortcut
        """
        if name in self.shortcuts:
            shortcut = self.shortcuts[name]
            shortcut.usage_count += 1
            shortcut.last_used = datetime.now()
            self.usage_stats[name] = shortcut.usage_count
            
            log_event(f"[SHORTCUT_HELPER] Updated usage for shortcut: {name}")
    
    def toggle_favorite(self, name: str) -> bool:
        """Toggle favorite status for a shortcut.
        
        Parameters
        ----------
        name : str
            Name of the shortcut
            
        Returns
        -------
        bool
            New favorite status
        """
        if name not in self.shortcuts:
            return False
        
        shortcut = self.shortcuts[name]
        shortcut.is_favorite = not shortcut.is_favorite
        
        if shortcut.is_favorite:
            self.favorites.add(name)
        else:
            self.favorites.discard(name)
        
        self._save_shortcuts()
        
        log_event(f"[SHORTCUT_HELPER] Toggled favorite for shortcut: {name}")
        return shortcut.is_favorite
    
    def get_shortcuts_by_category(self, category: str) -> List[Shortcut]:
        """Get shortcuts for a specific category.
        
        Parameters
        ----------
        category : str
            Category name
            
        Returns
        -------
        list
            List of shortcuts in the category
        """
        return self.categories.get(category, [])
    
    def get_favorite_shortcuts(self) -> List[Shortcut]:
        """Get favorite shortcuts.
        
        Returns
        -------
        list
            List of favorite shortcuts
        """
        return [self.shortcuts[name] for name in self.favorites if name in self.shortcuts]
    
    def get_most_used_shortcuts(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most used shortcuts.
        
        Parameters
        ----------
        limit : int
            Maximum number of shortcuts to return
            
        Returns
        -------
        list
            List of (shortcut_name, usage_count) tuples
        """
        sorted_usage = sorted(
            self.usage_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_usage[:limit]
    
    def get_unused_shortcuts(self) -> List[str]:
        """Get shortcuts that have never been used.
        
        Returns
        -------
        list
            List of unused shortcut names
        """
        return [name for name, count in self.usage_stats.items() if count == 0]
    
    def search_shortcuts(self, query: str) -> List[Shortcut]:
        """Search shortcuts by name, description, or command.
        
        Parameters
        ----------
        query : str
            Search query
            
        Returns
        -------
        list
            List of matching shortcuts
        """
        query_lower = query.lower()
        matches = []
        
        for shortcut in self.shortcuts.values():
            if (query_lower in shortcut.name.lower() or
                query_lower in shortcut.description.lower() or
                query_lower in shortcut.command.lower()):
                matches.append(shortcut)
        
        return matches
    
    def get_shortcut_suggestions(self, context: str = None) -> List[str]:
        """Get shortcut suggestions based on context.
        
        Parameters
        ----------
        context : str, optional
            Context for suggestions
            
        Returns
        -------
        list
            List of suggested shortcut names
        """
        suggestions = []
        
        if context:
            context_lower = context.lower()
            
            # Suggest based on context
            if "combat" in context_lower or "fight" in context_lower:
                suggestions.extend(["heal", "buff", "attack", "defend", "flee"])
            elif "travel" in context_lower or "move" in context_lower:
                suggestions.extend(["travel", "follow", "goto"])
            elif "craft" in context_lower or "build" in context_lower:
                suggestions.extend(["craft", "harvest", "survey"])
            elif "social" in context_lower or "chat" in context_lower:
                suggestions.extend(["say", "tell", "group", "guild"])
            elif "utility" in context_lower or "system" in context_lower:
                suggestions.extend(["loot", "status", "inventory", "equipment"])
        
        # Add most used shortcuts
        most_used = self.get_most_used_shortcuts(5)
        suggestions.extend([name for name, _ in most_used])
        
        # Add favorites
        favorites = self.get_favorite_shortcuts()
        suggestions.extend([s.name for s in favorites])
        
        # Remove duplicates and limit
        return list(dict.fromkeys(suggestions))[:10]
    
    def generate_shortcut_report(self) -> ShortcutAnalysis:
        """Generate comprehensive shortcut analysis.
        
        Returns
        -------
        ShortcutAnalysis
            Complete analysis results
        """
        # Build category analysis
        category_analysis = {}
        for category_name, shortcuts in self.categories.items():
            total_usage = sum(s.usage_count for s in shortcuts)
            most_used = max(shortcuts, key=lambda s: s.usage_count) if shortcuts else None
            
            category_analysis[category_name] = ShortcutCategory(
                name=category_name,
                shortcuts=shortcuts,
                total_usage=total_usage,
                most_used=most_used
            )
        
        # Get most used shortcuts
        most_used_shortcuts = self.get_most_used_shortcuts(10)
        
        # Get unused shortcuts
        unused_shortcuts = self.get_unused_shortcuts()
        
        # Get favorite shortcuts
        favorite_shortcuts = list(self.favorites)
        
        # Generate suggestions
        suggestions = []
        
        if unused_shortcuts:
            suggestions.append(f"Found {len(unused_shortcuts)} unused shortcuts")
        
        if len(self.favorites) < 5:
            suggestions.append("Consider adding more favorites for quick access")
        
        # Check for missing categories
        missing_categories = set(self.category_definitions.keys()) - set(self.categories.keys())
        if missing_categories:
            suggestions.append(f"Missing categories: {', '.join(missing_categories)}")
        
        return ShortcutAnalysis(
            total_shortcuts=len(self.shortcuts),
            categories=category_analysis,
            most_used_shortcuts=most_used_shortcuts,
            unused_shortcuts=unused_shortcuts,
            favorite_shortcuts=favorite_shortcuts,
            suggestions=suggestions
        )
    
    def export_shortcuts(self, file_path: str = None) -> str:
        """Export shortcuts to a file.
        
        Parameters
        ----------
        file_path : str, optional
            Path to export file
            
        Returns
        -------
        str
            Path to exported file
        """
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"data/shortcuts_export_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        export_data = {
            "shortcuts": [asdict(shortcut) for shortcut in self.shortcuts.values()],
            "categories": {cat: [s.name for s in shortcuts] for cat, shortcuts in self.categories.items()},
            "favorites": list(self.favorites),
            "usage_stats": dict(self.usage_stats),
            "export_date": datetime.now().isoformat()
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        log_event(f"[SHORTCUT_HELPER] Exported shortcuts to {file_path}")
        return file_path
    
    def import_shortcuts(self, file_path: str) -> bool:
        """Import shortcuts from a file.
        
        Parameters
        ----------
        file_path : str
            Path to import file
            
        Returns
        -------
        bool
            True if imported successfully
        """
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            # Clear existing shortcuts
            self.shortcuts.clear()
            self.categories.clear()
            self.favorites.clear()
            self.usage_stats.clear()
            
            # Import shortcuts
            for shortcut_data in import_data.get("shortcuts", []):
                shortcut = Shortcut(**shortcut_data)
                self.shortcuts[shortcut.name] = shortcut
                self.categories[shortcut.category].append(shortcut)
                
                if shortcut.is_favorite:
                    self.favorites.add(shortcut.name)
                
                self.usage_stats[shortcut.name] = shortcut.usage_count
            
            self._save_shortcuts()
            
            log_event(f"[SHORTCUT_HELPER] Imported shortcuts from {file_path}")
            return True
            
        except Exception as e:
            log_event(f"[SHORTCUT_HELPER] Error importing shortcuts: {e}")
            return False 