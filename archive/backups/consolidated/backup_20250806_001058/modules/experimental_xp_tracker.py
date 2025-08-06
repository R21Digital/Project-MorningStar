"""Experimental XP Tracker (Deep Skill Mapping) - Batch 114

This module provides comprehensive XP tracking across all profession categories
with advanced analytics, visualization, and skill path recommendations.

Features:
- Log XP gains with timestamps, quest name (if known), and zone
- Visualize XP gain rates per hour
- Detect which skills are progressing fastest
- Recommend optimal skill paths and detect leveling slowdowns
- Store XP gain summaries in session logs and charts (future UI phase)
"""

import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from android_ms11.utils.logging_utils import log_event


@dataclass
class XPGainEvent:
    """Represents a single XP gain event with enhanced tracking."""
    timestamp: str
    amount: int
    profession: str
    skill: str
    source: str  # quest, combat, crafting, exploration, etc.
    quest_name: Optional[str] = None
    zone: Optional[str] = None
    level_before: Optional[int] = None
    level_after: Optional[int] = None
    session_id: Optional[str] = None
    xp_rate_per_hour: Optional[float] = None
    skill_progress_percentage: Optional[float] = None


@dataclass
class SkillProgress:
    """Represents skill progression over time with enhanced metrics."""
    skill_name: str
    profession: str
    current_level: int
    total_xp: int
    xp_to_next: int
    progress_rate: float  # XP per hour
    last_gain: Optional[str] = None
    gains_history: List[XPGainEvent] = None
    zone_preferences: Dict[str, int] = None  # Zone -> XP gained
    quest_completion_rate: float = 0.0
    slowdown_detected: bool = False


@dataclass
class ProfessionAnalytics:
    """Enhanced analytics for a specific profession."""
    profession_name: str
    total_xp: int
    skills_count: int
    average_level: float
    fastest_skill: str
    slowest_skill: str
    xp_per_hour: float
    session_duration: float
    quest_completion_rate: float
    optimal_zones: List[str] = None
    skill_path_recommendation: List[str] = None


@dataclass
class XPSessionSummary:
    """Comprehensive session summary for storage and visualization."""
    session_id: str
    start_time: str
    end_time: str
    total_xp: int
    xp_per_hour: float
    profession_breakdown: Dict[str, int]
    skill_breakdown: Dict[str, int]
    source_breakdown: Dict[str, int]
    fastest_skills: List[str]
    slowdowns_detected: List[Dict[str, Any]]
    optimal_paths: Dict[str, List[str]]
    zone_efficiency: Dict[str, float]


