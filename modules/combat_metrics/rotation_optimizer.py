"""
Rotation Optimizer - Combat rotation analysis and optimization.

This module provides comprehensive rotation analysis including:
- Most efficient rotations identification
- Dead skills detection
- Rotation optimization recommendations
- Ability usage analysis
- Performance-based rotation suggestions
"""

import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


@dataclass
class RotationAnalysis:
    """Analysis results for a combat rotation."""
    rotation_id: str
    abilities_used: List[str]
    total_damage: int
    total_xp: int
    duration: float
    dps: float
    xp_per_hour: float
    efficiency_score: float
    ability_efficiency: Dict[str, float]
    recommendations: List[str]


@dataclass
class DeadSkill:
    """Information about a dead skill (rarely used ability)."""
    skill_name: str
    usage_count: int
    usage_percentage: float
    total_abilities_used: int
    last_used: Optional[datetime]
    recommended_action: str


class RotationOptimizer:
    """Advanced combat rotation optimization system."""
    
    def __init__(self, dead_skill_threshold: float = 0.05):
        """Initialize the rotation optimizer.
        
        Parameters
        ----------
        dead_skill_threshold : float
            Threshold for considering a skill "dead" (percentage of total usage)
        """
        self.dead_skill_threshold = dead_skill_threshold
        
        # Analysis storage
        self.rotation_history: List[RotationAnalysis] = []
        self.dead_skills: List[DeadSkill] = []
        
        # Performance metrics
        self.ability_performance: Dict[str, Dict[str, float]] = {}
        
        logger.info(f"RotationOptimizer initialized with dead_skill_threshold={dead_skill_threshold}")
    
    def analyze_session_rotation(self, session_data: Dict[str, Any]) -> RotationAnalysis:
        """Analyze the ability rotation used in a session.
        
        Parameters
        ----------
        session_data : dict
            Session data to analyze
            
        Returns
        -------
        RotationAnalysis
            Rotation analysis results
        """
        session_id = session_data.get("session_id", "unknown")
        abilities_used = session_data.get("abilities_used", {})
        events = session_data.get("events", [])
        
        # Extract ability usage from events
        ability_events = [
            event for event in events
            if event.get("event_type") == "ability_use" and event.get("ability_name")
        ]
        
        # Calculate rotation metrics
        total_damage = session_data.get("total_damage_dealt", 0)
        total_xp = session_data.get("total_xp_gained", 0)
        duration = session_data.get("duration", 0)
        
        dps = total_damage / duration if duration > 0 else 0
        xp_per_hour = (total_xp / duration) * 3600 if duration > 0 else 0
        
        # Calculate ability efficiency
        ability_efficiency = self._calculate_ability_efficiency(ability_events, total_damage)
        
        # Calculate overall efficiency score
        efficiency_score = self._calculate_rotation_efficiency(dps, xp_per_hour, abilities_used)
        
        # Generate recommendations
        recommendations = self._generate_rotation_recommendations(
            abilities_used, ability_efficiency, dps, xp_per_hour
        )
        
        rotation_analysis = RotationAnalysis(
            rotation_id=f"rotation_{session_id}",
            abilities_used=list(abilities_used.keys()),
            total_damage=total_damage,
            total_xp=total_xp,
            duration=duration,
            dps=dps,
            xp_per_hour=xp_per_hour,
            efficiency_score=efficiency_score,
            ability_efficiency=ability_efficiency,
            recommendations=recommendations
        )
        
        self.rotation_history.append(rotation_analysis)
        return rotation_analysis
    
    def find_dead_skills(self, sessions: List[Dict[str, Any]]) -> List[DeadSkill]:
        """Find skills that are rarely used across multiple sessions.
        
        Parameters
        ----------
        sessions : list
            List of session data to analyze
            
        Returns
        -------
        list
            List of dead skills
        """
        # Aggregate ability usage across all sessions
        total_ability_usage = Counter()
        ability_last_used = {}
        total_abilities = 0
        
        for session in sessions:
            abilities_used = session.get("abilities_used", {})
            events = session.get("events", [])
            
            # Count ability usage
            for ability, count in abilities_used.items():
                total_ability_usage[ability] += count
                total_abilities += count
            
            # Track last usage time
            for event in events:
                if event.get("event_type") == "ability_use" and event.get("ability_name"):
                    ability = event["ability_name"]
                    timestamp = datetime.fromisoformat(event["timestamp"])
                    if ability not in ability_last_used or timestamp > ability_last_used[ability]:
                        ability_last_used[ability] = timestamp
        
        # Find dead skills
        dead_skills = []
        for ability, count in total_ability_usage.items():
            usage_percentage = count / total_abilities if total_abilities > 0 else 0
            
            if usage_percentage < self.dead_skill_threshold:
                # Determine recommended action
                if usage_percentage == 0:
                    recommended_action = "Remove from rotation - never used"
                elif usage_percentage < 0.01:
                    recommended_action = "Consider removing - very rarely used"
                else:
                    recommended_action = "Review usage - low usage detected"
                
                dead_skill = DeadSkill(
                    skill_name=ability,
                    usage_count=count,
                    usage_percentage=usage_percentage * 100,
                    total_abilities_used=total_abilities,
                    last_used=ability_last_used.get(ability),
                    recommended_action=recommended_action
                )
                dead_skills.append(dead_skill)
        
        # Sort by usage percentage (lowest first)
        dead_skills.sort(key=lambda x: x.usage_percentage)
        self.dead_skills = dead_skills
        
        return dead_skills
    
    def find_most_efficient_rotations(self, sessions: List[Dict[str, Any]], 
                                    limit: int = 5) -> List[RotationAnalysis]:
        """Find the most efficient rotations from session data.
        
        Parameters
        ----------
        sessions : list
            List of session data to analyze
        limit : int
            Maximum number of rotations to return
            
        Returns
        -------
        list
            List of most efficient rotations
        """
        # Analyze rotations for all sessions
        rotations = []
        for session in sessions:
            rotation = self.analyze_session_rotation(session)
            rotations.append(rotation)
        
        # Sort by efficiency score
        rotations.sort(key=lambda x: x.efficiency_score, reverse=True)
        
        return rotations[:limit]
    
    def optimize_rotation(self, current_abilities: List[str], 
                         target_dps: float = 100.0,
                         target_xp_per_hour: float = 2000.0) -> Dict[str, Any]:
        """Generate rotation optimization recommendations.
        
        Parameters
        ----------
        current_abilities : list
            Current abilities in rotation
        target_dps : float
            Target DPS to achieve
        target_xp_per_hour : float
            Target XP per hour to achieve
            
        Returns
        -------
        dict
            Optimization recommendations
        """
        # Analyze current rotation performance
        current_performance = self._analyze_ability_performance(current_abilities)
        
        # Generate optimization strategy
        optimization = {
            "current_abilities": current_abilities,
            "target_dps": target_dps,
            "target_xp_per_hour": target_xp_per_hour,
            "current_performance": current_performance,
            "recommendations": [],
            "suggested_abilities": [],
            "priority_changes": []
        }
        
        # Analyze ability performance
        high_performing = []
        low_performing = []
        
        for ability, metrics in current_performance.items():
            if metrics.get("dps_contribution", 0) > target_dps / len(current_abilities):
                high_performing.append(ability)
            else:
                low_performing.append(ability)
        
        # Generate recommendations
        if low_performing:
            optimization["recommendations"].append(
                f"Consider replacing low-performing abilities: {', '.join(low_performing)}"
            )
        
        if len(current_abilities) < 5:
            optimization["recommendations"].append(
                "Rotation has few abilities - consider adding more for better coverage"
            )
        
        if len(current_abilities) > 10:
            optimization["recommendations"].append(
                "Rotation has many abilities - consider focusing on core abilities for consistency"
            )
        
        # Suggest ability priorities
        optimization["priority_changes"] = [
            f"Prioritize: {', '.join(high_performing)}",
            f"Review: {', '.join(low_performing)}"
        ]
        
        return optimization
    
    def analyze_ability_synergy(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well abilities work together.
        
        Parameters
        ----------
        sessions : list
            List of session data to analyze
            
        Returns
        -------
        dict
            Ability synergy analysis
        """
        # Extract ability combinations from sessions
        ability_combinations = defaultdict(int)
        ability_performance = defaultdict(list)
        
        for session in sessions:
            abilities_used = session.get("abilities_used", {})
            total_damage = session.get("total_damage_dealt", 0)
            duration = session.get("duration", 0)
            
            if duration > 0 and abilities_used:
                # Record ability combination
                combo = tuple(sorted(abilities_used.keys()))
                ability_combinations[combo] += 1
                
                # Record performance for each ability
                dps = total_damage / duration
                for ability in abilities_used:
                    ability_performance[ability].append(dps)
        
        # Find best combinations
        best_combinations = sorted(
            ability_combinations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Calculate average performance per ability
        ability_avg_performance = {}
        for ability, performances in ability_performance.items():
            if performances:
                ability_avg_performance[ability] = statistics.mean(performances)
        
        synergy_analysis = {
            "most_used_combinations": [
                {"abilities": list(combo), "usage_count": count}
                for combo, count in best_combinations
            ],
            "ability_performance": ability_avg_performance,
            "synergy_recommendations": []
        }
        
        # Generate synergy recommendations
        if ability_avg_performance:
            best_ability = max(ability_avg_performance.items(), key=lambda x: x[1])
            worst_ability = min(ability_avg_performance.items(), key=lambda x: x[1])
            
            synergy_analysis["synergy_recommendations"].extend([
                f"Best performing ability: {best_ability[0]} ({best_ability[1]:.1f} DPS)",
                f"Consider replacing: {worst_ability[0]} ({worst_ability[1]:.1f} DPS)"
            ])
        
        return synergy_analysis
    
    def get_rotation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive rotation statistics.
        
        Returns
        -------
        dict
            Rotation statistics
        """
        if not self.rotation_history:
            return {"error": "No rotation history available"}
        
        # Calculate statistics
        dps_values = [r.dps for r in self.rotation_history]
        xp_values = [r.xp_per_hour for r in self.rotation_history]
        efficiency_values = [r.efficiency_score for r in self.rotation_history]
        
        # Find most common abilities
        all_abilities = []
        for rotation in self.rotation_history:
            all_abilities.extend(rotation.abilities_used)
        
        ability_frequency = Counter(all_abilities)
        most_common_abilities = ability_frequency.most_common(5)
        
        stats = {
            "total_rotations_analyzed": len(self.rotation_history),
            "average_dps": statistics.mean(dps_values) if dps_values else 0,
            "average_xp_per_hour": statistics.mean(xp_values) if xp_values else 0,
            "average_efficiency": statistics.mean(efficiency_values) if efficiency_values else 0,
            "best_rotation": max(self.rotation_history, key=lambda x: x.efficiency_score).rotation_id if self.rotation_history else None,
            "most_common_abilities": [
                {"ability": ability, "frequency": count}
                for ability, count in most_common_abilities
            ],
            "dead_skills_found": len(self.dead_skills)
        }
        
        return stats
    
    def _calculate_ability_efficiency(self, ability_events: List[Dict[str, Any]], 
                                   total_damage: int) -> Dict[str, float]:
        """Calculate efficiency for each ability.
        
        Parameters
        ----------
        ability_events : list
            List of ability use events
        total_damage : int
            Total damage dealt
            
        Returns
        -------
        dict
            Ability efficiency metrics
        """
        ability_damage = defaultdict(int)
        ability_count = defaultdict(int)
        
        for event in ability_events:
            ability = event.get("ability_name")
            damage = event.get("damage_dealt", 0)
            
            if ability:
                ability_damage[ability] += damage
                ability_count[ability] += 1
        
        # Calculate efficiency metrics
        efficiency = {}
        for ability in ability_damage:
            count = ability_count[ability]
            total_damage_for_ability = ability_damage[ability]
            
            efficiency[ability] = {
                "avg_damage": total_damage_for_ability / count if count > 0 else 0,
                "usage_count": count,
                "damage_percentage": (total_damage_for_ability / total_damage) * 100 if total_damage > 0 else 0,
                "efficiency_score": total_damage_for_ability / count if count > 0 else 0
            }
        
        return efficiency
    
    def _calculate_rotation_efficiency(self, dps: float, xp_per_hour: float, 
                                    abilities_used: Dict[str, int]) -> float:
        """Calculate overall rotation efficiency.
        
        Parameters
        ----------
        dps : float
            Damage per second
        xp_per_hour : float
            XP per hour
        abilities_used : dict
            Abilities used and their counts
            
        Returns
        -------
        float
            Efficiency score (0.0 to 1.0)
        """
        # Normalize metrics
        dps_score = min(dps / 200.0, 1.0)  # 200 DPS = perfect
        xp_score = min(xp_per_hour / 5000.0, 1.0)  # 5000 XP/hour = perfect
        
        # Ability diversity bonus
        diversity_bonus = min(len(abilities_used) / 8.0, 1.0)  # 8 abilities = perfect diversity
        
        # Calculate efficiency
        efficiency = (dps_score * 0.6 + xp_score * 0.3 + diversity_bonus * 0.1)
        
        return max(0.0, min(1.0, efficiency))
    
    def _analyze_ability_performance(self, abilities: List[str]) -> Dict[str, Dict[str, float]]:
        """Analyze performance of specific abilities.
        
        Parameters
        ----------
        abilities : list
            List of abilities to analyze
            
        Returns
        -------
        dict
            Ability performance metrics
        """
        performance = {}
        
        for ability in abilities:
            # Find sessions where this ability was used
            ability_sessions = [
                rotation for rotation in self.rotation_history
                if ability in rotation.abilities_used
            ]
            
            if ability_sessions:
                avg_dps = statistics.mean([r.dps for r in ability_sessions])
                avg_xp = statistics.mean([r.xp_per_hour for r in ability_sessions])
                usage_frequency = len(ability_sessions) / len(self.rotation_history) if self.rotation_history else 0
                
                performance[ability] = {
                    "avg_dps": avg_dps,
                    "avg_xp_per_hour": avg_xp,
                    "usage_frequency": usage_frequency,
                    "dps_contribution": avg_dps * usage_frequency
                }
            else:
                performance[ability] = {
                    "avg_dps": 0,
                    "avg_xp_per_hour": 0,
                    "usage_frequency": 0,
                    "dps_contribution": 0
                }
        
        return performance
    
    def _generate_rotation_recommendations(self, abilities_used: Dict[str, int],
                                        ability_efficiency: Dict[str, float],
                                        dps: float, xp_per_hour: float) -> List[str]:
        """Generate rotation optimization recommendations.
        
        Parameters
        ----------
        abilities_used : dict
            Abilities used and their counts
        ability_efficiency : dict
            Efficiency metrics for each ability
        dps : float
            Current DPS
        xp_per_hour : float
            Current XP per hour
            
        Returns
        -------
        list
            List of recommendations
        """
        recommendations = []
        
        # Analyze ability usage
        if abilities_used:
            most_used = max(abilities_used.items(), key=lambda x: x[1])
            least_used = min(abilities_used.items(), key=lambda x: x[1])
            
            if most_used[1] > least_used[1] * 5:
                recommendations.append(f"Over-reliance on {most_used[0]} - consider diversifying")
            
            if least_used[1] < 2:
                recommendations.append(f"Rarely used ability: {least_used[0]} - consider removing or improving")
        
        # Analyze efficiency
        if ability_efficiency:
            best_ability = max(ability_efficiency.items(), key=lambda x: x[1].get("efficiency_score", 0))
            worst_ability = min(ability_efficiency.items(), key=lambda x: x[1].get("efficiency_score", 0))
            
            if best_ability[1].get("efficiency_score", 0) > worst_ability[1].get("efficiency_score", 0) * 2:
                recommendations.append(f"Consider focusing on {best_ability[0]} - much more efficient")
        
        # General recommendations
        if dps < 100:
            recommendations.append("Low DPS - consider upgrading abilities or equipment")
        
        if xp_per_hour < 2000:
            recommendations.append("Low XP gain - optimize for faster kills or better targets")
        
        if not recommendations:
            recommendations.append("Rotation appears well-balanced")
        
        return recommendations 