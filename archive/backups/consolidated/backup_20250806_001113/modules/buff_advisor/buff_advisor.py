"""Main Buff Advisor for MS11.

This module provides the main interface for the buff advisor system,
orchestrating character stat analysis, buff recommendations, template
recommendations, and build integration.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from android_ms11.utils.logging_utils import log_event

from .stat_analyzer import CharacterStatAnalyzer
from .buff_recommender import BuffRecommender
from .template_recommender import TemplateRecommender
from .build_integration import BuildIntegration


class BuffAdvisor:
    """Main buff advisor that orchestrates all recommendation components."""

    def __init__(self):
        """Initialize the buff advisor with all components."""
        self.stat_analyzer = CharacterStatAnalyzer()
        self.buff_recommender = BuffRecommender()
        self.template_recommender = TemplateRecommender()
        self.build_integration = BuildIntegration()
        
        self.recommendation_history = []
        self.character_cache = {}

    def analyze_character_and_recommend(self, stats_input: Dict[str, int] | str,
                                       character_name: str = None,
                                       optimization_type: str = "balanced",
                                       budget: str = "medium",
                                       include_build_awareness: bool = True) -> Dict[str, Any]:
        """Analyze character stats and provide comprehensive recommendations."""
        try:
            # Parse stats if string input (from /stats log)
            if isinstance(stats_input, str):
                stats = self.stat_analyzer.parse_stats_log(stats_input)
            else:
                stats = stats_input
            
            # If stats is empty, default to 0 values for all stats
            if not stats:
                stats = {
                    "strength": 0, "agility": 0, "constitution": 0,
                    "stamina": 0, "mind": 0, "focus": 0, "willpower": 0
                }
            
            # Analyze stat distribution
            stat_analysis = self.stat_analyzer.analyze_stat_distribution(stats)
            
            # Get optimization priorities
            priorities = self.stat_analyzer.get_optimization_priorities(stats, optimization_type)
            
            # Get buff recommendations
            buff_recommendations = self.buff_recommender.get_combined_recommendations(
                stats, optimization_type, budget
            )
            
            # Get template recommendations
            build_data = None
            if include_build_awareness:
                build_data = self.build_integration.get_build_data(character_name)
            
            template_recommendations = self.template_recommender.get_complete_template_recommendation(
                stats, build_data, optimization_type, budget
            )
            
            # Get build-aware analysis if requested
            build_analysis = {}
            if include_build_awareness:
                build_analysis = self.build_integration.analyze_with_build_context(
                    stats, character_name, optimization_type
                )
            
            # Compile comprehensive results
            results = {
                "timestamp": datetime.now().isoformat(),
                "character_name": character_name,
                "optimization_type": optimization_type,
                "budget": budget,
                "stats": stats,
                "stat_analysis": stat_analysis,
                "optimization_priorities": priorities,
                "buff_recommendations": buff_recommendations,
                "template_recommendations": template_recommendations,
                "build_analysis": build_analysis,
                "summary": self._generate_summary(stats, stat_analysis, priorities, 
                                                buff_recommendations, template_recommendations)
            }
            
            # Store in history
            self.recommendation_history.append(results)
            
            # Cache character stats
            if character_name:
                self.character_cache[character_name] = {
                    "stats": stats.copy(),
                    "last_analyzed": datetime.now().isoformat(),
                    "optimization_type": optimization_type
                }
            
            log_event(f"[BUFF_ADVISOR] Comprehensive analysis complete for {character_name}")
            return results
            
        except Exception as e:
            log_event(f"[BUFF_ADVISOR] Error in character analysis: {e}")
            return {"error": str(e)}

    def get_buff_recommendations(self, stats: Dict[str, int],
                                 optimization_type: str = "balanced",
                                 budget: str = "medium") -> Dict[str, Any]:
        """Get specific buff food and entertainer dance recommendations."""
        try:
            return self.buff_recommender.get_combined_recommendations(
                stats, optimization_type, budget
            )
        except Exception as e:
            log_event(f"[BUFF_ADVISOR] Error getting buff recommendations: {e}")
            return {"error": str(e)}

    def get_template_recommendations(self, stats: Dict[str, int],
                                    character_name: str = None,
                                    optimization_type: str = "balanced",
                                    budget: str = "medium") -> Dict[str, Any]:
        """Get armor and weapon setup recommendations."""
        try:
            build_data = self.build_integration.get_build_data(character_name)
            return self.template_recommender.get_complete_template_recommendation(
                stats, build_data, optimization_type, budget
            )
        except Exception as e:
            log_event(f"[BUFF_ADVISOR] Error getting template recommendations: {e}")
            return {"error": str(e)}

    def analyze_from_stats_log(self, log_content: str,
                               character_name: str = None,
                               optimization_type: str = "balanced",
                               budget: str = "medium") -> Dict[str, Any]:
        """Analyze character from a /stats log entry."""
        try:
            stats = self.stat_analyzer.parse_stats_log(log_content)
            
            if not stats:
                return {"error": "Could not parse stats from log content"}
            
            return self.analyze_character_and_recommend(
                stats, character_name, optimization_type, budget
            )
            
        except Exception as e:
            log_event(f"[BUFF_ADVISOR] Error analyzing from stats log: {e}")
            return {"error": str(e)}

    def get_build_compatibility_report(self, stats: Dict[str, int],
                                      character_name: str = None,
                                      optimization_type: str = "balanced") -> Dict[str, Any]:
        """Get a detailed build compatibility report."""
        try:
            build_data = self.build_integration.get_build_data(character_name)
            
            if not build_data:
                return {"error": "No build data available"}
            
            validation = self.build_integration.validate_build_compatibility(
                stats, build_data, optimization_type
            )
            
            analysis = self.build_integration.analyze_with_build_context(
                stats, character_name, optimization_type
            )
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "character_name": character_name,
                "build_data": build_data,
                "validation": validation,
                "analysis": analysis,
                "compatibility_score": analysis.get("build_aware_recommendations", {}).get("compatibility_score", 0.0)
            }
            
            log_event(f"[BUFF_ADVISOR] Build compatibility report generated for {character_name}")
            return report
            
        except Exception as e:
            log_event(f"[BUFF_ADVISOR] Error getting build compatibility report: {e}")
            return {"error": str(e)}

    def export_recommendations_report(self, results: Dict[str, Any],
                                     filepath: str = None) -> str:
        """Export recommendations to a JSON file."""
        try:
            if not filepath:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                character_name = results.get("character_name", "unknown")
                filepath = f"buff_advisor_report_{character_name}_{timestamp}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            log_event(f"[BUFF_ADVISOR] Recommendations exported to {filepath}")
            return filepath
            
        except Exception as e:
            log_event(f"[BUFF_ADVISOR] Error exporting recommendations: {e}")
            return ""

    def get_recommendation_history(self, character_name: str = None) -> List[Dict[str, Any]]:
        """Get recommendation history for a character."""
        if character_name:
            return [r for r in self.recommendation_history 
                   if r.get("character_name") == character_name]
        return self.recommendation_history

    def get_cached_character_stats(self, character_name: str) -> Dict[str, Any]:
        """Get cached character stats."""
        return self.character_cache.get(character_name, {})

    def _generate_summary(self, stats: Dict[str, int],
                          stat_analysis: Dict[str, Any],
                          priorities: List[Dict[str, Any]],
                          buff_recs: Dict[str, Any],
                          template_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the analysis and recommendations."""
        try:
            summary = {
                "total_stats": stat_analysis.get("total_stats", 0),
                "average_stat": stat_analysis.get("average_stat", 0),
                "weakest_stats": stat_analysis.get("weakest_stats", []),
                "strongest_stats": stat_analysis.get("strongest_stats", []),
                "top_priorities": [p["stat"] for p in priorities[:3]],
                "buff_recommendations_count": buff_recs.get("recommendation_count", 0),
                "template_recommendations": {
                    "armor_setup": template_recs.get("armor_setup", {}).get("template_name", "Unknown"),
                    "weapon_setup": template_recs.get("weapon_setup", {}).get("weapon_name", "Unknown")
                },
                "key_recommendations": []
            }
            
            # Add key recommendations
            if priorities:
                top_priority = priorities[0]
                summary["key_recommendations"].append(
                    f"Prioritize {top_priority['stat']} buffs (current: {top_priority['current_value']})"
                )
            
            if buff_recs.get("buff_food"):
                summary["key_recommendations"].append(
                    f"Consider {len(buff_recs['buff_food'])} buff food items"
                )
            
            if buff_recs.get("entertainer_dances"):
                summary["key_recommendations"].append(
                    f"Consider {len(buff_recs['entertainer_dances'])} entertainer dances"
                )
            
            return summary
            
        except Exception as e:
            log_event(f"[BUFF_ADVISOR] Error generating summary: {e}")
            return {}


def create_buff_advisor() -> BuffAdvisor:
    """Create a new BuffAdvisor instance."""
    return BuffAdvisor() 