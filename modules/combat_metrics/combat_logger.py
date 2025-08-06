"""
Combat Logger - Core combat metrics tracking system.

This module provides comprehensive combat session logging including:
- Real-time DPS calculation
- Ability usage tracking
- Enemy engagement statistics
- Session performance metrics
- Combat event logging
"""

import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from enum import Enum

logger = logging.getLogger(__name__)


class CombatEventType(Enum):
    """Types of combat events that can be logged."""
    ABILITY_USE = "ability_use"
    DAMAGE_DEALT = "damage_dealt"
    ENEMY_KILLED = "enemy_killed"
    PLAYER_DEATH = "player_death"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    ROTATION_START = "rotation_start"
    ROTATION_END = "rotation_end"


@dataclass
class CombatEvent:
    """Represents a single combat event."""
    event_type: CombatEventType
    timestamp: datetime
    ability_name: Optional[str] = None
    target: Optional[str] = None
    damage_dealt: Optional[int] = None
    damage_type: Optional[str] = None
    success: Optional[bool] = None
    cooldown_remaining: Optional[float] = None
    xp_gained: Optional[int] = None
    enemy_type: Optional[str] = None
    session_id: Optional[str] = None
    rotation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class CombatSession:
    """Represents a complete combat session."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[CombatEvent] = None
    total_damage_dealt: int = 0
    total_xp_gained: int = 0
    kills: int = 0
    deaths: int = 0
    targets_engaged: List[str] = None
    abilities_used: Dict[str, int] = None
    session_state: str = "active"
    
    def __post_init__(self):
        if self.events is None:
            self.events = []
        if self.targets_engaged is None:
            self.targets_engaged = []
        if self.abilities_used is None:
            self.abilities_used = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        data['events'] = [event.to_dict() for event in self.events]
        return data


class CombatLogger:
    """Comprehensive combat metrics logging system."""
    
    def __init__(self, logs_dir: str = "logs/combat"):
        """Initialize the combat logger.
        
        Parameters
        ----------
        logs_dir : str
            Directory to store combat log files
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[CombatSession] = None
        self.session_history: List[CombatSession] = []
        
        # Performance tracking
        self.dps_window = 60.0  # seconds for DPS calculation
        self.recent_damage_events: List[CombatEvent] = []
        
        # Statistics
        self.total_sessions = 0
        self.total_damage_dealt = 0
        self.total_xp_gained = 0
        self.total_kills = 0
        self.total_deaths = 0
        
        logger.info(f"CombatLogger initialized with logs directory: {self.logs_dir}")
    
    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new combat session.
        
        Parameters
        ----------
        session_id : str, optional
            Custom session ID, auto-generated if not provided
            
        Returns
        -------
        str
            Session ID for the new session
        """
        if session_id is None:
            session_id = f"combat_session_{int(time.time())}"
        
        self.current_session = CombatSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        # Log session start event
        self._log_event(CombatEventType.SESSION_START)
        
        logger.info(f"Started combat session: {session_id}")
        return session_id
    
    def end_session(self) -> Optional[Dict[str, Any]]:
        """End the current combat session.
        
        Returns
        -------
        dict, optional
            Session summary if session was active
        """
        if not self.current_session:
            logger.warning("No active session to end")
            return None
        
        self.current_session.end_time = datetime.now()
        self.current_session.session_state = "completed"
        
        # Log session end event
        self._log_event(CombatEventType.SESSION_END)
        
        # Calculate final statistics
        session_summary = self._calculate_session_summary()
        
        # Save session to file
        self._save_session(self.current_session)
        
        # Update global statistics
        self._update_global_stats(self.current_session)
        
        # Add to history
        self.session_history.append(self.current_session)
        self.total_sessions += 1
        
        logger.info(f"Ended combat session: {self.current_session.session_id}")
        logger.info(f"Session summary: {session_summary}")
        
        # Clear current session
        self.current_session = None
        
        return session_summary
    
    def log_ability_use(self, ability_name: str, target: str = None, 
                       damage_dealt: int = None, damage_type: str = None,
                       success: bool = True, cooldown_remaining: float = None,
                       xp_gained: int = None) -> None:
        """Log an ability usage event.
        
        Parameters
        ----------
        ability_name : str
            Name of the ability used
        target : str, optional
            Target of the ability
        damage_dealt : int, optional
            Damage dealt by the ability
        damage_type : str, optional
            Type of damage (physical, energy, etc.)
        success : bool
            Whether the ability was successful
        cooldown_remaining : float, optional
            Remaining cooldown time
        xp_gained : int, optional
            XP gained from the ability use
        """
        if not self.current_session:
            logger.warning("No active session to log ability use")
            return
        
        # Log ability use event
        self._log_event(
            CombatEventType.ABILITY_USE,
            ability_name=ability_name,
            target=target,
            damage_dealt=damage_dealt,
            damage_type=damage_type,
            success=success,
            cooldown_remaining=cooldown_remaining,
            xp_gained=xp_gained
        )
        
        # Update session statistics
        if damage_dealt:
            self.current_session.total_damage_dealt += damage_dealt
            self._add_damage_event(damage_dealt)
        
        if xp_gained:
            self.current_session.total_xp_gained += xp_gained
        
        # Track ability usage
        if ability_name not in self.current_session.abilities_used:
            self.current_session.abilities_used[ability_name] = 0
        self.current_session.abilities_used[ability_name] += 1
        
        # Track target
        if target and target not in self.current_session.targets_engaged:
            self.current_session.targets_engaged.append(target)
        
        logger.debug(f"Logged ability use: {ability_name} -> {target} (damage: {damage_dealt})")
    
    def log_enemy_kill(self, enemy_type: str, xp_gained: int = None) -> None:
        """Log an enemy kill event.
        
        Parameters
        ----------
        enemy_type : str
            Type of enemy killed
        xp_gained : int, optional
            XP gained from the kill
        """
        if not self.current_session:
            logger.warning("No active session to log enemy kill")
            return
        
        # Log kill event
        self._log_event(
            CombatEventType.ENEMY_KILLED,
            enemy_type=enemy_type,
            xp_gained=xp_gained
        )
        
        # Update session statistics
        self.current_session.kills += 1
        if xp_gained:
            self.current_session.total_xp_gained += xp_gained
        
        logger.debug(f"Logged enemy kill: {enemy_type} (XP: {xp_gained})")
    
    def log_player_death(self) -> None:
        """Log a player death event."""
        if not self.current_session:
            logger.warning("No active session to log player death")
            return
        
        # Log death event
        self._log_event(CombatEventType.PLAYER_DEATH)
        
        # Update session statistics
        self.current_session.deaths += 1
        
        logger.debug("Logged player death")
    
    def get_current_dps(self) -> float:
        """Calculate current DPS over the last window period.
        
        Returns
        -------
        float
            Current DPS (damage per second)
        """
        if not self.current_session:
            return 0.0
        
        # Clean old damage events
        current_time = datetime.now()
        self.recent_damage_events = [
            event for event in self.recent_damage_events
            if (current_time - event.timestamp).total_seconds() <= self.dps_window
        ]
        
        if not self.recent_damage_events:
            return 0.0
        
        # Calculate total damage in window
        total_damage = sum(event.damage_dealt or 0 for event in self.recent_damage_events)
        
        # Calculate time span
        oldest_event = min(self.recent_damage_events, key=lambda x: x.timestamp)
        time_span = (current_time - oldest_event.timestamp).total_seconds()
        
        if time_span <= 0:
            return 0.0
        
        dps = total_damage / time_span
        return dps
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics.
        
        Returns
        -------
        dict
            Current session statistics
        """
        if not self.current_session:
            return {}
        
        session_duration = (datetime.now() - self.current_session.start_time).total_seconds()
        
        return {
            "session_id": self.current_session.session_id,
            "duration": session_duration,
            "total_damage_dealt": self.current_session.total_damage_dealt,
            "total_xp_gained": self.current_session.total_xp_gained,
            "kills": self.current_session.kills,
            "deaths": self.current_session.deaths,
            "current_dps": self.get_current_dps(),
            "average_dps": self.current_session.total_damage_dealt / session_duration if session_duration > 0 else 0,
            "abilities_used": self.current_session.abilities_used.copy(),
            "targets_engaged": self.current_session.targets_engaged.copy(),
            "session_state": self.current_session.session_state
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global combat statistics across all sessions.
        
        Returns
        -------
        dict
            Global combat statistics
        """
        return {
            "total_sessions": self.total_sessions,
            "total_damage_dealt": self.total_damage_dealt,
            "total_xp_gained": self.total_xp_gained,
            "total_kills": self.total_kills,
            "total_deaths": self.total_deaths,
            "average_damage_per_session": self.total_damage_dealt / self.total_sessions if self.total_sessions > 0 else 0,
            "average_xp_per_session": self.total_xp_gained / self.total_sessions if self.total_sessions > 0 else 0,
            "kill_death_ratio": self.total_kills / self.total_deaths if self.total_deaths > 0 else float('inf')
        }
    
    def _log_event(self, event_type: CombatEventType, **kwargs) -> None:
        """Log a combat event to the current session.
        
        Parameters
        ----------
        event_type : CombatEventType
            Type of event to log
        **kwargs
            Additional event data
        """
        if not self.current_session:
            return
        
        event = CombatEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            session_id=self.current_session.session_id,
            **kwargs
        )
        
        self.current_session.events.append(event)
    
    def _add_damage_event(self, damage_dealt: int) -> None:
        """Add a damage event for DPS calculation.
        
        Parameters
        ----------
        damage_dealt : int
            Amount of damage dealt
        """
        if not self.current_session:
            return
        
        event = CombatEvent(
            event_type=CombatEventType.DAMAGE_DEALT,
            timestamp=datetime.now(),
            damage_dealt=damage_dealt,
            session_id=self.current_session.session_id
        )
        
        self.recent_damage_events.append(event)
    
    def _calculate_session_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics for the current session.
        
        Returns
        -------
        dict
            Session summary statistics
        """
        if not self.current_session:
            return {}
        
        session_duration = (self.current_session.end_time - self.current_session.start_time).total_seconds()
        
        return {
            "session_id": self.current_session.session_id,
            "duration": session_duration,
            "total_damage_dealt": self.current_session.total_damage_dealt,
            "total_xp_gained": self.current_session.total_xp_gained,
            "kills": self.current_session.kills,
            "deaths": self.current_session.deaths,
            "average_dps": self.current_session.total_damage_dealt / session_duration if session_duration > 0 else 0,
            "xp_per_hour": (self.current_session.total_xp_gained / session_duration) * 3600 if session_duration > 0 else 0,
            "damage_per_hour": (self.current_session.total_damage_dealt / session_duration) * 3600 if session_duration > 0 else 0,
            "abilities_used": self.current_session.abilities_used,
            "targets_engaged": self.current_session.targets_engaged
        }
    
    def _save_session(self, session: CombatSession) -> None:
        """Save a session to a JSON file.
        
        Parameters
        ----------
        session : CombatSession
            Session to save
        """
        filename = f"combat_stats_{session.session_id}.json"
        filepath = self.logs_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)
        
        logger.debug(f"Saved session to: {filepath}")
    
    def _update_global_stats(self, session: CombatSession) -> None:
        """Update global statistics with session data.
        
        Parameters
        ----------
        session : CombatSession
            Session to add to global stats
        """
        self.total_damage_dealt += session.total_damage_dealt
        self.total_xp_gained += session.total_xp_gained
        self.total_kills += session.kills
        self.total_deaths += session.deaths 