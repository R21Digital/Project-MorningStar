"""Macro Parser for reading and analyzing macro files and alias configurations.

This module handles parsing of macro files, alias configurations, and building
fallback maps for missing macros.
"""

import json
import logging
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict

from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

@dataclass
class Macro:
    """Data class for representing a macro."""
    name: str
    content: str
    file_path: str
    category: str = "general"
    priority: int = 1
    is_critical: bool = False
    last_modified: Optional[datetime] = None
    usage_count: int = 0
    dependencies: List[str] = None
    description: str = ""

@dataclass
class Alias:
    """Data class for representing an alias."""
    name: str
    command: str
    file_path: str
    category: str = "general"
    is_critical: bool = False
    last_used: Optional[datetime] = None
    usage_count: int = 0
    description: str = ""

@dataclass
class MacroAnalysis:
    """Data class for macro analysis results."""
    total_macros: int
    total_aliases: int
    critical_macros: List[str]
    critical_aliases: List[str]
    missing_macros: List[str]
    missing_aliases: List[str]
    macro_categories: Dict[str, int]
    alias_categories: Dict[str, int]
    most_used_macros: List[Tuple[str, int]]
    most_used_aliases: List[Tuple[str, int]]

class MacroParser:
    """Parser for macro files and alias configurations."""
    
    def __init__(self, swg_directory: str = None):
        """Initialize the macro parser.
        
        Parameters
        ----------
        swg_directory : str, optional
            Path to SWG installation directory
        """
        self.swg_directory = swg_directory or self._find_swg_directory()
        self.macros = {}
        self.aliases = {}
        self.macro_categories = defaultdict(list)
        self.alias_categories = defaultdict(list)
        
        # Common macro directories
        self.macro_dirs = [
            "macros",
            "macro",
            "ui/macros",
            "ui/macro"
        ]
        
        # Common alias files
        self.alias_files = [
            "alias.txt",
            "aliases.txt",
            "chat/alias.txt",
            "chat/aliases.txt"
        ]
        
        # Critical macros that should always be available
        self.critical_macros = {
            "heal": "Healing macro",
            "buff": "Buffing macro", 
            "travel": "Travel macro",
            "craft": "Crafting macro",
            "combat": "Combat macro",
            "loot": "Looting macro",
            "follow": "Follow macro",
            "attack": "Attack macro",
            "defend": "Defend macro",
            "flee": "Flee macro"
        }
        
        # Critical aliases
        self.critical_aliases = {
            "/heal": "Heal command",
            "/buff": "Buff command",
            "/travel": "Travel command",
            "/craft": "Craft command",
            "/loot": "Loot command",
            "/follow": "Follow command",
            "/attack": "Attack command",
            "/defend": "Defend command",
            "/flee": "Flee command"
        }
        
        # Macro categories for organization
        self.category_patterns = {
            "combat": ["attack", "defend", "flee", "heal", "buff", "debuff"],
            "crafting": ["craft", "harvest", "survey", "resource"],
            "travel": ["travel", "follow", "goto", "waypoint"],
            "social": ["say", "tell", "group", "guild", "trade"],
            "utility": ["loot", "inventory", "equipment", "status"],
            "profession": ["medic", "artisan", "scout", "marksman", "brawler"]
        }
        
        log_event(f"[MACRO_PARSER] Initialized with SWG directory: {self.swg_directory}")
    
    def _find_swg_directory(self) -> str:
        """Find SWG installation directory.
        
        Returns
        -------
        str
            Path to SWG directory
        """
        # Common SWG installation paths
        possible_paths = [
            "C:/Program Files (x86)/Sony/Star Wars Galaxies",
            "C:/Program Files/Sony/Star Wars Galaxies",
            "D:/Star Wars Galaxies",
            "E:/Star Wars Galaxies"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Default to current directory if not found
        return os.getcwd()
    
    def scan_macro_directories(self) -> Dict[str, List[str]]:
        """Scan for macro directories and files.
        
        Returns
        -------
        dict
            Dictionary of found macro directories and their files
        """
        found_dirs = {}
        
        for macro_dir in self.macro_dirs:
            full_path = os.path.join(self.swg_directory, macro_dir)
            if os.path.exists(full_path):
                files = []
                for file in os.listdir(full_path):
                    if file.endswith('.txt') or file.endswith('.macro'):
                        files.append(file)
                if files:
                    found_dirs[macro_dir] = files
        
        log_event(f"[MACRO_PARSER] Found macro directories: {list(found_dirs.keys())}")
        return found_dirs
    
    def parse_macro_file(self, file_path: str) -> List[Macro]:
        """Parse a macro file and extract macros.
        
        Parameters
        ----------
        file_path : str
            Path to macro file
            
        Returns
        -------
        list
            List of Macro objects
        """
        macros = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split by macro sections (usually separated by blank lines or headers)
            macro_sections = re.split(r'\n\s*\n', content)
            
            for section in macro_sections:
                if not section.strip():
                    continue
                
                lines = section.strip().split('\n')
                if not lines:
                    continue
                
                # Try to extract macro name from first line
                first_line = lines[0].strip()
                macro_name = self._extract_macro_name(first_line)
                
                if macro_name:
                    macro_content = '\n'.join(lines)
                    category = self._categorize_macro(macro_name, macro_content)
                    is_critical = macro_name.lower() in self.critical_macros
                    
                    macro = Macro(
                        name=macro_name,
                        content=macro_content,
                        file_path=file_path,
                        category=category,
                        is_critical=is_critical,
                        last_modified=datetime.fromtimestamp(os.path.getmtime(file_path))
                    )
                    
                    macros.append(macro)
                    
        except Exception as e:
            log_event(f"[MACRO_PARSER] Error parsing macro file {file_path}: {e}")
        
        return macros
    
    def _extract_macro_name(self, line: str) -> Optional[str]:
        """Extract macro name from a line.
        
        Parameters
        ----------
        line : str
            Line to extract name from
            
        Returns
        -------
        str or None
            Extracted macro name
        """
        # Common patterns for macro names
        patterns = [
            r'^(\w+)\s*[:=]',  # name: or name=
            r'^macro\s+(\w+)',  # macro name
            r'^(\w+)\s*$',      # just name
            r'^#\s*(\w+)',      # #name
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        
        return None
    
    def _categorize_macro(self, name: str, content: str) -> str:
        """Categorize a macro based on name and content.
        
        Parameters
        ----------
        name : str
            Macro name
        content : str
            Macro content
            
        Returns
        -------
        str
            Category name
        """
        name_lower = name.lower()
        content_lower = content.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in name_lower or pattern in content_lower:
                    return category
        
        return "general"
    
    def parse_alias_file(self, file_path: str) -> List[Alias]:
        """Parse an alias file and extract aliases.
        
        Parameters
        ----------
        file_path : str
            Path to alias file
            
        Returns
        -------
        list
            List of Alias objects
        """
        aliases = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse alias line (format: alias_name command)
                    parts = line.split(None, 1)
                    if len(parts) >= 2:
                        alias_name = parts[0]
                        command = parts[1]
                        
                        category = self._categorize_alias(alias_name, command)
                        is_critical = alias_name.lower() in self.critical_aliases
                        
                        alias = Alias(
                            name=alias_name,
                            command=command,
                            file_path=file_path,
                            category=category,
                            is_critical=is_critical
                        )
                        
                        aliases.append(alias)
                        
        except Exception as e:
            log_event(f"[MACRO_PARSER] Error parsing alias file {file_path}: {e}")
        
        return aliases
    
    def _categorize_alias(self, name: str, command: str) -> str:
        """Categorize an alias based on name and command.
        
        Parameters
        ----------
        name : str
            Alias name
        command : str
            Alias command
            
        Returns
        -------
        str
            Category name
        """
        name_lower = name.lower()
        command_lower = command.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in name_lower or pattern in command_lower:
                    return category
        
        return "general"
    
    def load_all_macros(self) -> Dict[str, Macro]:
        """Load all macros from discovered directories.
        
        Returns
        -------
        dict
            Dictionary of macro name to Macro object
        """
        macro_dirs = self.scan_macro_directories()
        
        for dir_name, files in macro_dirs.items():
            for file_name in files:
                file_path = os.path.join(self.swg_directory, dir_name, file_name)
                macros = self.parse_macro_file(file_path)
                
                for macro in macros:
                    self.macros[macro.name] = macro
                    self.macro_categories[macro.category].append(macro.name)
        
        log_event(f"[MACRO_PARSER] Loaded {len(self.macros)} macros")
        return self.macros
    
    def load_all_aliases(self) -> Dict[str, Alias]:
        """Load all aliases from discovered files.
        
        Returns
        -------
        dict
            Dictionary of alias name to Alias object
        """
        for alias_file in self.alias_files:
            file_path = os.path.join(self.swg_directory, alias_file)
            if os.path.exists(file_path):
                aliases = self.parse_alias_file(file_path)
                
                for alias in aliases:
                    self.aliases[alias.name] = alias
                    self.alias_categories[alias.category].append(alias.name)
        
        log_event(f"[MACRO_PARSER] Loaded {len(self.aliases)} aliases")
        return self.aliases
    
    def get_missing_critical_items(self) -> Tuple[List[str], List[str]]:
        """Get lists of missing critical macros and aliases.
        
        Returns
        -------
        tuple
            (missing_macros, missing_aliases)
        """
        missing_macros = []
        missing_aliases = []
        
        for macro_name in self.critical_macros:
            if macro_name not in self.macros:
                missing_macros.append(macro_name)
        
        for alias_name in self.critical_aliases:
            if alias_name not in self.aliases:
                missing_aliases.append(alias_name)
        
        return missing_macros, missing_aliases
    
    def analyze_macros(self) -> MacroAnalysis:
        """Analyze loaded macros and aliases.
        
        Returns
        -------
        MacroAnalysis
            Analysis results
        """
        # Count categories
        macro_categories = {cat: len(macros) for cat, macros in self.macro_categories.items()}
        alias_categories = {cat: len(aliases) for cat, aliases in self.alias_categories.items()}
        
        # Get critical items
        critical_macros = [name for name, macro in self.macros.items() if macro.is_critical]
        critical_aliases = [name for name, alias in self.aliases.items() if alias.is_critical]
        
        # Get missing items
        missing_macros, missing_aliases = self.get_missing_critical_items()
        
        # Get most used items (sorted by usage count)
        most_used_macros = sorted(
            [(name, macro.usage_count) for name, macro in self.macros.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        most_used_aliases = sorted(
            [(name, alias.usage_count) for name, alias in self.aliases.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        return MacroAnalysis(
            total_macros=len(self.macros),
            total_aliases=len(self.aliases),
            critical_macros=critical_macros,
            critical_aliases=critical_aliases,
            missing_macros=missing_macros,
            missing_aliases=missing_aliases,
            macro_categories=macro_categories,
            alias_categories=alias_categories,
            most_used_macros=most_used_macros,
            most_used_aliases=most_used_aliases
        )
    
    def save_analysis_report(self, analysis: MacroAnalysis, file_path: str = None) -> str:
        """Save macro analysis report to JSON file.
        
        Parameters
        ----------
        analysis : MacroAnalysis
            Analysis results to save
        file_path : str, optional
            Path to save file
            
        Returns
        -------
        str
            Path to saved file
        """
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"logs/macro_analysis_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis": asdict(analysis),
            "macros": {name: asdict(macro) for name, macro in self.macros.items()},
            "aliases": {name: asdict(alias) for name, alias in self.aliases.items()}
        }
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        log_event(f"[MACRO_PARSER] Saved analysis report to {file_path}")
        return file_path 