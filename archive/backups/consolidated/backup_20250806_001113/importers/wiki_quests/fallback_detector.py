#!/usr/bin/env python3
"""Fallback Detector Module for Batch 042.

This module provides fallback detection logic to determine if a quest is in the imported
database and retrieve quest information for the MS11 system.
"""

import json
import logging
import yaml
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from difflib import SequenceMatcher

from .wiki_parser import QuestData, QuestType, QuestDifficulty


class FallbackDetector:
    """Detects quests in the imported database and provides fallback information."""
    
    def __init__(self):
        """Initialize the fallback detector."""
        self.logger = logging.getLogger(__name__)
        
        # Data directories
        self.data_dir = Path("data")
        self.quests_dir = self.data_dir / "quests"
        
        # Database files
        self.quest_db_file = self.data_dir / "quest_database.json"
        self.quest_index_file = self.data_dir / "quest_index.yaml"
        
        # Load databases
        self.quest_database = self._load_quest_database()
        self.quest_index = self._load_quest_index()
        
        # Search patterns for quest detection
        self.quest_patterns = {
            'quest_id': r'quest[_-]?id[:\s]*([^\n\r]+)',
            'quest_name': r'name[:\s]*([^\n\r]+)',
            'npc_name': r'npc[:\s]*([^\n\r]+)',
            'planet_name': r'planet[:\s]*([^\n\r]+)',
            'coordinates': r'coordinates[:\s]*\[?(\d+)[,\s]+(\d+)\]?'
        }
        
        # Similarity threshold for fuzzy matching
        self.similarity_threshold = 0.8

    def detect_quest_in_database(self, quest_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect if a quest exists in the imported database."""
        try:
            # Try exact match first
            exact_match = self._find_exact_match(quest_info)
            if exact_match:
                return exact_match
            
            # Try fuzzy match
            fuzzy_match = self._find_fuzzy_match(quest_info)
            if fuzzy_match:
                return fuzzy_match
            
            # Try partial match
            partial_match = self._find_partial_match(quest_info)
            if partial_match:
                return partial_match
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting quest in database: {e}")
            return None

    def _find_exact_match(self, quest_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find exact match for quest in database."""
        quest_id = quest_info.get('quest_id', '').lower()
        quest_name = quest_info.get('name', '').lower()
        npc_name = quest_info.get('npc', '').lower()
        planet = quest_info.get('planet', '').lower()
        
        # Check by quest ID
        if quest_id and quest_id in self.quest_database:
            return self._get_quest_info(quest_id)
        
        # Check by exact name match
        for quest_id, quest_data in self.quest_database.items():
            if quest_data.get('name', '').lower() == quest_name:
                return self._get_quest_info(quest_id)
        
        # Check by NPC and planet combination
        if npc_name and planet:
            for quest_id, quest_data in self.quest_database.items():
                if (quest_data.get('npc', '').lower() == npc_name and 
                    quest_data.get('planet', '').lower() == planet):
                    return self._get_quest_info(quest_id)
        
        return None

    def _find_fuzzy_match(self, quest_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find fuzzy match for quest in database."""
        quest_name = quest_info.get('name', '').lower()
        npc_name = quest_info.get('npc', '').lower()
        
        best_match = None
        best_similarity = 0
        
        for quest_id, quest_data in self.quest_database.items():
            db_name = quest_data.get('name', '').lower()
            db_npc = quest_data.get('npc', '').lower()
            
            # Calculate name similarity
            name_similarity = SequenceMatcher(None, quest_name, db_name).ratio()
            
            # Calculate NPC similarity
            npc_similarity = 0
            if npc_name and db_npc:
                npc_similarity = SequenceMatcher(None, npc_name, db_npc).ratio()
            
            # Use the higher similarity score
            similarity = max(name_similarity, npc_similarity)
            
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = quest_id
        
        if best_match:
            return self._get_quest_info(best_match)
        
        return None

    def _find_partial_match(self, quest_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find partial match for quest in database."""
        quest_name = quest_info.get('name', '').lower()
        npc_name = quest_info.get('npc', '').lower()
        planet = quest_info.get('planet', '').lower()
        
        # Extract key words from quest name
        name_words = set(re.findall(r'\w+', quest_name))
        
        best_match = None
        best_score = 0
        
        for quest_id, quest_data in self.quest_database.items():
            db_name = quest_data.get('name', '').lower()
            db_npc = quest_data.get('npc', '').lower()
            db_planet = quest_data.get('planet', '').lower()
            
            score = 0
            
            # Check word overlap in names
            db_name_words = set(re.findall(r'\w+', db_name))
            word_overlap = len(name_words.intersection(db_name_words))
            if word_overlap > 0:
                score += word_overlap * 2
            
            # Check NPC match
            if npc_name and db_npc and npc_name in db_npc:
                score += 3
            
            # Check planet match
            if planet and db_planet and planet == db_planet:
                score += 2
            
            if score > best_score and score >= 2:  # Minimum score threshold
                best_score = score
                best_match = quest_id
        
        if best_match:
            return self._get_quest_info(best_match)
        
        return None

    def _get_quest_info(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed quest information from database."""
        if quest_id not in self.quest_database:
            return None
        
        quest_data = self.quest_database[quest_id]
        file_path = quest_data.get('file_path', '')
        
        # Load detailed quest data from file
        detailed_data = self._load_quest_file(file_path)
        
        if detailed_data:
            return {
                'quest_id': quest_id,
                'database_info': quest_data,
                'detailed_data': detailed_data,
                'match_confidence': 'exact'
            }
        
        return {
            'quest_id': quest_id,
            'database_info': quest_data,
            'detailed_data': None,
            'match_confidence': 'partial'
        }

    def _load_quest_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load detailed quest data from YAML file."""
        try:
            quest_file = Path(file_path)
            if quest_file.exists():
                with open(quest_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading quest file {file_path}: {e}")
        
        return None

    def get_quest_info(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get quest information by ID."""
        return self._get_quest_info(quest_id)

    def search_quests(self, search_term: str, search_type: str = 'name') -> List[Dict[str, Any]]:
        """Search for quests in the database."""
        results = []
        search_term_lower = search_term.lower()
        
        for quest_id, quest_data in self.quest_database.items():
            match_found = False
            
            if search_type == 'name':
                if search_term_lower in quest_data.get('name', '').lower():
                    match_found = True
            elif search_type == 'npc':
                if search_term_lower in quest_data.get('npc', '').lower():
                    match_found = True
            elif search_type == 'planet':
                if search_term_lower in quest_data.get('planet', '').lower():
                    match_found = True
            elif search_type == 'type':
                if search_term_lower in quest_data.get('quest_type', '').lower():
                    match_found = True
            elif search_type == 'all':
                # Search in all fields
                for field, value in quest_data.items():
                    if isinstance(value, str) and search_term_lower in value.lower():
                        match_found = True
                        break
            
            if match_found:
                results.append({
                    'quest_id': quest_id,
                    'database_info': quest_data,
                    'detailed_data': self._load_quest_file(quest_data.get('file_path', ''))
                })
        
        return results

    def get_quests_by_planet(self, planet: str) -> List[Dict[str, Any]]:
        """Get all quests for a specific planet."""
        planet_lower = planet.lower()
        results = []
        
        for quest_id, quest_data in self.quest_database.items():
            if quest_data.get('planet', '').lower() == planet_lower:
                results.append({
                    'quest_id': quest_id,
                    'database_info': quest_data,
                    'detailed_data': self._load_quest_file(quest_data.get('file_path', ''))
                })
        
        return results

    def get_quests_by_type(self, quest_type: str) -> List[Dict[str, Any]]:
        """Get all quests of a specific type."""
        quest_type_lower = quest_type.lower()
        results = []
        
        for quest_id, quest_data in self.quest_database.items():
            if quest_data.get('quest_type', '').lower() == quest_type_lower:
                results.append({
                    'quest_id': quest_id,
                    'database_info': quest_data,
                    'detailed_data': self._load_quest_file(quest_data.get('file_path', ''))
                })
        
        return results

    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the quest database."""
        total_quests = len(self.quest_database)
        
        # Count by planet
        planet_counts = {}
        for quest_data in self.quest_database.values():
            planet = quest_data.get('planet', 'unknown')
            planet_counts[planet] = planet_counts.get(planet, 0) + 1
        
        # Count by type
        type_counts = {}
        for quest_data in self.quest_database.values():
            quest_type = quest_data.get('quest_type', 'unknown')
            type_counts[quest_type] = type_counts.get(quest_type, 0) + 1
        
        # Count by difficulty
        difficulty_counts = {}
        for quest_data in self.quest_database.values():
            difficulty = quest_data.get('difficulty', 'unknown')
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        return {
            'total_quests': total_quests,
            'quests_by_planet': planet_counts,
            'quests_by_type': type_counts,
            'quests_by_difficulty': difficulty_counts
        }

    def is_quest_available(self, quest_info: Dict[str, Any]) -> bool:
        """Check if a quest is available in the database."""
        return self.detect_quest_in_database(quest_info) is not None

    def get_fallback_quest_data(self, quest_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get fallback quest data if exact match is not found."""
        # Try to find any related quests
        quest_name = quest_info.get('name', '')
        npc_name = quest_info.get('npc', '')
        planet = quest_info.get('planet', '')
        
        related_quests = []
        
        # Search for quests with similar names
        if quest_name:
            name_results = self.search_quests(quest_name, 'name')
            related_quests.extend(name_results)
        
        # Search for quests with same NPC
        if npc_name:
            npc_results = self.search_quests(npc_name, 'npc')
            related_quests.extend(npc_results)
        
        # Search for quests on same planet
        if planet:
            planet_results = self.get_quests_by_planet(planet)
            related_quests.extend(planet_results)
        
        # Remove duplicates
        unique_quests = {}
        for quest in related_quests:
            quest_id = quest['quest_id']
            if quest_id not in unique_quests:
                unique_quests[quest_id] = quest
        
        if unique_quests:
            # Return the most relevant quest (first one found)
            return list(unique_quests.values())[0]
        
        return None

    def _load_quest_database(self) -> Dict[str, Any]:
        """Load the quest database from file."""
        if self.quest_db_file.exists():
            try:
                with open(self.quest_db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading quest database: {e}")
        
        return {}

    def _load_quest_index(self) -> Dict[str, Any]:
        """Load the quest index from file."""
        if self.quest_index_file.exists():
            try:
                with open(self.quest_index_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                self.logger.error(f"Error loading quest index: {e}")
        
        return {}


def detect_quest_in_database(quest_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Detect if a quest exists in the imported database."""
    detector = FallbackDetector()
    return detector.detect_quest_in_database(quest_info)


def get_quest_info(quest_id: str) -> Optional[Dict[str, Any]]:
    """Get quest information by ID."""
    detector = FallbackDetector()
    return detector.get_quest_info(quest_id) 