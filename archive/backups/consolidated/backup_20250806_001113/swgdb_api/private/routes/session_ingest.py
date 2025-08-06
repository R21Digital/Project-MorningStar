#!/usr/bin/env python3
"""
SWGDB Private API v1 - Session Ingestion Endpoint
Handles POST /api/private/v1/sessions with Discord ID authentication
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
import hashlib
import hmac
import base64

from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import authentication guard
try:
    from ..auth.discord_token_guard import DiscordTokenGuard, verify_discord_token
except ImportError:
    # Fallback for development
    from auth.discord_token_guard import DiscordTokenGuard, verify_discord_token

# Import session schema
try:
    from ..schemas.session_v1 import SessionData, SessionIngestRequest, SessionIngestResponse
except ImportError:
    # Fallback for development
    from schemas.session_v1 import SessionData, SessionIngestRequest, SessionIngestResponse

# Initialize router
router = APIRouter(prefix="/api/private/v1", tags=["private"])

# Initialize token guard
token_guard = DiscordTokenGuard()

class SessionIngestHandler:
    """Handler for session data ingestion."""
    
    def __init__(self, data_dir: str = "data/character_sessions"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.data_dir / "sessions.json"
        self._load_sessions()
    
    def _load_sessions(self):
        """Load existing sessions data."""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load sessions: {e}")
                self.sessions = {}
        else:
            self.sessions = {}
    
    def _save_sessions(self):
        """Save sessions data to file."""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save sessions: {e}")
            raise HTTPException(status_code=500, detail="Failed to save session data")
    
    def _get_user_namespace(self, discord_id: str) -> str:
        """Get user-specific namespace for data storage."""
        return f"user_{discord_id}"
    
    def _validate_session_data(self, session_data: SessionData) -> bool:
        """Validate session data integrity."""
        try:
            # Check required fields
            if not session_data.session_id:
                return False
            
            # Validate timestamp
            if session_data.timestamp:
                try:
                    datetime.fromisoformat(session_data.timestamp.replace('Z', '+00:00'))
                except ValueError:
                    return False
            
            # Validate numeric fields
            if session_data.duration_minutes and session_data.duration_minutes < 0:
                return False
            
            if session_data.xp_gained and session_data.xp_gained < 0:
                return False
            
            if session_data.credits_earned and session_data.credits_earned < 0:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False
    
    def _process_session_data(self, session_data: SessionData, discord_id: str) -> Dict[str, Any]:
        """Process and store session data."""
        user_namespace = self._get_user_namespace(discord_id)
        
        # Initialize user namespace if not exists
        if user_namespace not in self.sessions:
            self.sessions[user_namespace] = {
                "discord_id": discord_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "sessions": [],
                "stats": {
                    "total_sessions": 0,
                    "total_duration_minutes": 0,
                    "total_xp_gained": 0,
                    "total_credits_earned": 0,
                    "average_session_length": 0
                }
            }
        
        # Validate session data
        if not self._validate_session_data(session_data):
            raise HTTPException(status_code=400, detail="Invalid session data")
        
        # Add session to user's namespace
        session_entry = {
            "session_id": session_data.session_id,
            "timestamp": session_data.timestamp or datetime.now(timezone.utc).isoformat(),
            "duration_minutes": session_data.duration_minutes or 0,
            "xp_gained": session_data.xp_gained or 0,
            "credits_earned": session_data.credits_earned or 0,
            "location": session_data.location or "",
            "activity_type": session_data.activity_type or "unknown",
            "notes": session_data.notes or "",
            "ingested_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Check for duplicate session
        existing_sessions = self.sessions[user_namespace]["sessions"]
        for existing in existing_sessions:
            if existing["session_id"] == session_data.session_id:
                # Update existing session
                existing.update(session_entry)
                logger.info(f"Updated existing session {session_data.session_id} for user {discord_id}")
                break
        else:
            # Add new session
            existing_sessions.append(session_entry)
            self.sessions[user_namespace]["stats"]["total_sessions"] += 1
            logger.info(f"Added new session {session_data.session_id} for user {discord_id}")
        
        # Update user stats
        self._update_user_stats(user_namespace)
        
        # Update last_updated timestamp
        self.sessions[user_namespace]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Save to file
        self._save_sessions()
        
        return session_entry
    
    def _update_user_stats(self, user_namespace: str):
        """Update user statistics."""
        user_data = self.sessions[user_namespace]
        sessions = user_data["sessions"]
        
        if not sessions:
            return
        
        total_duration = sum(s.get("duration_minutes", 0) for s in sessions)
        total_xp = sum(s.get("xp_gained", 0) for s in sessions)
        total_credits = sum(s.get("credits_earned", 0) for s in sessions)
        
        user_data["stats"].update({
            "total_duration_minutes": total_duration,
            "total_xp_gained": total_xp,
            "total_credits_earned": total_credits,
            "average_session_length": total_duration / len(sessions) if sessions else 0
        })
    
    def get_user_sessions(self, discord_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's session history."""
        user_namespace = self._get_user_namespace(discord_id)
        
        if user_namespace not in self.sessions:
            return []
        
        sessions = self.sessions[user_namespace]["sessions"]
        # Sort by timestamp (newest first)
        sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return sessions[:limit]
    
    def get_user_stats(self, discord_id: str) -> Dict[str, Any]:
        """Get user's session statistics."""
        user_namespace = self._get_user_namespace(discord_id)
        
        if user_namespace not in self.sessions:
            return {
                "total_sessions": 0,
                "total_duration_minutes": 0,
                "total_xp_gained": 0,
                "total_credits_earned": 0,
                "average_session_length": 0
            }
        
        return self.sessions[user_namespace]["stats"]

