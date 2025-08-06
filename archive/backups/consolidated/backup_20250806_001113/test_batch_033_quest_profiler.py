#!/usr/bin/env python3
"""
Unit tests for Batch 033 - Quest Knowledge Builder & Smart Profile Learning

Tests the quest profiler functionality including:
- Quest database initialization
- OCR text processing
- Quest information extraction
- YAML file generation
- Statistics calculation
"""

import pytest
import sys
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from quest_profiler import QuestProfiler, QuestMetadata, QuestObjective, QuestStep
from datetime import datetime


class TestQuestProfiler:
    """Test cases for the QuestProfiler class."""
    
    @pytest.fixture
    def profiler(self):
        """Create a QuestProfiler instance for testing."""
        with patch('quest_profiler.LegacyQuestManager') as mock_manager:
            mock_manager.return_value.list_all_quests.return_value = []
            profiler = QuestProfiler()
            return profiler
    
    @pytest.fixture
    def mock_quest_data(self):
        """Sample quest data for testing."""
        return {
            "id": "test_quest_1",
            "title": "Test Quest",
            "npc": "Test NPC",
            "location": "Test Location",
            "planet": "tatooine",
            "reward": "1000 credits",
            "difficulty": "easy",
            "level": 5
        }
    
    def test_quest_profiler_initialization(self, profiler):
        """Test QuestProfiler initialization."""
        assert profiler is not None
        assert hasattr(profiler, 'quest_database')
        assert hasattr(profiler, 'discovered_quests')
        assert hasattr(profiler, 'config')
        assert profiler.ocr_interval == 2.0
        assert "quest" in profiler.quest_detection_keywords
    
    def test_load_config_default(self, profiler):
        """Test default configuration loading."""
        config = profiler.config
        assert config['ocr_interval'] == 2.0
        assert 'quest' in config['quest_detection_keywords']
        assert 'https://swgr.org/wiki/' in config['wiki_sources']
        assert config['gpt_enabled'] is True
    
    def test_detect_quest_keywords(self, profiler):
        """Test quest keyword detection."""
        # Test positive cases
        assert profiler.detect_quest_keywords("This is a quest for you")
        assert profiler.detect_quest_keywords("Mission: Find the artifact")
        assert profiler.detect_quest_keywords("Task: Deliver the package")
        
        # Test negative cases
        assert not profiler.detect_quest_keywords("This is just some text")
        assert not profiler.detect_quest_keywords("No keywords here")
    
    def test_extract_quest_info(self, profiler):
        """Test quest information extraction from OCR text."""
        # Test successful extraction
        ocr_text = "Quest: Tatooine Artifact Hunt\nFrom: Mos Eisley Merchant\nLocation: Tatooine Desert\nReward: 1000 credits"
        quest_info = profiler.extract_quest_info(ocr_text)
        
        assert quest_info is not None
        assert quest_info['name'] == "Tatooine Artifact Hunt"
        assert quest_info['giver'] == "Mos Eisley Merchant"
        assert quest_info['location'] == "Tatooine Desert"
        assert quest_info['reward'] == "1000 credits"
        
        # Test failed extraction
        ocr_text = "Just some random text without quest information"
        quest_info = profiler.extract_quest_info(ocr_text)
        assert quest_info is None
    
    def test_extract_planet_from_location(self, profiler):
        """Test planet extraction from location strings."""
        # Test known planets
        assert profiler.extract_planet_from_location("Tatooine Desert") == "tatooine"
        assert profiler.extract_planet_from_location("Naboo Palace") == "naboo"
        assert profiler.extract_planet_from_location("Corellia City") == "corellia"
        
        # Test unknown location
        assert profiler.extract_planet_from_location("Unknown Location") == "unknown"
    
    def test_process_discovered_quest(self, profiler):
        """Test processing of discovered quests."""
        quest_info = {
            "name": "Unique Test Quest 12345",
            "giver": "Test NPC",
            "location": "Tatooine Desert",
            "reward": "500 credits"
        }
        
        initial_count = len(profiler.quest_database)
        profiler.process_discovered_quest(quest_info)
        
        # Check that quest was added
        assert len(profiler.quest_database) == initial_count + 1
        assert len(profiler.discovered_quests) == 1
        
        # Check quest metadata
        quest = profiler.discovered_quests[0]
        assert quest.name == "Unique Test Quest 12345"
        assert quest.giver == "Test NPC"
        assert quest.planet == "tatooine"
        assert quest.quest_type == "discovered"
        assert quest.source == "ocr"
    
    def test_duplicate_quest_handling(self, profiler):
        """Test that duplicate quests are not added."""
        quest_info = {
            "name": "Duplicate Quest",
            "giver": "Test NPC",
            "location": "Tatooine Desert",
            "reward": "500 credits"
        }
        
        # Add quest first time
        profiler.process_discovered_quest(quest_info)
        initial_count = len(profiler.quest_database)
        
        # Try to add same quest again
        profiler.process_discovered_quest(quest_info)
        
        # Count should not increase
        assert len(profiler.quest_database) == initial_count
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open')
    def test_generate_quest_yaml(self, mock_open, mock_mkdir, profiler):
        """Test YAML quest file generation."""
        metadata = QuestMetadata(
            quest_id="test_quest",
            name="Test Quest",
            giver="Test NPC",
            location="Test Location",
            planet="tatooine",
            coordinates=(100, 200),
            reward="500 credits",
            quest_type="discovered",
            difficulty="medium",
            level_requirement=5,
            discovered_time=datetime.now(),
            source="ocr"
        )
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        profiler.generate_quest_yaml(metadata)
        
        # Check that directory was created
        mock_mkdir.assert_called_with(exist_ok=True)
        
        # Check that file was opened for writing
        mock_open.assert_called()
    
    def test_get_quest_statistics(self, profiler):
        """Test quest statistics calculation."""
        # Add some test quests
        quest_info = {
            "name": "Unique Test Quest 1 67890",
            "giver": "Test NPC 1",
            "location": "Tatooine Desert",
            "reward": "500 credits"
        }
        profiler.process_discovered_quest(quest_info)
        
        quest_info2 = {
            "name": "Unique Test Quest 2 67890",
            "giver": "Test NPC 2",
            "location": "Naboo Palace",
            "reward": "1000 credits"
        }
        profiler.process_discovered_quest(quest_info2)
        
        stats = profiler.get_quest_statistics()
        
        assert stats['total_quests'] >= 2
        assert stats['discovered_quests'] == 2
        assert stats['ocr_discovered'] == 2
        assert 'tatooine' in stats['quests_by_planet']
        assert 'naboo' in stats['quests_by_planet']
        assert 'discovered' in stats['quests_by_type']
    
    def test_get_quests_by_planet(self, profiler):
        """Test planet-specific quest filtering."""
        # Add quests on different planets
        quests = [
            {"name": "Tatooine Quest", "giver": "NPC1", "location": "Tatooine Desert", "reward": "500"},
            {"name": "Naboo Quest", "giver": "NPC2", "location": "Naboo Palace", "reward": "1000"},
            {"name": "Corellia Quest", "giver": "NPC3", "location": "Corellia City", "reward": "750"}
        ]
        
        for quest_info in quests:
            profiler.process_discovered_quest(quest_info)
        
        planet_counts = profiler.get_quests_by_planet()
        
        assert planet_counts['tatooine'] >= 1
        assert planet_counts['naboo'] >= 1
        assert planet_counts['corellia'] >= 1
    
    def test_get_quests_by_type(self, profiler):
        """Test quest type filtering."""
        # Add quests of different types
        quests = [
            {"name": "Legacy Quest", "giver": "NPC1", "location": "Tatooine", "reward": "500"},
            {"name": "Theme Park Quest", "giver": "NPC2", "location": "Naboo", "reward": "1000"}
        ]
        
        for quest_info in quests:
            profiler.process_discovered_quest(quest_info)
        
        type_counts = profiler.get_quests_by_type()
        
        assert type_counts['discovered'] >= 2
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open')
    def test_save_quest_database(self, mock_open, mock_mkdir, profiler):
        """Test quest database saving."""
        # Add a test quest
        quest_info = {
            "name": "Test Quest",
            "giver": "Test NPC",
            "location": "Tatooine Desert",
            "reward": "500 credits"
        }
        profiler.process_discovered_quest(quest_info)
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        profiler.save_quest_database()
        
        # Check that directory was created
        mock_mkdir.assert_called_with(exist_ok=True)
        
        # Check that file was opened for writing
        mock_open.assert_called()
    
    def test_scrape_wiki_quests(self, profiler):
        """Test wiki quest scraping (placeholder)."""
        # This is a placeholder test since the actual implementation is not complete
        result = profiler.scrape_wiki_quests("https://example.com")
        assert isinstance(result, list)
    
    def test_infer_with_gpt(self, profiler):
        """Test GPT inference (placeholder)."""
        # This is a placeholder test since the actual implementation is not complete
        unclear_text = "Some unclear OCR text"
        result = profiler.infer_with_gpt(unclear_text)
        assert isinstance(result, str)
        assert result == unclear_text  # Placeholder returns original text


