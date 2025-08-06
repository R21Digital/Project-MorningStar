"""Respec Advisor for Combat Feedback Module.

This module provides recommendations for when a respec might be beneficial
based on performance analysis, skill stagnation, and build inefficiency.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from android_ms11.utils.logging_utils import log_event


class RespecAdvisor:
    """Provides respec recommendations based on performance analysis."""

    def __init__(self):
        """Initialize the respec advisor."""
        self.respec_thresholds = {
            "critical_performance_drop": 0.25,  # 25% DPS drop
            "stagnation_days": 7,               # 7 days without improvement
            "skill_overlap_count": 3,           # 3+ overlapping skills
            "inefficiency_score": 0.6,          # 60% efficiency threshold
            "health_score_threshold": 0.7       # 70% health score threshold
        }
        
        self.respec_reasons = {
            "performance_drop": "Significant performance decline detected",
            "skill_stagnation": "Skill progression has stagnated",
            "build_inefficiency": "Current build shows inefficiency",
            "overlap_issues": "Too many overlapping skills",
            "health_decline": "Overall skill tree health is poor"
        }
        
        self.recommendation_history = []
        
    def analyze_respec_needs(self, session_comparison: Dict[str, Any],
                           skill_analysis: Dict[str, Any],
                           performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze whether a respec is recommended.
        
        Parameters
        ----------
        session_comparison : dict
            Results from session comparison analysis
        skill_analysis : dict
            Results from skill tree analysis
        performance_metrics : dict
            Current performance metrics
            
        Returns
        -------
        dict
            Respec analysis with recommendations
        """
        try:
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "respec_recommended": False,
                "confidence": 0.0,
                "reasons": [],
                "recommendations": [],
                "alternative_suggestions": []
            }
            
            # Check for performance drop
            performance_reason = self._check_performance_drop(session_comparison)
            if performance_reason:
                analysis["reasons"].append(performance_reason)
            
            # Check for skill stagnation
            stagnation_reason = self._check_skill_stagnation(skill_analysis)
            if stagnation_reason:
                analysis["reasons"].append(stagnation_reason)
            
            # Check for build inefficiency
            inefficiency_reason = self._check_build_inefficiency(skill_analysis)
            if inefficiency_reason:
                analysis["reasons"].append(inefficiency_reason)
            
            # Check for overlap issues
            overlap_reason = self._check_overlap_issues(skill_analysis)
            if overlap_reason:
                analysis["reasons"].append(overlap_reason)
            
            # Check for health decline
            health_reason = self._check_health_decline(skill_analysis)
            if health_reason:
                analysis["reasons"].append(health_reason)
            
            # Determine if respec is recommended
            analysis["respec_recommended"] = len(analysis["reasons"]) >= 2
            
            # Calculate confidence based on number and severity of issues
            analysis["confidence"] = self._calculate_respec_confidence(analysis["reasons"])
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_respec_recommendations(analysis)
            
            # Generate alternative suggestions
            analysis["alternative_suggestions"] = self._generate_alternative_suggestions(analysis)
            
            # Store recommendation
            self.recommendation_history.append(analysis)
            
            return analysis
            
        except Exception as e:
            log_event(f"[RESPEC_ADVISOR] Error analyzing respec needs: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_respec_recommendations(self, current_build: Dict[str, Any],
                                 performance_history: List[Dict[str, Any]],
                                 skill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific respec recommendations based on current situation.
        
        Parameters
        ----------
        current_build : dict
            Current build information
        performance_history : list
            History of performance data
        skill_data : dict
            Current skill information
            
        Returns
        -------
        dict
            Detailed respec recommendations
        """
        try:
            # Analyze current situation
            session_comparison = self._create_session_comparison(performance_history)
            skill_analysis = self._create_skill_analysis(skill_data)
            performance_metrics = self._extract_performance_metrics(performance_history)
            
            # Get respec analysis
            respec_analysis = self.analyze_respec_needs(session_comparison, skill_analysis, performance_metrics)
            
            # Generate specific recommendations
            specific_recommendations = self._generate_specific_recommendations(
                respec_analysis, current_build, skill_data
            )
            
            return {
                "respec_analysis": respec_analysis,
                "specific_recommendations": specific_recommendations,
                "build_suggestions": self._suggest_alternative_builds(current_build, skill_data),
                "timing_recommendations": self._suggest_respec_timing(respec_analysis)
            }
            
        except Exception as e:
            log_event(f"[RESPEC_ADVISOR] Error getting respec recommendations: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_respec_urgency(self, analysis: Dict[str, Any]) -> str:
        """Check the urgency level of a respec recommendation.
        
        Parameters
        ----------
        analysis : dict
            Respec analysis results
            
        Returns
        -------
        str
            Urgency level: "critical", "high", "medium", "low", "none"
        """
        if not analysis.get("respec_recommended", False):
            return "none"
        
        confidence = analysis.get("confidence", 0.0)
        reasons = analysis.get("reasons", [])
        
        # Check for critical issues
        critical_indicators = [
            "performance_drop" in str(reasons),
            confidence >= 0.8,
            len(reasons) >= 3
        ]
        
        if any(critical_indicators):
            return "critical"
        elif confidence >= 0.6:
            return "high"
        elif confidence >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _check_performance_drop(self, session_comparison: Dict[str, Any]) -> Optional[str]:
        """Check for significant performance drop."""
        comparison = session_comparison.get("comparison", {})
        
        if "dps" in comparison:
            dps_change = comparison["dps"]["change_percentage"]
            if dps_change <= -self.respec_thresholds["critical_performance_drop"]:
                return {
                    "type": "performance_drop",
                    "severity": "critical",
                    "description": f"DPS dropped {abs(dps_change)*100:.1f}%",
                    "threshold": self.respec_thresholds["critical_performance_drop"]
                }
        
        return None
    
    def _check_skill_stagnation(self, skill_analysis: Dict[str, Any]) -> Optional[str]:
        """Check for skill stagnation."""
        stagnation = skill_analysis.get("stagnation", {})
        
        if stagnation.get("stagnation_detected", False):
            indicators = stagnation.get("indicators", [])
            return {
                "type": "skill_stagnation",
                "severity": "high",
                "description": f"Skill stagnation detected: {', '.join(indicators)}",
                "days_analyzed": stagnation.get("days_analyzed", 0)
            }
        
        return None
    
    def _check_build_inefficiency(self, skill_analysis: Dict[str, Any]) -> Optional[str]:
        """Check for build inefficiency."""
        inefficiency = skill_analysis.get("inefficiency", {})
        total_inefficient = inefficiency.get("total_inefficient", 0)
        total_underutilized = inefficiency.get("total_underutilized", 0)
        
        if total_inefficient + total_underutilized >= 3:
            return {
                "type": "build_inefficiency",
                "severity": "medium",
                "description": f"{total_inefficient} inefficient, {total_underutilized} underutilized skills",
                "total_issues": total_inefficient + total_underutilized
            }
        
        return None
    
    def _check_overlap_issues(self, skill_analysis: Dict[str, Any]) -> Optional[str]:
        """Check for skill overlap issues."""
        overlap = skill_analysis.get("overlap", {})
        total_overlaps = overlap.get("total_overlaps", 0)
        
        if total_overlaps >= self.respec_thresholds["skill_overlap_count"]:
            return {
                "type": "overlap_issues",
                "severity": "medium",
                "description": f"{total_overlaps} overlapping skill groups detected",
                "overlap_count": total_overlaps
            }
        
        return None
    
    def _check_health_decline(self, skill_analysis: Dict[str, Any]) -> Optional[str]:
        """Check for overall skill tree health decline."""
        health_score = skill_analysis.get("health_score", 1.0)
        
        if health_score < self.respec_thresholds["health_score_threshold"]:
            return {
                "type": "health_decline",
                "severity": "high",
                "description": f"Skill tree health score: {health_score:.2f}",
                "health_score": health_score
            }
        
        return None
    
    def _calculate_respec_confidence(self, reasons: List[Dict[str, Any]]) -> float:
        """Calculate confidence level for respec recommendation."""
        if not reasons:
            return 0.0
        
        # Base confidence on number of reasons
        base_confidence = min(len(reasons) * 0.3, 0.9)
        
        # Adjust based on severity
        severity_multiplier = 1.0
        for reason in reasons:
            severity = reason.get("severity", "medium")
            if severity == "critical":
                severity_multiplier += 0.2
            elif severity == "high":
                severity_multiplier += 0.1
        
        return min(base_confidence * severity_multiplier, 1.0)
    
    def _generate_respec_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate respec recommendations."""
        recommendations = []
        
        if analysis.get("respec_recommended", False):
            confidence = analysis.get("confidence", 0.0)
            
            if confidence >= 0.8:
                recommendations.append("🚨 Strong respec recommendation - multiple critical issues detected")
            elif confidence >= 0.6:
                recommendations.append("⚠️ Respec recommended - significant performance issues detected")
            else:
                recommendations.append("💡 Consider respec - some optimization opportunities identified")
            
            # Add specific recommendations based on reasons
            reasons = analysis.get("reasons", [])
            for reason in reasons:
                reason_type = reason.get("type", "")
                if reason_type == "performance_drop":
                    recommendations.append("💡 Focus on damage-dealing skills in respec")
                elif reason_type == "skill_stagnation":
                    recommendations.append("💡 Consider different skill progression path")
                elif reason_type == "build_inefficiency":
                    recommendations.append("💡 Remove inefficient skills, add complementary ones")
                elif reason_type == "overlap_issues":
                    recommendations.append("💡 Consolidate overlapping skills into focused build")
        
        return recommendations
    
    def _generate_alternative_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate alternative suggestions before respec."""
        suggestions = []
        
        if not analysis.get("respec_recommended", False):
            return suggestions
        
        # Suggest alternatives to respec
        suggestions.append("💡 Try different ability rotation before respec")
        suggestions.append("💡 Review gear and buff optimization")
        suggestions.append("💡 Consider different farming locations")
        suggestions.append("💡 Experiment with different combat strategies")
        
        return suggestions
    
    def _create_session_comparison(self, performance_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create session comparison data."""
        if len(performance_history) < 2:
            return {"comparison": {}}
        
        current = performance_history[-1]
        previous = performance_history[-2]
        
        return {
            "comparison": {
                "dps": {
                    "current": current.get("dps", 0),
                    "previous": previous.get("dps", 0),
                    "change_percentage": (current.get("dps", 0) - previous.get("dps", 0)) / max(previous.get("dps", 1), 1)
                }
            }
        }
    
    def _create_skill_analysis(self, skill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create skill analysis data."""
        return {
            "stagnation": {
                "stagnation_detected": skill_data.get("stagnation_detected", False),
                "indicators": skill_data.get("stagnation_indicators", [])
            },
            "overlap": {
                "total_overlaps": skill_data.get("overlap_count", 0)
            },
            "inefficiency": {
                "total_inefficient": skill_data.get("inefficient_count", 0),
                "total_underutilized": skill_data.get("underutilized_count", 0)
            },
            "health_score": skill_data.get("health_score", 1.0)
        }
    
    def _extract_performance_metrics(self, performance_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract performance metrics from history."""
        if not performance_history:
            return {}
        
        latest = performance_history[-1]
        return {
            "dps": latest.get("dps", 0),
            "xp_per_hour": latest.get("xp_per_hour", 0),
            "efficiency": latest.get("efficiency_score", 0)
        }
    
    def _generate_specific_recommendations(self, analysis: Dict[str, Any],
                                        current_build: Dict[str, Any],
                                        skill_data: Dict[str, Any]) -> List[str]:
        """Generate specific respec recommendations."""
        recommendations = []
        
        if not analysis.get("respec_recommended", False):
            return recommendations
        
        # Add build-specific recommendations
        build_type = current_build.get("type", "unknown")
        if build_type == "rifleman":
            recommendations.append("💡 Consider focusing on rifle specialization")
        elif build_type == "medic":
            recommendations.append("💡 Balance healing and combat skills")
        
        # Add skill-specific recommendations
        inefficient_skills = skill_data.get("inefficient_skills", [])
        if inefficient_skills:
            recommendations.append(f"💡 Remove {len(inefficient_skills)} inefficient skills")
        
        return recommendations
    
    def _suggest_alternative_builds(self, current_build: Dict[str, Any],
                                  skill_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest alternative builds."""
        suggestions = []
        
        current_type = current_build.get("type", "unknown")
        
        # Suggest complementary builds
        if current_type == "rifleman":
            suggestions.append({
                "name": "Rifleman + Medic",
                "description": "Add healing capabilities",
                "focus": "balanced_combat_healing"
            })
        elif current_type == "medic":
            suggestions.append({
                "name": "Medic + Rifleman",
                "description": "Add ranged combat",
                "focus": "healing_with_combat"
            })
        
        return suggestions
    
    def _suggest_respec_timing(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest optimal timing for respec."""
        urgency = self.check_respec_urgency(analysis)
        
        timing_suggestions = {
            "critical": "Immediate respec recommended",
            "high": "Respec within 1-2 sessions",
            "medium": "Consider respec after current session",
            "low": "Monitor performance, respec if issues persist",
            "none": "No respec needed at this time"
        }
        
        return {
            "urgency": urgency,
            "recommendation": timing_suggestions.get(urgency, "Monitor performance"),
            "confidence": analysis.get("confidence", 0.0)
        }


def create_respec_advisor() -> RespecAdvisor:
    """Create a new RespecAdvisor instance."""
    return RespecAdvisor() 