# Initialize handler
session_handler = SessionIngestHandler()

@router.post("/sessions", response_model=SessionIngestResponse)
async def ingest_session(
    request: SessionIngestRequest,
    authorization: str = Header(None),
    x_discord_id: str = Header(None)
):
    """
    Ingest session data for authenticated user.
    
    Args:
        request: Session data to ingest
        authorization: Bearer token for authentication
        x_discord_id: Discord ID header
    
    Returns:
        SessionIngestResponse with ingestion status
    """
    try:
        # Verify authentication
        if not authorization or not x_discord_id:
            raise HTTPException(
                status_code=401, 
                detail="Missing authorization header or Discord ID"
            )
        
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401, 
                detail="Invalid authorization format. Expected 'Bearer <token>'"
            )
        
        token = authorization[7:]  # Remove "Bearer " prefix
        
        # Verify Discord token
        if not verify_discord_token(token, x_discord_id):
            raise HTTPException(
                status_code=401, 
                detail="Invalid or expired token"
            )
        
        logger.info(f"Processing session ingestion for Discord ID: {x_discord_id}")
        
        # Process session data
        session_entry = session_handler._process_session_data(request.session_data, x_discord_id)
        
        # Prepare response
        response = SessionIngestResponse(
            success=True,
            session_id=request.session_data.session_id,
            discord_id=x_discord_id,
            ingested_at=session_entry["ingested_at"],
            message="Session data ingested successfully"
        )
        
        logger.info(f"Successfully ingested session {request.session_data.session_id} for user {x_discord_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session ingestion error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/sessions/{discord_id}", response_model=Dict[str, Any])
async def get_user_sessions(
    discord_id: str,
    limit: int = 50,
    authorization: str = Header(None)
):
    """
    Get user's session history.
    
    Args:
        discord_id: Discord ID to retrieve sessions for
        limit: Maximum number of sessions to return
        authorization: Bearer token for authentication
    
    Returns:
        User's session history and statistics
    """
    try:
        # Verify authentication
        if not authorization:
            raise HTTPException(
                status_code=401, 
                detail="Missing authorization header"
            )
        
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401, 
                detail="Invalid authorization format. Expected 'Bearer <token>'"
            )
        
        token = authorization[7:]  # Remove "Bearer " prefix
        
        # Verify Discord token
        if not verify_discord_token(token, discord_id):
            raise HTTPException(
                status_code=401, 
                detail="Invalid or expired token"
            )
        
        # Get user data
        sessions = session_handler.get_user_sessions(discord_id, limit)
        stats = session_handler.get_user_stats(discord_id)
        
        return {
            "discord_id": discord_id,
            "sessions": sessions,
            "stats": stats,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "session_ingest"
    } 