class TestQuestMetadata:
    """Test cases for the QuestMetadata dataclass."""
    
    def test_quest_metadata_creation(self):
        """Test QuestMetadata dataclass creation."""
        metadata = QuestMetadata(
            quest_id="test_quest",
            name="Test Quest",
            giver="Test NPC",
            location="Test Location",
            planet="tatooine",
            coordinates=(100, 200),
            reward="500 credits",
            quest_type="discovered",
            difficulty="medium",
            level_requirement=5,
            discovered_time=datetime.now(),
            source="ocr"
        )
        
        assert metadata.quest_id == "test_quest"
        assert metadata.name == "Test Quest"
        assert metadata.giver == "Test NPC"
        assert metadata.planet == "tatooine"
        assert metadata.coordinates == (100, 200)
        assert metadata.quest_type == "discovered"
        assert metadata.source == "ocr"


class TestQuestObjective:
    """Test cases for the QuestObjective dataclass."""
    
    def test_quest_objective_creation(self):
        """Test QuestObjective dataclass creation."""
        objective = QuestObjective(
            objective_id="collect_artifact",
            description="Collect the ancient artifact",
            objective_type="collect",
            target="ancient_artifact",
            coordinates=(100, 200),
            count=1,
            completed=False
        )
        
        assert objective.objective_id == "collect_artifact"
        assert objective.description == "Collect the ancient artifact"
        assert objective.objective_type == "collect"
        assert objective.target == "ancient_artifact"
        assert objective.coordinates == (100, 200)
        assert objective.count == 1
        assert objective.completed is False


class TestQuestStep:
    """Test cases for the QuestStep dataclass."""
    
    def test_quest_step_creation(self):
        """Test QuestStep dataclass creation."""
        step = QuestStep(
            step_id="talk_to_npc",
            step_type="dialogue",
            description="Talk to the quest giver",
            npc_id="quest_giver",
            coordinates=(100, 200),
            requirements={"level": 5},
            completed=False
        )
        
        assert step.step_id == "talk_to_npc"
        assert step.step_type == "dialogue"
        assert step.description == "Talk to the quest giver"
        assert step.npc_id == "quest_giver"
        assert step.coordinates == (100, 200)
        assert step.requirements == {"level": 5}
        assert step.completed is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 