#!/usr/bin/env python3
"""NPC Matcher Module for Batch 043.

This module provides functionality to match detected NPC names with quests
in the local quest database.
"""

import logging
import json
import yaml
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from difflib import SequenceMatcher
from dataclasses import dataclass

from importers.wiki_quests import FallbackDetector, get_quest_info


@dataclass
class QuestMatch:
    """Represents a match between an NPC and a quest."""
    npc_name: str
    quest_id: str
    quest_name: str
    match_confidence: float
    match_type: str  # 'exact', 'fuzzy', 'partial'
    quest_data: Dict[str, Any]
    planet: Optional[str] = None
    quest_type: Optional[str] = None


@dataclass
class NPCMatchResult:
    """Represents the result of matching an NPC to quests."""
    npc_name: str
    coordinates: Tuple[int, int]
    detected_time: float
    matches: List[QuestMatch]
    total_matches: int
    best_match: Optional[QuestMatch] = None


class NPCMatcher:
    """Matches detected NPC names with quests in the local database."""
    
    def __init__(self):
        """Initialize the NPC matcher."""
        self.logger = logging.getLogger(__name__)
        
        # Load quest database
        self.quest_database = self._load_quest_database()
        self.quest_index = self._load_quest_index()
        
        # Initialize fallback detector
        self.fallback_detector = FallbackDetector()
        
        # Matching thresholds
        self.exact_threshold = 0.95
        self.fuzzy_threshold = 0.7
        self.partial_threshold = 0.5
        
        # NPC name variations and aliases
        self.npc_aliases = {
            'mos eisley merchant': ['merchant', 'trader', 'vendor'],
            'coronet security': ['security officer', 'guard', 'patrol'],
            'theed palace guard': ['palace guard', 'royal guard', 'guard'],
            'anchorhead mechanic': ['mechanic', 'repair', 'technician'],
            'bestine mayor': ['mayor', 'official', 'administrator'],
            'kadaara smuggler': ['smuggler', 'trader', 'merchant'],
            'tyrena cantina owner': ['cantina owner', 'bartender', 'innkeeper'],
            'dearic merchant': ['merchant', 'trader', 'vendor'],
            'kaadara trader': ['trader', 'merchant', 'vendor'],
            'talus mining coordinator': ['mining coordinator', 'miner', 'coordinator'],
            'rori pirate': ['pirate', 'smuggler', 'outlaw'],
            'lok mercenary': ['mercenary', 'fighter', 'soldier'],
            'dantooine farmer': ['farmer', 'agriculturalist', 'rancher'],
            'yavin4 rebel': ['rebel', 'freedom fighter', 'resistance'],
            'endor ewok': ['ewok', 'native', 'tribesman'],
            'dathomir witch': ['witch', 'force user', 'sorcerer'],
            'naboo royal': ['royal', 'noble', 'aristocrat'],
            'corellia engineer': ['engineer', 'technician', 'mechanic'],
            'tatooine moisture farmer': ['moisture farmer', 'farmer', 'agriculturalist'],
            'kashyyyk wookiee': ['wookiee', 'warrior', 'guardian']
        }
    
    def match_npc_to_quests(self, npc_detection) -> NPCMatchResult:
        """Match an NPC detection to quests in the database."""
        self.logger.info(f"Matching NPC: {npc_detection.name}")
        
        matches = []
        npc_name = npc_detection.name.lower().strip()
        
        # Try exact match first
        exact_matches = self._find_exact_matches(npc_name)
        matches.extend(exact_matches)
        
        # Try fuzzy match if no exact matches
        if not exact_matches:
            fuzzy_matches = self._find_fuzzy_matches(npc_name)
            matches.extend(fuzzy_matches)
        
        # Try partial match if still no matches
        if not matches:
            partial_matches = self._find_partial_matches(npc_name)
            matches.extend(partial_matches)
        
        # Try alias matching
        if not matches:
            alias_matches = self._find_alias_matches(npc_name)
            matches.extend(alias_matches)
        
        # Sort matches by confidence
        matches.sort(key=lambda x: x.match_confidence, reverse=True)
        
        # Get best match
        best_match = matches[0] if matches else None
        
        result = NPCMatchResult(
            npc_name=npc_detection.name,
            coordinates=npc_detection.coordinates,
            detected_time=npc_detection.detected_time,
            matches=matches,
            total_matches=len(matches),
            best_match=best_match
        )
        
        if matches:
            self.logger.info(f"Found {len(matches)} quest matches for {npc_detection.name}")
            for match in matches[:3]:  # Log top 3 matches
                self.logger.info(f"  - {match.quest_name} (confidence: {match.match_confidence:.2f})")
        else:
            self.logger.warning(f"No quest matches found for {npc_detection.name}")
        
        return result
    
    def _find_exact_matches(self, npc_name: str) -> List[QuestMatch]:
        """Find exact matches for NPC name."""
        matches = []
        
        # Search in quest database
        for quest_id, quest_data in self.quest_database.items():
            quest_npc = quest_data.get('npc', '').lower()
            if quest_npc == npc_name:
                match = QuestMatch(
                    npc_name=npc_name,
                    quest_id=quest_id,
                    quest_name=quest_data.get('name', ''),
                    match_confidence=1.0,
                    match_type='exact',
                    quest_data=quest_data,
                    planet=quest_data.get('planet'),
                    quest_type=quest_data.get('quest_type')
                )
                matches.append(match)
        
        return matches
    
    def _find_fuzzy_matches(self, npc_name: str) -> List[QuestMatch]:
        """Find fuzzy matches for NPC name."""
        matches = []
        
        for quest_id, quest_data in self.quest_database.items():
            quest_npc = quest_data.get('npc', '').lower()
            
            # Calculate similarity
            similarity = SequenceMatcher(None, npc_name, quest_npc).ratio()
            
            if similarity >= self.fuzzy_threshold:
                match = QuestMatch(
                    npc_name=npc_name,
                    quest_id=quest_id,
                    quest_name=quest_data.get('name', ''),
                    match_confidence=similarity,
                    match_type='fuzzy',
                    quest_data=quest_data,
                    planet=quest_data.get('planet'),
                    quest_type=quest_data.get('quest_type')
                )
                matches.append(match)
        
        return matches
    
    def _find_partial_matches(self, npc_name: str) -> List[QuestMatch]:
        """Find partial matches for NPC name."""
        matches = []
        
        for quest_id, quest_data in self.quest_database.items():
            quest_npc = quest_data.get('npc', '').lower()
            
            # Check if NPC name contains quest NPC or vice versa
            if npc_name in quest_npc or quest_npc in npc_name:
                # Calculate similarity for partial matches
                similarity = SequenceMatcher(None, npc_name, quest_npc).ratio()
                
                if similarity >= self.partial_threshold:
                    match = QuestMatch(
                        npc_name=npc_name,
                        quest_id=quest_id,
                        quest_name=quest_data.get('name', ''),
                        match_confidence=similarity,
                        match_type='partial',
                        quest_data=quest_data,
                        planet=quest_data.get('planet'),
                        quest_type=quest_data.get('quest_type')
                    )
                    matches.append(match)
        
        return matches
    
    def _find_alias_matches(self, npc_name: str) -> List[QuestMatch]:
        """Find matches using NPC aliases."""
        matches = []
        
        # Check if NPC name matches any aliases
        for base_name, aliases in self.npc_aliases.items():
            if npc_name in aliases or npc_name == base_name:
                # Search for quests with the base name
                for quest_id, quest_data in self.quest_database.items():
                    quest_npc = quest_data.get('npc', '').lower()
                    
                    if quest_npc == base_name or quest_npc in aliases:
                        similarity = SequenceMatcher(None, npc_name, quest_npc).ratio()
                        
                        match = QuestMatch(
                            npc_name=npc_name,
                            quest_id=quest_id,
                            quest_name=quest_data.get('name', ''),
                            match_confidence=similarity,
                            match_type='alias',
                            quest_data=quest_data,
                            planet=quest_data.get('planet'),
                            quest_type=quest_data.get('quest_type')
                        )
                        matches.append(match)
        
        return matches
    
    def get_available_quests(self, npc_name: str, planet: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available quests for an NPC, optionally filtered by planet."""
        self.logger.info(f"Getting available quests for {npc_name} on {planet or 'any planet'}")
        
        available_quests = []
        
        # Search in quest index by planet
        if planet:
            planet_quests = self.quest_index.get(planet.lower(), [])
            for quest_entry in planet_quests:
                quest_npc = quest_entry.get('npc', '').lower()
                
                # Check if NPC matches
                if self._is_npc_match(npc_name, quest_npc):
                    quest_id = quest_entry['quest_id']
                    quest_data = self.quest_database.get(quest_id, {})
                    
                    if quest_data:
                        available_quests.append({
                            'quest_id': quest_id,
                            'name': quest_data.get('name', ''),
                            'description': quest_data.get('description', ''),
                            'level_requirement': quest_data.get('level_requirement', 0),
                            'difficulty': quest_data.get('difficulty', 'medium'),
                            'quest_type': quest_data.get('quest_type', 'unknown'),
                            'rewards': quest_data.get('rewards', []),
                            'prerequisites': quest_data.get('prerequisites', []),
                            'objectives': quest_data.get('objectives', [])
                        })
        else:
            # Search all quests
            for quest_id, quest_data in self.quest_database.items():
                quest_npc = quest_data.get('npc', '').lower()
                
                if self._is_npc_match(npc_name, quest_npc):
                    available_quests.append({
                        'quest_id': quest_id,
                        'name': quest_data.get('name', ''),
                        'description': quest_data.get('description', ''),
                        'level_requirement': quest_data.get('level_requirement', 0),
                        'difficulty': quest_data.get('difficulty', 'medium'),
                        'quest_type': quest_data.get('quest_type', 'unknown'),
                        'rewards': quest_data.get('rewards', []),
                        'prerequisites': quest_data.get('prerequisites', []),
                        'objectives': quest_data.get('objectives', [])
                    })
        
        self.logger.info(f"Found {len(available_quests)} available quests for {npc_name}")
        return available_quests
    
    def _is_npc_match(self, detected_npc: str, quest_npc: str) -> bool:
        """Check if detected NPC matches quest NPC."""
        if detected_npc is None:
            detected_npc = ""
        detected_npc = detected_npc.lower()
        quest_npc = quest_npc.lower()
        
        # Exact match
        if detected_npc == quest_npc:
            return True
        
        # Fuzzy match
        similarity = SequenceMatcher(None, detected_npc, quest_npc).ratio()
        if similarity >= self.fuzzy_threshold:
            return True
        
        # Partial match
        if detected_npc in quest_npc or quest_npc in detected_npc:
            return True
        
        # Alias match
        for base_name, aliases in self.npc_aliases.items():
            if (detected_npc in aliases or detected_npc == base_name) and quest_npc == base_name:
                return True
        
        return False
    
    def _load_quest_database(self) -> Dict[str, Any]:
        """Load the quest database from file."""
        db_file = Path("data/quest_database.json")
        if db_file.exists():
            try:
                with open(db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading quest database: {e}")
        
        return {}
    
    def _load_quest_index(self) -> Dict[str, Any]:
        """Load the quest index from file."""
        index_file = Path("data/quest_index.yaml")
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                self.logger.error(f"Error loading quest index: {e}")
        
        return {}


def match_npc_to_quests(npc_detection) -> NPCMatchResult:
    """Match an NPC detection to quests in the database."""
    matcher = NPCMatcher()
    return matcher.match_npc_to_quests(npc_detection)


def get_available_quests(npc_name: str, planet: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get available quests for an NPC."""
    matcher = NPCMatcher()
    return matcher.get_available_quests(npc_name, planet) 