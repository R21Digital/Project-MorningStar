#!/usr/bin/env python3
"""
SWGDB Private API v1 - Loot Ingestion Endpoint
Handles POST /api/private/v1/loot with Discord ID authentication
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

# Import loot schema
try:
    from ..schemas.loot_v1 import LootData, LootIngestRequest, LootIngestResponse
except ImportError:
    # Fallback for development - create basic schema
    from pydantic import BaseModel
    from typing import List, Optional
    
    class LootItem(BaseModel):
        item_name: str
        quantity: int = 1
        rarity: Optional[str] = None
        value_credits: Optional[int] = None
        item_type: Optional[str] = None
    
    class LootData(BaseModel):
        session_id: str
        timestamp: Optional[str] = None
        location: Optional[str] = None
        loot_items: List[LootItem]
        total_value: Optional[int] = None
        notes: Optional[str] = None
    
    class LootIngestRequest(BaseModel):
        loot_data: LootData
    
    class LootIngestResponse(BaseModel):
        success: bool
        session_id: str
        discord_id: str
        ingested_at: str
        message: str

# Initialize router
router = APIRouter(prefix="/api/private/v1", tags=["private"])

# Initialize token guard
token_guard = DiscordTokenGuard()

class LootIngestHandler:
    """Handler for loot data ingestion."""
    
    def __init__(self, data_dir: str = "data/character_loot"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.loot_file = self.data_dir / "loot.json"
        self._load_loot()
    
    def _load_loot(self):
        """Load existing loot data."""
        if self.loot_file.exists():
            try:
                with open(self.loot_file, 'r', encoding='utf-8') as f:
                    self.loot_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load loot data: {e}")
                self.loot_data = {}
        else:
            self.loot_data = {}
    
    def _save_loot(self):
        """Save loot data to file."""
        try:
            with open(self.loot_file, 'w', encoding='utf-8') as f:
                json.dump(self.loot_data, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save loot data: {e}")
            raise HTTPException(status_code=500, detail="Failed to save loot data")
    
    def _get_user_namespace(self, discord_id: str) -> str:
        """Get user-specific namespace for data storage."""
        return f"user_{discord_id}"
    
    def _validate_loot_data(self, loot_data: LootData) -> bool:
        """Validate loot data integrity."""
        try:
            # Check required fields
            if not loot_data.session_id:
                return False
            
            if not loot_data.loot_items:
                return False
            
            # Validate timestamp
            if loot_data.timestamp:
                try:
                    datetime.fromisoformat(loot_data.timestamp.replace('Z', '+00:00'))
                except ValueError:
                    return False
            
            # Validate loot items
            for item in loot_data.loot_items:
                if not item.item_name:
                    return False
                if item.quantity <= 0:
                    return False
                if item.value_credits and item.value_credits < 0:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Loot validation error: {e}")
            return False
    
    def _calculate_total_value(self, loot_items: List[LootItem]) -> int:
        """Calculate total value of loot items."""
        total = 0
        for item in loot_items:
            if item.value_credits:
                total += item.value_credits * item.quantity
        return total
    
    def _process_loot_data(self, loot_data: LootData, discord_id: str) -> Dict[str, Any]:
        """Process and store loot data."""
        user_namespace = self._get_user_namespace(discord_id)
        
        # Initialize user namespace if not exists
        if user_namespace not in self.loot_data:
            self.loot_data[user_namespace] = {
                "discord_id": discord_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "loot_sessions": [],
                "stats": {
                    "total_sessions": 0,
                    "total_items": 0,
                    "total_value": 0,
                    "unique_items": 0,
                    "average_session_value": 0
                }
            }
        
        # Validate loot data
        if not self._validate_loot_data(loot_data):
            raise HTTPException(status_code=400, detail="Invalid loot data")
        
        # Calculate total value if not provided
        total_value = loot_data.total_value
        if total_value is None:
            total_value = self._calculate_total_value(loot_data.loot_items)
        
        # Prepare loot session entry
        loot_session = {
            "session_id": loot_data.session_id,
            "timestamp": loot_data.timestamp or datetime.now(timezone.utc).isoformat(),
            "location": loot_data.location or "",
            "loot_items": [item.dict() for item in loot_data.loot_items],
            "total_value": total_value,
            "notes": loot_data.notes or "",
            "ingested_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Check for duplicate session
        existing_sessions = self.loot_data[user_namespace]["loot_sessions"]
        for existing in existing_sessions:
            if existing["session_id"] == loot_data.session_id:
                # Update existing session
                existing.update(loot_session)
                logger.info(f"Updated existing loot session {loot_data.session_id} for user {discord_id}")
                break
        else:
            # Add new session
            existing_sessions.append(loot_session)
            self.loot_data[user_namespace]["stats"]["total_sessions"] += 1
            logger.info(f"Added new loot session {loot_data.session_id} for user {discord_id}")
        
        # Update user stats
        self._update_user_stats(user_namespace)
        
        # Update last_updated timestamp
        self.loot_data[user_namespace]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Save to file
        self._save_loot()
        
        return loot_session
    
    def _update_user_stats(self, user_namespace: str):
        """Update user statistics."""
        user_data = self.loot_data[user_namespace]
        sessions = user_data["loot_sessions"]
        
        if not sessions:
            return
        
        total_items = 0
        total_value = 0
        unique_items = set()
        
        for session in sessions:
            total_value += session.get("total_value", 0)
            for item in session.get("loot_items", []):
                total_items += item.get("quantity", 1)
                unique_items.add(item.get("item_name", ""))
        
        user_data["stats"].update({
            "total_items": total_items,
            "total_value": total_value,
            "unique_items": len(unique_items),
            "average_session_value": total_value / len(sessions) if sessions else 0
        })
    
    def get_user_loot_sessions(self, discord_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's loot session history."""
        user_namespace = self._get_user_namespace(discord_id)
        
        if user_namespace not in self.loot_data:
            return []
        
        sessions = self.loot_data[user_namespace]["loot_sessions"]
        # Sort by timestamp (newest first)
        sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return sessions[:limit]
    
    def get_user_loot_stats(self, discord_id: str) -> Dict[str, Any]:
        """Get user's loot statistics."""
        user_namespace = self._get_user_namespace(discord_id)
        
        if user_namespace not in self.loot_data:
            return {
                "total_sessions": 0,
                "total_items": 0,
                "total_value": 0,
                "unique_items": 0,
                "average_session_value": 0
            }
        
        return self.loot_data[user_namespace]["stats"]
    
    def get_user_item_history(self, discord_id: str, item_name: str = None) -> List[Dict[str, Any]]:
        """Get user's item history."""
        user_namespace = self._get_user_namespace(discord_id)
        
        if user_namespace not in self.loot_data:
            return []
        
        sessions = self.loot_data[user_namespace]["loot_sessions"]
        item_history = []
        
        for session in sessions:
            for item in session.get("loot_items", []):
                if item_name is None or item.get("item_name") == item_name:
                    item_history.append({
                        "session_id": session["session_id"],
                        "timestamp": session["timestamp"],
                        "location": session["location"],
                        "item_name": item.get("item_name"),
                        "quantity": item.get("quantity", 1),
                        "rarity": item.get("rarity"),
                        "value_credits": item.get("value_credits"),
                        "item_type": item.get("item_type")
                    })
        
        # Sort by timestamp (newest first)
        item_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return item_history