class ExperimentalXPTracker:
    """Advanced XP tracking with deep skill mapping and analytics for Batch 114."""
    
    def __init__(self, config_path: str = "config/xp_tracker_config.json"):
        """Initialize the experimental XP tracker.
        
        Parameters
        ----------
        config_path : str
            Path to XP tracker configuration file
        """
        self.config_path = Path(config_path)
        self.xp_events: List[XPGainEvent] = []
        self.skill_progress: Dict[str, SkillProgress] = {}
        self.profession_analytics: Dict[str, ProfessionAnalytics] = {}
        
        # Real-time tracking
        self.current_session_id = None
        self.session_start_time = None
        self.session_xp_gains = defaultdict(int)
        
        # Analytics windows
        self.hourly_xp_rates = deque(maxlen=24)  # Last 24 hours
        self.daily_xp_totals = deque(maxlen=30)  # Last 30 days
        
        # Zone tracking
        self.zone_xp_efficiency = defaultdict(lambda: {"total_xp": 0, "time_spent": 0, "events": 0})
        
        # Load configuration
        self._load_config()
        
        log_event("[XP_TRACKER] Experimental XP tracker initialized for Batch 114")
    
    def _load_config(self):
        """Load XP tracker configuration."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self._create_default_config()
        except Exception as e:
            log_event(f"[XP_TRACKER] Error loading config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default XP tracker configuration."""
        default_config = {
            "professions": {
                "marksman": {
                    "skills": ["combat_marksman_novice", "combat_marksman_marksman", "combat_marksman_rifleman"],
                    "category": "combat",
                    "optimal_zones": ["dantooine", "naboo", "corellia"]
                },
                "artisan": {
                    "skills": ["crafting_artisan_novice", "crafting_artisan_engineering", "crafting_artisan_armorsmith"],
                    "category": "crafting",
                    "optimal_zones": ["tatooine", "lok", "rori"]
                },
                "medic": {
                    "skills": ["science_medic_novice", "science_medic_doctor", "science_medic_combat_medic"],
                    "category": "science",
                    "optimal_zones": ["dantooine", "naboo", "talus"]
                },
                "scout": {
                    "skills": ["outdoors_scout_novice", "outdoors_scout_ranger", "outdoors_scout_creature_handler"],
                    "category": "outdoors",
                    "optimal_zones": ["dantooine", "yavin4", "endor"]
                },
                "brawler": {
                    "skills": ["combat_brawler_novice", "combat_brawler_unarmed", "combat_brawler_teras_kasi"],
                    "category": "combat",
                    "optimal_zones": ["tatooine", "lok", "dantooine"]
                },
                "entertainer": {
                    "skills": ["social_entertainer_novice", "social_entertainer_musician", "social_entertainer_dancer"],
                    "category": "social",
                    "optimal_zones": ["coruscant", "naboo", "corellia"]
                }
            },
            "xp_sources": {
                "quest": {"base_multiplier": 1.0, "bonus_conditions": ["completion_time", "difficulty"]},
                "combat": {"base_multiplier": 0.8, "bonus_conditions": ["kill_count", "damage_dealt"]},
                "crafting": {"base_multiplier": 1.2, "bonus_conditions": ["quality", "complexity"]},
                "exploration": {"base_multiplier": 0.6, "bonus_conditions": ["discovery_type", "zone_level"]},
                "social": {"base_multiplier": 0.5, "bonus_conditions": ["interaction_type", "audience_size"]}
            },
            "analytics_settings": {
                "hourly_rate_window": 24,
                "daily_total_window": 30,
                "skill_progress_threshold": 0.1,
                "slowdown_detection_threshold": 0.5,
                "zone_efficiency_min_events": 5
            },
            "visualization_settings": {
                "chart_style": "seaborn",
                "figure_size": [12, 8],
                "color_palette": "viridis"
            }
        }
        
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.config = default_config
        log_event(f"[XP_TRACKER] Created default config at {self.config_path}")
    
    def start_session(self, session_id: str = None) -> str:
        """Start a new XP tracking session.
        
        Parameters
        ----------
        session_id : str, optional
            Custom session ID, auto-generated if not provided
            
        Returns
        -------
        str
            Session ID
        """
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session_id = session_id
        self.session_start_time = datetime.now()
        self.session_xp_gains.clear()
        
        log_event(f"[XP_TRACKER] Started session: {session_id}")
        return session_id
    
    def record_xp_gain(self, amount: int, profession: str, skill: str, 
                       source: str = "unknown", quest_name: str = None, 
                       zone: str = None, level_before: int = None, 
                       level_after: int = None) -> XPGainEvent:
        """Record an XP gain event with enhanced tracking.
        
        Parameters
        ----------
        amount : int
            XP amount gained
        profession : str
            Profession that gained XP
        skill : str
            Specific skill that gained XP
        source : str
            Source of XP (quest, combat, crafting, etc.)
        quest_name : str, optional
            Name of quest if applicable
        zone : str, optional
            Zone where XP was gained
        level_before : int, optional
            Level before XP gain
        level_after : int, optional
            Level after XP gain
            
        Returns
        -------
        XPGainEvent
            Recorded XP gain event
        """
        # Calculate XP rate per hour
        xp_rate_per_hour = self._calculate_current_xp_rate()
        
        # Calculate skill progress percentage
        skill_progress_percentage = self._calculate_skill_progress_percentage(skill, profession)
        
        event = XPGainEvent(
            timestamp=datetime.now().isoformat(),
            amount=amount,
            profession=profession,
            skill=skill,
            source=source,
            quest_name=quest_name,
            zone=zone,
            level_before=level_before,
            level_after=level_after,
            session_id=self.current_session_id,
            xp_rate_per_hour=xp_rate_per_hour,
            skill_progress_percentage=skill_progress_percentage
        )
        
        self.xp_events.append(event)
        self.session_xp_gains[skill] += amount
        
        # Update zone efficiency tracking
        if zone:
            self._update_zone_efficiency(zone, amount)
        
        # Update skill progress
        self._update_skill_progress(event)
        
        # Update analytics
        self._update_analytics(event)
        
        log_event(f"[XP_TRACKER] Recorded {amount} XP for {skill} ({profession}) from {source} in {zone or 'unknown zone'}")
        
        return event
    
    def _calculate_current_xp_rate(self) -> float:
        """Calculate current XP rate per hour."""
        if not self.xp_events:
            return 0.0
        
        # Look at last hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        recent_events = [e for e in self.xp_events 
                        if datetime.fromisoformat(e.timestamp) > cutoff_time]
        
        if not recent_events:
            return 0.0
        
        total_xp = sum(e.amount for e in recent_events)
        return total_xp
    
    def _calculate_skill_progress_percentage(self, skill: str, profession: str) -> float:
        """Calculate skill progress percentage."""
        skill_key = f"{profession}_{skill}"
        if skill_key in self.skill_progress:
            progress = self.skill_progress[skill_key]
            # Calculate percentage based on level progression
            if progress.current_level > 0:
                return min(100.0, (progress.total_xp / (progress.current_level * 1000)) * 100)
        return 0.0
    
    def _update_zone_efficiency(self, zone: str, xp_amount: int):
        """Update zone efficiency tracking."""
        self.zone_xp_efficiency[zone]["total_xp"] += xp_amount
        self.zone_xp_efficiency[zone]["events"] += 1
    
    def _update_skill_progress(self, event: XPGainEvent):
        """Update skill progress tracking with enhanced metrics."""
        skill_key = f"{event.profession}_{event.skill}"
        
        if skill_key not in self.skill_progress:
            self.skill_progress[skill_key] = SkillProgress(
                skill_name=event.skill,
                profession=event.profession,
                current_level=event.level_after or 0,
                total_xp=0,
                xp_to_next=0,
                progress_rate=0.0,
                gains_history=[],
                zone_preferences=defaultdict(int)
            )
        
        progress = self.skill_progress[skill_key]
        progress.total_xp += event.amount
        progress.last_gain = event.timestamp
        progress.gains_history.append(event)
        
        # Update zone preferences
        if event.zone:
            progress.zone_preferences[event.zone] += event.amount
        
        # Calculate progress rate (last hour)
        recent_gains = [e for e in progress.gains_history 
                       if (datetime.now() - datetime.fromisoformat(e.timestamp)).total_seconds() < 3600]
        if recent_gains:
            progress.progress_rate = sum(e.amount for e in recent_gains)
        
        # Calculate quest completion rate
        quest_events = [e for e in progress.gains_history if e.source == "quest"]
        progress.quest_completion_rate = len(quest_events) / max(len(progress.gains_history), 1)
        
        # Detect slowdown
        progress.slowdown_detected = self._detect_skill_slowdown(progress)
    
    def _detect_skill_slowdown(self, progress: SkillProgress) -> bool:
        """Detect if a skill is experiencing slowdown."""
        if len(progress.gains_history) < 5:
            return False
        
        # Compare recent rate to historical rate
        recent_events = progress.gains_history[-5:]  # Last 5 events
        historical_events = progress.gains_history[:-5]  # All but last 5
        
        if not historical_events:
            return False
        
        recent_rate = sum(e.amount for e in recent_events) / len(recent_events)
        historical_rate = sum(e.amount for e in historical_events) / len(historical_events)
        
        if historical_rate == 0:
            return False
        
        slowdown_threshold = self.config["analytics_settings"]["slowdown_detection_threshold"]
        return recent_rate < historical_rate * slowdown_threshold
    
    def _update_analytics(self, event: XPGainEvent):
        """Update analytics data with enhanced tracking."""
        # Update hourly rates
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.hourly_xp_rates.append({
            "hour": current_hour.isoformat(),
            "xp_gained": event.amount,
            "profession": event.profession,
            "source": event.source,
            "zone": event.zone
        })
        
        # Update daily totals
        current_day = datetime.now().date()
        daily_total = sum(e.amount for e in self.xp_events 
                         if datetime.fromisoformat(e.timestamp).date() == current_day)
        
        self.daily_xp_totals.append({
            "date": current_day.isoformat(),
            "total_xp": daily_total
        })
    
    def get_skill_progress(self, skill_name: str) -> Optional[SkillProgress]:
        """Get progress for a specific skill.
        
        Parameters
        ----------
        skill_name : str
            Name of the skill
            
        Returns
        -------
        SkillProgress or None
            Skill progress if found
        """
        for progress in self.skill_progress.values():
            if progress.skill_name == skill_name:
                return progress
        return None
    
    def get_fastest_progressing_skills(self, limit: int = 5) -> List[SkillProgress]:
        """Get skills progressing fastest.
        
        Parameters
        ----------
        limit : int
            Maximum number of skills to return
            
        Returns
        -------
        list
            List of fastest progressing skills
        """
        sorted_skills = sorted(
            self.skill_progress.values(),
            key=lambda x: x.progress_rate,
            reverse=True
        )
        return sorted_skills[:limit]
    
    def get_slowest_progressing_skills(self, limit: int = 5) -> List[SkillProgress]:
        """Get skills progressing slowest.
        
        Parameters
        ----------
        limit : int
            Maximum number of skills to return
            
        Returns
        -------
        list
            List of slowest progressing skills
        """
        sorted_skills = sorted(
            self.skill_progress.values(),
            key=lambda x: x.progress_rate
        )
        return sorted_skills[:limit]
    
    def calculate_xp_rate_per_hour(self, hours: int = 1) -> float:
        """Calculate XP gain rate per hour.
        
        Parameters
        ----------
        hours : int
            Number of hours to look back
            
        Returns
        -------
        float
            XP per hour rate
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [e for e in self.xp_events 
                        if datetime.fromisoformat(e.timestamp) > cutoff_time]
        
        if not recent_events:
            return 0.0
        
        total_xp = sum(e.amount for e in recent_events)
        return total_xp / hours
    
    def detect_leveling_slowdowns(self, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Detect skills that are leveling slower than expected.
        
        Parameters
        ----------
        threshold : float
            Slowdown threshold (0.5 = 50% slower than average)
            
        Returns
        -------
        list
            List of skills with slowdowns
        """
        slowdowns = []
        avg_rate = statistics.mean([s.progress_rate for s in self.skill_progress.values()])
        
        for progress in self.skill_progress.values():
            if progress.progress_rate < avg_rate * threshold:
                slowdowns.append({
                    "skill": progress.skill_name,
                    "profession": progress.profession,
                    "current_rate": progress.progress_rate,
                    "expected_rate": avg_rate,
                    "slowdown_percentage": ((avg_rate - progress.progress_rate) / avg_rate) * 100,
                    "zone_preferences": dict(progress.zone_preferences),
                    "quest_completion_rate": progress.quest_completion_rate
                })
        
        return sorted(slowdowns, key=lambda x: x["slowdown_percentage"], reverse=True)
    
    def recommend_optimal_skill_paths(self) -> Dict[str, List[str]]:
        """Recommend optimal skill paths based on current progress.
        
        Returns
        -------
        dict
            Recommended skill paths by profession
        """
        recommendations = {}
        
        for profession, config in self.config["professions"].items():
            profession_skills = config["skills"]
            skill_progress = {}
            
            # Get progress for each skill in profession
            for skill in profession_skills:
                progress = self.get_skill_progress(skill)
                if progress:
                    skill_progress[skill] = progress.progress_rate
                else:
                    skill_progress[skill] = 0.0
            
            # Sort by progress rate (fastest first)
            sorted_skills = sorted(skill_progress.items(), key=lambda x: x[1], reverse=True)
            recommendations[profession] = [skill for skill, rate in sorted_skills]
        
        return recommendations
    
    def get_profession_analytics(self, profession: str) -> Optional[ProfessionAnalytics]:
        """Get analytics for a specific profession.
        
        Parameters
        ----------
        profession : str
            Profession name
            
        Returns
        -------
        ProfessionAnalytics or None
            Profession analytics if found
        """
        profession_skills = [s for s in self.skill_progress.values() 
                           if s.profession.lower() == profession.lower()]
        
        if not profession_skills:
            return None
        
        total_xp = sum(s.total_xp for s in profession_skills)
        avg_level = statistics.mean(s.current_level for s in profession_skills)
        
        fastest_skill = max(profession_skills, key=lambda x: x.progress_rate)
        slowest_skill = min(profession_skills, key=lambda x: x.progress_rate)
        
        # Calculate XP per hour for profession
        profession_events = [e for e in self.xp_events 
                           if e.profession.lower() == profession.lower()]
        recent_events = [e for e in profession_events 
                        if (datetime.now() - datetime.fromisoformat(e.timestamp)).total_seconds() < 3600]
        xp_per_hour = sum(e.amount for e in recent_events)
        
        # Calculate quest completion rate
        quest_events = [e for e in profession_events if e.source == "quest"]
        quest_completion_rate = len(quest_events) / max(len(profession_events), 1)
        
        # Get optimal zones for profession
        optimal_zones = self.config["professions"].get(profession, {}).get("optimal_zones", [])
        
        # Get skill path recommendation
        skill_path_recommendation = self.recommend_optimal_skill_paths().get(profession, [])
        
        return ProfessionAnalytics(
            profession_name=profession,
            total_xp=total_xp,
            skills_count=len(profession_skills),
            average_level=avg_level,
            fastest_skill=fastest_skill.skill_name,
            slowest_skill=slowest_skill.skill_name,
            xp_per_hour=xp_per_hour,
            session_duration=(datetime.now() - self.session_start_time).total_seconds() / 3600 if self.session_start_time else 0,
            quest_completion_rate=quest_completion_rate,
            optimal_zones=optimal_zones,
            skill_path_recommendation=skill_path_recommendation
        )
    
    def generate_xp_summary(self) -> Dict[str, Any]:
        """Generate comprehensive XP summary.
        
        Returns
        -------
        dict
            XP summary with analytics
        """
        if not self.xp_events:
            return {"error": "No XP events recorded"}
        
        total_xp = sum(e.amount for e in self.xp_events)
        session_duration = (datetime.now() - self.session_start_time).total_seconds() / 3600 if self.session_start_time else 0
        
        # XP by source
        xp_by_source = defaultdict(int)
        for event in self.xp_events:
            xp_by_source[event.source] += event.amount
        
        # XP by profession
        xp_by_profession = defaultdict(int)
        for event in self.xp_events:
            xp_by_profession[event.profession] += event.amount
        
        # XP by zone
        xp_by_zone = defaultdict(int)
        for event in self.xp_events:
            if event.zone:
                xp_by_zone[event.zone] += event.amount
        
        # Top gaining skills
        xp_by_skill = defaultdict(int)
        for event in self.xp_events:
            xp_by_skill[event.skill] += event.amount
        
        top_skills = sorted(xp_by_skill.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_xp": total_xp,
            "session_duration_hours": session_duration,
            "xp_per_hour": total_xp / max(session_duration, 1),
            "xp_by_source": dict(xp_by_source),
            "xp_by_profession": dict(xp_by_profession),
            "xp_by_zone": dict(xp_by_zone),
            "top_gaining_skills": dict(top_skills),
            "fastest_progressing_skills": [s.skill_name for s in self.get_fastest_progressing_skills()],
            "slowdowns_detected": self.detect_leveling_slowdowns(),
            "optimal_paths": self.recommend_optimal_skill_paths(),
            "zone_efficiency": {zone: data["total_xp"] / max(data["events"], 1) 
                              for zone, data in self.zone_xp_efficiency.items()}
        }
    
    def create_xp_visualization(self, save_path: str = None) -> str:
        """Create XP visualization charts.
        
        Parameters
        ----------
        save_path : str, optional
            Path to save the visualization
            
        Returns
        -------
        str
            Path to saved visualization
        """
        if not MATPLOTLIB_AVAILABLE:
            log_event("[XP_TRACKER] Matplotlib not available - visualization disabled")
            return None
            
        if not self.xp_events:
            log_event("[XP_TRACKER] No XP events to visualize")
            return None
        
        try:
            # Set up the plot style
            plt.style.use('seaborn')
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('XP Tracker Analytics Dashboard', fontsize=16, fontweight='bold')
            
            # 1. XP over time
            timestamps = [datetime.fromisoformat(e.timestamp) for e in self.xp_events]
            xp_amounts = [e.amount for e in self.xp_events]
            cumulative_xp = [sum(xp_amounts[:i+1]) for i in range(len(xp_amounts))]
            
            axes[0, 0].plot(timestamps, cumulative_xp, marker='o', linewidth=2, markersize=4)
            axes[0, 0].set_title('Cumulative XP Over Time')
            axes[0, 0].set_xlabel('Time')
            axes[0, 0].set_ylabel('Cumulative XP')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 2. XP by source
            xp_by_source = defaultdict(int)
            for event in self.xp_events:
                xp_by_source[event.source] += event.amount
            
            if xp_by_source:
                sources = list(xp_by_source.keys())
                amounts = list(xp_by_source.values())
                axes[0, 1].pie(amounts, labels=sources, autopct='%1.1f%%', startangle=90)
                axes[0, 1].set_title('XP by Source')
            
            # 3. XP by profession
            xp_by_profession = defaultdict(int)
            for event in self.xp_events:
                xp_by_profession[event.profession] += event.amount
            
            if xp_by_profession:
                professions = list(xp_by_profession.keys())
                amounts = list(xp_by_profession.values())
                axes[1, 0].bar(professions, amounts, color='skyblue')
                axes[1, 0].set_title('XP by Profession')
                axes[1, 0].set_xlabel('Profession')
                axes[1, 0].set_ylabel('Total XP')
                axes[1, 0].tick_params(axis='x', rotation=45)
            
            # 4. Top skills by XP rate
            fastest_skills = self.get_fastest_progressing_skills(5)
            if fastest_skills:
                skill_names = [s.skill_name for s in fastest_skills]
                rates = [s.progress_rate for s in fastest_skills]
                axes[1, 1].barh(skill_names, rates, color='lightgreen')
                axes[1, 1].set_title('Fastest Progressing Skills')
                axes[1, 1].set_xlabel('XP per Hour')
            
            plt.tight_layout()
            
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"logs/xp_visualization_{timestamp}.png"
            
            Path(save_path).parent.mkdir(exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            log_event(f"[XP_TRACKER] Created XP visualization: {save_path}")
            return save_path
            
        except Exception as e:
            log_event(f"[XP_TRACKER] Error creating visualization: {e}")
            return None
    
    def export_xp_data(self, filepath: str = None) -> str:
        """Export XP data to JSON file with enhanced session summary.
        
        Parameters
        ----------
        filepath : str, optional
            Path to save the export file
            
        Returns
        -------
        str
            Path to the exported file
        """
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/session_logs/xp_data_{timestamp}.json"
        
        # Generate session summary
        summary = self.generate_xp_summary()
        session_summary = XPSessionSummary(
            session_id=self.current_session_id,
            start_time=self.session_start_time.isoformat() if self.session_start_time else None,
            end_time=datetime.now().isoformat(),
            total_xp=summary.get("total_xp", 0),
            xp_per_hour=summary.get("xp_per_hour", 0),
            profession_breakdown=summary.get("xp_by_profession", {}),
            skill_breakdown=summary.get("top_gaining_skills", {}),
            source_breakdown=summary.get("xp_by_source", {}),
            fastest_skills=summary.get("fastest_progressing_skills", []),
            slowdowns_detected=summary.get("slowdowns_detected", []),
            optimal_paths=summary.get("optimal_paths", {}),
            zone_efficiency=summary.get("zone_efficiency", {})
        )
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "session_summary": asdict(session_summary),
            "xp_events": [asdict(event) for event in self.xp_events],
            "skill_progress": {k: asdict(v) for k, v in self.skill_progress.items()},
            "hourly_rates": list(self.hourly_xp_rates),
            "daily_totals": list(self.daily_xp_totals),
            "zone_efficiency": dict(self.zone_xp_efficiency),
            "summary": summary
        }
        
        Path(filepath).parent.mkdir(exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        log_event(f"[XP_TRACKER] Exported XP data to {filepath}")
        return filepath
    
    def get_zone_recommendations(self, profession: str) -> List[Dict[str, Any]]:
        """Get zone recommendations for a profession based on XP efficiency.
        
        Parameters
        ----------
        profession : str
            Profession name
            
        Returns
        -------
        list
            List of zone recommendations with efficiency data
        """
        profession_events = [e for e in self.xp_events 
                           if e.profession.lower() == profession.lower()]
        
        zone_efficiency = defaultdict(lambda: {"total_xp": 0, "events": 0, "avg_xp": 0})
        
        for event in profession_events:
            if event.zone:
                zone_efficiency[event.zone]["total_xp"] += event.amount
                zone_efficiency[event.zone]["events"] += 1
        
        # Calculate average XP per event for each zone
        for zone, data in zone_efficiency.items():
            data["avg_xp"] = data["total_xp"] / max(data["events"], 1)
        
        # Sort by efficiency
        sorted_zones = sorted(zone_efficiency.items(), 
                            key=lambda x: x[1]["avg_xp"], reverse=True)
        
        return [{"zone": zone, **data} for zone, data in sorted_zones]
    
    def reset_session(self) -> None:
        """Reset session XP tracking."""
        self.session_xp_gains.clear()
        self.zone_xp_efficiency.clear()
        self.hourly_xp_rates.clear()
        self.daily_xp_totals.clear()
        
        log_event("[XP_TRACKER] Session XP tracking reset") 