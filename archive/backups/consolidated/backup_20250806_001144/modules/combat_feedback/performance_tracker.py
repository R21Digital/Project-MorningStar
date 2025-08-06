"""Performance Tracker for Combat Feedback Module.

This module provides functionality to track combat performance over time
and maintain historical data for performance analysis and respec recommendations.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from android_ms11.utils.logging_utils import log_event


class PerformanceTracker:
    """Tracks combat performance over time and maintains historical data."""

    def __init__(self, data_dir: str = "data/combat_feedback"):
        """Initialize the performance tracker.
        
        Parameters
        ----------
        data_dir : str
            Directory to store performance data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.performance_history = []
        self.session_cache = {}
        
        # Load existing data
        self._load_performance_data()
        
    def record_session(self, session_data: Dict[str, Any]) -> bool:
        """Record a new combat session.
        
        Parameters
        ----------
        session_data : dict
            Session data including performance metrics
            
        Returns
        -------
        bool
            True if session recorded successfully
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in session_data:
                session_data["timestamp"] = datetime.now().isoformat()
            
            # Generate session ID if not present
            if "session_id" not in session_data:
                session_data["session_id"] = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Calculate additional metrics
            session_data = self._calculate_session_metrics(session_data)
            
            # Store in memory
            self.performance_history.append(session_data)
            
            # Cache for quick access
            self.session_cache[session_data["session_id"]] = session_data
            
            # Save to disk
            self._save_performance_data()
            
            log_event(f"[PERFORMANCE_TRACKER] Recorded session: {session_data['session_id']}")
            return True
            
        except Exception as e:
            log_event(f"[PERFORMANCE_TRACKER] Error recording session: {e}")
            return False
    
    def get_performance_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get performance history for the specified number of days.
        
        Parameters
        ----------
        days : int
            Number of days to look back
            
        Returns
        -------
        list
            List of session data for the specified period
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_sessions = [
            session for session in self.performance_history
            if datetime.fromisoformat(session.get("timestamp", "1970-01-01")) > cutoff_date
        ]
        
        return recent_sessions
    
    def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session by ID.
        
        Parameters
        ----------
        session_id : str
            Session ID to retrieve
            
        Returns
        -------
        dict or None
            Session data if found, None otherwise
        """
        return self.session_cache.get(session_id)
    
    def calculate_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Calculate performance trends over the specified period.
        
        Parameters
        ----------
        days : int
            Number of days to analyze
            
        Returns
        -------
        dict
            Performance trend analysis
        """
        recent_sessions = self.get_performance_history(days)
        
        if len(recent_sessions) < 2:
            return {
                "status": "insufficient_data",
                "message": f"Need at least 2 sessions, found {len(recent_sessions)}",
                "trends": {}
            }
        
        # Calculate trends for key metrics
        trends = {}
        
        # DPS trend
        dps_values = [s.get("dps", 0) for s in recent_sessions]
        trends["dps"] = self._calculate_trend(dps_values)
        
        # XP per hour trend
        xp_values = [s.get("xp_per_hour", 0) for s in recent_sessions]
        trends["xp_per_hour"] = self._calculate_trend(xp_values)
        
        # Efficiency trend
        efficiency_values = [s.get("efficiency_score", 0) for s in recent_sessions]
        trends["efficiency"] = self._calculate_trend(efficiency_values)
        
        # Damage per hour trend
        damage_values = [s.get("damage_per_hour", 0) for s in recent_sessions]
        trends["damage_per_hour"] = self._calculate_trend(damage_values)
        
        return {
            "status": "trends_calculated",
            "sessions_analyzed": len(recent_sessions),
            "days_analyzed": days,
            "trends": trends
        }
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get a summary of performance over the specified period.
        
        Parameters
        ----------
        days : int
            Number of days to summarize
            
        Returns
        -------
        dict
            Performance summary
        """
        recent_sessions = self.get_performance_history(days)
        
        if not recent_sessions:
            return {
                "status": "no_data",
                "message": "No sessions found for the specified period"
            }
        
        # Calculate summary statistics
        dps_values = [s.get("dps", 0) for s in recent_sessions]
        xp_values = [s.get("xp_per_hour", 0) for s in recent_sessions]
        efficiency_values = [s.get("efficiency_score", 0) for s in recent_sessions]
        
        summary = {
            "status": "summary_calculated",
            "sessions_count": len(recent_sessions),
            "days_analyzed": days,
            "dps": {
                "average": sum(dps_values) / len(dps_values) if dps_values else 0,
                "min": min(dps_values) if dps_values else 0,
                "max": max(dps_values) if dps_values else 0,
                "trend": self._calculate_trend(dps_values)
            },
            "xp_per_hour": {
                "average": sum(xp_values) / len(xp_values) if xp_values else 0,
                "min": min(xp_values) if xp_values else 0,
                "max": max(xp_values) if xp_values else 0,
                "trend": self._calculate_trend(xp_values)
            },
            "efficiency": {
                "average": sum(efficiency_values) / len(efficiency_values) if efficiency_values else 0,
                "min": min(efficiency_values) if efficiency_values else 0,
                "max": max(efficiency_values) if efficiency_values else 0,
                "trend": self._calculate_trend(efficiency_values)
            }
        }
        
        return summary
    
    def detect_performance_anomalies(self, days: int = 7) -> Dict[str, Any]:
        """Detect performance anomalies in recent sessions.
        
        Parameters
        ----------
        days : int
            Number of days to analyze
            
        Returns
        -------
        dict
            Anomaly detection results
        """
        recent_sessions = self.get_performance_history(days)
        
        if len(recent_sessions) < 3:
            return {
                "status": "insufficient_data",
                "message": "Need at least 3 sessions for anomaly detection",
                "anomalies": []
            }
        
        anomalies = []
        
        # Calculate baseline metrics
        dps_values = [s.get("dps", 0) for s in recent_sessions]
        xp_values = [s.get("xp_per_hour", 0) for s in recent_sessions]
        
        if dps_values:
            avg_dps = sum(dps_values) / len(dps_values)
            dps_std = self._calculate_std(dps_values)
            
            # Check for DPS anomalies (2 standard deviations from mean)
            for session in recent_sessions:
                session_dps = session.get("dps", 0)
                if abs(session_dps - avg_dps) > 2 * dps_std:
                    anomalies.append({
                        "session_id": session.get("session_id"),
                        "timestamp": session.get("timestamp"),
                        "type": "dps_anomaly",
                        "value": session_dps,
                        "expected_range": f"{avg_dps - 2*dps_std:.1f} - {avg_dps + 2*dps_std:.1f}"
                    })
        
        if xp_values:
            avg_xp = sum(xp_values) / len(xp_values)
            xp_std = self._calculate_std(xp_values)
            
            # Check for XP anomalies
            for session in recent_sessions:
                session_xp = session.get("xp_per_hour", 0)
                if abs(session_xp - avg_xp) > 2 * xp_std:
                    anomalies.append({
                        "session_id": session.get("session_id"),
                        "timestamp": session.get("timestamp"),
                        "type": "xp_anomaly",
                        "value": session_xp,
                        "expected_range": f"{avg_xp - 2*xp_std:.1f} - {avg_xp + 2*xp_std:.1f}"
                    })
        
        return {
            "status": "anomalies_detected",
            "sessions_analyzed": len(recent_sessions),
            "anomalies_found": len(anomalies),
            "anomalies": anomalies
        }
    
    def export_performance_data(self, output_file: str = None) -> str:
        """Export performance data to a file.
        
        Parameters
        ----------
        output_file : str, optional
            Output file path (defaults to timestamped file)
            
        Returns
        -------
        str
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.data_dir / f"performance_export_{timestamp}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_sessions": len(self.performance_history),
            "sessions": self.performance_history
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        log_event(f"[PERFORMANCE_TRACKER] Exported data to: {output_file}")
        return str(output_file)
    
    def _calculate_session_metrics(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional metrics for a session."""
        # Calculate efficiency score if not present
        if "efficiency_score" not in session_data:
            dps = session_data.get("dps", 0)
            xp_per_hour = session_data.get("xp_per_hour", 0)
            kills = session_data.get("kills", 0)
            deaths = session_data.get("deaths", 0)
            
            # Simple efficiency calculation
            efficiency = 0.0
            if dps > 0 and xp_per_hour > 0:
                efficiency = min(1.0, (dps * xp_per_hour) / (kills + 1) / (deaths + 1))
            
            session_data["efficiency_score"] = efficiency
        
        # Calculate damage per hour if not present
        if "damage_per_hour" not in session_data:
            dps = session_data.get("dps", 0)
            duration = session_data.get("duration", 0)
            
            if duration > 0:
                session_data["damage_per_hour"] = dps * 3600 / duration
            else:
                session_data["damage_per_hour"] = 0
        
        return session_data
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend of values (positive = increasing, negative = decreasing)."""
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
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation of values."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _load_performance_data(self) -> None:
        """Load performance data from disk."""
        data_file = self.data_dir / "performance_history.json"
        
        if data_file.exists():
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                self.performance_history = data.get("sessions", [])
                
                # Rebuild cache
                for session in self.performance_history:
                    if "session_id" in session:
                        self.session_cache[session["session_id"]] = session
                
                log_event(f"[PERFORMANCE_TRACKER] Loaded {len(self.performance_history)} sessions")
                
            except Exception as e:
                log_event(f"[PERFORMANCE_TRACKER] Error loading performance data: {e}")
    
    def _save_performance_data(self) -> None:
        """Save performance data to disk."""
        data_file = self.data_dir / "performance_history.json"
        
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "total_sessions": len(self.performance_history),
                "sessions": self.performance_history
            }
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            log_event(f"[PERFORMANCE_TRACKER] Error saving performance data: {e}")


def create_performance_tracker(data_dir: str = "data/combat_feedback") -> PerformanceTracker:
    """Create a new PerformanceTracker instance."""
    return PerformanceTracker(data_dir) 