#!/usr/bin/env python3
"""
SWGDB Private API v1 - Session Data Pydantic Models
Pydantic models for session data validation
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator

class PerformanceMetrics(BaseModel):
    """Performance metrics for a session."""
    fps_average: Optional[float] = Field(None, ge=0, le=1000, description="Average FPS during the session")
    cpu_usage: Optional[float] = Field(None, ge=0, le=100, description="Average CPU usage percentage")
    memory_usage: Optional[float] = Field(None, ge=0, description="Average memory usage in MB")
    network_latency: Optional[float] = Field(None, ge=0, description="Average network latency in ms")

class CombatStats(BaseModel):
    """Combat statistics for a session."""
    kills: Optional[int] = Field(None, ge=0, description="Number of kills during the session")
    deaths: Optional[int] = Field(None, ge=0, description="Number of deaths during the session")
    damage_dealt: Optional[int] = Field(None, ge=0, description="Total damage dealt during the session")
    damage_taken: Optional[int] = Field(None, ge=0, description="Total damage taken during the session")
    healing_done: Optional[int] = Field(None, ge=0, description="Total healing done during the session")

class CraftingStats(BaseModel):
    """Crafting statistics for a session."""
    items_crafted: Optional[int] = Field(None, ge=0, description="Number of items crafted during the session")
    materials_used: Optional[int] = Field(None, ge=0, description="Number of materials used during the session")
    experimentation_success_rate: Optional[float] = Field(None, ge=0, le=100, description="Experimentation success rate percentage")

class QuestStats(BaseModel):
    """Quest statistics for a session."""
    quests_completed: Optional[int] = Field(None, ge=0, description="Number of quests completed during the session")
    quests_started: Optional[int] = Field(None, ge=0, description="Number of quests started during the session")
    quest_xp_gained: Optional[int] = Field(None, ge=0, description="XP gained from quests during the session")

class SessionData(BaseModel):
    """Session data model."""
    session_id: str = Field(..., min_length=1, max_length=255, description="Unique identifier for the session")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp when the session occurred")
    duration_minutes: Optional[int] = Field(None, ge=0, le=1440, description="Duration of the session in minutes")
    xp_gained: Optional[int] = Field(None, ge=0, le=1000000, description="Experience points gained during the session")
    credits_earned: Optional[int] = Field(None, ge=0, le=1000000000, description="Credits earned during the session")
    location: Optional[str] = Field(None, max_length=255, description="Location where the session took place")
    activity_type: Optional[str] = Field("unknown", description="Type of activity performed during the session")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes about the session")
    character_name: Optional[str] = Field(None, max_length=100, description="Name of the character involved in the session")
    profession: Optional[str] = Field(None, max_length=50, description="Character's profession during the session")
    level: Optional[int] = Field(None, ge=1, le=90, description="Character's level during the session")
    server: Optional[str] = Field(None, max_length=50, description="Server where the session took place")
    faction: Optional[str] = Field("unknown", description="Character's faction during the session")
    performance_metrics: Optional[PerformanceMetrics] = Field(None, description="Performance metrics for the session")
    combat_stats: Optional[CombatStats] = Field(None, description="Combat statistics for the session")
    crafting_stats: Optional[CraftingStats] = Field(None, description="Crafting statistics for the session")
    quest_stats: Optional[QuestStats] = Field(None, description="Quest statistics for the session")

    @validator('activity_type')
    def validate_activity_type(cls, v):
        """Validate activity type."""
        valid_types = [
            "combat", "crafting", "questing", "farming", 
            "trading", "exploration", "social", "other", "unknown"
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid activity type. Must be one of: {valid_types}")
        return v

    @validator('faction')
    def validate_faction(cls, v):
        """Validate faction."""
        valid_factions = ["rebel", "imperial", "neutral", "unknown"]
        if v not in valid_factions:
            raise ValueError(f"Invalid faction. Must be one of: {valid_factions}")
        return v

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Invalid timestamp format. Must be ISO 8601 format.")
        return v

    @validator('session_id')
    def validate_session_id(cls, v):
        """Validate session ID format."""
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Session ID must contain only alphanumeric characters, hyphens, and underscores.")
        return v

class SessionIngestRequest(BaseModel):
    """Request model for session ingestion."""
    session_data: SessionData = Field(..., description="Session data to be ingested")

class SessionIngestResponse(BaseModel):
    """Response model for session ingestion."""
    success: bool = Field(..., description="Whether the ingestion was successful")
    session_id: str = Field(..., description="Session ID that was ingested")
    discord_id: str = Field(..., description="Discord ID of the user")
    ingested_at: str = Field(..., description="Timestamp when the data was ingested")
    message: str = Field(..., description="Response message")

# Additional models for API responses
class SessionStats(BaseModel):
    """Session statistics model."""
    total_sessions: int = Field(0, description="Total number of sessions")
    total_duration_minutes: int = Field(0, description="Total duration in minutes")
    total_xp_gained: int = Field(0, description="Total XP gained")
    total_credits_earned: int = Field(0, description="Total credits earned")
    average_session_length: float = Field(0, description="Average session length in minutes")

class UserSessionsResponse(BaseModel):
    """Response model for user sessions retrieval."""
    discord_id: str = Field(..., description="Discord ID of the user")
    sessions: List[Dict[str, Any]] = Field(..., description="List of user sessions")
    stats: SessionStats = Field(..., description="User session statistics")
    retrieved_at: str = Field(..., description="Timestamp when data was retrieved")

# Utility functions
def create_session_data(
    session_id: str,
    duration_minutes: Optional[int] = None,
    xp_gained: Optional[int] = None,
    credits_earned: Optional[int] = None,
    location: Optional[str] = None,
    activity_type: str = "unknown",
    notes: Optional[str] = None,
    character_name: Optional[str] = None,
    profession: Optional[str] = None,
    level: Optional[int] = None,
    server: Optional[str] = None,
    faction: str = "unknown",
    timestamp: Optional[str] = None
) -> SessionData:
    """
    Create a SessionData instance with the given parameters.
    
    Args:
        session_id: Unique session identifier
        duration_minutes: Session duration in minutes
        xp_gained: XP gained during session
        credits_earned: Credits earned during session
        location: Session location
        activity_type: Type of activity performed
        notes: Additional notes
        character_name: Character name
        profession: Character profession
        level: Character level
        server: Server name
        faction: Character faction
        timestamp: Session timestamp (ISO 8601)
    
    Returns:
        SessionData instance
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    return SessionData(
        session_id=session_id,
        timestamp=timestamp,
        duration_minutes=duration_minutes,
        xp_gained=xp_gained,
        credits_earned=credits_earned,
        location=location,
        activity_type=activity_type,
        notes=notes,
        character_name=character_name,
        profession=profession,
        level=level,
        server=server,
        faction=faction
    )

def validate_session_json(data: Dict[str, Any]) -> bool:
    """
    Validate session data against JSON schema.
    
    Args:
        data: Session data dictionary
    
    Returns:
        True if valid, False otherwise
    """
    try:
        # Create request model to validate
        request = SessionIngestRequest(session_data=data.get("session_data", {}))
        return True
    except Exception:
        return False 