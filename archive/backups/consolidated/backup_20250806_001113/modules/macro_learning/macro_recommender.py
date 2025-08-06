"""Macro Recommender for suggesting missing macros and building fallback maps.

This module provides intelligent recommendations for missing macros and
creates fallback maps when macros are not found.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

@dataclass
class MacroRecommendation:
    """Data class for macro recommendations."""
    macro_name: str
    category: str
    priority: int
    reason: str
    suggested_content: str
    alternatives: List[str]
    is_critical: bool
    estimated_usage: float

@dataclass
class FallbackMap:
    """Data class for fallback macro maps."""
    original_macro: str
    fallback_macro: str
    confidence: float
    category: str
    usage_context: str
    alternatives: List[str]

@dataclass
class RecommendationReport:
    """Data class for recommendation report."""
    total_recommendations: int
    critical_recommendations: int
    missing_macros: List[str]
    missing_aliases: List[str]
    fallback_maps: List[FallbackMap]
    recommendations: List[MacroRecommendation]
    priority_order: List[str]

class MacroRecommender:
    """Recommender for missing macros and fallback maps."""
    
    def __init__(self, data_directory: str = "data/macros"):
        """Initialize the macro recommender.
        
        Parameters
        ----------
        data_directory : str
            Directory containing best practice macros
        """
        self.data_directory = data_directory
        self.best_practice_macros = {}
        self.fallback_maps = {}
        self.recommendations = {}
        
        # Critical macro definitions
        self.critical_macros = {
            "heal": {
                "category": "combat",
                "priority": 1,
                "content": "/heal {target}\n/say Healing {target}",
                "alternatives": ["cure", "medic", "healing"],
                "usage_context": "Combat healing"
            },
            "buff": {
                "category": "combat", 
                "priority": 1,
                "content": "/buff {target}\n/say Buffing {target}",
                "alternatives": ["enhance", "boost", "buffing"],
                "usage_context": "Combat buffing"
            },
            "travel": {
                "category": "travel",
                "priority": 1,
                "content": "/travel {destination}\n/say Traveling to {destination}",
                "alternatives": ["goto", "move", "traveling"],
                "usage_context": "Travel commands"
            },
            "craft": {
                "category": "crafting",
                "priority": 1,
                "content": "/craft {item}\n/say Crafting {item}",
                "alternatives": ["build", "create", "crafting"],
                "usage_context": "Crafting activities"
            },
            "loot": {
                "category": "utility",
                "priority": 1,
                "content": "/loot\n/say Looting",
                "alternatives": ["collect", "gather", "looting"],
                "usage_context": "Looting items"
            },
            "follow": {
                "category": "travel",
                "priority": 2,
                "content": "/follow {target}\n/say Following {target}",
                "alternatives": ["chase", "pursue", "following"],
                "usage_context": "Following players"
            },
            "attack": {
                "category": "combat",
                "priority": 1,
                "content": "/attack {target}\n/say Attacking {target}",
                "alternatives": ["fight", "engage", "attacking"],
                "usage_context": "Combat attacks"
            },
            "defend": {
                "category": "combat",
                "priority": 2,
                "content": "/defend\n/say Defending",
                "alternatives": ["guard", "protect", "defending"],
                "usage_context": "Combat defense"
            },
            "flee": {
                "category": "combat",
                "priority": 1,
                "content": "/flee\n/say Fleeing",
                "alternatives": ["run", "escape", "fleeing"],
                "usage_context": "Combat escape"
            }
        }
        
        # Load best practice macros
        self._load_best_practice_macros()
        
        log_event(f"[MACRO_RECOMMENDER] Initialized with {len(self.best_practice_macros)} best practice macros")
    
    def _load_best_practice_macros(self) -> None:
        """Load best practice macros from data directory."""
        try:
            # Ensure directory exists
            os.makedirs(self.data_directory, exist_ok=True)
            
            # Load from JSON file if it exists
            best_practice_file = os.path.join(self.data_directory, "best_practice_macros.json")
            if os.path.exists(best_practice_file):
                with open(best_practice_file, 'r') as f:
                    self.best_practice_macros = json.load(f)
            else:
                # Create default best practice macros
                self.best_practice_macros = self.critical_macros
                self._save_best_practice_macros()
                
        except Exception as e:
            log_event(f"[MACRO_RECOMMENDER] Error loading best practice macros: {e}")
            self.best_practice_macros = self.critical_macros
    
    def _save_best_practice_macros(self) -> None:
        """Save best practice macros to file."""
        try:
            best_practice_file = os.path.join(self.data_directory, "best_practice_macros.json")
            with open(best_practice_file, 'w') as f:
                json.dump(self.best_practice_macros, f, indent=2)
            
            log_event(f"[MACRO_RECOMMENDER] Saved best practice macros to {best_practice_file}")
        except Exception as e:
            log_event(f"[MACRO_RECOMMENDER] Error saving best practice macros: {e}")
    
    def find_missing_macros(self, existing_macros: Dict[str, Any]) -> List[str]:
        """Find missing macros from critical list.
        
        Parameters
        ----------
        existing_macros : dict
            Dictionary of existing macro names
            
        Returns
        -------
        list
            List of missing macro names
        """
        missing = []
        
        for macro_name in self.critical_macros:
            if macro_name not in existing_macros:
                missing.append(macro_name)
        
        return missing
    
    def create_fallback_map(self, missing_macro: str, available_macros: Dict[str, Any]) -> Optional[FallbackMap]:
        """Create a fallback map for a missing macro.
        
        Parameters
        ----------
        missing_macro : str
            Name of missing macro
        available_macros : dict
            Dictionary of available macros
            
        Returns
        -------
        FallbackMap or None
            Fallback map if suitable alternative found
        """
        if missing_macro not in self.critical_macros:
            return None
        
        macro_info = self.critical_macros[missing_macro]
        alternatives = macro_info.get("alternatives", [])
        
        # Look for alternative macros
        for alternative in alternatives:
            if alternative in available_macros:
                return FallbackMap(
                    original_macro=missing_macro,
                    fallback_macro=alternative,
                    confidence=0.8,
                    category=macro_info["category"],
                    usage_context=macro_info["usage_context"],
                    alternatives=[alt for alt in alternatives if alt != alternative]
                )
        
        # Look for macros in same category
        category = macro_info["category"]
        for macro_name, macro_data in available_macros.items():
            # Handle both Macro objects and dictionaries
            if hasattr(macro_data, 'category'):
                macro_category = macro_data.category
            else:
                macro_category = macro_data.get("category", "general")
            
            if macro_category == category:
                return FallbackMap(
                    original_macro=missing_macro,
                    fallback_macro=macro_name,
                    confidence=0.6,
                    category=category,
                    usage_context=macro_info["usage_context"],
                    alternatives=alternatives
                )
        
        return None
    
    def generate_recommendations(self, missing_macros: List[str], 
                                existing_macros: Dict[str, Any]) -> List[MacroRecommendation]:
        """Generate recommendations for missing macros.
        
        Parameters
        ----------
        missing_macros : list
            List of missing macro names
        existing_macros : dict
            Dictionary of existing macros
            
        Returns
        -------
        list
            List of MacroRecommendation objects
        """
        recommendations = []
        
        for macro_name in missing_macros:
            if macro_name in self.critical_macros:
                macro_info = self.critical_macros[macro_name]
                
                # Create fallback map
                fallback_map = self.create_fallback_map(macro_name, existing_macros)
                
                recommendation = MacroRecommendation(
                    macro_name=macro_name,
                    category=macro_info["category"],
                    priority=macro_info["priority"],
                    reason=f"Critical {macro_info['category']} macro missing",
                    suggested_content=macro_info["content"],
                    alternatives=macro_info["alternatives"],
                    is_critical=True,
                    estimated_usage=0.9 if macro_info["priority"] == 1 else 0.7
                )
                
                recommendations.append(recommendation)
                
                if fallback_map:
                    self.fallback_maps[macro_name] = fallback_map
        
        # Sort by priority
        recommendations.sort(key=lambda x: (x.priority, x.estimated_usage), reverse=True)
        
        return recommendations
    
    def recommend_macros_for_category(self, category: str, 
                                     existing_macros: Dict[str, Any]) -> List[MacroRecommendation]:
        """Recommend macros for a specific category.
        
        Parameters
        ----------
        category : str
            Category to recommend for
        existing_macros : dict
            Dictionary of existing macros
            
        Returns
        -------
        list
            List of MacroRecommendation objects
        """
        recommendations = []
        
        # Get category-specific best practices
        category_macros = {
            name: info for name, info in self.best_practice_macros.items()
            if info["category"] == category
        }
        
        for macro_name, macro_info in category_macros.items():
            if macro_name not in existing_macros:
                recommendation = MacroRecommendation(
                    macro_name=macro_name,
                    category=category,
                    priority=macro_info["priority"],
                    reason=f"Recommended {category} macro",
                    suggested_content=macro_info["content"],
                    alternatives=macro_info["alternatives"],
                    is_critical=macro_name in self.critical_macros,
                    estimated_usage=0.6
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def create_macro_file(self, macro_name: str, content: str, 
                         file_path: str = None) -> str:
        """Create a macro file with the given content.
        
        Parameters
        ----------
        macro_name : str
            Name of the macro
        content : str
            Macro content
        file_path : str, optional
            Path to save file
            
        Returns
        -------
        str
            Path to created file
        """
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"data/macros/{macro_name}_{timestamp}.txt"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create macro content
        macro_content = f"# {macro_name.upper()} MACRO\n"
        macro_content += f"# Created: {datetime.now().isoformat()}\n"
        macro_content += f"# Category: {self.critical_macros.get(macro_name, {}).get('category', 'general')}\n\n"
        macro_content += content
        
        with open(file_path, 'w') as f:
            f.write(macro_content)
        
        log_event(f"[MACRO_RECOMMENDER] Created macro file: {file_path}")
        return file_path
    
    def generate_comprehensive_report(self, missing_macros: List[str], 
                                    missing_aliases: List[str],
                                    existing_macros: Dict[str, Any],
                                    existing_aliases: Dict[str, Any]) -> RecommendationReport:
        """Generate comprehensive recommendation report.
        
        Parameters
        ----------
        missing_macros : list
            List of missing macro names
        missing_aliases : list
            List of missing alias names
        existing_macros : dict
            Dictionary of existing macros
        existing_aliases : dict
            Dictionary of existing aliases
            
        Returns
        -------
        RecommendationReport
            Complete recommendation report
        """
        # Generate macro recommendations
        macro_recommendations = self.generate_recommendations(missing_macros, existing_macros)
        
        # Create fallback maps
        fallback_maps = []
        for macro_name in missing_macros:
            fallback_map = self.create_fallback_map(macro_name, existing_macros)
            if fallback_map:
                fallback_maps.append(fallback_map)
        
        # Determine priority order
        priority_order = []
        critical_recommendations = [r for r in macro_recommendations if r.is_critical]
        
        # Add critical macros first
        for rec in critical_recommendations:
            priority_order.append(rec.macro_name)
        
        # Add other missing macros
        for macro_name in missing_macros:
            if macro_name not in priority_order:
                priority_order.append(macro_name)
        
        return RecommendationReport(
            total_recommendations=len(macro_recommendations),
            critical_recommendations=len(critical_recommendations),
            missing_macros=missing_macros,
            missing_aliases=missing_aliases,
            fallback_maps=fallback_maps,
            recommendations=macro_recommendations,
            priority_order=priority_order
        )
    
    def save_recommendation_report(self, report: RecommendationReport, 
                                  file_path: str = None) -> str:
        """Save recommendation report to JSON file.
        
        Parameters
        ----------
        report : RecommendationReport
            Report to save
        file_path : str, optional
            Path to save file
            
        Returns
        -------
        str
            Path to saved file
        """
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"logs/macro_recommendations_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "report": asdict(report),
            "best_practice_macros": self.best_practice_macros,
            "fallback_maps": {name: asdict(fallback) for name, fallback in self.fallback_maps.items()}
        }
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        log_event(f"[MACRO_RECOMMENDER] Saved recommendation report to {file_path}")
        return file_path
    
    def get_best_practice_macro(self, macro_name: str) -> Optional[Dict[str, Any]]:
        """Get best practice macro by name.
        
        Parameters
        ----------
        macro_name : str
            Name of the macro
            
        Returns
        -------
        dict or None
            Best practice macro data
        """
        return self.best_practice_macros.get(macro_name)
    
    def add_best_practice_macro(self, macro_name: str, macro_data: Dict[str, Any]) -> None:
        """Add a new best practice macro.
        
        Parameters
        ----------
        macro_name : str
            Name of the macro
        macro_data : dict
            Macro data
        """
        self.best_practice_macros[macro_name] = macro_data
        self._save_best_practice_macros()
        
        log_event(f"[MACRO_RECOMMENDER] Added best practice macro: {macro_name}")
    
    def get_fallback_macro(self, macro_name: str) -> Optional[str]:
        """Get fallback macro for a missing macro.
        
        Parameters
        ----------
        macro_name : str
            Name of missing macro
            
        Returns
        -------
        str or None
            Fallback macro name
        """
        fallback_map = self.fallback_maps.get(macro_name)
        return fallback_map.fallback_macro if fallback_map else None 