#!/usr/bin/env python3
"""Quest Acquisition Module for Batch 043.

This module provides functionality to trigger smart quest acquisition logic
and log unmatched NPCs for future training.
"""

import logging
import json
import time
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from .npc_matcher import NPCMatchResult, QuestMatch


@dataclass
class QuestAcquisitionRequest:
    """Represents a quest acquisition request."""
    npc_name: str
    quest_id: str
    quest_name: str
    confidence: float
    coordinates: Tuple[int, int]
    timestamp: float
    acquisition_type: str  # 'automatic', 'manual', 'suggested'


@dataclass
class UnmatchedNPC:
    """Represents an unmatched NPC for future training."""
    name: str
    coordinates: Tuple[int, int]
    detected_time: float
    quest_icon_type: str
    confidence: float
    planet: Optional[str] = None
    zone: Optional[str] = None
    context: Optional[str] = None


class QuestAcquisition:
    """Handles quest acquisition logic and unmatched NPC logging."""
    
    def __init__(self):
        """Initialize the quest acquisition handler."""
        self.logger = logging.getLogger(__name__)
        
        # Data directories
        self.data_dir = Path("data")
        self.unmatched_dir = self.data_dir / "unmatched_npcs"
        self.unmatched_dir.mkdir(exist_ok=True)
        
        # Files
        self.unmatched_file = self.unmatched_dir / "unmatched_npcs.json"
        self.acquisition_log = self.unmatched_dir / "acquisition_log.json"
        
        # Load existing unmatched NPCs
        self.unmatched_npcs = self._load_unmatched_npcs()
        
        # Acquisition thresholds
        self.auto_threshold = 0.8
        self.suggest_threshold = 0.6
        self.log_threshold = 0.3
        
        # Acquisition statistics
        self.stats = {
            'total_requests': 0,
            'automatic_acquisitions': 0,
            'manual_acquisitions': 0,
            'suggested_acquisitions': 0,
            'failed_acquisitions': 0,
            'unmatched_logged': 0
        }
    
    def trigger_quest_acquisition(self, match_result: NPCMatchResult) -> Dict[str, Any]:
        """Trigger quest acquisition based on match result."""
        self.logger.info(f"Triggering quest acquisition for {match_result.npc_name}")
        
        if not match_result.best_match:
            # No matches found, log as unmatched
            self._log_unmatched_npc(match_result)
            return {
                'success': False,
                'reason': 'no_matches',
                'npc_name': match_result.npc_name
            }
        
        best_match = match_result.best_match
        
        # Determine acquisition type based on confidence
        if best_match.match_confidence >= self.auto_threshold:
            acquisition_type = 'automatic'
            success = self._perform_automatic_acquisition(best_match)
        elif best_match.match_confidence >= self.suggest_threshold:
            acquisition_type = 'suggested'
            success = self._perform_suggested_acquisition(best_match)
        else:
            acquisition_type = 'manual'
            success = self._perform_manual_acquisition(best_match)
        
        # Create acquisition request
        request = QuestAcquisitionRequest(
            npc_name=match_result.npc_name,
            quest_id=best_match.quest_id,
            quest_name=best_match.quest_name,
            confidence=best_match.match_confidence,
            coordinates=match_result.coordinates,
            timestamp=time.time(),
            acquisition_type=acquisition_type
        )
        
        # Log acquisition
        self._log_acquisition(request, success)
        
        # Update statistics
        self.stats['total_requests'] += 1
        if success:
            if acquisition_type == 'automatic':
                self.stats['automatic_acquisitions'] += 1
            elif acquisition_type == 'suggested':
                self.stats['suggested_acquisitions'] += 1
            else:
                self.stats['manual_acquisitions'] += 1
        else:
            self.stats['failed_acquisitions'] += 1
        
        return {
            'success': success,
            'acquisition_type': acquisition_type,
            'quest_id': best_match.quest_id,
            'quest_name': best_match.quest_name,
            'confidence': best_match.match_confidence,
            'npc_name': match_result.npc_name
        }
    
    def _perform_automatic_acquisition(self, quest_match: QuestMatch) -> bool:
        """Perform automatic quest acquisition."""
        self.logger.info(f"Performing automatic acquisition for {quest_match.quest_name}")
        
        try:
            # Here you would integrate with the game's quest system
            # For now, we'll simulate the acquisition process
            
            # Check prerequisites
            if not self._check_prerequisites(quest_match.quest_data):
                self.logger.warning(f"Prerequisites not met for {quest_match.quest_name}")
                return False
            
            # Check level requirement
            if not self._check_level_requirement(quest_match.quest_data):
                self.logger.warning(f"Level requirement not met for {quest_match.quest_name}")
                return False
            
            # Simulate quest acceptance
            self.logger.info(f"Automatically accepted quest: {quest_match.quest_name}")
            
            # Here you would trigger the actual quest acceptance in the game
            # self._accept_quest_in_game(quest_match.quest_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in automatic acquisition: {e}")
            return False
    
    def _perform_suggested_acquisition(self, quest_match: QuestMatch) -> bool:
        """Perform suggested quest acquisition."""
        self.logger.info(f"Suggesting quest acquisition for {quest_match.quest_name}")
        
        try:
            # Create suggestion for user
            suggestion = {
                'quest_id': quest_match.quest_id,
                'quest_name': quest_match.quest_name,
                'confidence': quest_match.match_confidence,
                'npc_name': quest_match.npc_name,
                'description': quest_match.quest_data.get('description', ''),
                'level_requirement': quest_match.quest_data.get('level_requirement', 0),
                'rewards': quest_match.quest_data.get('rewards', []),
                'objectives': quest_match.quest_data.get('objectives', [])
            }
            
            # Here you would display the suggestion to the user
            # self._display_quest_suggestion(suggestion)
            
            self.logger.info(f"Quest suggestion created: {quest_match.quest_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in suggested acquisition: {e}")
            return False
    
    def _perform_manual_acquisition(self, quest_match: QuestMatch) -> bool:
        """Perform manual quest acquisition."""
        self.logger.info(f"Manual acquisition required for {quest_match.quest_name}")
        
        try:
            # Create manual acquisition request
            manual_request = {
                'quest_id': quest_match.quest_id,
                'quest_name': quest_match.quest_name,
                'confidence': quest_match.match_confidence,
                'npc_name': quest_match.npc_name,
                'reason': 'low_confidence',
                'quest_data': quest_match.quest_data
            }
            
            # Here you would queue the manual acquisition
            # self._queue_manual_acquisition(manual_request)
            
            self.logger.info(f"Manual acquisition queued: {quest_match.quest_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in manual acquisition: {e}")
            return False
    
    def _check_prerequisites(self, quest_data: Dict[str, Any]) -> bool:
        """Check if quest prerequisites are met."""
        prerequisites = quest_data.get('prerequisites', [])
        
        if not prerequisites:
            return True
        
        # Here you would check actual prerequisites in the game
        # For now, we'll assume prerequisites are met
        self.logger.debug(f"Checking {len(prerequisites)} prerequisites")
        return True
    
    def _check_level_requirement(self, quest_data: Dict[str, Any]) -> bool:
        """Check if level requirement is met."""
        required_level = quest_data.get('level_requirement', 0)
        
        # Here you would check actual character level
        # For now, we'll assume level requirement is met
        character_level = 50  # Placeholder
        return character_level >= required_level
    
    def log_unmatched_npc(self, npc_detection, planet: Optional[str] = None, zone: Optional[str] = None) -> bool:
        """Log an unmatched NPC for future training."""
        self.logger.info(f"Logging unmatched NPC: {npc_detection.name}")
        
        try:
            unmatched_npc = UnmatchedNPC(
                name=npc_detection.name,
                coordinates=npc_detection.coordinates,
                detected_time=npc_detection.detected_time,
                quest_icon_type=npc_detection.quest_icon.icon_type,
                confidence=npc_detection.confidence,
                planet=planet,
                zone=zone,
                context=f"Detected at {datetime.now().isoformat()}"
            )
            
            # Add to unmatched list
            self.unmatched_npcs.append(asdict(unmatched_npc))
            
            # Save to file
            self._save_unmatched_npcs()
            
            self.stats['unmatched_logged'] += 1
            self.logger.info(f"Logged unmatched NPC: {npc_detection.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging unmatched NPC: {e}")
            return False
    
    def _log_unmatched_npc(self, match_result: NPCMatchResult):
        """Log unmatched NPC from match result."""
        # Create a mock NPC detection for logging
        class MockNPCDetection:
            def __init__(self, name, coordinates, detected_time, quest_icon):
                self.name = name
                self.coordinates = coordinates
                self.detected_time = detected_time
                self.quest_icon = quest_icon
                self.confidence = 0.5
        
        mock_detection = MockNPCDetection(
            name=match_result.npc_name,
            coordinates=match_result.coordinates,
            detected_time=match_result.detected_time,
            quest_icon=type('MockIcon', (), {'icon_type': 'quest'})()
        )
        
        self.log_unmatched_npc(mock_detection)
    
    def _log_acquisition(self, request: QuestAcquisitionRequest, success: bool):
        """Log quest acquisition attempt."""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'npc_name': request.npc_name,
                'quest_id': request.quest_id,
                'quest_name': request.quest_name,
                'confidence': request.confidence,
                'acquisition_type': request.acquisition_type,
                'success': success,
                'coordinates': request.coordinates
            }
            
            # Load existing log
            log_data = []
            if self.acquisition_log.exists():
                with open(self.acquisition_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            
            # Add new entry
            log_data.append(log_entry)
            
            # Save log
            with open(self.acquisition_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error logging acquisition: {e}")
    
    def _load_unmatched_npcs(self) -> List[Dict[str, Any]]:
        """Load unmatched NPCs from file."""
        if self.unmatched_file.exists():
            try:
                with open(self.unmatched_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading unmatched NPCs: {e}")
        
        return []
    
    def _save_unmatched_npcs(self):
        """Save unmatched NPCs to file."""
        try:
            with open(self.unmatched_file, 'w', encoding='utf-8') as f:
                json.dump(self.unmatched_npcs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving unmatched NPCs: {e}")
    
    def get_acquisition_stats(self) -> Dict[str, Any]:
        """Get acquisition statistics."""
        return {
            'stats': self.stats,
            'total_unmatched': len(self.unmatched_npcs),
            'recent_acquisitions': self._get_recent_acquisitions()
        }
    
    def _get_recent_acquisitions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent acquisition attempts."""
        if not self.acquisition_log.exists():
            return []
        
        try:
            with open(self.acquisition_log, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            # Return most recent entries
            return log_data[-limit:] if len(log_data) > limit else log_data
            
        except Exception as e:
            self.logger.error(f"Error loading recent acquisitions: {e}")
            return []


def trigger_quest_acquisition(match_result: NPCMatchResult) -> Dict[str, Any]:
    """Trigger quest acquisition based on match result."""
    acquisition = QuestAcquisition()
    return acquisition.trigger_quest_acquisition(match_result)


def log_unmatched_npc(npc_detection, planet: Optional[str] = None, zone: Optional[str] = None) -> bool:
    """Log an unmatched NPC for future training."""
    acquisition = QuestAcquisition()
    return acquisition.log_unmatched_npc(npc_detection, planet, zone) 