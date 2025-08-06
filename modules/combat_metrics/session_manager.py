"""
Combat Session Manager - Session history and management system.

This module provides comprehensive session management including:
- Session history tracking
- Session loading and saving
- Session comparison and analysis
- Session statistics aggregation
- Performance trending
"""

import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class SessionSummary:
    """Summary statistics for a combat session."""
    session_id: str
    start_time: datetime
    end_time: datetime
    duration: float
    total_damage_dealt: int
    total_xp_gained: int
    kills: int
    deaths: int
    average_dps: float
    xp_per_hour: float
    damage_per_hour: float
    abilities_used: Dict[str, int]
    targets_engaged: List[str]
    session_state: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data


class CombatSessionManager:
    """Comprehensive combat session management system."""
    
    def __init__(self, logs_dir: str = "logs/combat"):
        """Initialize the session manager.
        
        Parameters
        ----------
        logs_dir : str
            Directory containing combat session logs
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Session storage
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_summaries: Dict[str, SessionSummary] = {}
        
        # Statistics
        self.total_sessions = 0
        self.total_duration = 0.0
        self.total_damage_dealt = 0
        self.total_xp_gained = 0
        self.total_kills = 0
        self.total_deaths = 0
        
        # Load existing sessions
        self._load_existing_sessions()
        
        logger.info(f"CombatSessionManager initialized with {len(self.sessions)} existing sessions")
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a session from file.
        
        Parameters
        ----------
        session_id : str
            ID of the session to load
            
        Returns
        -------
        dict, optional
            Session data if found
        """
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Try to load from file
        filename = f"combat_stats_{session_id}.json"
        filepath = self.logs_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Session file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                session_data = json.load(f)
            
            self.sessions[session_id] = session_data
            self._create_session_summary(session_data)
            
            logger.info(f"Loaded session: {session_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """Save a session to file.
        
        Parameters
        ----------
        session_data : dict
            Session data to save
            
        Returns
        -------
        bool
            True if saved successfully
        """
        session_id = session_data.get("session_id")
        if not session_id:
            logger.error("Session data missing session_id")
            return False
        
        try:
            # Save to memory
            self.sessions[session_id] = session_data
            
            # Create summary
            self._create_session_summary(session_data)
            
            # Save to file
            filename = f"combat_stats_{session_id}.json"
            filepath = self.logs_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"Saved session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")
            return False
    
    def get_session_summary(self, session_id: str) -> Optional[SessionSummary]:
        """Get summary for a specific session.
        
        Parameters
        ----------
        session_id : str
            ID of the session
            
        Returns
        -------
        SessionSummary, optional
            Session summary if found
        """
        if session_id not in self.session_summaries:
            # Try to load the session
            if not self.load_session(session_id):
                return None
        
        return self.session_summaries.get(session_id)
    
    def get_recent_sessions(self, limit: int = 10) -> List[SessionSummary]:
        """Get recent sessions ordered by start time.
        
        Parameters
        ----------
        limit : int
            Maximum number of sessions to return
            
        Returns
        -------
        list
            List of recent session summaries
        """
        summaries = list(self.session_summaries.values())
        summaries.sort(key=lambda x: x.start_time, reverse=True)
        return summaries[:limit]
    
    def get_sessions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[SessionSummary]:
        """Get sessions within a date range.
        
        Parameters
        ----------
        start_date : datetime
            Start of date range
        end_date : datetime
            End of date range
            
        Returns
        -------
        list
            Sessions within the date range
        """
        summaries = []
        for summary in self.session_summaries.values():
            if start_date <= summary.start_time <= end_date:
                summaries.append(summary)
        
        summaries.sort(key=lambda x: x.start_time)
        return summaries
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get comprehensive session statistics.
        
        Returns
        -------
        dict
            Session statistics
        """
        if not self.session_summaries:
            return {"error": "No sessions available"}
        
        # Calculate statistics
        durations = [s.duration for s in self.session_summaries.values()]
        damages = [s.total_damage_dealt for s in self.session_summaries.values()]
        xp_gains = [s.total_xp_gained for s in self.session_summaries.values()]
        dps_values = [s.average_dps for s in self.session_summaries.values()]
        xp_rates = [s.xp_per_hour for s in self.session_summaries.values()]
        
        stats = {
            "total_sessions": len(self.session_summaries),
            "total_duration": sum(durations),
            "total_damage_dealt": sum(damages),
            "total_xp_gained": sum(xp_gains),
            "total_kills": sum(s.kills for s in self.session_summaries.values()),
            "total_deaths": sum(s.deaths for s in self.session_summaries.values()),
            "average_session_duration": statistics.mean(durations) if durations else 0,
            "average_damage_per_session": statistics.mean(damages) if damages else 0,
            "average_xp_per_session": statistics.mean(xp_gains) if xp_gains else 0,
            "average_dps": statistics.mean(dps_values) if dps_values else 0,
            "average_xp_per_hour": statistics.mean(xp_rates) if xp_rates else 0,
            "best_dps_session": max(self.session_summaries.values(), key=lambda x: x.average_dps).session_id if self.session_summaries else None,
            "longest_session": max(self.session_summaries.values(), key=lambda x: x.duration).session_id if self.session_summaries else None,
            "most_xp_session": max(self.session_summaries.values(), key=lambda x: x.total_xp_gained).session_id if self.session_summaries else None
        }
        
        return stats
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get performance trends over the specified period.
        
        Parameters
        ----------
        days : int
            Number of days to analyze
            
        Returns
        -------
        dict
            Performance trends
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        recent_sessions = self.get_sessions_by_date_range(start_date, end_date)
        
        if not recent_sessions:
            return {"error": f"No sessions found in the last {days} days"}
        
        # Group sessions by day
        daily_stats = defaultdict(list)
        for session in recent_sessions:
            day_key = session.start_time.date()
            daily_stats[day_key].append(session)
        
        # Calculate daily averages
        daily_averages = {}
        for day, sessions in daily_stats.items():
            daily_averages[str(day)] = {
                "sessions": len(sessions),
                "avg_dps": statistics.mean([s.average_dps for s in sessions]),
                "avg_xp_per_hour": statistics.mean([s.xp_per_hour for s in sessions]),
                "total_damage": sum(s.total_damage_dealt for s in sessions),
                "total_xp": sum(s.total_xp_gained for s in sessions)
            }
        
        # Calculate trends
        dps_values = [s.average_dps for s in recent_sessions]
        xp_values = [s.xp_per_hour for s in recent_sessions]
        
        trends = {
            "dps_trend": "improving" if len(dps_values) > 1 and dps_values[-1] > dps_values[0] else "declining" if len(dps_values) > 1 and dps_values[-1] < dps_values[0] else "stable",
            "xp_trend": "improving" if len(xp_values) > 1 and xp_values[-1] > xp_values[0] else "declining" if len(xp_values) > 1 and xp_values[-1] < xp_values[0] else "stable",
            "sessions_per_day": len(recent_sessions) / days,
            "daily_averages": daily_averages
        }
        
        return trends
    
    def compare_sessions(self, session_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple sessions.
        
        Parameters
        ----------
        session_ids : list
            List of session IDs to compare
            
        Returns
        -------
        dict
            Session comparison results
        """
        if len(session_ids) < 2:
            return {"error": "Need at least 2 sessions to compare"}
        
        summaries = []
        for session_id in session_ids:
            summary = self.get_session_summary(session_id)
            if summary:
                summaries.append(summary)
        
        if len(summaries) < 2:
            return {"error": "Could not load enough sessions for comparison"}
        
        # Calculate comparison metrics
        comparison = {
            "sessions_compared": len(summaries),
            "duration_range": {
                "min": min(s.duration for s in summaries),
                "max": max(s.duration for s in summaries),
                "avg": statistics.mean(s.duration for s in summaries)
            },
            "dps_range": {
                "min": min(s.average_dps for s in summaries),
                "max": max(s.average_dps for s in summaries),
                "avg": statistics.mean(s.average_dps for s in summaries)
            },
            "xp_per_hour_range": {
                "min": min(s.xp_per_hour for s in summaries),
                "max": max(s.xp_per_hour for s in summaries),
                "avg": statistics.mean(s.xp_per_hour for s in summaries)
            },
            "best_performing_session": max(summaries, key=lambda x: x.average_dps).session_id,
            "most_efficient_session": max(summaries, key=lambda x: x.xp_per_hour).session_id
        }
        
        return comparison
    
    def find_dead_skills(self, threshold: float = 0.05) -> List[str]:
        """Find skills that are rarely used (dead skills).
        
        Parameters
        ----------
        threshold : float
            Usage threshold (percentage of total ability uses)
            
        Returns
        -------
        list
            List of dead skill names
        """
        if not self.session_summaries:
            return []
        
        # Aggregate ability usage across all sessions
        total_ability_usage = defaultdict(int)
        total_abilities = 0
        
        for summary in self.session_summaries.values():
            for ability, count in summary.abilities_used.items():
                total_ability_usage[ability] += count
                total_abilities += count
        
        if total_abilities == 0:
            return []
        
        # Find abilities below threshold
        dead_skills = []
        for ability, count in total_ability_usage.items():
            usage_percentage = count / total_abilities
            if usage_percentage < threshold:
                dead_skills.append(ability)
        
        return dead_skills
    
    def get_most_efficient_rotations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Find the most efficient ability rotations.
        
        Parameters
        ----------
        limit : int
            Maximum number of rotations to return
            
        Returns
        -------
        list
            List of efficient rotations
        """
        if not self.session_summaries:
            return []
        
        # Calculate efficiency for each session
        session_efficiencies = []
        for summary in self.session_summaries.values():
            if summary.duration > 0:
                efficiency = {
                    "session_id": summary.session_id,
                    "dps": summary.average_dps,
                    "xp_per_hour": summary.xp_per_hour,
                    "damage_per_hour": summary.damage_per_hour,
                    "efficiency_score": (summary.average_dps * 0.6) + (summary.xp_per_hour * 0.4),
                    "abilities_used": summary.abilities_used,
                    "duration": summary.duration
                }
                session_efficiencies.append(efficiency)
        
        # Sort by efficiency score
        session_efficiencies.sort(key=lambda x: x["efficiency_score"], reverse=True)
        
        return session_efficiencies[:limit]
    
    def _load_existing_sessions(self) -> None:
        """Load existing session files from the logs directory."""
        if not self.logs_dir.exists():
            return
        
        for filepath in self.logs_dir.glob("combat_stats_*.json"):
            try:
                with open(filepath, 'r') as f:
                    session_data = json.load(f)
                
                session_id = session_data.get("session_id")
                if session_id:
                    self.sessions[session_id] = session_data
                    self._create_session_summary(session_data)
                
            except Exception as e:
                logger.error(f"Error loading session file {filepath}: {e}")
    
    def _create_session_summary(self, session_data: Dict[str, Any]) -> None:
        """Create a session summary from session data.
        
        Parameters
        ----------
        session_data : dict
            Session data to summarize
        """
        session_id = session_data.get("session_id")
        if not session_id:
            return
        
        try:
            start_time = datetime.fromisoformat(session_data["start_time"])
            end_time = datetime.fromisoformat(session_data["end_time"]) if session_data.get("end_time") else start_time
            
            duration = (end_time - start_time).total_seconds()
            
            summary = SessionSummary(
                session_id=session_id,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                total_damage_dealt=session_data.get("total_damage_dealt", 0),
                total_xp_gained=session_data.get("total_xp_gained", 0),
                kills=session_data.get("kills", 0),
                deaths=session_data.get("deaths", 0),
                average_dps=session_data.get("total_damage_dealt", 0) / duration if duration > 0 else 0,
                xp_per_hour=(session_data.get("total_xp_gained", 0) / duration) * 3600 if duration > 0 else 0,
                damage_per_hour=(session_data.get("total_damage_dealt", 0) / duration) * 3600 if duration > 0 else 0,
                abilities_used=session_data.get("abilities_used", {}),
                targets_engaged=session_data.get("targets_engaged", []),
                session_state=session_data.get("session_state", "unknown")
            )
            
            self.session_summaries[session_id] = summary
            
        except Exception as e:
            logger.error(f"Error creating summary for session {session_id}: {e}") 