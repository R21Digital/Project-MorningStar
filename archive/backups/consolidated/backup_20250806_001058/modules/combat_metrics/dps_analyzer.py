"""
DPS Analyzer - Advanced damage per second analysis system.

This module provides comprehensive DPS analysis including:
- Real-time DPS calculation
- Burst vs sustained DPS analysis
- Damage efficiency metrics
- DPS trend analysis
- Performance benchmarking
"""

import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class DPSWindow:
    """Represents a DPS calculation window."""
    start_time: datetime
    end_time: datetime
    total_damage: int
    damage_events: int
    dps: float
    window_size: float  # seconds
    
    @property
    def duration(self) -> float:
        """Get window duration in seconds."""
        return (self.end_time - self.start_time).total_seconds()


@dataclass
class DPSAnalysis:
    """Comprehensive DPS analysis results."""
    session_id: str
    analysis_time: datetime
    total_duration: float
    total_damage: int
    average_dps: float
    peak_dps: float
    sustained_dps: float
    burst_dps: float
    dps_windows: List[DPSWindow]
    damage_distribution: Dict[str, int]
    efficiency_metrics: Dict[str, float]
    recommendations: List[str]


class DPSAnalyzer:
    """Advanced DPS analysis and optimization system."""
    
    def __init__(self, window_size: float = 10.0, burst_window: float = 5.0):
        """Initialize the DPS analyzer.
        
        Parameters
        ----------
        window_size : float
            Size of DPS calculation windows in seconds
        burst_window : float
            Size of burst DPS calculation window in seconds
        """
        self.window_size = window_size
        self.burst_window = burst_window
        
        # Analysis storage
        self.damage_events: List[Dict[str, Any]] = []
        self.dps_windows: List[DPSWindow] = []
        self.analysis_history: List[DPSAnalysis] = []
        
        logger.info(f"DPSAnalyzer initialized with window_size={window_size}s, burst_window={burst_window}s")
    
    def add_damage_event(self, damage: int, timestamp: Optional[datetime] = None, 
                        ability_name: Optional[str] = None, target: Optional[str] = None) -> None:
        """Add a damage event for analysis.
        
        Parameters
        ----------
        damage : int
            Amount of damage dealt
        timestamp : datetime, optional
            When the damage occurred (defaults to now)
        ability_name : str, optional
            Name of the ability that dealt damage
        target : str, optional
            Target of the damage
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        event = {
            "timestamp": timestamp,
            "damage": damage,
            "ability_name": ability_name,
            "target": target
        }
        
        self.damage_events.append(event)
        logger.debug(f"Added damage event: {damage} damage at {timestamp}")
    
    def calculate_current_dps(self, window_size: Optional[float] = None) -> float:
        """Calculate current DPS over the specified window.
        
        Parameters
        ----------
        window_size : float, optional
            Window size in seconds (defaults to instance window_size)
            
        Returns
        -------
        float
            Current DPS
        """
        if window_size is None:
            window_size = self.window_size
        
        if not self.damage_events:
            return 0.0
        
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=window_size)
        
        # Filter events within window
        recent_events = [
            event for event in self.damage_events
            if event["timestamp"] >= cutoff_time
        ]
        
        if not recent_events:
            return 0.0
        
        total_damage = sum(event["damage"] for event in recent_events)
        time_span = (current_time - min(event["timestamp"] for event in recent_events)).total_seconds()
        
        if time_span <= 0:
            return 0.0
        
        dps = total_damage / time_span
        return dps
    
    def calculate_burst_dps(self) -> float:
        """Calculate burst DPS over the burst window.
        
        Returns
        -------
        float
            Burst DPS
        """
        return self.calculate_current_dps(self.burst_window)
    
    def calculate_sustained_dps(self, duration: float = 300.0) -> float:
        """Calculate sustained DPS over a longer period.
        
        Parameters
        ----------
        duration : float
            Duration to calculate sustained DPS over (default 5 minutes)
            
        Returns
        -------
        float
            Sustained DPS
        """
        return self.calculate_current_dps(duration)
    
    def analyze_dps_trends(self, num_windows: int = 10) -> Dict[str, Any]:
        """Analyze DPS trends over multiple windows.
        
        Parameters
        ----------
        num_windows : int
            Number of windows to analyze
            
        Returns
        -------
        dict
            DPS trend analysis
        """
        if not self.damage_events:
            return {"error": "No damage events to analyze"}
        
        # Calculate DPS for multiple windows
        current_time = datetime.now()
        dps_values = []
        
        for i in range(num_windows):
            window_start = current_time - timedelta(seconds=self.window_size * (i + 1))
            window_end = current_time - timedelta(seconds=self.window_size * i)
            
            window_events = [
                event for event in self.damage_events
                if window_start <= event["timestamp"] <= window_end
            ]
            
            if window_events:
                total_damage = sum(event["damage"] for event in window_events)
                dps = total_damage / self.window_size
                dps_values.append(dps)
        
        if not dps_values:
            return {"error": "No valid DPS windows found"}
        
        # Calculate trend statistics
        trend_analysis = {
            "average_dps": statistics.mean(dps_values),
            "median_dps": statistics.median(dps_values),
            "peak_dps": max(dps_values),
            "min_dps": min(dps_values),
            "dps_std": statistics.stdev(dps_values) if len(dps_values) > 1 else 0,
            "trend_direction": "increasing" if dps_values[0] < dps_values[-1] else "decreasing" if dps_values[0] > dps_values[-1] else "stable",
            "consistency": "high" if len(dps_values) > 1 and statistics.stdev(dps_values) < statistics.mean(dps_values) * 0.2 else "low"
        }
        
        return trend_analysis
    
    def calculate_damage_efficiency(self) -> Dict[str, float]:
        """Calculate damage efficiency metrics.
        
        Returns
        -------
        dict
            Damage efficiency metrics
        """
        if not self.damage_events:
            return {}
        
        # Group damage by ability
        ability_damage = defaultdict(int)
        ability_count = defaultdict(int)
        
        for event in self.damage_events:
            ability = event.get("ability_name", "unknown")
            ability_damage[ability] += event["damage"]
            ability_count[ability] += 1
        
        # Calculate efficiency metrics
        efficiency_metrics = {}
        
        for ability, total_damage in ability_damage.items():
            count = ability_count[ability]
            avg_damage = total_damage / count if count > 0 else 0
            
            efficiency_metrics[f"{ability}_total_damage"] = total_damage
            efficiency_metrics[f"{ability}_usage_count"] = count
            efficiency_metrics[f"{ability}_avg_damage"] = avg_damage
            efficiency_metrics[f"{ability}_damage_percentage"] = (total_damage / sum(ability_damage.values())) * 100
        
        # Overall efficiency
        total_damage = sum(ability_damage.values())
        total_events = len(self.damage_events)
        
        efficiency_metrics["overall_avg_damage"] = total_damage / total_events if total_events > 0 else 0
        efficiency_metrics["damage_consistency"] = statistics.stdev([event["damage"] for event in self.damage_events]) if len(self.damage_events) > 1 else 0
        
        return efficiency_metrics
    
    def generate_dps_windows(self) -> List[DPSWindow]:
        """Generate DPS windows for analysis.
        
        Returns
        -------
        list
            List of DPS windows
        """
        if not self.damage_events:
            return []
        
        # Sort events by timestamp
        sorted_events = sorted(self.damage_events, key=lambda x: x["timestamp"])
        
        windows = []
        current_time = datetime.now()
        
        # Create windows from current time backwards
        for i in range(10):  # Generate 10 windows
            window_end = current_time - timedelta(seconds=self.window_size * i)
            window_start = window_end - timedelta(seconds=self.window_size)
            
            # Find events in this window
            window_events = [
                event for event in sorted_events
                if window_start <= event["timestamp"] <= window_end
            ]
            
            if window_events:
                total_damage = sum(event["damage"] for event in window_events)
                dps = total_damage / self.window_size
                
                window = DPSWindow(
                    start_time=window_start,
                    end_time=window_end,
                    total_damage=total_damage,
                    damage_events=len(window_events),
                    dps=dps,
                    window_size=self.window_size
                )
                windows.append(window)
        
        return windows
    
    def analyze_session(self, session_id: str, session_data: Dict[str, Any]) -> DPSAnalysis:
        """Perform comprehensive DPS analysis on a session.
        
        Parameters
        ----------
        session_id : str
            ID of the session to analyze
        session_data : dict
            Session data containing events and statistics
            
        Returns
        -------
        DPSAnalysis
            Comprehensive DPS analysis results
        """
        # Extract damage events from session data
        events = session_data.get("events", [])
        damage_events = [
            event for event in events
            if event.get("event_type") == "damage_dealt" and event.get("damage_dealt")
        ]
        
        # Add events to analyzer
        for event in damage_events:
            self.add_damage_event(
                damage=event["damage_dealt"],
                timestamp=datetime.fromisoformat(event["timestamp"]),
                ability_name=event.get("ability_name"),
                target=event.get("target")
            )
        
        # Calculate various DPS metrics
        total_duration = session_data.get("duration", 0)
        total_damage = session_data.get("total_damage_dealt", 0)
        
        average_dps = total_damage / total_duration if total_duration > 0 else 0
        peak_dps = self.calculate_burst_dps()
        sustained_dps = self.calculate_sustained_dps()
        
        # Generate DPS windows
        dps_windows = self.generate_dps_windows()
        
        # Calculate damage distribution
        damage_distribution = defaultdict(int)
        for event in damage_events:
            ability = event.get("ability_name", "unknown")
            damage_distribution[ability] += event["damage_dealt"]
        
        # Calculate efficiency metrics
        efficiency_metrics = self.calculate_damage_efficiency()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            average_dps, peak_dps, sustained_dps, damage_distribution, efficiency_metrics
        )
        
        # Create analysis result
        analysis = DPSAnalysis(
            session_id=session_id,
            analysis_time=datetime.now(),
            total_duration=total_duration,
            total_damage=total_damage,
            average_dps=average_dps,
            peak_dps=peak_dps,
            sustained_dps=sustained_dps,
            burst_dps=peak_dps,
            dps_windows=dps_windows,
            damage_distribution=dict(damage_distribution),
            efficiency_metrics=efficiency_metrics,
            recommendations=recommendations
        )
        
        self.analysis_history.append(analysis)
        return analysis
    
    def _generate_recommendations(self, avg_dps: float, peak_dps: float, 
                                sustained_dps: float, damage_dist: Dict[str, int],
                                efficiency_metrics: Dict[str, float]) -> List[str]:
        """Generate DPS optimization recommendations.
        
        Parameters
        ----------
        avg_dps : float
            Average DPS
        peak_dps : float
            Peak DPS
        sustained_dps : float
            Sustained DPS
        damage_dist : dict
            Damage distribution by ability
        efficiency_metrics : dict
            Efficiency metrics
            
        Returns
        -------
        list
            List of recommendations
        """
        recommendations = []
        
        # Analyze DPS consistency
        if peak_dps > avg_dps * 2:
            recommendations.append("High burst DPS detected - consider optimizing sustained damage output")
        
        if sustained_dps < avg_dps * 0.8:
            recommendations.append("Sustained DPS is lower than average - focus on consistent damage rotation")
        
        # Analyze ability usage
        if damage_dist:
            top_ability = max(damage_dist.items(), key=lambda x: x[1])
            total_damage = sum(damage_dist.values())
            top_percentage = (top_ability[1] / total_damage) * 100
            
            if top_percentage > 70:
                recommendations.append(f"Over-reliance on {top_ability[0]} ({top_percentage:.1f}% of damage) - diversify ability usage")
        
        # Analyze efficiency
        if "overall_avg_damage" in efficiency_metrics:
            avg_damage = efficiency_metrics["overall_avg_damage"]
            if avg_damage < 100:  # Assuming 100 is a reasonable threshold
                recommendations.append("Low average damage per ability - consider upgrading abilities or equipment")
        
        # General recommendations
        if not recommendations:
            recommendations.append("DPS performance is well-balanced - maintain current rotation")
        
        return recommendations
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of all analyses performed.
        
        Returns
        -------
        dict
            Analysis summary
        """
        if not self.analysis_history:
            return {"error": "No analyses performed"}
        
        # Aggregate statistics
        avg_dps_values = [analysis.average_dps for analysis in self.analysis_history]
        peak_dps_values = [analysis.peak_dps for analysis in self.analysis_history]
        
        summary = {
            "total_analyses": len(self.analysis_history),
            "average_dps_across_sessions": statistics.mean(avg_dps_values),
            "peak_dps_across_sessions": max(peak_dps_values),
            "most_recent_analysis": self.analysis_history[-1].session_id if self.analysis_history else None,
            "analysis_trend": "improving" if len(avg_dps_values) > 1 and avg_dps_values[-1] > avg_dps_values[0] else "stable"
        }
        
        return summary 