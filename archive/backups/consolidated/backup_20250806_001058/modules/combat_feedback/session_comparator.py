"""Session Comparator for Combat Feedback Module.

This module provides functionality to compare combat performance across sessions
and detect significant performance changes that might indicate the need for a respec.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from android_ms11.utils.logging_utils import log_event


class SessionComparator:
    """Compares combat performance across sessions and detects significant changes."""

    def __init__(self):
        """Initialize the session comparator."""
        self.performance_thresholds = {
            "critical_drop": 0.25,  # 25% drop triggers critical alert
            "warning_drop": 0.15,   # 15% drop triggers warning
            "improvement": 0.10,    # 10% improvement is notable
            "stagnation_days": 7    # 7 days without improvement = stagnation
        }
        
        self.comparison_history = []
        
    def compare_sessions(self, current_session: Dict[str, Any], 
                        previous_sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare current session performance with previous sessions.
        
        Parameters
        ----------
        current_session : dict
            Current session data with performance metrics
        previous_sessions : list
            List of previous session data for comparison
            
        Returns
        -------
        dict
            Comparison results with alerts and recommendations
        """
        try:
            if not previous_sessions:
                return {
                    "status": "no_comparison_data",
                    "message": "No previous sessions available for comparison",
                    "alerts": [],
                    "recommendations": []
                }
            
            # Calculate current session metrics
            current_metrics = self._extract_session_metrics(current_session)
            
            # Calculate average of previous sessions
            previous_metrics = self._calculate_average_metrics(previous_sessions)
            
            # Compare metrics
            comparison = self._compare_metrics(current_metrics, previous_metrics)
            
            # Generate alerts
            alerts = self._generate_alerts(comparison)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(comparison, current_metrics, previous_metrics)
            
            # Store comparison
            comparison_data = {
                "timestamp": datetime.now().isoformat(),
                "current_session": current_session.get("session_id", "unknown"),
                "comparison": comparison,
                "alerts": alerts,
                "recommendations": recommendations
            }
            self.comparison_history.append(comparison_data)
            
            return {
                "status": "comparison_complete",
                "comparison": comparison,
                "alerts": alerts,
                "recommendations": recommendations,
                "current_metrics": current_metrics,
                "previous_metrics": previous_metrics
            }
            
        except Exception as e:
            log_event(f"[SESSION_COMPARATOR] Error comparing sessions: {e}")
            return {
                "status": "error",
                "error": str(e),
                "alerts": [],
                "recommendations": []
            }
    
    def detect_performance_drop(self, current_dps: float, previous_dps: float) -> Tuple[str, float]:
        """Detect if there's a significant performance drop.
        
        Parameters
        ----------
        current_dps : float
            Current session DPS
        previous_dps : float
            Previous session average DPS
            
        Returns
        -------
        tuple
            (alert_level, drop_percentage)
        """
        if previous_dps == 0:
            return "no_data", 0.0
            
        drop_percentage = (previous_dps - current_dps) / previous_dps
        
        if drop_percentage >= self.performance_thresholds["critical_drop"]:
            return "critical", drop_percentage
        elif drop_percentage >= self.performance_thresholds["warning_drop"]:
            return "warning", drop_percentage
        else:
            return "normal", drop_percentage
    
    def detect_skill_stagnation(self, sessions: List[Dict[str, Any]], 
                               days_threshold: int = None) -> Dict[str, Any]:
        """Detect if skill progression has stagnated.
        
        Parameters
        ----------
        sessions : list
            List of recent sessions
        days_threshold : int, optional
            Number of days to consider for stagnation (defaults to self.thresholds)
            
        Returns
        -------
        dict
            Stagnation analysis results
        """
        if days_threshold is None:
            days_threshold = self.performance_thresholds["stagnation_days"]
            
        # Filter sessions to recent period
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        recent_sessions = [
            s for s in sessions 
            if datetime.fromisoformat(s.get("timestamp", "1970-01-01")) > cutoff_date
        ]
        
        if len(recent_sessions) < 2:
            return {
                "stagnation_detected": False,
                "reason": "insufficient_data",
                "sessions_analyzed": len(recent_sessions)
            }
        
        # Analyze skill progression
        skill_progression = self._analyze_skill_progression(recent_sessions)
        
        # Check for stagnation indicators
        stagnation_indicators = []
        
        # Check if DPS has been flat
        dps_values = [s.get("dps", 0) for s in recent_sessions]
        if len(dps_values) >= 3:
            dps_variance = self._calculate_variance(dps_values)
            if dps_variance < 0.05:  # Less than 5% variance
                stagnation_indicators.append("dps_flat")
        
        # Check if XP rate has been declining
        xp_rates = [s.get("xp_per_hour", 0) for s in recent_sessions]
        if len(xp_rates) >= 3:
            xp_trend = self._calculate_trend(xp_rates)
            if xp_trend < -0.1:  # Declining trend
                stagnation_indicators.append("xp_declining")
        
        # Check if no new skills learned
        if skill_progression.get("new_skills_learned", 0) == 0:
            stagnation_indicators.append("no_skill_progression")
        
        stagnation_detected = len(stagnation_indicators) >= 2
        
        return {
            "stagnation_detected": stagnation_detected,
            "indicators": stagnation_indicators,
            "skill_progression": skill_progression,
            "sessions_analyzed": len(recent_sessions),
            "days_analyzed": days_threshold
        }
    
    def _extract_session_metrics(self, session: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics from a session."""
        return {
            "dps": session.get("dps", 0.0),
            "xp_per_hour": session.get("xp_per_hour", 0.0),
            "damage_per_hour": session.get("damage_per_hour", 0.0),
            "kills": session.get("kills", 0),
            "deaths": session.get("deaths", 0),
            "efficiency": session.get("efficiency_score", 0.0),
            "duration": session.get("duration", 0.0)
        }
    
    def _calculate_average_metrics(self, sessions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average metrics across multiple sessions."""
        if not sessions:
            return {}
        
        metrics_sum = {}
        metrics_count = {}
        
        for session in sessions:
            session_metrics = self._extract_session_metrics(session)
            for key, value in session_metrics.items():
                if key not in metrics_sum:
                    metrics_sum[key] = 0.0
                    metrics_count[key] = 0
                metrics_sum[key] += value
                metrics_count[key] += 1
        
        return {
            key: metrics_sum[key] / metrics_count[key] 
            for key in metrics_sum.keys()
        }
    
    def _compare_metrics(self, current: Dict[str, float], 
                        previous: Dict[str, float]) -> Dict[str, Any]:
        """Compare current metrics with previous average."""
        comparison = {}
        
        for metric in current.keys():
            if metric in previous:
                current_val = current[metric]
                previous_val = previous[metric]
                
                if previous_val != 0:
                    change_percentage = (current_val - previous_val) / previous_val
                else:
                    change_percentage = 0.0
                
                comparison[metric] = {
                    "current": current_val,
                    "previous": previous_val,
                    "change_percentage": change_percentage,
                    "improved": change_percentage > 0,
                    "declined": change_percentage < 0
                }
        
        return comparison
    
    def _generate_alerts(self, comparison: Dict[str, Any]) -> List[str]:
        """Generate alerts based on performance comparison."""
        alerts = []
        
        for metric, data in comparison.items():
            change_pct = data["change_percentage"]
            
            if metric == "dps" and change_pct <= -self.performance_thresholds["critical_drop"]:
                alerts.append(f"⚠️ Combat output dropped {abs(change_pct)*100:.1f}% vs last session")
            elif metric == "dps" and change_pct <= -self.performance_thresholds["warning_drop"]:
                alerts.append(f"⚠️ Combat output dropped {abs(change_pct)*100:.1f}% vs last session")
            elif metric == "efficiency" and change_pct <= -self.performance_thresholds["warning_drop"]:
                alerts.append(f"⚠️ Combat efficiency dropped {abs(change_pct)*100:.1f}%")
            elif metric == "xp_per_hour" and change_pct <= -self.performance_thresholds["warning_drop"]:
                alerts.append(f"⚠️ XP rate dropped {abs(change_pct)*100:.1f}%")
        
        return alerts
    
    def _generate_recommendations(self, comparison: Dict[str, Any], 
                                current_metrics: Dict[str, float],
                                previous_metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on performance analysis."""
        recommendations = []
        
        # Check for significant DPS drop
        if "dps" in comparison:
            dps_change = comparison["dps"]["change_percentage"]
            if dps_change <= -self.performance_thresholds["critical_drop"]:
                recommendations.append("💡 Suggest trying a new build?")
                recommendations.append("💡 Consider reviewing ability rotation")
                recommendations.append("💡 Check if gear needs upgrading")
        
        # Check for efficiency issues
        if "efficiency" in comparison:
            eff_change = comparison["efficiency"]["change_percentage"]
            if eff_change <= -self.performance_thresholds["warning_drop"]:
                recommendations.append("💡 Review combat strategy")
                recommendations.append("💡 Consider different target selection")
        
        # Check for XP rate issues
        if "xp_per_hour" in comparison:
            xp_change = comparison["xp_per_hour"]["change_percentage"]
            if xp_change <= -self.performance_thresholds["warning_drop"]:
                recommendations.append("💡 Consider different farming locations")
                recommendations.append("💡 Review XP optimization strategy")
        
        return recommendations
    
    def _analyze_skill_progression(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skill progression across sessions."""
        new_skills = 0
        skill_changes = []
        
        for session in sessions:
            skills_learned = session.get("skills_learned", [])
            new_skills += len(skills_learned)
            if skills_learned:
                skill_changes.extend(skills_learned)
        
        return {
            "new_skills_learned": new_skills,
            "skill_changes": skill_changes,
            "sessions_with_progression": len([s for s in sessions if s.get("skills_learned", [])])
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (positive = increasing, negative = decreasing)."""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * val for i, val in enumerate(values))
        x2_sum = sum(i * i for i in range(n))
        
        if n * x2_sum - x_sum * x_sum == 0:
            return 0.0
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope


def create_session_comparator() -> SessionComparator:
    """Create a new SessionComparator instance."""
    return SessionComparator() 