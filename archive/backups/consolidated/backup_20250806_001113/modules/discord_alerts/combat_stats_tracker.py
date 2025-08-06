"""Combat Stats Tracker for advanced performance monitoring.

This module tracks comprehensive combat statistics including:
- Total damage dealt and DPS over time
- Kill count by enemy type
- Skill usage frequency and effectiveness
- Combat session duration and efficiency
- Real-time performance metrics
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict, deque
from dataclasses import dataclass, asdict

from core.combat_metrics_logger import CombatMetricsLogger
from core.dps_analyzer import DPSAnalyzer
from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

@dataclass
class SkillUsage:
    """Data class for tracking skill usage statistics."""
    name: str
    usage_count: int = 0
    total_damage: int = 0
    average_damage: float = 0.0
    last_used: Optional[datetime] = None
    cooldown_time: float = 0.0
    uptime_percentage: float = 0.0
    skill_line: str = "unknown"

@dataclass
class CombatSession:
    """Data class for tracking individual combat sessions."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    enemy_type: str = "unknown"
    enemy_level: int = 1
    total_damage: int = 0
    skills_used: List[str] = None
    duration: float = 0.0
    dps: float = 0.0
    result: str = "unknown"

@dataclass
class PerformanceSummary:
    """Data class for overall performance summary."""
    session_id: str
    total_damage: int
    total_kills: int
    session_duration: float
    average_dps: float
    most_used_skills: List[Tuple[str, int]]
    least_used_skills: List[Tuple[str, int]]
    skill_line_uptime: Dict[str, float]
    efficiency_score: float
    timestamp: datetime

