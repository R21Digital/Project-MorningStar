#!/usr/bin/env python3
"""
Session Upload Bridge to SWGDB

This module handles uploading sanitized bot session data to the user's SWGDB dashboard.
It serializes logs, sanitizes sensitive data, and pushes to SWGDB API with authentication.
"""

import json
import os
import time
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import asdict, dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.log_serializer import SessionLogSerializer
from swgdb_api.push_session_data import SWGDBAPIClient


@dataclass
class UploadConfig:
    """Configuration for session uploads."""
    swgdb_api_url: str
    api_key: str
    user_hash: str
    upload_interval_minutes: int = 5
    max_retries: int = 3
    retry_delay_seconds: int = 30
    sanitize_data: bool = True
    include_events: bool = True
    include_locations: bool = True
    include_communications: bool = False  # Sensitive data
    include_player_encounters: bool = False  # Privacy concern


@dataclass
class UploadedSession:
    """Represents an uploaded session."""
    session_id: str
    upload_timestamp: str
    swgdb_session_id: Optional[str] = None
    upload_status: str = "pending"
    error_message: Optional[str] = None
    retry_count: int = 0


class SessionUploader:
    """Handles uploading session data to SWGDB."""
    
    def __init__(self, config: UploadConfig):
        self.config = config
        self.serializer = SessionLogSerializer()
        self.swgdb_client = SWGDBAPIClient(
            api_url=config.swgdb_api_url,
            api_key=config.api_key,
            user_hash=config.user_hash
        )
        self.uploaded_sessions: List[UploadedSession] = []
        self.upload_history_file = Path("data/upload_history.json")
        self._load_upload_history()
    
    def _load_upload_history(self) -> None:
        """Load upload history from file."""
        if self.upload_history_file.exists():
            try:
                with open(self.upload_history_file, 'r') as f:
                    data = json.load(f)
                    self.uploaded_sessions = [
                        UploadedSession(**session_data) 
                        for session_data in data.get("sessions", [])
                    ]
            except Exception as e:
                print(f"Error loading upload history: {e}")
                self.uploaded_sessions = []
    
    def _save_upload_history(self) -> None:
        """Save upload history to file."""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "sessions": [asdict(session) for session in self.uploaded_sessions]
            }
            self.upload_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.upload_history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving upload history: {e}")
    
    def find_session_logs(self) -> List[Path]:
        """Find all session log files that need uploading."""
        session_dirs = [
            Path("logs/sessions"),
            Path("data/session_logs"),
            Path("session_logs")
        ]
        
        session_files = []
        for session_dir in session_dirs:
            if session_dir.exists():
                # Find JSON session files
                json_files = list(session_dir.glob("session_*.json"))
                json_files.extend(session_dir.glob("*.json"))
                
                for file_path in json_files:
                    # Check if already uploaded
                    if not self._is_session_uploaded(file_path):
                        session_files.append(file_path)
        
        return session_files
    
    def _is_session_uploaded(self, file_path: Path) -> bool:
        """Check if a session file has already been uploaded."""
        session_id = self._extract_session_id(file_path)
        return any(s.session_id == session_id for s in self.uploaded_sessions)
    
    def _extract_session_id(self, file_path: Path) -> str:
        """Extract session ID from filename."""
        filename = file_path.stem
        if filename.startswith("session_"):
            return filename
        return filename
    
    def load_session_data(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and validate session data from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required fields
            required_fields = ["session_id", "start_time", "end_time"]
            if not all(field in data for field in required_fields):
                print(f"Missing required fields in {file_path}")
                return None
            
            return data
        except Exception as e:
            print(f"Error loading session data from {file_path}: {e}")
            return None
    
    def sanitize_session_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize session data for upload."""
        if not self.config.sanitize_data:
            return data
        
        sanitized = data.copy()
        
        # Remove sensitive data
        if not self.config.include_communications:
            sanitized.pop("communication_events", None)
            sanitized.pop("guild_alerts", None)
        
        if not self.config.include_player_encounters:
            sanitized.pop("player_encounters", None)
        
        if not self.config.include_locations:
            sanitized.pop("locations_visited", None)
        
        # Sanitize action logs (remove sensitive info)
        if "actions" in sanitized:
            sanitized["actions"] = self._sanitize_actions(sanitized["actions"])
        
        # Add sanitization metadata
        sanitized["_sanitized"] = True
        sanitized["_sanitization_timestamp"] = datetime.now().isoformat()
        sanitized["_original_data_keys"] = list(data.keys())
        
        return sanitized
    
    def _sanitize_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sanitize action logs to remove sensitive information."""
        sanitized_actions = []
        
        sensitive_patterns = [
            "whisper", "tell", "guild", "password", "token", "key",
            "private", "secret", "confidential"
        ]
        
        for action in actions:
            sanitized_action = action.copy()
            
            # Check if action contains sensitive information
            action_text = str(action.get("action", "")).lower()
            if any(pattern in action_text for pattern in sensitive_patterns):
                sanitized_action["action"] = "[SENSITIVE_ACTION_REMOVED]"
                sanitized_action["_sanitized"] = True
            
            sanitized_actions.append(sanitized_action)
        
        return sanitized_actions
    
    def prepare_session_for_upload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare session data for SWGDB upload."""
        # Serialize the data using the log serializer
        serialized_data = self.serializer.serialize_session(data)
        
        # Add upload metadata
        serialized_data.update({
            "upload_metadata": {
                "upload_timestamp": datetime.now().isoformat(),
                "uploader_version": "1.0.0",
                "data_source": "ms11_bot",
                "sanitized": self.config.sanitize_data,
                "include_events": self.config.include_events,
                "include_locations": self.config.include_locations
            }
        })
        
        return serialized_data
    
    def upload_session(self, file_path: Path) -> Optional[UploadedSession]:
        """Upload a single session to SWGDB."""
        session_id = self._extract_session_id(file_path)
        
        # Load session data
        data = self.load_session_data(file_path)
        if not data:
            return None
        
        # Create upload session record
        uploaded_session = UploadedSession(
            session_id=session_id,
            upload_timestamp=datetime.now().isoformat()
        )
        
        try:
            # Sanitize data
            sanitized_data = self.sanitize_session_data(data)
            
            # Prepare for upload
            upload_data = self.prepare_session_for_upload(sanitized_data)
            
            # Upload to SWGDB
            response = self.swgdb_client.push_session_data(upload_data)
            
            if response.get("success"):
                uploaded_session.upload_status = "success"
                uploaded_session.swgdb_session_id = response.get("swgdb_session_id")
                print(f"✅ Successfully uploaded session {session_id}")
            else:
                uploaded_session.upload_status = "failed"
                uploaded_session.error_message = response.get("error", "Unknown error")
                print(f"❌ Failed to upload session {session_id}: {uploaded_session.error_message}")
            
        except Exception as e:
            uploaded_session.upload_status = "error"
            uploaded_session.error_message = str(e)
            print(f"❌ Error uploading session {session_id}: {e}")
        
        # Add to upload history
        self.uploaded_sessions.append(uploaded_session)
        self._save_upload_history()
        
        return uploaded_session
    
    def upload_all_sessions(self) -> Dict[str, Any]:
        """Upload all pending sessions to SWGDB."""
        session_files = self.find_session_logs()
        
        if not session_files:
            return {
                "total_sessions": 0,
                "uploaded": 0,
                "failed": 0,
                "message": "No new sessions to upload"
            }
        
        print(f"Found {len(session_files)} sessions to upload")
        
        results = {
            "total_sessions": len(session_files),
            "uploaded": 0,
            "failed": 0,
            "sessions": []
        }
        
        for file_path in session_files:
            print(f"Uploading {file_path.name}...")
            
            uploaded_session = self.upload_session(file_path)
            if uploaded_session:
                results["sessions"].append(asdict(uploaded_session))
                
                if uploaded_session.upload_status == "success":
                    results["uploaded"] += 1
                else:
                    results["failed"] += 1
        
        print(f"Upload complete: {results['uploaded']} successful, {results['failed']} failed")
        return results
    
    def retry_failed_uploads(self) -> Dict[str, Any]:
        """Retry failed uploads."""
        failed_sessions = [
            s for s in self.uploaded_sessions 
            if s.upload_status in ["failed", "error"] and s.retry_count < self.config.max_retries
        ]
        
        if not failed_sessions:
            return {
                "total_retries": 0,
                "successful": 0,
                "still_failed": 0
            }
        
        print(f"Retrying {len(failed_sessions)} failed uploads...")
        
        results = {
            "total_retries": len(failed_sessions),
            "successful": 0,
            "still_failed": 0
        }
        
        for session in failed_sessions:
            session.retry_count += 1
            
            # Find the original file
            session_files = self.find_session_logs()
            file_path = next(
                (f for f in session_files if self._extract_session_id(f) == session.session_id),
                None
            )
            
            if file_path:
                print(f"Retrying upload for session {session.session_id} (attempt {session.retry_count})")
                
                uploaded_session = self.upload_session(file_path)
                if uploaded_session and uploaded_session.upload_status == "success":
                    results["successful"] += 1
                else:
                    results["still_failed"] += 1
            else:
                print(f"Could not find file for session {session.session_id}")
                results["still_failed"] += 1
        
        self._save_upload_history()
        return results
    
    def get_upload_statistics(self) -> Dict[str, Any]:
        """Get upload statistics."""
        total_sessions = len(self.uploaded_sessions)
        successful = len([s for s in self.uploaded_sessions if s.upload_status == "success"])
        failed = len([s for s in self.uploaded_sessions if s.upload_status in ["failed", "error"]])
        pending = len([s for s in self.uploaded_sessions if s.upload_status == "pending"])
        
        return {
            "total_sessions": total_sessions,
            "successful": successful,
            "failed": failed,
            "pending": pending,
            "success_rate": (successful / total_sessions * 100) if total_sessions > 0 else 0,
            "last_upload": max([s.upload_timestamp for s in self.uploaded_sessions]) if self.uploaded_sessions else None
        }
    
    def cleanup_old_sessions(self, days_to_keep: int = 30) -> int:
        """Clean up old session files and upload records."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Remove old upload records
        original_count = len(self.uploaded_sessions)
        self.uploaded_sessions = [
            s for s in self.uploaded_sessions
            if datetime.fromisoformat(s.upload_timestamp) > cutoff_date
        ]
        
        removed_count = original_count - len(self.uploaded_sessions)
        if removed_count > 0:
            self._save_upload_history()
            print(f"Removed {removed_count} old upload records")
        
        return removed_count


def create_upload_config() -> UploadConfig:
    """Create upload configuration from environment or defaults."""
    return UploadConfig(
        swgdb_api_url=os.getenv("SWGDB_API_URL", "https://api.swgdb.com/v1"),
        api_key=os.getenv("SWGDB_API_KEY", ""),
        user_hash=os.getenv("SWGDB_USER_HASH", ""),
        upload_interval_minutes=int(os.getenv("UPLOAD_INTERVAL_MINUTES", "5")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        retry_delay_seconds=int(os.getenv("RETRY_DELAY_SECONDS", "30")),
        sanitize_data=os.getenv("SANITIZE_DATA", "true").lower() == "true",
        include_events=os.getenv("INCLUDE_EVENTS", "true").lower() == "true",
        include_locations=os.getenv("INCLUDE_LOCATIONS", "true").lower() == "true",
        include_communications=os.getenv("INCLUDE_COMMUNICATIONS", "false").lower() == "true",
        include_player_encounters=os.getenv("INCLUDE_PLAYER_ENCOUNTERS", "false").lower() == "true"
    )


def main():
    """Main function for testing the session uploader."""
    config = create_upload_config()
    
    if not config.api_key or not config.user_hash:
        print("❌ Missing SWGDB API credentials")
        print("Please set SWGDB_API_KEY and SWGDB_USER_HASH environment variables")
        return
    
    uploader = SessionUploader(config)
    
    # Upload all pending sessions
    results = uploader.upload_all_sessions()
    print(f"Upload results: {results}")
    
    # Show statistics
    stats = uploader.get_upload_statistics()
    print(f"Upload statistics: {stats}")


if __name__ == '__main__':
    main() 