"""Buff Recommender for Buff Advisor Module.

This module provides specific recommendations for buff food and entertainer dances
based on character stats and optimization goals.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from android_ms11.utils.logging_utils import log_event


class BuffRecommender:
    """Recommends buff food and entertainer dances based on character stats."""

    def __init__(self):
        """Initialize the buff recommender."""
        self.buff_food_data = {
            "strength_food": {
                "items": ["Ryshcate", "Spiced Tea", "Caf", "Corellian Brandy"],
                "stat_bonus": {"strength": 25, "constitution": 10},
                "duration": 3600,  # 1 hour
                "cost": "medium"
            },
            "agility_food": {
                "items": ["Smoked Shaak Roast", "Bantha Steak", "Spice Bread"],
                "stat_bonus": {"agility": 25, "stamina": 10},
                "duration": 3600,
                "cost": "medium"
            },
            "constitution_food": {
                "items": ["Durindfire", "Spice Wine", "Corellian Ale"],
                "stat_bonus": {"constitution": 25, "stamina": 15},
                "duration": 3600,
                "cost": "high"
            },
            "mind_food": {
                "items": ["Spice Tea", "Caf", "Corellian Brandy"],
                "stat_bonus": {"mind": 25, "focus": 10},
                "duration": 3600,
                "cost": "medium"
            },
            "focus_food": {
                "items": ["Spice Bread", "Ryshcate", "Spiced Tea"],
                "stat_bonus": {"focus": 25, "willpower": 10},
                "duration": 3600,
                "cost": "medium"
            },
            "stamina_food": {
                "items": ["Bantha Steak", "Smoked Shaak Roast", "Durindfire"],
                "stat_bonus": {"stamina": 25, "constitution": 10},
                "duration": 3600,
                "cost": "medium"
            }
        }
        
        self.entertainer_dances = {
            "strength_dance": {
                "name": "Might Dance",
                "stat_bonus": {"strength": 30, "constitution": 15},
                "duration": 7200,  # 2 hours
                "entertainer_level": "master",
                "cost": "high"
            },
            "agility_dance": {
                "name": "Agility Dance", 
                "stat_bonus": {"agility": 30, "stamina": 15},
                "duration": 7200,
                "entertainer_level": "master",
                "cost": "high"
            },
            "constitution_dance": {
                "name": "Constitution Dance",
                "stat_bonus": {"constitution": 30, "stamina": 20},
                "duration": 7200,
                "entertainer_level": "expert",
                "cost": "medium"
            },
            "mind_dance": {
                "name": "Mind Dance",
                "stat_bonus": {"mind": 30, "focus": 15},
                "duration": 7200,
                "entertainer_level": "master",
                "cost": "high"
            },
            "focus_dance": {
                "name": "Focus Dance",
                "stat_bonus": {"focus": 30, "willpower": 15},
                "duration": 7200,
                "entertainer_level": "expert",
                "cost": "medium"
            },
            "stamina_dance": {
                "name": "Stamina Dance",
                "stat_bonus": {"stamina": 30, "constitution": 15},
                "duration": 7200,
                "entertainer_level": "journeyman",
                "cost": "low"
            }
        }

    def recommend_buff_food(self, stats: Dict[str, int], 
                           optimization_type: str = "balanced",
                           budget: str = "medium") -> List[Dict[str, Any]]:
        """Recommend buff food based on character stats and optimization goals."""
        try:
            recommendations = []
            
            # Get optimization priorities
            priorities = self._get_food_priorities(stats, optimization_type)
            
            for priority in priorities:
                stat_name = priority["stat"]
                food_type = f"{stat_name}_food"
                
                if food_type in self.buff_food_data:
                    food_data = self.buff_food_data[food_type]
                    
                    # Check if within budget
                    if self._is_within_budget(food_data["cost"], budget):
                        recommendation = {
                            "type": "buff_food",
                            "stat_target": stat_name,
                            "items": food_data["items"],
                            "stat_bonus": food_data["stat_bonus"],
                            "duration": food_data["duration"],
                            "cost": food_data["cost"],
                            "priority_score": priority["priority_score"],
                            "current_stat": stats.get(stat_name, 0),
                            "expected_improvement": food_data["stat_bonus"].get(stat_name, 0)
                        }
                        
                        recommendations.append(recommendation)
            
            # Sort by priority score
            recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
            
            log_event(f"[BUFF_RECOMMENDER] Recommended {len(recommendations)} buff foods for {optimization_type}")
            return recommendations
            
        except Exception as e:
            log_event(f"[BUFF_RECOMMENDER] Error recommending buff food: {e}")
            return []

    def recommend_entertainer_dances(self, stats: Dict[str, int],
                                    optimization_type: str = "balanced",
                                    budget: str = "medium") -> List[Dict[str, Any]]:
        """Recommend entertainer dances based on character stats and optimization goals."""
        try:
            recommendations = []
            
            # Get optimization priorities
            priorities = self._get_dance_priorities(stats, optimization_type)
            
            for priority in priorities:
                stat_name = priority["stat"]
                dance_type = f"{stat_name}_dance"
                
                if dance_type in self.entertainer_dances:
                    dance_data = self.entertainer_dances[dance_type]
                    
                    # Check if within budget
                    if self._is_within_budget(dance_data["cost"], budget):
                        recommendation = {
                            "type": "entertainer_dance",
                            "dance_name": dance_data["name"],
                            "stat_target": stat_name,
                            "stat_bonus": dance_data["stat_bonus"],
                            "duration": dance_data["duration"],
                            "entertainer_level": dance_data["entertainer_level"],
                            "cost": dance_data["cost"],
                            "priority_score": priority["priority_score"],
                            "current_stat": stats.get(stat_name, 0),
                            "expected_improvement": dance_data["stat_bonus"].get(stat_name, 0)
                        }
                        
                        recommendations.append(recommendation)
            
            # Sort by priority score
            recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
            
            log_event(f"[BUFF_RECOMMENDER] Recommended {len(recommendations)} entertainer dances for {optimization_type}")
            return recommendations
            
        except Exception as e:
            log_event(f"[BUFF_RECOMMENDER] Error recommending entertainer dances: {e}")
            return []

    def get_combined_recommendations(self, stats: Dict[str, int],
                                    optimization_type: str = "balanced",
                                    budget: str = "medium") -> Dict[str, Any]:
        """Get combined buff food and entertainer dance recommendations."""
        try:
            food_recs = self.recommend_buff_food(stats, optimization_type, budget)
            dance_recs = self.recommend_entertainer_dances(stats, optimization_type, budget)
            
            # Calculate total expected improvements
            total_improvements = {}
            for rec in food_recs + dance_recs:
                for stat, bonus in rec["stat_bonus"].items():
                    total_improvements[stat] = total_improvements.get(stat, 0) + bonus
            
            combined = {
                "timestamp": datetime.now().isoformat(),
                "optimization_type": optimization_type,
                "budget": budget,
                "buff_food": food_recs,
                "entertainer_dances": dance_recs,
                "total_expected_improvements": total_improvements,
                "recommendation_count": len(food_recs) + len(dance_recs)
            }
            
            log_event(f"[BUFF_RECOMMENDER] Combined recommendations: {combined['recommendation_count']} total")
            return combined
            
        except Exception as e:
            log_event(f"[BUFF_RECOMMENDER] Error getting combined recommendations: {e}")
            return {}

    def _get_food_priorities(self, stats: Dict[str, int], optimization_type: str) -> List[Dict[str, Any]]:
        """Get food priorities based on optimization type."""
        priorities = []
        
        if optimization_type == "pve_damage":
            target_stats = ["strength", "agility", "constitution"]
        elif optimization_type == "healing":
            target_stats = ["mind", "focus", "constitution"]
        elif optimization_type == "buff_stack":
            target_stats = ["constitution", "stamina", "strength"]
        else:  # balanced
            target_stats = ["strength", "agility", "constitution", "mind", "focus", "stamina"]
        
        for stat_name in target_stats:
            if stat_name in stats:
                current_value = stats[stat_name]
                priority_score = max(0, 100 - current_value)  # Lower stats get higher priority
                
                priorities.append({
                    "stat": stat_name,
                    "current_value": current_value,
                    "priority_score": priority_score
                })
        
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        return priorities

    def _get_dance_priorities(self, stats: Dict[str, int], optimization_type: str) -> List[Dict[str, Any]]:
        """Get dance priorities based on optimization type."""
        return self._get_food_priorities(stats, optimization_type)  # Same logic for now

    def _is_within_budget(self, item_cost: str, budget: str) -> bool:
        """Check if an item is within the specified budget."""
        cost_levels = {"low": 1, "medium": 2, "high": 3}
        budget_levels = {"low": 1, "medium": 2, "high": 3}
        
        return cost_levels.get(item_cost, 2) <= budget_levels.get(budget, 2)


def create_buff_recommender() -> BuffRecommender:
    """Create a new BuffRecommender instance."""
    return BuffRecommender() 