class CombatStatsTracker:
    """Advanced combat statistics tracker with real-time monitoring."""
    
    def __init__(self, session_id: str = None):
        """Initialize the combat stats tracker.
        
        Parameters
        ----------
        session_id : str, optional
            Unique session identifier
        """
        self.session_id = session_id or f"combat_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start = datetime.now()
        self.session_end = None
        
        # Core tracking data
        self.total_damage = 0
        self.total_kills = 0
        self.session_duration = 0.0
        
        # Skill tracking
        self.skills_usage = defaultdict(lambda: SkillUsage(name=""))
        self.skill_line_uptime = defaultdict(float)
        self.skill_cooldowns = {}
        
        # Combat sessions
        self.combat_sessions = []
        self.current_session = None
        
        # Performance metrics
        self.dps_samples = deque(maxlen=100)
        self.damage_by_enemy_type = defaultdict(int)
        self.kills_by_enemy_type = defaultdict(int)
        
        # Real-time tracking
        self.last_update = datetime.now()
        self.update_interval = 1.0  # seconds
        
        # Integration with existing systems
        self.metrics_logger = CombatMetricsLogger(session_id=self.session_id)
        self.dps_analyzer = DPSAnalyzer(self.metrics_logger)
        
        # Log directory
        self.log_dir = Path("logs/combat_stats")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        log_event(f"[COMBAT_STATS] Initialized tracker for session: {self.session_id}")
    
    def start_combat_session(self, enemy_type: str = "unknown", enemy_level: int = 1) -> str:
        """Start a new combat session.
        
        Parameters
        ----------
        enemy_type : str
            Type of enemy being fought
        enemy_level : int
            Level of the enemy
            
        Returns
        -------
        str
            Combat session ID
        """
        session_id = f"combat_{len(self.combat_sessions)}_{datetime.now().strftime('%H%M%S')}"
        
        self.current_session = CombatSession(
            session_id=session_id,
            start_time=datetime.now(),
            enemy_type=enemy_type,
            enemy_level=enemy_level,
            skills_used=[]
        )
        
        # Also start the metrics logger session
        self.metrics_logger.start_combat_session(enemy_type, enemy_level)
        
        log_event(f"[COMBAT_STATS] Started combat session {session_id} vs {enemy_type} (L{enemy_level})")
        return session_id
    
    def end_combat_session(self, result: str = "victory", enemy_hp_remaining: int = 0) -> Dict[str, Any]:
        """End the current combat session.
        
        Parameters
        ----------
        result : str
            Result of the combat (victory, defeat, flee)
        enemy_hp_remaining : int
            Remaining HP of the enemy
            
        Returns
        -------
        dict
            Session summary data
        """
        if not self.current_session:
            log_event("[COMBAT_STATS] No active combat session to end")
            return {}
        
        # End the session
        self.current_session.end_time = datetime.now()
        self.current_session.duration = (self.current_session.end_time - self.current_session.start_time).total_seconds()
        self.current_session.result = result
        
        # Calculate DPS for this session
        if self.current_session.duration > 0:
            self.current_session.dps = self.current_session.total_damage / self.current_session.duration
        else:
            self.current_session.dps = 0.0
        
        # Update overall stats
        self.total_damage += self.current_session.total_damage
        if result == "victory":
            self.total_kills += 1
            self.kills_by_enemy_type[self.current_session.enemy_type] += 1
        
        # Store the session
        self.combat_sessions.append(self.current_session)
        
        # End the metrics logger session
        metrics_summary = self.metrics_logger.end_combat_session(result, enemy_hp_remaining)
        
        # Update session duration
        self.session_duration = (datetime.now() - self.session_start).total_seconds()
        
        log_event(f"[COMBAT_STATS] Ended combat session {self.current_session.session_id} - "
                 f"Damage: {self.current_session.total_damage}, DPS: {self.current_session.dps:.2f}")
        
        session_summary = asdict(self.current_session)
        session_summary.update(metrics_summary)
        
        self.current_session = None
        return session_summary
    
    def record_skill_usage(self, skill_name: str, damage_dealt: int = 0, 
                          target: str = None, cooldown: float = 0.0, skill_line: str = "unknown") -> None:
        """Record skill usage and damage.
        
        Parameters
        ----------
        skill_name : str
            Name of the skill used
        damage_dealt : int
            Damage dealt by the skill
        target : str, optional
            Target of the skill
        cooldown : float
            Cooldown time of the skill
        skill_line : str
            Skill line the skill belongs to
        """
        now = datetime.now()
        
        # Update skill usage tracking
        if skill_name not in self.skills_usage:
            self.skills_usage[skill_name] = SkillUsage(name=skill_name, skill_line=skill_line)
        
        skill_usage = self.skills_usage[skill_name]
        skill_usage.usage_count += 1
        skill_usage.total_damage += damage_dealt
        skill_usage.last_used = now
        skill_usage.cooldown_time = cooldown
        skill_usage.skill_line = skill_line
        
        # Calculate average damage
        skill_usage.average_damage = skill_usage.total_damage / skill_usage.usage_count
        
        # Update current session
        if self.current_session:
            self.current_session.total_damage += damage_dealt
            if skill_name not in self.current_session.skills_used:
                self.current_session.skills_used.append(skill_name)
        
        # Update overall damage
        self.total_damage += damage_dealt
        
        # Update skill line uptime
        if skill_line != "unknown":
            self.skill_line_uptime[skill_line] += cooldown
        
        # Record in metrics logger
        self.metrics_logger.record_skill_usage(skill_name, damage_dealt, target, cooldown)
        
        # Update DPS samples
        if self.session_duration > 0:
            current_dps = self.total_damage / self.session_duration
            self.dps_samples.append(current_dps)
        
        log_event(f"[COMBAT_STATS] Skill used: {skill_name} - Damage: {damage_dealt}, "
                 f"Total uses: {skill_usage.usage_count}")
    
    def record_enemy_kill(self, enemy_type: str, damage_dealt: int = 0) -> None:
        """Record an enemy kill.
        
        Parameters
        ----------
        enemy_type : str
            Type of enemy killed
        damage_dealt : int
            Total damage dealt to the enemy
        """
        self.total_kills += 1
        self.kills_by_enemy_type[enemy_type] += 1
        self.damage_by_enemy_type[enemy_type] += damage_dealt
        
        log_event(f"[COMBAT_STATS] Enemy killed: {enemy_type} - Total kills: {self.total_kills}")
    
    def get_performance_summary(self) -> PerformanceSummary:
        """Get comprehensive performance summary.
        
        Returns
        -------
        PerformanceSummary
            Complete performance summary
        """
        # Calculate most and least used skills
        skill_usage_list = [(name, usage.usage_count) for name, usage in self.skills_usage.items()]
        skill_usage_list.sort(key=lambda x: x[1], reverse=True)
        
        most_used_skills = skill_usage_list[:5]  # Top 5
        least_used_skills = skill_usage_list[-5:] if len(skill_usage_list) >= 5 else skill_usage_list
        
        # Calculate average DPS
        average_dps = 0.0
        if self.session_duration > 0:
            average_dps = self.total_damage / self.session_duration
        
        # Calculate efficiency score (damage per second per skill used)
        total_skill_uses = sum(usage.usage_count for usage in self.skills_usage.values())
        efficiency_score = 0.0
        if total_skill_uses > 0 and self.session_duration > 0:
            efficiency_score = (self.total_damage / self.session_duration) / total_skill_uses
        
        # Calculate skill line uptime percentages
        total_uptime = sum(self.skill_line_uptime.values())
        skill_line_uptime_percentages = {}
        if total_uptime > 0:
            for skill_line, uptime in self.skill_line_uptime.items():
                skill_line_uptime_percentages[skill_line] = (uptime / total_uptime) * 100
        
        return PerformanceSummary(
            session_id=self.session_id,
            total_damage=self.total_damage,
            total_kills=self.total_kills,
            session_duration=self.session_duration,
            average_dps=average_dps,
            most_used_skills=most_used_skills,
            least_used_skills=least_used_skills,
            skill_line_uptime=skill_line_uptime_percentages,
            efficiency_score=efficiency_score,
            timestamp=datetime.now()
        )
    
    def get_skill_analysis(self) -> Dict[str, Any]:
        """Get detailed skill analysis.
        
        Returns
        -------
        dict
            Detailed skill analysis data
        """
        analysis = {
            "skill_usage": {},
            "skill_line_analysis": {},
            "effectiveness_ranking": [],
            "unused_skills": []
        }
        
        # Detailed skill usage analysis
        for skill_name, usage in self.skills_usage.items():
            uptime_percentage = 0.0
            if self.session_duration > 0 and usage.cooldown_time > 0:
                uptime_percentage = (usage.usage_count * usage.cooldown_time / self.session_duration) * 100
            
            analysis["skill_usage"][skill_name] = {
                "usage_count": usage.usage_count,
                "total_damage": usage.total_damage,
                "average_damage": usage.average_damage,
                "uptime_percentage": uptime_percentage,
                "skill_line": usage.skill_line,
                "last_used": usage.last_used.isoformat() if usage.last_used else None
            }
        
        # Skill line analysis
        for skill_line, uptime in self.skill_line_uptime.items():
            analysis["skill_line_analysis"][skill_line] = {
                "total_uptime": uptime,
                "uptime_percentage": (uptime / self.session_duration * 100) if self.session_duration > 0 else 0,
                "skills_in_line": [name for name, usage in self.skills_usage.items() 
                                 if usage.skill_line == skill_line]
            }
        
        # Effectiveness ranking
        effectiveness_data = []
        for skill_name, usage in self.skills_usage.items():
            if usage.usage_count > 0:
                effectiveness = usage.total_damage / usage.usage_count
                effectiveness_data.append((skill_name, effectiveness, usage.usage_count))
        
        effectiveness_data.sort(key=lambda x: x[1], reverse=True)
        analysis["effectiveness_ranking"] = effectiveness_data
        
        return analysis
    
    def save_session_data(self) -> str:
        """Save session data to JSON file.
        
        Returns
        -------
        str
            Path to saved file
        """
        session_data = {
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "session_end": self.session_end.isoformat() if self.session_end else None,
            "total_damage": self.total_damage,
            "total_kills": self.total_kills,
            "session_duration": self.session_duration,
            "combat_sessions": [asdict(session) for session in self.combat_sessions],
            "skill_usage": {name: asdict(usage) for name, usage in self.skills_usage.items()},
            "skill_line_uptime": dict(self.skill_line_uptime),
            "damage_by_enemy_type": dict(self.damage_by_enemy_type),
            "kills_by_enemy_type": dict(self.kills_by_enemy_type),
            "performance_summary": asdict(self.get_performance_summary()),
            "skill_analysis": self.get_skill_analysis()
        }
        
        filename = f"combat_stats_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.log_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        log_event(f"[COMBAT_STATS] Saved session data to {filepath}")
        return str(filepath)
    
    def end_session(self) -> Dict[str, Any]:
        """End the tracking session and return final summary.
        
        Returns
        -------
        dict
            Final session summary
        """
        self.session_end = datetime.now()
        self.session_duration = (self.session_end - self.session_start).total_seconds()
        
        # Get final performance summary
        performance_summary = self.get_performance_summary()
        skill_analysis = self.get_skill_analysis()
        
        # Save session data
        saved_file = self.save_session_data()
        
        final_summary = {
            "session_id": self.session_id,
            "session_duration": self.session_duration,
            "performance_summary": asdict(performance_summary),
            "skill_analysis": skill_analysis,
            "saved_file": saved_file,
            "timestamp": datetime.now().isoformat()
        }
        
        log_event(f"[COMBAT_STATS] Session ended - Total damage: {self.total_damage}, "
                 f"Total kills: {self.total_kills}, Duration: {self.session_duration:.2f}s")
        
        return final_summary 