# Initialize handler
loot_handler = LootIngestHandler()

@router.post("/loot", response_model=LootIngestResponse)
async def ingest_loot(
    request: LootIngestRequest,
    authorization: str = Header(None),
    x_discord_id: str = Header(None)
):
    """
    Ingest loot data for authenticated user.
    
    Args:
        request: Loot data to ingest
        authorization: Bearer token for authentication
        x_discord_id: Discord ID header
    
    Returns:
        LootIngestResponse with ingestion status
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
        
        logger.info(f"Processing loot ingestion for Discord ID: {x_discord_id}")
        
        # Process loot data
        loot_session = loot_handler._process_loot_data(request.loot_data, x_discord_id)
        
        # Prepare response
        response = LootIngestResponse(
            success=True,
            session_id=request.loot_data.session_id,
            discord_id=x_discord_id,
            ingested_at=loot_session["ingested_at"],
            message="Loot data ingested successfully"
        )
        
        logger.info(f"Successfully ingested loot session {request.loot_data.session_id} for user {x_discord_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Loot ingestion error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/loot/{discord_id}", response_model=Dict[str, Any])
async def get_user_loot_sessions(
    discord_id: str,
    limit: int = 50,
    authorization: str = Header(None)
):
    """
    Get user's loot session history.
    
    Args:
        discord_id: Discord ID to retrieve loot sessions for
        limit: Maximum number of sessions to return
        authorization: Bearer token for authentication
    
    Returns:
        User's loot session history and statistics
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
        sessions = loot_handler.get_user_loot_sessions(discord_id, limit)
        stats = loot_handler.get_user_loot_stats(discord_id)
        
        return {
            "discord_id": discord_id,
            "loot_sessions": sessions,
            "stats": stats,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get loot sessions error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/loot/{discord_id}/items", response_model=Dict[str, Any])
async def get_user_item_history(
    discord_id: str,
    item_name: str = None,
    limit: int = 100,
    authorization: str = Header(None)
):
    """
    Get user's item history.
    
    Args:
        discord_id: Discord ID to retrieve item history for
        item_name: Optional item name filter
        limit: Maximum number of items to return
        authorization: Bearer token for authentication
    
    Returns:
        User's item history
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
        
        # Get item history
        item_history = loot_handler.get_user_item_history(discord_id, item_name)
        
        return {
            "discord_id": discord_id,
            "item_name": item_name,
            "item_history": item_history[:limit],
            "total_items": len(item_history),
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get item history error: {e}")
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
        "service": "loot_ingest"
    } 