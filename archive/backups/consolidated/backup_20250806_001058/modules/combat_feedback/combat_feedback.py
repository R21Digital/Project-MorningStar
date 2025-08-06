"""Combat Feedback - Main interface for combat feedback and respec tracking.

This module provides the main interface for the combat feedback system,
orchestrating session comparison, skill analysis, and respec recommendations.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from android_ms11.utils.logging_utils import log_event

from .session_comparator import SessionComparator
from .skill_analyzer import SkillAnalyzer
from .respec_advisor import RespecAdvisor
from .performance_tracker import PerformanceTracker


class CombatFeedback:
    """Main interface for combat feedback and respec tracking system."""

    def __init__(self, data_dir: str = "data/combat_feedback"):
        """Initialize the combat feedback system.
        
        Parameters
        ----------
        data_dir : str
            Directory for storing performance data
        """
        self.session_comparator = SessionComparator()
        self.skill_analyzer = SkillAnalyzer()
        self.respec_advisor = RespecAdvisor()
        self.performance_tracker = PerformanceTracker(data_dir)
        
        self.feedback_history = []
        
        log_event("[COMBAT_FEEDBACK] Combat feedback system initialized")
    
    def analyze_combat_session(self, session_data: Dict[str, Any],
                             current_skills: List[str] = None,
                             build_skills: List[str] = None) -> Dict[str, Any]:
        """Analyze a combat session and provide feedback.
        
        Parameters
        ----------
        session_data : dict
            Current session data with performance metrics
        current_skills : list, optional
            List of currently known skills
        build_skills : list, optional
            List of skills in the current build
            
        Returns
        -------
        dict
            Comprehensive combat feedback analysis
        """
        try:
            # Record the session
            self.performance_tracker.record_session(session_data)
            
            # Get performance history for comparison
            recent_sessions = self.performance_tracker.get_performance_history(days=7)
            
            # Compare with previous sessions
            session_comparison = self.session_comparator.compare_sessions(
                session_data, recent_sessions[:-1]  # Exclude current session
            )
            
            # Analyze skill tree if skills provided
            skill_analysis = None
            if current_skills and build_skills:
                skill_analysis = self.skill_analyzer.analyze_skill_tree(
                    current_skills, build_skills, recent_sessions
                )
            
            # Get respec recommendations
            respec_analysis = self.respec_advisor.analyze_respec_needs(
                session_comparison, skill_analysis or {}, session_data
            )
            
            # Generate comprehensive feedback
            feedback = {
                "timestamp": datetime.now().isoformat(),
                "session_id": session_data.get("session_id", "unknown"),
                "session_comparison": session_comparison,
                "skill_analysis": skill_analysis,
                "respec_analysis": respec_analysis,
                "alerts": [],
                "recommendations": []
            }
            
            # Collect alerts
            if session_comparison.get("alerts"):
                feedback["alerts"].extend(session_comparison["alerts"])
            
            if skill_analysis and skill_analysis.get("recommendations"):
                feedback["alerts"].extend(skill_analysis["recommendations"])
            
            if respec_analysis.get("recommendations"):
                feedback["alerts"].extend(respec_analysis["recommendations"])
            
            # Collect recommendations
            if session_comparison.get("recommendations"):
                feedback["recommendations"].extend(session_comparison["recommendations"])
            
            if respec_analysis.get("alternative_suggestions"):
                feedback["recommendations"].extend(respec_analysis["alternative_suggestions"])
            
            # Store feedback
            self.feedback_history.append(feedback)
            
            return feedback
            
        except Exception as e:
            log_event(f"[COMBAT_FEEDBACK] Error analyzing combat session: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_performance_feedback(self, days: int = 7) -> Dict[str, Any]:
        """Get performance feedback for the specified period.
        
        Parameters
        ----------
        days : int
            Number of days to analyze
            
        Returns
        -------
        dict
            Performance feedback summary
        """
        try:
            # Get performance summary
            performance_summary = self.performance_tracker.get_performance_summary(days)
            
            # Get performance trends
            performance_trends = self.performance_tracker.calculate_performance_trends(days)
            
            # Get recent sessions for comparison
            recent_sessions = self.performance_tracker.get_performance_history(days)
            
            # Detect anomalies
            anomalies = self.performance_tracker.detect_performance_anomalies(days)
            
            # Generate feedback
            feedback = {
                "timestamp": datetime.now().isoformat(),
                "days_analyzed": days,
                "performance_summary": performance_summary,
                "performance_trends": performance_trends,
                "anomalies": anomalies,
                "sessions_analyzed": len(recent_sessions),
                "alerts": [],
                "recommendations": []
            }
            
            # Generate alerts based on trends
            if performance_trends.get("trends"):
                trends = performance_trends["trends"]
                
                if trends.get("dps", 0) < -0.1:  # DPS declining
                    feedback["alerts"].append("⚠️ DPS trend is declining")
                
                if trends.get("efficiency", 0) < -0.1:  # Efficiency declining
                    feedback["alerts"].append("⚠️ Combat efficiency is declining")
                
                if trends.get("xp_per_hour", 0) < -0.1:  # XP rate declining
                    feedback["alerts"].append("⚠️ XP rate is declining")
            
            # Generate recommendations
            if anomalies.get("anomalies"):
                feedback["recommendations"].append("💡 Investigate performance anomalies")
            
            if performance_summary.get("dps", {}).get("trend", 0) < 0:
                feedback["recommendations"].append("💡 Consider optimizing combat rotation")
            
            return feedback
            
        except Exception as e:
            log_event(f"[COMBAT_FEEDBACK] Error getting performance feedback: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_respec_recommendations(self, current_build: Dict[str, Any],
                                 current_skills: List[str] = None) -> Dict[str, Any]:
        """Get detailed respec recommendations.
        
        Parameters
        ----------
        current_build : dict
            Current build information
        current_skills : list, optional
            List of currently known skills
            
        Returns
        -------
        dict
            Detailed respec recommendations
        """
        try:
            # Get performance history
            performance_history = self.performance_tracker.get_performance_history(days=30)
            
            # Create skill data
            skill_data = {
                "current_skills": current_skills or [],
                "build_skills": current_build.get("skills", []),
                "stagnation_detected": False,
                "stagnation_indicators": [],
                "overlap_count": 0,
                "inefficient_count": 0,
                "underutilized_count": 0,
                "health_score": 0.8  # Default health score
            }
            
            # Analyze skill tree if skills provided
            if current_skills:
                skill_analysis = self.skill_analyzer.analyze_skill_tree(
                    current_skills, current_build.get("skills", []), performance_history
                )
                
                # Update skill data with analysis results
                skill_data.update({
                    "stagnation_detected": skill_analysis.get("stagnation", {}).get("stagnation_detected", False),
                    "stagnation_indicators": skill_analysis.get("stagnation", {}).get("indicators", []),
                    "overlap_count": skill_analysis.get("overlap", {}).get("total_overlaps", 0),
                    "inefficient_count": skill_analysis.get("inefficiency", {}).get("total_inefficient", 0),
                    "underutilized_count": skill_analysis.get("inefficiency", {}).get("total_underutilized", 0),
                    "health_score": skill_analysis.get("health_score", 0.8)
                })
            
            # Get respec recommendations
            recommendations = self.respec_advisor.get_respec_recommendations(
                current_build, performance_history, skill_data
            )
            
            return recommendations
            
        except Exception as e:
            log_event(f"[COMBAT_FEEDBACK] Error getting respec recommendations: {e}")
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
        return self.respec_advisor.check_respec_urgency(analysis)
    
    def export_feedback_report(self, output_file: str = None) -> str:
        """Export a comprehensive feedback report.
        
        Parameters
        ----------
        output_file : str, optional
            Output file path (defaults to timestamped file)
            
        Returns
        -------
        str
            Path to exported report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"combat_feedback_report_{timestamp}.json"
        
        report_data = {
            "export_timestamp": datetime.now().isoformat(),
            "feedback_history": self.feedback_history,
            "performance_summary": self.performance_tracker.get_performance_summary(days=30),
            "performance_trends": self.performance_tracker.calculate_performance_trends(days=7),
            "anomalies": self.performance_tracker.detect_performance_anomalies(days=7)
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        log_event(f"[COMBAT_FEEDBACK] Exported feedback report to: {output_file}")
        return output_file
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get a summary of recent feedback.
        
        Returns
        -------
        dict
            Feedback summary
        """
        recent_feedback = self.feedback_history[-10:] if self.feedback_history else []
        
        summary = {
            "total_feedback_entries": len(self.feedback_history),
            "recent_feedback_count": len(recent_feedback),
            "alerts_generated": sum(len(f.get("alerts", [])) for f in recent_feedback),
            "recommendations_generated": sum(len(f.get("recommendations", [])) for f in recent_feedback),
            "respec_recommendations": sum(1 for f in recent_feedback if f.get("respec_analysis", {}).get("respec_recommended", False))
        }
        
        return summary
    
    def clear_history(self) -> None:
        """Clear feedback history."""
        self.feedback_history.clear()
        log_event("[COMBAT_FEEDBACK] Feedback history cleared")


def create_combat_feedback(data_dir: str = "data/combat_feedback") -> CombatFeedback:
    """Create a new CombatFeedback instance."""
    return CombatFeedback(data_dir) 