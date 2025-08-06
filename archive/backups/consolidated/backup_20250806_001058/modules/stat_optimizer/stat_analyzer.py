"""Stat Analyzer for Stat Optimizer Module.

This module analyzes character stats against optimal thresholds and provides
detailed recommendations for PvE damage, buff stacking, and healing optimization.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

class StatAnalyzer:
    """Analyzes character stats and provides optimization recommendations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the stat analyzer.
        
        Parameters
        ----------
        config : dict, optional
            Configuration for analysis settings
        """
        self.config = config or {}
        self.analysis_history = []
        
        # Analysis weights for different optimization types
        self.optimization_weights = {
            "pve_damage": {
                "strength": 0.25,
                "agility": 0.20,
                "constitution": 0.20,
                "stamina": 0.15,
                "mind": 0.10,
                "focus": 0.05,
                "willpower": 0.05
            },
            "buff_stack": {
                "strength": 0.20,
                "agility": 0.15,
                "constitution": 0.20,
                "stamina": 0.15,
                "mind": 0.15,
                "focus": 0.10,
                "willpower": 0.05
            },
            "healing": {
                "strength": 0.05,
                "agility": 0.10,
                "constitution": 0.20,
                "stamina": 0.15,
                "mind": 0.25,
                "focus": 0.20,
                "willpower": 0.05
            }
        }
        
        log_event("[STAT_ANALYZER] Initialized stat analyzer")
    
    def analyze_character_stats(self, character_stats: Dict[str, int], 
                              optimization_type: str = "pve_damage",
                              thresholds: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze character stats against optimal thresholds.
        
        Parameters
        ----------
        character_stats : dict
            Current character stats (strength, agility, etc.)
        optimization_type : str
            Type of optimization to analyze (pve_damage, buff_stack, healing)
        thresholds : dict, optional
            Stat thresholds to compare against
            
        Returns
        -------
        dict
            Comprehensive analysis results
        """
        if not thresholds:
            log_event("[STAT_ANALYZER] No thresholds provided, using defaults")
            return self._analyze_with_defaults(character_stats, optimization_type)
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "optimization_type": optimization_type,
            "character_stats": character_stats.copy(),
            "thresholds": thresholds,
            "analysis": {},
            "recommendations": [],
            "score": 0.0,
            "issues": [],
            "warnings": []
        }
        
        # Analyze each stat
        total_score = 0.0
        total_weight = 0.0
        
        for stat_name, current_value in character_stats.items():
            if stat_name not in thresholds:
                continue
                
            stat_analysis = self._analyze_single_stat(
                stat_name, current_value, thresholds[stat_name], optimization_type
            )
            
            analysis["analysis"][stat_name] = stat_analysis
            
            # Calculate weighted score
            weight = self.optimization_weights.get(optimization_type, {}).get(stat_name, 0.1)
            total_weight += weight
            total_score += stat_analysis["score"] * weight
            
            # Collect issues and warnings
            if stat_analysis["status"] == "critical":
                analysis["issues"].append(f"{stat_name}: {stat_analysis['message']}")
            elif stat_analysis["status"] == "warning":
                analysis["warnings"].append(f"{stat_name}: {stat_analysis['message']}")
        
        # Calculate overall score
        if total_weight > 0:
            analysis["score"] = total_score / total_weight
        else:
            analysis["score"] = 0.0
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        # Store analysis in history
        self.analysis_history.append(analysis)
        
        log_event(f"[STAT_ANALYZER] Analysis complete - Score: {analysis['score']:.2f}")
        return analysis
    
    def _analyze_single_stat(self, stat_name: str, current_value: int, 
                           threshold: Dict[str, int], optimization_type: str) -> Dict[str, Any]:
        """Analyze a single stat against its threshold.
        
        Parameters
        ----------
        stat_name : str
            Name of the stat being analyzed
        current_value : int
            Current value of the stat
        threshold : dict
            Threshold values (min, optimal, max)
        optimization_type : str
            Type of optimization being analyzed
            
        Returns
        -------
        dict
            Analysis results for the stat
        """
        min_val = threshold.get("min", 0)
        optimal_val = threshold.get("optimal", 100)
        max_val = threshold.get("max", 200)
        
        # Calculate percentage of optimal
        if optimal_val > 0:
            percentage = (current_value / optimal_val) * 100
        else:
            percentage = 0
        
        # Determine status and message
        if current_value < min_val:
            status = "critical"
            message = f"Below minimum threshold ({current_value} < {min_val})"
        elif current_value < optimal_val * 0.8:
            status = "warning"
            message = f"Below optimal range ({current_value} < {optimal_val * 0.8:.0f})"
        elif current_value > max_val:
            status = "warning"
            message = f"Above maximum threshold ({current_value} > {max_val})"
        elif current_value >= optimal_val * 0.9:
            status = "optimal"
            message = f"Within optimal range ({current_value} >= {optimal_val * 0.9:.0f})"
        else:
            status = "suboptimal"
            message = f"Below optimal but acceptable ({current_value} < {optimal_val})"
        
        # Calculate score (0-100)
        if current_value <= min_val:
            score = 0
        elif current_value >= optimal_val:
            score = 100
        else:
            # Linear interpolation between min and optimal
            score = ((current_value - min_val) / (optimal_val - min_val)) * 100
        
        return {
            "current_value": current_value,
            "min_threshold": min_val,
            "optimal_value": optimal_val,
            "max_threshold": max_val,
            "percentage_of_optimal": percentage,
            "status": status,
            "message": message,
            "score": score
        }
    
    def _analyze_with_defaults(self, character_stats: Dict[str, int], 
                              optimization_type: str) -> Dict[str, Any]:
        """Analyze stats using default thresholds.
        
        Parameters
        ----------
        character_stats : dict
            Current character stats
        optimization_type : str
            Type of optimization
            
        Returns
        -------
        dict
            Analysis results using default thresholds
        """
        # Use default thresholds based on optimization type
        default_thresholds = {
            "pve_damage": {
                "strength": {"min": 100, "optimal": 150, "max": 200},
                "agility": {"min": 80, "optimal": 120, "max": 160},
                "constitution": {"min": 90, "optimal": 130, "max": 180},
                "stamina": {"min": 70, "optimal": 100, "max": 140},
                "mind": {"min": 50, "optimal": 80, "max": 120},
                "focus": {"min": 60, "optimal": 90, "max": 130},
                "willpower": {"min": 40, "optimal": 70, "max": 110}
            },
            "buff_stack": {
                "strength": {"min": 120, "optimal": 170, "max": 220},
                "agility": {"min": 100, "optimal": 140, "max": 180},
                "constitution": {"min": 110, "optimal": 150, "max": 200},
                "stamina": {"min": 90, "optimal": 120, "max": 160},
                "mind": {"min": 70, "optimal": 100, "max": 140},
                "focus": {"min": 80, "optimal": 110, "max": 150},
                "willpower": {"min": 60, "optimal": 90, "max": 130}
            },
            "healing": {
                "strength": {"min": 60, "optimal": 90, "max": 130},
                "agility": {"min": 70, "optimal": 100, "max": 140},
                "constitution": {"min": 100, "optimal": 140, "max": 180},
                "stamina": {"min": 80, "optimal": 110, "max": 150},
                "mind": {"min": 120, "optimal": 160, "max": 200},
                "focus": {"min": 130, "optimal": 170, "max": 210},
                "willpower": {"min": 110, "optimal": 150, "max": 190}
            }
        }
        
        thresholds = default_thresholds.get(optimization_type, {})
        return self.analyze_character_stats(character_stats, optimization_type, thresholds)
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results.
        
        Parameters
        ----------
        analysis : dict
            Analysis results
            
        Returns
        -------
        list
            List of recommendations
        """
        recommendations = []
        optimization_type = analysis["optimization_type"]
        
        # Overall score recommendations
        score = analysis["score"]
        if score < 50:
            recommendations.append("Critical: Major stat reallocation needed")
        elif score < 70:
            recommendations.append("Warning: Significant stat improvements recommended")
        elif score < 85:
            recommendations.append("Good: Minor optimizations possible")
        else:
            recommendations.append("Excellent: Stats are well-optimized")
        
        # Specific recommendations based on optimization type
        if optimization_type == "pve_damage":
            recommendations.extend(self._get_damage_recommendations(analysis))
        elif optimization_type == "buff_stack":
            recommendations.extend(self._get_buff_recommendations(analysis))
        elif optimization_type == "healing":
            recommendations.extend(self._get_healing_recommendations(analysis))
        
        # Priority recommendations for critical issues
        critical_stats = [stat for stat, data in analysis["analysis"].items() 
                        if data["status"] == "critical"]
        if critical_stats:
            recommendations.append(f"Priority: Focus on improving {', '.join(critical_stats)}")
        
        return recommendations
    
    def _get_damage_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Get recommendations specific to PvE damage optimization."""
        recommendations = []
        
        # Check key damage stats
        strength_analysis = analysis["analysis"].get("strength", {})
        agility_analysis = analysis["analysis"].get("agility", {})
        
        if strength_analysis.get("status") in ["critical", "warning"]:
            recommendations.append("Increase Strength for better melee damage")
        
        if agility_analysis.get("status") in ["critical", "warning"]:
            recommendations.append("Improve Agility for better ranged accuracy")
        
        return recommendations
    
    def _get_buff_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Get recommendations specific to buff stacking optimization."""
        recommendations = []
        
        # Check buff-relevant stats
        constitution_analysis = analysis["analysis"].get("constitution", {})
        mind_analysis = analysis["analysis"].get("mind", {})
        
        if constitution_analysis.get("status") in ["critical", "warning"]:
            recommendations.append("Increase Constitution for better buff duration")
        
        if mind_analysis.get("status") in ["critical", "warning"]:
            recommendations.append("Improve Mind for better buff effectiveness")
        
        return recommendations
    
    def _get_healing_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Get recommendations specific to healing optimization."""
        recommendations = []
        
        # Check healing-relevant stats
        mind_analysis = analysis["analysis"].get("mind", {})
        focus_analysis = analysis["analysis"].get("focus", {})
        
        if mind_analysis.get("status") in ["critical", "warning"]:
            recommendations.append("Increase Mind for better healing power")
        
        if focus_analysis.get("status") in ["critical", "warning"]:
            recommendations.append("Improve Focus for better healing efficiency")
        
        return recommendations
    
    def get_analysis_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of analysis results.
        
        Parameters
        ----------
        analysis : dict
            Full analysis results
            
        Returns
        -------
        dict
            Summary of analysis
        """
        return {
            "optimization_type": analysis["optimization_type"],
            "overall_score": analysis["score"],
            "critical_issues": len(analysis["issues"]),
            "warnings": len(analysis["warnings"]),
            "recommendations_count": len(analysis["recommendations"]),
            "timestamp": analysis["timestamp"]
        }
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis history.
        
        Parameters
        ----------
        limit : int, optional
            Maximum number of recent analyses to return
            
        Returns
        -------
        list
            Recent analysis summaries
        """
        recent = self.analysis_history[-limit:] if self.analysis_history else []
        return [self.get_analysis_summary(analysis) for analysis in recent]


def create_stat_analyzer(config: Dict[str, Any] = None) -> StatAnalyzer:
    """Create a stat analyzer instance.
    
    Parameters
    ----------
    config : dict, optional
        Configuration for the analyzer
        
    Returns
    -------
    StatAnalyzer
        Configured analyzer instance
    """
    return StatAnalyzer(config) 