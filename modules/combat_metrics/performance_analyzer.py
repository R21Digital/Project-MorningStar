"""
Performance Analyzer - Combat performance analysis and optimization.

This module provides comprehensive performance analysis including:
- XP/damage per hour calculations
- Performance efficiency metrics
- Performance benchmarking
- Optimization recommendations
- Performance trending analysis
"""

import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics for a session."""
    session_id: str
    duration: float
    total_damage: int
    total_xp: int
    kills: int
    deaths: int
    dps: float
    xp_per_hour: float
    damage_per_hour: float
    efficiency_score: float
    performance_grade: str
    recommendations: List[str]


@dataclass
class PerformanceBenchmark:
    """Performance benchmark data."""
    benchmark_name: str
    dps_target: float
    xp_per_hour_target: float
    damage_per_hour_target: float
    efficiency_target: float
    description: str


class PerformanceAnalyzer:
    """Advanced combat performance analysis system."""
    
    def __init__(self):
        """Initialize the performance analyzer."""
        # Performance benchmarks
        self.benchmarks = {
            "beginner": PerformanceBenchmark(
                "beginner", 50.0, 1000.0, 5000.0, 0.6, "Beginner level performance"
            ),
            "intermediate": PerformanceBenchmark(
                "intermediate", 100.0, 2000.0, 10000.0, 0.7, "Intermediate level performance"
            ),
            "advanced": PerformanceBenchmark(
                "advanced", 200.0, 4000.0, 20000.0, 0.8, "Advanced level performance"
            ),
            "expert": PerformanceBenchmark(
                "expert", 400.0, 8000.0, 40000.0, 0.9, "Expert level performance"
            ),
            "elite": PerformanceBenchmark(
                "elite", 800.0, 16000.0, 80000.0, 0.95, "Elite level performance"
            )
        }
        
        # Performance thresholds
        self.thresholds = {
            "excellent": 0.9,
            "good": 0.7,
            "average": 0.5,
            "poor": 0.3
        }
        
        logger.info("PerformanceAnalyzer initialized")
    
    def analyze_session_performance(self, session_data: Dict[str, Any]) -> PerformanceMetrics:
        """Analyze performance for a single session.
        
        Parameters
        ----------
        session_data : dict
            Session data to analyze
            
        Returns
        -------
        PerformanceMetrics
            Performance analysis results
        """
        # Extract basic metrics
        duration = session_data.get("duration", 0)
        total_damage = session_data.get("total_damage_dealt", 0)
        total_xp = session_data.get("total_xp_gained", 0)
        kills = session_data.get("kills", 0)
        deaths = session_data.get("deaths", 0)
        
        # Calculate rates
        dps = total_damage / duration if duration > 0 else 0
        xp_per_hour = (total_xp / duration) * 3600 if duration > 0 else 0
        damage_per_hour = (total_damage / duration) * 3600 if duration > 0 else 0
        
        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(dps, xp_per_hour, kills, deaths)
        
        # Determine performance grade
        performance_grade = self._determine_performance_grade(efficiency_score)
        
        # Generate recommendations
        recommendations = self._generate_performance_recommendations(
            dps, xp_per_hour, damage_per_hour, kills, deaths, efficiency_score
        )
        
        return PerformanceMetrics(
            session_id=session_data.get("session_id", "unknown"),
            duration=duration,
            total_damage=total_damage,
            total_xp=total_xp,
            kills=kills,
            deaths=deaths,
            dps=dps,
            xp_per_hour=xp_per_hour,
            damage_per_hour=damage_per_hour,
            efficiency_score=efficiency_score,
            performance_grade=performance_grade,
            recommendations=recommendations
        )
    
    def compare_to_benchmark(self, performance: PerformanceMetrics, 
                           benchmark_name: str = "intermediate") -> Dict[str, Any]:
        """Compare performance to a specific benchmark.
        
        Parameters
        ----------
        performance : PerformanceMetrics
            Performance to compare
        benchmark_name : str
            Name of benchmark to compare against
            
        Returns
        -------
        dict
            Benchmark comparison results
        """
        if benchmark_name not in self.benchmarks:
            return {"error": f"Benchmark '{benchmark_name}' not found"}
        
        benchmark = self.benchmarks[benchmark_name]
        
        # Calculate performance ratios
        dps_ratio = performance.dps / benchmark.dps_target if benchmark.dps_target > 0 else 0
        xp_ratio = performance.xp_per_hour / benchmark.xp_per_hour_target if benchmark.xp_per_hour_target > 0 else 0
        damage_ratio = performance.damage_per_hour / benchmark.damage_per_hour_target if benchmark.damage_per_hour_target > 0 else 0
        efficiency_ratio = performance.efficiency_score / benchmark.efficiency_target if benchmark.efficiency_target > 0 else 0
        
        # Determine if performance meets benchmark
        meets_benchmark = all([
            dps_ratio >= 1.0,
            xp_ratio >= 1.0,
            damage_ratio >= 1.0,
            efficiency_ratio >= 1.0
        ])
        
        comparison = {
            "benchmark_name": benchmark_name,
            "benchmark_description": benchmark.description,
            "meets_benchmark": meets_benchmark,
            "metrics": {
                "dps": {
                    "actual": performance.dps,
                    "target": benchmark.dps_target,
                    "ratio": dps_ratio,
                    "meets_target": dps_ratio >= 1.0
                },
                "xp_per_hour": {
                    "actual": performance.xp_per_hour,
                    "target": benchmark.xp_per_hour_target,
                    "ratio": xp_ratio,
                    "meets_target": xp_ratio >= 1.0
                },
                "damage_per_hour": {
                    "actual": performance.damage_per_hour,
                    "target": benchmark.damage_per_hour_target,
                    "ratio": damage_ratio,
                    "meets_target": damage_ratio >= 1.0
                },
                "efficiency": {
                    "actual": performance.efficiency_score,
                    "target": benchmark.efficiency_target,
                    "ratio": efficiency_ratio,
                    "meets_target": efficiency_ratio >= 1.0
                }
            },
            "overall_score": statistics.mean([dps_ratio, xp_ratio, damage_ratio, efficiency_ratio])
        }
        
        return comparison
    
    def analyze_performance_trends(self, sessions: List[Dict[str, Any]], 
                                 days: int = 7) -> Dict[str, Any]:
        """Analyze performance trends over multiple sessions.
        
        Parameters
        ----------
        sessions : list
            List of session data to analyze
        days : int
            Number of days to analyze
            
        Returns
        -------
        dict
            Performance trend analysis
        """
        if not sessions:
            return {"error": "No sessions to analyze"}
        
        # Analyze each session
        performances = []
        for session in sessions:
            performance = self.analyze_session_performance(session)
            performances.append(performance)
        
        # Calculate trends
        dps_values = [p.dps for p in performances]
        xp_values = [p.xp_per_hour for p in performances]
        efficiency_values = [p.efficiency_score for p in performances]
        
        # Determine trend direction
        def calculate_trend(values):
            if len(values) < 2:
                return "insufficient_data"
            slope = (values[-1] - values[0]) / len(values)
            if slope > 0.05:
                return "improving"
            elif slope < -0.05:
                return "declining"
            else:
                return "stable"
        
        trends = {
            "dps_trend": calculate_trend(dps_values),
            "xp_trend": calculate_trend(xp_values),
            "efficiency_trend": calculate_trend(efficiency_values),
            "average_dps": statistics.mean(dps_values) if dps_values else 0,
            "average_xp_per_hour": statistics.mean(xp_values) if xp_values else 0,
            "average_efficiency": statistics.mean(efficiency_values) if efficiency_values else 0,
            "best_performance": max(performances, key=lambda x: x.efficiency_score).session_id if performances else None,
            "sessions_analyzed": len(performances)
        }
        
        return trends
    
    def calculate_xp_efficiency(self, session_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate XP efficiency metrics.
        
        Parameters
        ----------
        session_data : dict
            Session data to analyze
            
        Returns
        -------
        dict
            XP efficiency metrics
        """
        duration = session_data.get("duration", 0)
        total_xp = session_data.get("total_xp_gained", 0)
        kills = session_data.get("kills", 0)
        deaths = session_data.get("deaths", 0)
        
        if duration <= 0:
            return {"error": "Invalid session duration"}
        
        # Calculate XP metrics
        xp_per_hour = (total_xp / duration) * 3600
        xp_per_kill = total_xp / kills if kills > 0 else 0
        xp_per_minute = total_xp / (duration / 60)
        
        # Calculate efficiency ratios
        efficiency_metrics = {
            "xp_per_hour": xp_per_hour,
            "xp_per_kill": xp_per_kill,
            "xp_per_minute": xp_per_minute,
            "kills_per_hour": (kills / duration) * 3600,
            "death_rate": deaths / duration if duration > 0 else 0,
            "xp_efficiency": xp_per_hour / 1000.0,  # Normalized to 1000 XP/hour baseline
            "kill_efficiency": kills / max(deaths, 1)  # Kill/death ratio
        }
        
        return efficiency_metrics
    
    def calculate_damage_efficiency(self, session_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate damage efficiency metrics.
        
        Parameters
        ----------
        session_data : dict
            Session data to analyze
            
        Returns
        -------
        dict
            Damage efficiency metrics
        """
        duration = session_data.get("duration", 0)
        total_damage = session_data.get("total_damage_dealt", 0)
        abilities_used = session_data.get("abilities_used", {})
        
        if duration <= 0:
            return {"error": "Invalid session duration"}
        
        # Calculate damage metrics
        dps = total_damage / duration
        damage_per_hour = (total_damage / duration) * 3600
        
        # Calculate ability efficiency
        total_abilities = sum(abilities_used.values())
        avg_damage_per_ability = total_damage / total_abilities if total_abilities > 0 else 0
        
        # Calculate efficiency ratios
        efficiency_metrics = {
            "dps": dps,
            "damage_per_hour": damage_per_hour,
            "damage_per_ability": avg_damage_per_ability,
            "abilities_per_minute": (total_abilities / duration) * 60,
            "damage_efficiency": dps / 100.0,  # Normalized to 100 DPS baseline
            "ability_efficiency": avg_damage_per_ability / 50.0  # Normalized to 50 damage per ability baseline
        }
        
        return efficiency_metrics
    
    def get_performance_recommendations(self, performance: PerformanceMetrics) -> List[str]:
        """Get performance improvement recommendations.
        
        Parameters
        ----------
        performance : PerformanceMetrics
            Performance to analyze
            
        Returns
        -------
        list
            List of recommendations
        """
        recommendations = []
        
        # DPS recommendations
        if performance.dps < 50:
            recommendations.append("Focus on improving damage output - consider upgrading abilities or equipment")
        elif performance.dps < 100:
            recommendations.append("DPS is below intermediate level - optimize ability rotation for better damage")
        
        # XP recommendations
        if performance.xp_per_hour < 1000:
            recommendations.append("XP gain is low - focus on higher-level enemies or better XP sources")
        elif performance.xp_per_hour < 2000:
            recommendations.append("XP gain could be improved - optimize for faster kills or better XP targets")
        
        # Efficiency recommendations
        if performance.efficiency_score < 0.5:
            recommendations.append("Overall efficiency is poor - review combat strategy and ability usage")
        elif performance.efficiency_score < 0.7:
            recommendations.append("Efficiency could be improved - focus on consistent performance")
        
        # Death rate recommendations
        if performance.deaths > 0:
            recommendations.append("Deaths detected - focus on survivability and defensive abilities")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Performance is well-balanced - maintain current strategy")
        
        return recommendations
    
    def _calculate_efficiency_score(self, dps: float, xp_per_hour: float, 
                                 kills: int, deaths: int) -> float:
        """Calculate overall efficiency score.
        
        Parameters
        ----------
        dps : float
            Damage per second
        xp_per_hour : float
            XP gained per hour
        kills : int
            Number of kills
        deaths : int
            Number of deaths
            
        Returns
        -------
        float
            Efficiency score (0.0 to 1.0)
        """
        # Normalize metrics to 0-1 scale
        dps_score = min(dps / 200.0, 1.0)  # 200 DPS = perfect score
        xp_score = min(xp_per_hour / 5000.0, 1.0)  # 5000 XP/hour = perfect score
        kill_score = min(kills / 50.0, 1.0)  # 50 kills = perfect score
        death_penalty = min(deaths / 10.0, 1.0)  # 10 deaths = maximum penalty
        
        # Calculate weighted efficiency score
        efficiency = (dps_score * 0.4 + xp_score * 0.3 + kill_score * 0.2) * (1.0 - death_penalty * 0.3)
        
        return max(0.0, min(1.0, efficiency))
    
    def _determine_performance_grade(self, efficiency_score: float) -> str:
        """Determine performance grade based on efficiency score.
        
        Parameters
        ----------
        efficiency_score : float
            Efficiency score (0.0 to 1.0)
            
        Returns
        -------
        str
            Performance grade
        """
        if efficiency_score >= self.thresholds["excellent"]:
            return "A+"
        elif efficiency_score >= self.thresholds["good"]:
            return "B+"
        elif efficiency_score >= self.thresholds["average"]:
            return "C+"
        elif efficiency_score >= self.thresholds["poor"]:
            return "D"
        else:
            return "F"
    
    def _generate_performance_recommendations(self, dps: float, xp_per_hour: float,
                                           damage_per_hour: float, kills: int, deaths: int,
                                           efficiency_score: float) -> List[str]:
        """Generate specific performance recommendations.
        
        Parameters
        ----------
        dps : float
            Damage per second
        xp_per_hour : float
            XP per hour
        damage_per_hour : float
            Damage per hour
        kills : int
            Number of kills
        deaths : int
            Number of deaths
        efficiency_score : float
            Overall efficiency score
            
        Returns
        -------
        list
            List of recommendations
        """
        recommendations = []
        
        # DPS-based recommendations
        if dps < 50:
            recommendations.append("Low DPS detected - upgrade abilities or equipment")
        elif dps < 100:
            recommendations.append("Moderate DPS - optimize ability rotation")
        
        # XP-based recommendations
        if xp_per_hour < 1000:
            recommendations.append("Low XP gain - target higher-level enemies")
        elif xp_per_hour < 2000:
            recommendations.append("Moderate XP gain - optimize for faster kills")
        
        # Kill/death ratio recommendations
        if deaths > 0:
            kdr = kills / deaths if deaths > 0 else kills
            if kdr < 2:
                recommendations.append("Poor kill/death ratio - improve survivability")
        
        # Efficiency-based recommendations
        if efficiency_score < 0.5:
            recommendations.append("Low efficiency - review overall combat strategy")
        elif efficiency_score < 0.7:
            recommendations.append("Moderate efficiency - focus on consistency")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Good performance - maintain current strategy")
        
        return recommendations 