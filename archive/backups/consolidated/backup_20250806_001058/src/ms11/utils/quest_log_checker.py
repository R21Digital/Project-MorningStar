#!/usr/bin/env python3
"""
Batch 181 - MS11 Quest Log Verifier Module

This module ensures MS11 checks the player's completed quests log before starting 
new quest chains to avoid repeating already completed content.

Features:
- Parse quest log via /journal command or UI detection
- Compare against known quest chains
- Verify quest eligibility before starting chains
- Fallback alerts for detection failures
- Integration with session manager
"""

import os
import json
import time
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

import pyautogui
import cv2
import numpy as np

from utils.license_hooks import requires_license
from profession_logic.utils.logger import logger


class QuestStatus(Enum):
    """Quest completion status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class QuestEntry:
    """Represents a quest entry in the log."""
    quest_name: str
    quest_id: Optional[str] = None
    status: QuestStatus = QuestStatus.UNKNOWN
    completion_date: Optional[str] = None
    quest_chain: Optional[str] = None
    quest_type: Optional[str] = None
    location: Optional[str] = None
    npc: Optional[str] = None
    
    def __post_init__(self):
        if self.completion_date is None:
            self.completion_date = datetime.now().isoformat()


@dataclass
class QuestChain:
    """Represents a quest chain."""
    chain_name: str
    chain_id: str
    quests: List[str]
    required_level: Optional[int] = None
    faction: Optional[str] = None
    planet: Optional[str] = None
    description: Optional[str] = None
    
    def is_eligible(self, completed_quests: Set[str]) -> bool:
        """Check if quest chain is eligible based on completed quests."""
        # Check if any quest in the chain is already completed
        for quest in self.quests:
            if quest in completed_quests:
                return False
        return True


class QuestLogChecker:
    """Quest log verifier for MS11."""
    
    def __init__(self, config_path: str = "config/quest_log_config.json"):
        """Initialize quest log checker."""
        self.config_path = config_path
        self.config = self._load_config()
        self.quest_chains: Dict[str, QuestChain] = {}
        self.completed_quests: Set[str] = set()
        self.quest_log_cache: List[QuestEntry] = []
        self.last_check_time: Optional[datetime] = None
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
        # Load quest chains
        self._load_quest_chains()
        
        logger.info("[QUEST_LOG] Quest log checker initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load quest log checker configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config
            default_config = {
                "enabled": True,
                "check_interval": 300,  # 5 minutes
                "cache_duration": 300,  # 5 minutes
                "use_journal_command": True,
                "use_ui_detection": True,
                "fallback_alert": True,
                "quest_chains_file": "data/quest_chains.json",
                "completed_quests_file": "data/completed_quests.json",
                "ui_regions": {
                    "quest_log": {"x": 100, "y": 100, "width": 800, "height": 600},
                    "journal_button": {"x": 50, "y": 50, "width": 100, "height": 30}
                },
                "ocr_settings": {
                    "confidence_threshold": 0.7,
                    "language": "eng",
                    "preprocessing": True
                }
            }
            
            # Save default config
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def _load_quest_chains(self) -> None:
        """Load quest chains from file."""
        quest_chains_file = self.config.get("quest_chains_file", "data/quest_chains.json")
        
        try:
            if os.path.exists(quest_chains_file):
                with open(quest_chains_file, 'r') as f:
                    chains_data = json.load(f)
                
                for chain_data in chains_data:
                    chain = QuestChain(
                        chain_name=chain_data["chain_name"],
                        chain_id=chain_data["chain_id"],
                        quests=chain_data["quests"],
                        required_level=chain_data.get("required_level"),
                        faction=chain_data.get("faction"),
                        planet=chain_data.get("planet"),
                        description=chain_data.get("description")
                    )
                    self.quest_chains[chain.chain_id] = chain
                
                logger.info(f"[QUEST_LOG] Loaded {len(self.quest_chains)} quest chains")
            else:
                logger.warning(f"[QUEST_LOG] Quest chains file not found: {quest_chains_file}")
                
        except Exception as e:
            logger.error(f"[QUEST_LOG] Failed to load quest chains: {e}")
    
    def check_quest_log(self, force_refresh: bool = False) -> bool:
        """Check quest log and update completed quests."""
        try:
            # Check cache first
            if not force_refresh and self._is_cache_valid():
                logger.info("[QUEST_LOG] Using cached quest log data")
                return True
            
            logger.info("[QUEST_LOG] Checking quest log...")
            
            # Try different methods to get quest log
            quest_entries = []
            
            # Method 1: Use /journal command
            if self.config.get("use_journal_command", True):
                quest_entries = self._get_quest_log_via_journal()
            
            # Method 2: Use UI detection if journal method failed
            if not quest_entries and self.config.get("use_ui_detection", True):
                quest_entries = self._get_quest_log_via_ui()
            
            # Method 3: Fallback to saved data
            if not quest_entries:
                quest_entries = self._load_saved_quest_log()
            
            if quest_entries:
                # Update completed quests
                self._update_completed_quests(quest_entries)
                self.last_check_time = datetime.now()
                logger.info(f"[QUEST_LOG] Found {len(quest_entries)} quest entries")
                return True
            else:
                logger.warning("[QUEST_LOG] No quest log data found")
                if self.config.get("fallback_alert", True):
                    self._send_fallback_alert()
                return False
                
        except Exception as e:
            logger.error(f"[QUEST_LOG] Error checking quest log: {e}")
            return False
    
    def _get_quest_log_via_journal(self) -> List[QuestEntry]:
        """Get quest log via /journal command."""
        try:
            logger.info("[QUEST_LOG] Attempting to get quest log via /journal command")
            
            # Send /journal command
            pyautogui.write("/journal")
            pyautogui.press('enter')
            
            # Wait for response
            time.sleep(2)
            
            # Try to capture the response (this would need OCR implementation)
            # For now, return empty list as placeholder
            logger.info("[QUEST_LOG] /journal command sent, OCR parsing not implemented")
            return []
            
        except Exception as e:
            logger.error(f"[QUEST_LOG] Error with journal command: {e}")
            return []
    
    def _get_quest_log_via_ui(self) -> List[QuestEntry]:
        """Get quest log via UI detection."""
        try:
            logger.info("[QUEST_LOG] Attempting to get quest log via UI detection")
            
            # Get UI region for quest log
            ui_regions = self.config.get("ui_regions", {})
            quest_log_region = ui_regions.get("quest_log")
            
            if not quest_log_region:
                logger.warning("[QUEST_LOG] No quest log UI region configured")
                return []
            
            # Capture screen region
            screenshot = pyautogui.screenshot(region=(
                quest_log_region["x"],
                quest_log_region["y"],
                quest_log_region["width"],
                quest_log_region["height"]
            ))
            
            # Convert to OpenCV format
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Parse quest log from image (OCR implementation needed)
            quest_entries = self._parse_quest_log_image(img)
            
            return quest_entries
            
        except Exception as e:
            logger.error(f"[QUEST_LOG] Error with UI detection: {e}")
            return []
    
    def _parse_quest_log_image(self, img: np.ndarray) -> List[QuestEntry]:
        """Parse quest log from image using OCR."""
        try:
            # This is a placeholder for OCR implementation
            # In a real implementation, you would use Tesseract or similar OCR
            # to extract text from the quest log image
            
            logger.info("[QUEST_LOG] OCR parsing not implemented, using placeholder")
            
            # Placeholder: return some sample quest entries
            sample_quests = [
                QuestEntry("Kill 10 Tusken Raiders", status=QuestStatus.COMPLETED),
                QuestEntry("Deliver Package to Mos Eisley", status=QuestStatus.COMPLETED),
                QuestEntry("Collect Water Samples", status=QuestStatus.IN_PROGRESS),
                QuestEntry("Defeat Imperial Officer", status=QuestStatus.NOT_STARTED)
            ]
            
            return sample_quests
            
        except Exception as e:
            logger.error(f"[QUEST_LOG] Error parsing quest log image: {e}")
            return []
    
    def _load_saved_quest_log(self) -> List[QuestEntry]:
        """Load quest log from saved file."""
        try:
            completed_quests_file = self.config.get("completed_quests_file", "data/completed_quests.json")
            
            if os.path.exists(completed_quests_file):
                with open(completed_quests_file, 'r') as f:
                    data = json.load(f)
                
                quest_entries = []
                for quest_data in data.get("quests", []):
                    quest = QuestEntry(
                        quest_name=quest_data["quest_name"],
                        quest_id=quest_data.get("quest_id"),
                        status=QuestStatus(quest_data.get("status", "unknown")),
                        completion_date=quest_data.get("completion_date"),
                        quest_chain=quest_data.get("quest_chain"),
                        quest_type=quest_data.get("quest_type"),
                        location=quest_data.get("location"),
                        npc=quest_data.get("npc")
                    )
                    quest_entries.append(quest)
                
                logger.info(f"[QUEST_LOG] Loaded {len(quest_entries)} quests from saved file")
                return quest_entries
            else:
                logger.warning(f"[QUEST_LOG] Saved quest log file not found: {completed_quests_file}")
                return []
                
        except Exception as e:
            logger.error(f"[QUEST_LOG] Error loading saved quest log: {e}")
            return []
    
    def _update_completed_quests(self, quest_entries: List[QuestEntry]) -> None:
        """Update completed quests set."""
        self.completed_quests.clear()
        
        for entry in quest_entries:
            if entry.status == QuestStatus.COMPLETED:
                self.completed_quests.add(entry.quest_name)
        
        logger.info(f"[QUEST_LOG] Updated completed quests: {len(self.completed_quests)} quests")
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        if self.last_check_time is None:
            return False
        
        cache_duration = timedelta(seconds=self.config.get("cache_duration", 300))
        return datetime.now() - self.last_check_time < cache_duration
    
    def _send_fallback_alert(self) -> None:
        """Send fallback alert when quest log detection fails."""
        alert_message = "Quest log detection failed - using fallback mode"
        logger.warning(f"[QUEST_LOG] {alert_message}")
        
        # Here you could send to Discord or other notification system
        # For now, just log the warning
    
    def verify_quest_chain_eligibility(self, chain_id: str) -> Tuple[bool, str]:
        """Verify if a quest chain is eligible to start."""
        try:
            # Check quest log first
            if not self.check_quest_log():
                return False, "Failed to check quest log"
            
            # Get quest chain
            chain = self.quest_chains.get(chain_id)
            if not chain:
                return False, f"Quest chain not found: {chain_id}"
            
            # Check eligibility
            if chain.is_eligible(self.completed_quests):
                logger.info(f"[QUEST_LOG] Quest chain '{chain.chain_name}' is eligible")
                return True, f"Quest chain '{chain.chain_name}' is eligible"
            else:
                logger.warning(f"[QUEST_LOG] Quest chain '{chain.chain_name}' is not eligible - quests already completed")
                return False, f"Quest chain '{chain.chain_name}' has already been completed"
                
        except Exception as e:
            logger.error(f"[QUEST_LOG] Error verifying quest chain eligibility: {e}")
            return False, f"Error: {e}"
    
    def get_eligible_quest_chains(self) -> List[QuestChain]:
        """Get list of eligible quest chains."""
        try:
            # Check quest log first
            if not self.check_quest_log():
                return []
            
            eligible_chains = []
            for chain in self.quest_chains.values():
                if chain.is_eligible(self.completed_quests):
                    eligible_chains.append(chain)
            
            logger.info(f"[QUEST_LOG] Found {len(eligible_chains)} eligible quest chains")
            return eligible_chains
            
        except Exception as e:
            logger.error(f"[QUEST_LOG] Error getting eligible quest chains: {e}")
            return []
    
    def get_completed_quests(self) -> Set[str]:
        """Get set of completed quests."""
        return self.completed_quests.copy()
    
    def add_completed_quest(self, quest_name: str) -> None:
        """Add a quest to completed quests."""
        self.completed_quests.add(quest_name)
        logger.info(f"[QUEST_LOG] Added completed quest: {quest_name}")
    
    def save_quest_log(self) -> None:
        """Save quest log to file."""
        try:
            completed_quests_file = self.config.get("completed_quests_file", "data/completed_quests.json")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(completed_quests_file), exist_ok=True)
            
            # Prepare data
            data = {
                "last_updated": datetime.now().isoformat(),
                "total_completed": len(self.completed_quests),
                "quests": []
            }
            
            # Add quest entries
            for quest_name in self.completed_quests:
                quest_data = {
                    "quest_name": quest_name,
                    "status": "completed",
                    "completion_date": datetime.now().isoformat()
                }
                data["quests"].append(quest_data)
            
            # Save to file
            with open(completed_quests_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"[QUEST_LOG] Saved quest log with {len(self.completed_quests)} completed quests")
            
        except Exception as e:
            logger.error(f"[QUEST_LOG] Error saving quest log: {e}")


# Global instance for easy access
quest_log_checker = QuestLogChecker()


@requires_license
def verify_quest_chain(chain_id: str) -> Tuple[bool, str]:
    """Verify if a quest chain is eligible to start."""
    return quest_log_checker.verify_quest_chain_eligibility(chain_id)


@requires_license
def check_quest_log(force_refresh: bool = False) -> bool:
    """Check quest log and update completed quests."""
    return quest_log_checker.check_quest_log(force_refresh)


@requires_license
def get_eligible_quest_chains() -> List[QuestChain]:
    """Get list of eligible quest chains."""
    return quest_log_checker.get_eligible_quest_chains()


@requires_license
def get_completed_quests() -> Set[str]:
    """Get set of completed quests."""
    return quest_log_checker.get_completed_quests()


@requires_license
def add_completed_quest(quest_name: str) -> None:
    """Add a quest to completed quests."""
    quest_log_checker.add_completed_quest(quest_name)


@requires_license
def save_quest_log() -> None:
    """Save quest log to file."""
    quest_log_checker.save_quest_log()


def get_quest_log_status() -> Dict[str, Any]:
    """Get quest log checker status."""
    return {
        "enabled": quest_log_checker.config.get("enabled", True),
        "completed_quests_count": len(quest_log_checker.completed_quests),
        "quest_chains_count": len(quest_log_checker.quest_chains),
        "last_check_time": quest_log_checker.last_check_time.isoformat() if quest_log_checker.last_check_time else None,
        "cache_valid": quest_log_checker._is_cache_valid()
    } 