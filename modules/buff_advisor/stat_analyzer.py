"""Character Stat Analyzer for Buff Advisor Module.

This module provides functionality to analyze character stats from parsed /stats logs
or user input to determine optimal buff and template recommendations.
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from android_ms11.utils.logging_utils import log_event


class CharacterStatAnalyzer:
    """Analyzes character stats for buff and template recommendations."""

    def __init__(self):
        """Initialize the character stat analyzer."""
        self.stat_patterns = {
            "strength": r"Strength:\s*(\d+)",
            "agility": r"Agility:\s*(\d+)", 
            "constitution": r"Constitution:\s*(\d+)",
            "stamina": r"Stamina:\s*(\d+)",
            "mind": r"Mind:\s*(\d+)",
            "focus": r"Focus:\s*(\d+)",
            "willpower": r"Willpower:\s*(\d+)"
        }
        
        self.stat_thresholds = {
            "low": {"min": 0, "max": 80},
            "medium": {"min": 81, "max": 120},
            "high": {"min": 121, "max": 160},
            "excellent": {"min": 161, "max": 200}
        }
        
        self.optimization_targets = {
            "pve_damage": ["strength", "agility", "constitution"],
            "buff_stack": ["strength", "agility", "constitution", "stamina"],
            "healing": ["mind", "focus", "constitution"],
            "balanced": ["strength", "agility", "constitution", "stamina", "mind", "focus"]
        }

    def parse_stats_log(self, log_content: str) -> Dict[str, int]:
        """Parse character stats from a /stats log entry."""
        try:
            stats = {}
            
            for stat_name, pattern in self.stat_patterns.items():
                match = re.search(pattern, log_content, re.IGNORECASE)
                if match:
                    stats[stat_name] = int(match.group(1))
                else:
                    stats[stat_name] = 0
            
            log_event(f"[STAT_ANALYZER] Parsed stats: {stats}")
            return stats
            
        except Exception as e:
            log_event(f"[STAT_ANALYZER] Error parsing stats log: {e}")
            return {}

    def analyze_stat_distribution(self, stats: Dict[str, int]) -> Dict[str, Any]:
        """Analyze the distribution of character stats."""
        try:
            analysis = {
                "total_stats": sum(stats.values()),
                "average_stat": sum(stats.values()) / len(stats) if stats else 0,
                "stat_levels": {},
                "weakest_stats": [],
                "strongest_stats": [],
                "optimization_opportunities": []
            }
            
            # Categorize each stat by level
            for stat_name, value in stats.items():
                level = self._categorize_stat_level(value)
                analysis["stat_levels"][stat_name] = {
                    "value": value,
                    "level": level,
                    "threshold": self.stat_thresholds[level]
                }
            
            # Find weakest and strongest stats
            sorted_stats = sorted(stats.items(), key=lambda x: x[1])
            analysis["weakest_stats"] = [stat for stat, _ in sorted_stats[:3]]
            analysis["strongest_stats"] = [stat for stat, _ in sorted_stats[-3:]]
            
            # Identify optimization opportunities
            for stat_name, value in stats.items():
                if value < 100:  # Below optimal threshold
                    analysis["optimization_opportunities"].append({
                        "stat": stat_name,
                        "current": value,
                        "recommended_min": 100,
                        "improvement_needed": 100 - value
                    })
            
            log_event(f"[STAT_ANALYZER] Analysis complete - Total: {analysis['total_stats']}, Avg: {analysis['average_stat']:.1f}")
            return analysis
            
        except Exception as e:
            log_event(f"[STAT_ANALYZER] Error analyzing stat distribution: {e}")
            return {}

    def get_optimization_priorities(self, stats: Dict[str, int], 
                                   optimization_type: str = "balanced") -> List[Dict[str, Any]]:
        """Get optimization priorities based on stat goals."""
        try:
            priorities = []
            target_stats = self.optimization_targets.get(optimization_type, [])
            
            for stat_name in target_stats:
                if stat_name in stats:
                    current_value = stats[stat_name]
                    priority_score = self._calculate_priority_score(stat_name, current_value, optimization_type)
                    
                    priorities.append({
                        "stat": stat_name,
                        "current_value": current_value,
                        "priority_score": priority_score,
                        "recommended_min": self._get_recommended_min(stat_name, optimization_type),
                        "optimization_type": optimization_type
                    })
            
            # Sort by priority score (highest first)
            priorities.sort(key=lambda x: x["priority_score"], reverse=True)
            
            log_event(f"[STAT_ANALYZER] Optimization priorities for {optimization_type}: {len(priorities)} stats")
            return priorities
            
        except Exception as e:
            log_event(f"[STAT_ANALYZER] Error getting optimization priorities: {e}")
            return []

    def _categorize_stat_level(self, value: int) -> str:
        """Categorize a stat value into low/medium/high/excellent."""
        for level, threshold in self.stat_thresholds.items():
            if threshold["min"] <= value <= threshold["max"]:
                return level
        return "excellent" if value > 200 else "low"

    def _calculate_priority_score(self, stat_name: str, current_value: int, 
                                 optimization_type: str) -> float:
        """Calculate priority score for a stat based on optimization type."""
        base_score = 100 - current_value  # Lower stats get higher priority
        
        # Adjust based on optimization type
        if optimization_type == "pve_damage" and stat_name in ["strength", "agility"]:
            base_score *= 1.5
        elif optimization_type == "healing" and stat_name in ["mind", "focus"]:
            base_score *= 1.5
        elif optimization_type == "buff_stack" and stat_name in ["constitution", "stamina"]:
            base_score *= 1.3
            
        return base_score

    def _get_recommended_min(self, stat_name: str, optimization_type: str) -> int:
        """Get recommended minimum value for a stat based on optimization type."""
        base_min = 100
        
        if optimization_type == "pve_damage":
            if stat_name in ["strength", "agility"]:
                return 120
            elif stat_name == "constitution":
                return 110
        elif optimization_type == "healing":
            if stat_name in ["mind", "focus"]:
                return 130
            elif stat_name == "constitution":
                return 110
        elif optimization_type == "buff_stack":
            if stat_name in ["constitution", "stamina"]:
                return 120
                
        return base_min


def create_stat_analyzer() -> CharacterStatAnalyzer:
    """Create a new CharacterStatAnalyzer instance."""
    return CharacterStatAnalyzer() 