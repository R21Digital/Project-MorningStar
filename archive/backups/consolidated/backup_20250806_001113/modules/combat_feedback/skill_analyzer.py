"""Skill Analyzer for Combat Feedback Module.

This module provides functionality to analyze skill trees for stagnation,
overlap, and inefficiency that might indicate the need for a respec.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

from android_ms11.utils.logging_utils import log_event


class SkillAnalyzer:
    """Analyzes skill trees for stagnation, overlap, and inefficiency."""

    def __init__(self):
        """Initialize the skill analyzer."""
        self.skill_categories = {
            "combat": ["rifle", "pistol", "carbine", "melee", "unarmed"],
            "support": ["healing", "buffs", "debuffs", "utility"],
            "crafting": ["artisan", "chef", "architect", "weaponsmith", "armorsmith"],
            "social": ["entertainer", "trader", "politician"]
        }
        
        self.inefficiency_patterns = {
            "overlap": {
                "description": "Skills that provide similar functionality",
                "examples": ["rifle_shot", "rifle_hit", "pistol_shot", "pistol_hit"]
            },
            "redundancy": {
                "description": "Skills that are rarely used or ineffective",
                "examples": ["unused_abilities", "low_damage_skills"]
            },
            "stagnation": {
                "description": "Skills that haven't improved in recent sessions",
                "examples": ["unchanged_skills", "no_progression"]
            }
        }
        
        self.analysis_history = []
        
    def analyze_skill_tree(self, current_skills: List[str], 
                          build_skills: List[str],
                          session_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skill tree for stagnation, overlap, and inefficiency.
        
        Parameters
        ----------
        current_skills : list
            List of currently known skills
        build_skills : list
            List of skills in the current build
        session_history : list
            List of recent session data
            
        Returns
        -------
        dict
            Skill analysis results with recommendations
        """
        try:
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "current_skills": current_skills,
                "build_skills": build_skills,
                "skill_count": len(current_skills),
                "build_completion": len([s for s in build_skills if s in current_skills]) / len(build_skills) if build_skills else 0
            }
            
            # Analyze skill stagnation
            stagnation_analysis = self._analyze_skill_stagnation(current_skills, session_history)
            analysis["stagnation"] = stagnation_analysis
            
            # Analyze skill overlap
            overlap_analysis = self._analyze_skill_overlap(current_skills, build_skills)
            analysis["overlap"] = overlap_analysis
            
            # Analyze inefficiency
            inefficiency_analysis = self._analyze_skill_inefficiency(current_skills, build_skills, session_history)
            analysis["inefficiency"] = inefficiency_analysis
            
            # Generate recommendations
            recommendations = self._generate_skill_recommendations(analysis)
            analysis["recommendations"] = recommendations
            
            # Calculate overall health score
            health_score = self._calculate_skill_tree_health(analysis)
            analysis["health_score"] = health_score
            
            # Store analysis
            self.analysis_history.append(analysis)
            
            return analysis
            
        except Exception as e:
            log_event(f"[SKILL_ANALYZER] Error analyzing skill tree: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def detect_skill_stagnation(self, current_skills: List[str], 
                               session_history: List[Dict[str, Any]],
                               days_threshold: int = 7) -> Dict[str, Any]:
        """Detect if skill progression has stagnated.
        
        Parameters
        ----------
        current_skills : list
            Current known skills
        session_history : list
            Recent session history
        days_threshold : int
            Number of days to consider for stagnation
            
        Returns
        -------
        dict
            Stagnation analysis results
        """
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        recent_sessions = [
            s for s in session_history 
            if datetime.fromisoformat(s.get("timestamp", "1970-01-01")) > cutoff_date
        ]
        
        # Analyze skill progression over time
        skill_progression = self._analyze_skill_progression_timeline(current_skills, recent_sessions)
        
        # Check for stagnation indicators
        stagnation_indicators = []
        
        # Check if no new skills learned recently
        if skill_progression.get("new_skills_learned", 0) == 0:
            stagnation_indicators.append("no_recent_progression")
        
        # Check if skill usage is declining
        if skill_progression.get("skill_usage_trend", 0) < -0.1:
            stagnation_indicators.append("declining_usage")
        
        # Check if skill efficiency is flat
        if skill_progression.get("efficiency_variance", 0) < 0.05:
            stagnation_indicators.append("flat_efficiency")
        
        stagnation_detected = len(stagnation_indicators) >= 2
        
        return {
            "stagnation_detected": stagnation_detected,
            "indicators": stagnation_indicators,
            "skill_progression": skill_progression,
            "days_analyzed": days_threshold,
            "sessions_analyzed": len(recent_sessions)
        }
    
    def analyze_skill_overlap(self, current_skills: List[str], 
                            build_skills: List[str]) -> Dict[str, Any]:
        """Analyze skill overlap and redundancy.
        
        Parameters
        ----------
        current_skills : list
            Current known skills
        build_skills : list
            Skills in the current build
            
        Returns
        -------
        dict
            Overlap analysis results
        """
        overlap_groups = []
        redundant_skills = []
        
        # Group skills by category
        skill_categories = self._categorize_skills(current_skills)
        
        # Find overlapping skills within categories
        for category, skills in skill_categories.items():
            if len(skills) > 1:
                # Check for functional overlap
                overlap = self._find_functional_overlap(skills)
                if overlap:
                    overlap_groups.append({
                        "category": category,
                        "skills": overlap,
                        "description": f"Multiple {category} skills with similar function"
                    })
        
        # Find redundant skills (not in build but learned)
        redundant = [skill for skill in current_skills if skill not in build_skills]
        if redundant:
            redundant_skills = self._analyze_redundant_skills(redundant)
        
        return {
            "overlap_groups": overlap_groups,
            "redundant_skills": redundant_skills,
            "total_overlaps": len(overlap_groups),
            "total_redundant": len(redundant_skills)
        }
    
    def analyze_skill_inefficiency(self, current_skills: List[str],
                                 build_skills: List[str],
                                 session_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skill inefficiency and underutilization.
        
        Parameters
        ----------
        current_skills : list
            Current known skills
        build_skills : list
            Skills in the current build
        session_history : list
            Recent session history
            
        Returns
        -------
        dict
            Inefficiency analysis results
        """
        inefficient_skills = []
        underutilized_skills = []
        
        # Analyze skill usage patterns
        usage_patterns = self._analyze_skill_usage(current_skills, session_history)
        
        # Find inefficient skills (low damage, high cooldown, etc.)
        for skill in current_skills:
            efficiency = self._calculate_skill_efficiency(skill, session_history)
            if efficiency < 0.5:  # Less than 50% efficiency
                inefficient_skills.append({
                    "skill": skill,
                    "efficiency": efficiency,
                    "reason": "low_efficiency"
                })
        
        # Find underutilized skills (learned but rarely used)
        for skill in current_skills:
            usage_rate = usage_patterns.get(skill, {}).get("usage_rate", 0)
            if usage_rate < 0.1:  # Used in less than 10% of sessions
                underutilized_skills.append({
                    "skill": skill,
                    "usage_rate": usage_rate,
                    "reason": "underutilized"
                })
        
        return {
            "inefficient_skills": inefficient_skills,
            "underutilized_skills": underutilized_skills,
            "total_inefficient": len(inefficient_skills),
            "total_underutilized": len(underutilized_skills)
        }
    
    def _analyze_skill_stagnation(self, current_skills: List[str], 
                                 session_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skill stagnation patterns."""
        return self.detect_skill_stagnation(current_skills, session_history)
    
    def _analyze_skill_overlap(self, current_skills: List[str], 
                              build_skills: List[str]) -> Dict[str, Any]:
        """Analyze skill overlap patterns."""
        return self.analyze_skill_overlap(current_skills, build_skills)
    
    def _analyze_skill_inefficiency(self, current_skills: List[str],
                                   build_skills: List[str],
                                   session_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skill inefficiency patterns."""
        return self.analyze_skill_inefficiency(current_skills, build_skills, session_history)
    
    def _analyze_skill_progression_timeline(self, current_skills: List[str],
                                          recent_sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skill progression over time."""
        new_skills = 0
        skill_usage_trend = 0.0
        efficiency_variance = 0.0
        
        # Count new skills learned
        for session in recent_sessions:
            skills_learned = session.get("skills_learned", [])
            new_skills += len(skills_learned)
        
        # Calculate usage trend
        if len(recent_sessions) >= 2:
            usage_rates = [s.get("skill_usage_rate", 0) for s in recent_sessions]
            skill_usage_trend = self._calculate_trend(usage_rates)
        
        # Calculate efficiency variance
        if len(recent_sessions) >= 3:
            efficiency_scores = [s.get("skill_efficiency", 0) for s in recent_sessions]
            efficiency_variance = self._calculate_variance(efficiency_scores)
        
        return {
            "new_skills_learned": new_skills,
            "skill_usage_trend": skill_usage_trend,
            "efficiency_variance": efficiency_variance,
            "sessions_analyzed": len(recent_sessions)
        }
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills by type."""
        categories = {}
        
        for skill in skills:
            category = self._determine_skill_category(skill)
            if category not in categories:
                categories[category] = []
            categories[category].append(skill)
        
        return categories
    
    def _determine_skill_category(self, skill: str) -> str:
        """Determine the category of a skill."""
        skill_lower = skill.lower()
        
        for category, keywords in self.skill_categories.items():
            for keyword in keywords:
                if keyword in skill_lower:
                    return category
        
        return "other"
    
    def _find_functional_overlap(self, skills: List[str]) -> List[str]:
        """Find skills with functional overlap."""
        overlap = []
        
        # Simple overlap detection based on skill names
        for i, skill1 in enumerate(skills):
            for skill2 in skills[i+1:]:
                if self._skills_overlap(skill1, skill2):
                    if skill1 not in overlap:
                        overlap.append(skill1)
                    if skill2 not in overlap:
                        overlap.append(skill2)
        
        return overlap
    
    def _skills_overlap(self, skill1: str, skill2: str) -> bool:
        """Check if two skills have functional overlap."""
        # Simple overlap detection based on skill name patterns
        skill1_lower = skill1.lower()
        skill2_lower = skill2.lower()
        
        # Check for similar weapon types
        weapon_types = ["rifle", "pistol", "carbine", "melee"]
        for weapon in weapon_types:
            if weapon in skill1_lower and weapon in skill2_lower:
                return True
        
        # Check for similar action types
        action_types = ["shot", "hit", "strike", "attack"]
        for action in action_types:
            if action in skill1_lower and action in skill2_lower:
                return True
        
        return False
    
    def _analyze_redundant_skills(self, redundant_skills: List[str]) -> List[Dict[str, Any]]:
        """Analyze redundant skills."""
        analysis = []
        
        for skill in redundant_skills:
            analysis.append({
                "skill": skill,
                "category": self._determine_skill_category(skill),
                "reason": "not_in_build"
            })
        
        return analysis
    
    def _analyze_skill_usage(self, skills: List[str], 
                            session_history: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze skill usage patterns."""
        usage_patterns = {}
        
        for skill in skills:
            usage_count = 0
            total_sessions = len(session_history)
            
            for session in session_history:
                skills_used = session.get("skills_used", [])
                if skill in skills_used:
                    usage_count += 1
            
            usage_rate = usage_count / total_sessions if total_sessions > 0 else 0
            
            usage_patterns[skill] = {
                "usage_count": usage_count,
                "usage_rate": usage_rate,
                "total_sessions": total_sessions
            }
        
        return usage_patterns
    
    def _calculate_skill_efficiency(self, skill: str, 
                                  session_history: List[Dict[str, Any]]) -> float:
        """Calculate efficiency of a specific skill."""
        # Placeholder efficiency calculation
        # In a real implementation, this would analyze damage output, cooldown usage, etc.
        return 0.7  # Default 70% efficiency
    
    def _generate_skill_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on skill analysis."""
        recommendations = []
        
        # Stagnation recommendations
        if analysis.get("stagnation", {}).get("stagnation_detected", False):
            recommendations.append("💡 Consider respeccing to focus on underutilized skills")
            recommendations.append("💡 Review skill rotation for efficiency improvements")
        
        # Overlap recommendations
        overlap_count = analysis.get("overlap", {}).get("total_overlaps", 0)
        if overlap_count > 0:
            recommendations.append("💡 Consider removing overlapping skills to optimize build")
        
        # Inefficiency recommendations
        inefficient_count = analysis.get("inefficiency", {}).get("total_inefficient", 0)
        if inefficient_count > 0:
            recommendations.append("💡 Review inefficient skills for potential replacement")
        
        # Health score recommendations
        health_score = analysis.get("health_score", 0)
        if health_score < 0.6:
            recommendations.append("💡 Skill tree health is low - consider respec")
        elif health_score < 0.8:
            recommendations.append("💡 Skill tree could benefit from optimization")
        
        return recommendations
    
    def _calculate_skill_tree_health(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall health score of the skill tree."""
        health_score = 1.0
        
        # Penalize for stagnation
        if analysis.get("stagnation", {}).get("stagnation_detected", False):
            health_score -= 0.2
        
        # Penalize for overlap
        overlap_count = analysis.get("overlap", {}).get("total_overlaps", 0)
        health_score -= overlap_count * 0.1
        
        # Penalize for inefficiency
        inefficient_count = analysis.get("inefficiency", {}).get("total_inefficient", 0)
        health_score -= inefficient_count * 0.05
        
        return max(0.0, health_score)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend of values."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * val for i, val in enumerate(values))
        x2_sum = sum(i * i for i in range(n))
        
        if n * x2_sum - x_sum * x_sum == 0:
            return 0.0
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance


def create_skill_analyzer() -> SkillAnalyzer:
    """Create a new SkillAnalyzer instance."""
    return SkillAnalyzer() 