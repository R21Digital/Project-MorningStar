"""Lockout Tracker for Heroic Content.

This module provides functionality to track lockout timers for heroic instances,
managing per-character and per-instance cooldowns.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from android_ms11.utils.logging_utils import log_event


class LockoutTracker:
    """Tracks lockout timers for heroic instances per character and instance."""

    def __init__(self, data_dir: str = "data/heroics/lockouts"):
        """Initialize the lockout tracker.

        Parameters
        ----------
        data_dir : str
            Directory to store lockout data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.lockout_data = {}
        self.character_lockouts = {}
        self.instance_lockouts = {}
        
        # Load existing lockout data
        self._load_lockout_data()

    def record_heroic_completion(self, character_name: str, heroic_id: str,
                                 difficulty: str = "normal") -> bool:
        """Record a heroic completion and set lockout timer.

        Parameters
        ----------
        character_name : str
            Name of the character who completed the heroic
        heroic_id : str
            ID of the heroic instance
        difficulty : str, optional
            Difficulty tier (normal/hard), defaults to "normal"

        Returns
        -------
        bool
            True if completion recorded successfully
        """
        try:
            timestamp = time.time()
            
            # Create lockout entry
            lockout_entry = {
                "character_name": character_name,
                "heroic_id": heroic_id,
                "difficulty": difficulty,
                "completion_time": timestamp,
                "lockout_until": self._calculate_lockout_end(heroic_id, difficulty, timestamp)
            }
            
            # Store in memory
            lockout_key = f"{character_name}_{heroic_id}_{difficulty}"
            self.lockout_data[lockout_key] = lockout_entry
            
            # Update character and instance tracking
            if character_name not in self.character_lockouts:
                self.character_lockouts[character_name] = {}
            
            if heroic_id not in self.instance_lockouts:
                self.instance_lockouts[heroic_id] = {}
            
            self.character_lockouts[character_name][f"{heroic_id}_{difficulty}"] = lockout_entry
            self.instance_lockouts[heroic_id][f"{character_name}_{difficulty}"] = lockout_entry
            
            # Save to disk
            self._save_lockout_data()
            
            log_event(f"[LOCKOUT_TRACKER] Recorded completion: {character_name} - {heroic_id} ({difficulty})")
            return True
            
        except Exception as e:
            log_event(f"[LOCKOUT_TRACKER] Error recording completion: {e}")
            return False

    def check_lockout_status(self, character_name: str, heroic_id: str,
                             difficulty: str = "normal") -> Dict[str, Any]:
        """Check if a character is locked out of a heroic instance.

        Parameters
        ----------
        character_name : str
            Name of the character to check
        heroic_id : str
            ID of the heroic instance
        difficulty : str, optional
            Difficulty tier (normal/hard), defaults to "normal"

        Returns
        -------
        dict
            Lockout status information
        """
        try:
            lockout_key = f"{character_name}_{heroic_id}_{difficulty}"
            current_time = time.time()
            
            if lockout_key not in self.lockout_data:
                return {
                    "locked_out": False,
                    "time_remaining": 0,
                    "reset_time": None,
                    "can_enter": True
                }
            
            lockout_entry = self.lockout_data[lockout_key]
            lockout_until = lockout_entry["lockout_until"]
            
            if current_time < lockout_until:
                time_remaining = lockout_until - current_time
                return {
                    "locked_out": True,
                    "time_remaining": time_remaining,
                    "reset_time": datetime.fromtimestamp(lockout_until).isoformat(),
                    "can_enter": False,
                    "completion_time": datetime.fromtimestamp(lockout_entry["completion_time"]).isoformat()
                }
            else:
                return {
                    "locked_out": False,
                    "time_remaining": 0,
                    "reset_time": None,
                    "can_enter": True
                }
                
        except Exception as e:
            log_event(f"[LOCKOUT_TRACKER] Error checking lockout status: {e}")
            return {
                "locked_out": False,
                "time_remaining": 0,
                "reset_time": None,
                "can_enter": True,
                "error": str(e)
            }

    def get_character_lockouts(self, character_name: str) -> Dict[str, Any]:
        """Get all lockouts for a specific character.

        Parameters
        ----------
        character_name : str
            Name of the character

        Returns
        -------
        dict
            All lockout information for the character
        """
        try:
            if character_name not in self.character_lockouts:
                return {
                    "character_name": character_name,
                    "active_lockouts": [],
                    "available_heroics": []
                }
            
            current_time = time.time()
            active_lockouts = []
            available_heroics = []
            
            for lockout_key, lockout_entry in self.character_lockouts[character_name].items():
                if current_time < lockout_entry["lockout_until"]:
                    active_lockouts.append({
                        "heroic_id": lockout_entry["heroic_id"],
                        "difficulty": lockout_entry["difficulty"],
                        "time_remaining": lockout_entry["lockout_until"] - current_time,
                        "reset_time": datetime.fromtimestamp(lockout_entry["lockout_until"]).isoformat()
                    })
                else:
                    available_heroics.append({
                        "heroic_id": lockout_entry["heroic_id"],
                        "difficulty": lockout_entry["difficulty"]
                    })
            
            return {
                "character_name": character_name,
                "active_lockouts": active_lockouts,
                "available_heroics": available_heroics,
                "total_lockouts": len(active_lockouts)
            }
            
        except Exception as e:
            log_event(f"[LOCKOUT_TRACKER] Error getting character lockouts: {e}")
            return {
                "character_name": character_name,
                "active_lockouts": [],
                "available_heroics": [],
                "error": str(e)
            }

    def get_instance_lockouts(self, heroic_id: str) -> Dict[str, Any]:
        """Get all lockouts for a specific heroic instance.

        Parameters
        ----------
        heroic_id : str
            ID of the heroic instance

        Returns
        -------
        dict
            All lockout information for the instance
        """
        try:
            if heroic_id not in self.instance_lockouts:
                return {
                    "heroic_id": heroic_id,
                    "active_lockouts": [],
                    "available_characters": []
                }
            
            current_time = time.time()
            active_lockouts = []
            available_characters = []
            
            for lockout_key, lockout_entry in self.instance_lockouts[heroic_id].items():
                if current_time < lockout_entry["lockout_until"]:
                    active_lockouts.append({
                        "character_name": lockout_entry["character_name"],
                        "difficulty": lockout_entry["difficulty"],
                        "time_remaining": lockout_entry["lockout_until"] - current_time,
                        "reset_time": datetime.fromtimestamp(lockout_entry["lockout_until"]).isoformat()
                    })
                else:
                    available_characters.append({
                        "character_name": lockout_entry["character_name"],
                        "difficulty": lockout_entry["difficulty"]
                    })
            
            return {
                "heroic_id": heroic_id,
                "active_lockouts": active_lockouts,
                "available_characters": available_characters,
                "total_lockouts": len(active_lockouts)
            }
            
        except Exception as e:
            log_event(f"[LOCKOUT_TRACKER] Error getting instance lockouts: {e}")
            return {
                "heroic_id": heroic_id,
                "active_lockouts": [],
                "available_characters": [],
                "error": str(e)
            }

    def clear_expired_lockouts(self) -> int:
        """Clear expired lockout entries and return count of cleared entries.

        Returns
        -------
        int
            Number of expired lockouts cleared
        """
        try:
            current_time = time.time()
            expired_keys = []
            
            for lockout_key, lockout_entry in self.lockout_data.items():
                if current_time >= lockout_entry["lockout_until"]:
                    expired_keys.append(lockout_key)
            
            # Remove expired entries
            for key in expired_keys:
                del self.lockout_data[key]
                
                # Also remove from character and instance tracking
                character_name = key.split("_")[0]
                heroic_id = key.split("_")[1]
                difficulty = key.split("_")[2]
                
                if character_name in self.character_lockouts:
                    char_key = f"{heroic_id}_{difficulty}"
                    if char_key in self.character_lockouts[character_name]:
                        del self.character_lockouts[character_name][char_key]
                
                if heroic_id in self.instance_lockouts:
                    inst_key = f"{character_name}_{difficulty}"
                    if inst_key in self.instance_lockouts[heroic_id]:
                        del self.instance_lockouts[heroic_id][inst_key]
            
            # Save updated data
            if expired_keys:
                self._save_lockout_data()
                log_event(f"[LOCKOUT_TRACKER] Cleared {len(expired_keys)} expired lockouts")
            
            return len(expired_keys)
            
        except Exception as e:
            log_event(f"[LOCKOUT_TRACKER] Error clearing expired lockouts: {e}")
            return 0

    def export_lockout_data(self, filepath: str = None) -> str:
        """Export lockout data to a JSON file.

        Parameters
        ----------
        filepath : str, optional
            Path to save the export file

        Returns
        -------
        str
            Path to the exported file
        """
        try:
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = self.data_dir / f"lockout_export_{timestamp}.json"
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "lockout_data": self.lockout_data,
                "character_lockouts": self.character_lockouts,
                "instance_lockouts": self.instance_lockouts
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            log_event(f"[LOCKOUT_TRACKER] Exported lockout data to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            log_event(f"[LOCKOUT_TRACKER] Error exporting lockout data: {e}")
            return ""

    def _calculate_lockout_end(self, heroic_id: str, difficulty: str, completion_time: float) -> float:
        """Calculate when the lockout ends based on heroic and difficulty.

        Parameters
        ----------
        heroic_id : str
            ID of the heroic instance
        difficulty : str
            Difficulty tier
        completion_time : float
            Timestamp of completion

        Returns
        -------
        float
            Timestamp when lockout ends
        """
        # Default lockout times (in seconds)
        default_lockouts = {
            "normal": 86400,  # 24 hours
            "hard": 604800    # 7 days
        }
        
        lockout_duration = default_lockouts.get(difficulty, default_lockouts["normal"])
        return completion_time + lockout_duration

    def _load_lockout_data(self) -> None:
        """Load lockout data from disk."""
        try:
            data_file = self.data_dir / "lockout_data.json"
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.lockout_data = data.get("lockout_data", {})
                    self.character_lockouts = data.get("character_lockouts", {})
                    self.instance_lockouts = data.get("instance_lockouts", {})
                    
                log_event(f"[LOCKOUT_TRACKER] Loaded {len(self.lockout_data)} lockout entries")
            else:
                log_event("[LOCKOUT_TRACKER] No existing lockout data found")
                
        except Exception as e:
            log_event(f"[LOCKOUT_TRACKER] Error loading lockout data: {e}")

    def _save_lockout_data(self) -> None:
        """Save lockout data to disk."""
        try:
            data_file = self.data_dir / "lockout_data.json"
            data = {
                "last_updated": datetime.now().isoformat(),
                "lockout_data": self.lockout_data,
                "character_lockouts": self.character_lockouts,
                "instance_lockouts": self.instance_lockouts
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            log_event(f"[LOCKOUT_TRACKER] Error saving lockout data: {e}")


def create_lockout_tracker(data_dir: str = "data/heroics/lockouts") -> LockoutTracker:
    """Create a new lockout tracker instance.

    Parameters
    ----------
    data_dir : str
        Directory to store lockout data

    Returns
    -------
    LockoutTracker
        New lockout tracker instance
    """
    return LockoutTracker(data_dir) 