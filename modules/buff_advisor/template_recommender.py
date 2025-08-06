"""Template Recommender for Buff Advisor Module.

This module provides armor setup recommendations based on character stats
and build awareness from Batch 070.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from android_ms11.utils.logging_utils import log_event


class TemplateRecommender:
    """Recommends armor setups based on character stats and build awareness."""

    def __init__(self):
        """Initialize the template recommender."""
        self.armor_templates = {
            "rifleman": {
                "name": "Rifleman Combat Armor",
                "slots": {
                    "head": {"stat_bonus": {"agility": 15, "stamina": 10}},
                    "chest": {"stat_bonus": {"strength": 20, "constitution": 15}},
                    "legs": {"stat_bonus": {"agility": 15, "stamina": 10}},
                    "feet": {"stat_bonus": {"agility": 10, "stamina": 5}},
                    "hands": {"stat_bonus": {"agility": 10, "stamina": 5}}
                },
                "set_bonus": {"agility": 25, "stamina": 20},
                "combat_style": "ranged",
                "cost": "medium"
            },
            "pistoleer": {
                "name": "Pistoleer Combat Armor",
                "slots": {
                    "head": {"stat_bonus": {"agility": 15, "stamina": 10}},
                    "chest": {"stat_bonus": {"strength": 15, "agility": 10}},
                    "legs": {"stat_bonus": {"agility": 15, "stamina": 10}},
                    "feet": {"stat_bonus": {"agility": 10, "stamina": 5}},
                    "hands": {"stat_bonus": {"agility": 10, "stamina": 5}}
                },
                "set_bonus": {"agility": 30, "stamina": 15},
                "combat_style": "ranged",
                "cost": "medium"
            },
            "medic": {
                "name": "Medic Support Armor",
                "slots": {
                    "head": {"stat_bonus": {"mind": 15, "focus": 10}},
                    "chest": {"stat_bonus": {"constitution": 20, "mind": 15}},
                    "legs": {"stat_bonus": {"constitution": 15, "stamina": 10}},
                    "feet": {"stat_bonus": {"constitution": 10, "stamina": 5}},
                    "hands": {"stat_bonus": {"mind": 10, "focus": 5}}
                },
                "set_bonus": {"mind": 25, "constitution": 20},
                "combat_style": "support",
                "cost": "high"
            },
            "healer": {
                "name": "Healer Support Armor",
                "slots": {
                    "head": {"stat_bonus": {"mind": 20, "focus": 15}},
                    "chest": {"stat_bonus": {"constitution": 15, "mind": 20}},
                    "legs": {"stat_bonus": {"constitution": 15, "stamina": 10}},
                    "feet": {"stat_bonus": {"constitution": 10, "stamina": 5}},
                    "hands": {"stat_bonus": {"mind": 15, "focus": 10}}
                },
                "set_bonus": {"mind": 30, "focus": 20},
                "combat_style": "support",
                "cost": "high"
            },
            "balanced": {
                "name": "Balanced Combat Armor",
                "slots": {
                    "head": {"stat_bonus": {"strength": 10, "agility": 10}},
                    "chest": {"stat_bonus": {"constitution": 20, "stamina": 15}},
                    "legs": {"stat_bonus": {"agility": 10, "stamina": 10}},
                    "feet": {"stat_bonus": {"agility": 5, "stamina": 5}},
                    "hands": {"stat_bonus": {"strength": 5, "agility": 5}}
                },
                "set_bonus": {"strength": 15, "agility": 15, "constitution": 15},
                "combat_style": "balanced",
                "cost": "medium"
            }
        }
        
        self.weapon_templates = {
            "rifle": {
                "name": "Rifle Setup",
                "weapon_bonus": {"agility": 20, "stamina": 10},
                "range": "long",
                "damage_type": "kinetic"
            },
            "pistol": {
                "name": "Pistol Setup", 
                "weapon_bonus": {"agility": 15, "stamina": 5},
                "range": "medium",
                "damage_type": "kinetic"
            },
            "carbine": {
                "name": "Carbine Setup",
                "weapon_bonus": {"agility": 18, "stamina": 8},
                "range": "medium",
                "damage_type": "kinetic"
            },
            "melee": {
                "name": "Melee Setup",
                "weapon_bonus": {"strength": 25, "constitution": 15},
                "range": "close",
                "damage_type": "kinetic"
            }
        }

    def recommend_armor_setup(self, stats: Dict[str, int],
                              build_data: Dict[str, Any] = None,
                              optimization_type: str = "balanced",
                              budget: str = "medium") -> Dict[str, Any]:
        """Recommend armor setup based on character stats and build data."""
        try:
            # Determine optimal armor template based on build and stats
            template_name = self._select_armor_template(stats, build_data, optimization_type)
            
            if template_name not in self.armor_templates:
                template_name = "balanced"  # Fallback
                
            template = self.armor_templates[template_name]
            
            # Check if within budget
            if not self._is_within_budget(template["cost"], budget):
                # Try to find a cheaper alternative
                template_name = self._find_cheaper_template(optimization_type, budget)
                template = self.armor_templates.get(template_name, self.armor_templates["balanced"])
            
            # Calculate total stat bonuses
            total_bonuses = {}
            for slot, slot_data in template["slots"].items():
                for stat, bonus in slot_data["stat_bonus"].items():
                    total_bonuses[stat] = total_bonuses.get(stat, 0) + bonus
            
            # Add set bonus
            for stat, bonus in template["set_bonus"].items():
                total_bonuses[stat] = total_bonuses.get(stat, 0) + bonus
            
            recommendation = {
                "template_name": template["name"],
                "template_type": template_name,
                "combat_style": template["combat_style"],
                "cost": template["cost"],
                "slots": template["slots"],
                "set_bonus": template["set_bonus"],
                "total_stat_bonuses": total_bonuses,
                "optimization_type": optimization_type,
                "budget": budget
            }
            
            log_event(f"[TEMPLATE_RECOMMENDER] Recommended {template_name} armor setup")
            return recommendation
            
        except Exception as e:
            log_event(f"[TEMPLATE_RECOMMENDER] Error recommending armor setup: {e}")
            return {}

    def recommend_weapon_setup(self, stats: Dict[str, int],
                               build_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Recommend weapon setup based on character stats and build data."""
        try:
            # Determine optimal weapon based on build data
            weapon_type = self._select_weapon_type(build_data)
            
            if weapon_type not in self.weapon_templates:
                weapon_type = "rifle"  # Default fallback
                
            weapon = self.weapon_templates[weapon_type]
            
            recommendation = {
                "weapon_name": weapon["name"],
                "weapon_type": weapon_type,
                "range": weapon["range"],
                "damage_type": weapon["damage_type"],
                "weapon_bonus": weapon["weapon_bonus"]
            }
            
            log_event(f"[TEMPLATE_RECOMMENDER] Recommended {weapon_type} weapon setup")
            return recommendation
            
        except Exception as e:
            log_event(f"[TEMPLATE_RECOMMENDER] Error recommending weapon setup: {e}")
            return {}

    def get_complete_template_recommendation(self, stats: Dict[str, int],
                                            build_data: Dict[str, Any] = None,
                                            optimization_type: str = "balanced",
                                            budget: str = "medium") -> Dict[str, Any]:
        """Get complete template recommendation including armor and weapon setups."""
        try:
            armor_rec = self.recommend_armor_setup(stats, build_data, optimization_type, budget)
            weapon_rec = self.recommend_weapon_setup(stats, build_data)
            
            # Calculate total expected improvements
            total_improvements = {}
            
            if armor_rec:
                for stat, bonus in armor_rec["total_stat_bonuses"].items():
                    total_improvements[stat] = total_improvements.get(stat, 0) + bonus
            
            if weapon_rec:
                for stat, bonus in weapon_rec["weapon_bonus"].items():
                    total_improvements[stat] = total_improvements.get(stat, 0) + bonus
            
            complete = {
                "timestamp": datetime.now().isoformat(),
                "optimization_type": optimization_type,
                "budget": budget,
                "armor_setup": armor_rec,
                "weapon_setup": weapon_rec,
                "total_expected_improvements": total_improvements,
                "build_data": build_data
            }
            
            log_event(f"[TEMPLATE_RECOMMENDER] Complete template recommendation generated")
            return complete
            
        except Exception as e:
            log_event(f"[TEMPLATE_RECOMMENDER] Error getting complete template recommendation: {e}")
            return {}

    def _select_armor_template(self, stats: Dict[str, int], 
                               build_data: Dict[str, Any] = None,
                               optimization_type: str = "balanced") -> str:
        """Select the optimal armor template based on stats and build data."""
        if build_data and "professions" in build_data:
            professions = build_data["professions"]
            
            # Check for specific profession templates
            if "rifleman" in professions:
                return "rifleman"
            elif "pistoleer" in professions:
                return "pistoleer"
            elif "medic" in professions or "doctor" in professions:
                return "medic"
            elif "healer" in professions or "combat_medic" in professions:
                return "healer"
        
        # Fall back to optimization type
        if optimization_type == "pve_damage":
            return "rifleman"
        elif optimization_type == "healing":
            return "medic"
        elif optimization_type == "buff_stack":
            return "balanced"
        else:
            return "balanced"

    def _select_weapon_type(self, build_data: Dict[str, Any] = None) -> str:
        """Select the optimal weapon type based on build data."""
        if build_data and "weapons" in build_data:
            weapons = build_data["weapons"]
            
            if "rifle" in weapons:
                return "rifle"
            elif "pistol" in weapons:
                return "pistol"
            elif "carbine" in weapons:
                return "carbine"
            elif "melee" in weapons or "sword" in weapons:
                return "melee"
        
        return "rifle"  # Default

    def _find_cheaper_template(self, optimization_type: str, budget: str) -> str:
        """Find a cheaper armor template within budget."""
        if budget == "low":
            return "balanced"
        elif budget == "medium":
            if optimization_type == "pve_damage":
                return "pistoleer"
            elif optimization_type == "healing":
                return "medic"
            else:
                return "balanced"
        else:
            return "balanced"

    def _is_within_budget(self, item_cost: str, budget: str) -> bool:
        """Check if an item is within the specified budget."""
        cost_levels = {"low": 1, "medium": 2, "high": 3}
        budget_levels = {"low": 1, "medium": 2, "high": 3}
        
        return cost_levels.get(item_cost, 2) <= budget_levels.get(budget, 2)


def create_template_recommender() -> TemplateRecommender:
    """Create a new TemplateRecommender instance."""
    return TemplateRecommender() 