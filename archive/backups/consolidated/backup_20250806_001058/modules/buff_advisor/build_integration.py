"""Build Integration for Buff Advisor Module.

This module integrates the buff advisor with the build awareness system
from Batch 070 to provide comprehensive recommendations.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from android_ms11.utils.logging_utils import log_event


class BuildIntegration:
    """Integrates buff advisor with build awareness system."""

    def __init__(self):
        """Initialize the build integration system."""
        self.build_awareness = None
        self.stat_optimizer = None
        
        # Try to import build awareness components
        try:
            from core.build_aware_behavior import BuildAwareBehavior
            self.build_awareness = BuildAwareBehavior()
            log_event("[BUILD_INTEGRATION] Build awareness system loaded")
        except ImportError:
            log_event("[BUILD_INTEGRATION] Build awareness system not available")
        
        # Try to import stat optimizer components
        try:
            from modules.stat_optimizer import StatOptimizer
            self.stat_optimizer = StatOptimizer()
            log_event("[BUILD_INTEGRATION] Stat optimizer system loaded")
        except ImportError:
            log_event("[BUILD_INTEGRATION] Stat optimizer system not available")

    def get_build_data(self, character_name: str = None) -> Dict[str, Any]:
        """Get current build data from build awareness system."""
        try:
            if not self.build_awareness:
                return {}
            
            # Get current build data
            build_data = self.build_awareness.get_current_build_data()
            
            if character_name:
                build_data["character_name"] = character_name
            
            log_event(f"[BUILD_INTEGRATION] Retrieved build data for {character_name or 'current character'}")
            return build_data
            
        except Exception as e:
            log_event(f"[BUILD_INTEGRATION] Error getting build data: {e}")
            return {}

    def analyze_with_build_context(self, stats: Dict[str, int],
                                   character_name: str = None,
                                   optimization_type: str = "balanced") -> Dict[str, Any]:
        """Analyze stats with build context from Batch 070."""
        try:
            build_data = self.get_build_data(character_name)
            
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "character_name": character_name,
                "stats": stats,
                "build_data": build_data,
                "optimization_type": optimization_type,
                "build_aware_recommendations": {}
            }
            
            # Add build-specific analysis
            if build_data:
                analysis["build_aware_recommendations"] = self._analyze_build_compatibility(
                    stats, build_data, optimization_type
                )
            
            log_event(f"[BUILD_INTEGRATION] Build-aware analysis complete for {character_name}")
            return analysis
            
        except Exception as e:
            log_event(f"[BUILD_INTEGRATION] Error in build-aware analysis: {e}")
            return {}

    def get_comprehensive_recommendations(self, stats: Dict[str, int],
                                         character_name: str = None,
                                         optimization_type: str = "balanced",
                                         budget: str = "medium") -> Dict[str, Any]:
        """Get comprehensive recommendations including build awareness."""
        try:
            # Get build data
            build_data = self.get_build_data(character_name)
            
            # Get stat optimizer analysis if available
            stat_analysis = {}
            if self.stat_optimizer:
                stat_analysis = self.stat_optimizer.optimize_character_stats(
                    stats, character_name, optimization_type
                )
            
            # Build-aware analysis
            build_analysis = self.analyze_with_build_context(
                stats, character_name, optimization_type
            )
            
            comprehensive = {
                "timestamp": datetime.now().isoformat(),
                "character_name": character_name,
                "optimization_type": optimization_type,
                "budget": budget,
                "stats": stats,
                "build_data": build_data,
                "stat_analysis": stat_analysis,
                "build_analysis": build_analysis,
                "recommendations": {
                    "build_compatible": build_analysis.get("build_aware_recommendations", {}),
                    "stat_optimized": stat_analysis.get("recommendations", [])
                }
            }
            
            log_event(f"[BUILD_INTEGRATION] Comprehensive recommendations generated for {character_name}")
            return comprehensive
            
        except Exception as e:
            log_event(f"[BUILD_INTEGRATION] Error getting comprehensive recommendations: {e}")
            return {}

    def validate_build_compatibility(self, stats: Dict[str, int],
                                    build_data: Dict[str, Any],
                                    optimization_type: str = "balanced") -> Dict[str, Any]:
        """Validate if current stats are compatible with the build."""
        try:
            validation = {
                "compatible": True,
                "issues": [],
                "warnings": [],
                "suggestions": []
            }
            
            if not build_data:
                validation["compatible"] = False
                validation["issues"].append("No build data available")
                return validation
            
            # Check profession compatibility
            if "professions" in build_data:
                professions = build_data["professions"]
                validation.update(self._validate_profession_compatibility(stats, professions))
            
            # Check weapon compatibility
            if "weapons" in build_data:
                weapons = build_data["weapons"]
                validation.update(self._validate_weapon_compatibility(stats, weapons))
            
            # Check combat style compatibility
            if "combat_style" in build_data:
                combat_style = build_data["combat_style"]
                validation.update(self._validate_combat_style_compatibility(stats, combat_style))
            
            log_event(f"[BUILD_INTEGRATION] Build compatibility validation complete")
            return validation
            
        except Exception as e:
            log_event(f"[BUILD_INTEGRATION] Error validating build compatibility: {e}")
            return {"compatible": False, "issues": [f"Validation error: {e}"]}

    def _analyze_build_compatibility(self, stats: Dict[str, int],
                                     build_data: Dict[str, Any],
                                     optimization_type: str) -> Dict[str, Any]:
        """Analyze compatibility between stats and build data."""
        try:
            analysis = {
                "compatibility_score": 0.0,
                "missing_stats": [],
                "optimal_stats": [],
                "recommendations": []
            }
            
            if not build_data:
                return analysis
            
            # Calculate compatibility score
            total_score = 0
            stat_count = 0
            
            for stat_name, stat_value in stats.items():
                if stat_value > 0:
                    stat_count += 1
                    # Basic scoring: higher stats = better compatibility
                    score = min(stat_value / 150.0, 1.0)  # Cap at 150 for scoring
                    total_score += score
            
            if stat_count > 0:
                analysis["compatibility_score"] = total_score / stat_count
            
            # Identify missing stats for build
            if "professions" in build_data:
                professions = build_data["professions"]
                analysis["missing_stats"] = self._identify_missing_stats(stats, professions)
                analysis["optimal_stats"] = self._identify_optimal_stats(stats, professions)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_build_recommendations(
                stats, build_data, analysis
            )
            
            return analysis
            
        except Exception as e:
            log_event(f"[BUILD_INTEGRATION] Error analyzing build compatibility: {e}")
            return {}

    def _validate_profession_compatibility(self, stats: Dict[str, int], 
                                          professions: List[str]) -> Dict[str, Any]:
        """Validate if stats are suitable for the professions."""
        issues = []
        warnings = []
        suggestions = []
        
        for profession in professions:
            if profession == "rifleman":
                if stats.get("agility", 0) < 100:
                    warnings.append(f"Low agility ({stats.get('agility', 0)}) for rifleman")
                if stats.get("stamina", 0) < 80:
                    suggestions.append("Consider buffing stamina for rifleman")
                    
            elif profession == "pistoleer":
                if stats.get("agility", 0) < 90:
                    warnings.append(f"Low agility ({stats.get('agility', 0)}) for pistoleer")
                    
            elif profession in ["medic", "doctor"]:
                if stats.get("mind", 0) < 100:
                    warnings.append(f"Low mind ({stats.get('mind', 0)}) for {profession}")
                if stats.get("focus", 0) < 90:
                    suggestions.append(f"Consider buffing focus for {profession}")
        
        return {"issues": issues, "warnings": warnings, "suggestions": suggestions}

    def _validate_weapon_compatibility(self, stats: Dict[str, int], 
                                      weapons: List[str]) -> Dict[str, Any]:
        """Validate if stats are suitable for the weapons."""
        issues = []
        warnings = []
        suggestions = []
        
        for weapon in weapons:
            if weapon in ["rifle", "carbine"]:
                if stats.get("agility", 0) < 100:
                    warnings.append(f"Low agility ({stats.get('agility', 0)}) for {weapon}")
                    
            elif weapon == "pistol":
                if stats.get("agility", 0) < 90:
                    warnings.append(f"Low agility ({stats.get('agility', 0)}) for pistol")
                    
            elif weapon in ["sword", "melee"]:
                if stats.get("strength", 0) < 100:
                    warnings.append(f"Low strength ({stats.get('strength', 0)}) for {weapon}")
        
        return {"issues": issues, "warnings": warnings, "suggestions": suggestions}

    def _validate_combat_style_compatibility(self, stats: Dict[str, int], 
                                            combat_style: str) -> Dict[str, Any]:
        """Validate if stats are suitable for the combat style."""
        issues = []
        warnings = []
        suggestions = []
        
        if combat_style == "ranged":
            if stats.get("agility", 0) < 100:
                warnings.append(f"Low agility ({stats.get('agility', 0)}) for ranged combat")
                
        elif combat_style == "melee":
            if stats.get("strength", 0) < 100:
                warnings.append(f"Low strength ({stats.get('strength', 0)}) for melee combat")
                
        elif combat_style == "support":
            if stats.get("mind", 0) < 100:
                warnings.append(f"Low mind ({stats.get('mind', 0)}) for support role")
            if stats.get("focus", 0) < 90:
                suggestions.append("Consider buffing focus for support role")
        
        return {"issues": issues, "warnings": warnings, "suggestions": suggestions}

    def _identify_missing_stats(self, stats: Dict[str, int], 
                                professions: List[str]) -> List[str]:
        """Identify stats that are missing for the professions."""
        missing = []
        
        for profession in professions:
            if profession == "rifleman":
                if stats.get("agility", 0) < 100:
                    missing.append("agility")
                if stats.get("stamina", 0) < 80:
                    missing.append("stamina")
                    
            elif profession == "pistoleer":
                if stats.get("agility", 0) < 90:
                    missing.append("agility")
                    
            elif profession in ["medic", "doctor"]:
                if stats.get("mind", 0) < 100:
                    missing.append("mind")
                if stats.get("focus", 0) < 90:
                    missing.append("focus")
        
        return list(set(missing))  # Remove duplicates

    def _identify_optimal_stats(self, stats: Dict[str, int], 
                                professions: List[str]) -> List[str]:
        """Identify stats that are optimal for the professions."""
        optimal = []
        
        for profession in professions:
            if profession == "rifleman":
                if stats.get("agility", 0) >= 120:
                    optimal.append("agility")
                if stats.get("stamina", 0) >= 100:
                    optimal.append("stamina")
                    
            elif profession == "pistoleer":
                if stats.get("agility", 0) >= 110:
                    optimal.append("agility")
                    
            elif profession in ["medic", "doctor"]:
                if stats.get("mind", 0) >= 120:
                    optimal.append("mind")
                if stats.get("focus", 0) >= 110:
                    optimal.append("focus")
        
        return list(set(optimal))  # Remove duplicates

    def _generate_build_recommendations(self, stats: Dict[str, int],
                                        build_data: Dict[str, Any],
                                        analysis: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on build analysis."""
        recommendations = []
        
        if analysis["compatibility_score"] < 0.7:
            recommendations.append("Consider buffing to improve build compatibility")
        
        if analysis["missing_stats"]:
            missing_str = ", ".join(analysis["missing_stats"])
            recommendations.append(f"Prioritize buffing: {missing_str}")
        
        if "professions" in build_data:
            professions = build_data["professions"]
            if "rifleman" in professions and stats.get("agility", 0) < 100:
                recommendations.append("Focus on agility buffs for rifleman effectiveness")
            elif "medic" in professions and stats.get("mind", 0) < 100:
                recommendations.append("Focus on mind buffs for healing effectiveness")
        
        return recommendations


def create_build_integration() -> BuildIntegration:
    """Create a new BuildIntegration instance."""
    return BuildIntegration() 