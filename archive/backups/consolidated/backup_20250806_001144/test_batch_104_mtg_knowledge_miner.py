"""Test suite for Batch 104 - MTG Repo Knowledge Miner."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from core.mtg_knowledge_miner import (
    MTGKnowledgeMiner,
    KnowledgeEntry,
    KnowledgeType,
    SourceType,
    mtg_knowledge_miner
)
from core.mtg_knowledge_integration import (
    MTGKnowledgeIntegration,
    KnowledgeIntegration,
    IntegrationType,
    IntegrationStatus,
    mtg_knowledge_integration
)


class TestKnowledgeEntry:
    """Test the KnowledgeEntry dataclass."""
    
    def test_knowledge_entry_creation(self):
        """Test creating a KnowledgeEntry."""
        entry = KnowledgeEntry(
            id="test123",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://github.com/test",
            title="Test Quest",
            content="Test content",
            metadata={"test": "data"},
            extracted_at=datetime.now(),
            confidence_score=0.8,
            tags=["test", "quest"]
        )
        
        assert entry.id == "test123"
        assert entry.knowledge_type == KnowledgeType.QUEST_LOGIC
        assert entry.source_type == SourceType.GITHUB_REPO
        assert entry.confidence_score == 0.8
        assert "test" in entry.tags
    
    def test_knowledge_entry_serialization(self):
        """Test KnowledgeEntry serialization to/from dict."""
        original_entry = KnowledgeEntry(
            id="test123",
            knowledge_type=KnowledgeType.CRAFTING_STATS,
            source_type=SourceType.FORUM_POST,
            source_url="https://forum.test",
            title="Test Crafting",
            content="Crafting content",
            metadata={"craft": "data"},
            extracted_at=datetime.now(),
            confidence_score=0.9,
            tags=["crafting", "stats"]
        )
        
        # Convert to dict
        entry_dict = original_entry.to_dict()
        
        # Convert back from dict
        restored_entry = KnowledgeEntry.from_dict(entry_dict)
        
        assert restored_entry.id == original_entry.id
        assert restored_entry.knowledge_type == original_entry.knowledge_type
        assert restored_entry.source_type == original_entry.source_type
        assert restored_entry.title == original_entry.title
        assert restored_entry.content == original_entry.content
        assert restored_entry.confidence_score == original_entry.confidence_score
        assert restored_entry.tags == original_entry.tags


class TestMTGKnowledgeMiner:
    """Test the MTGKnowledgeMiner class."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def miner(self, temp_data_dir):
        """Create a MTGKnowledgeMiner instance for testing."""
        return MTGKnowledgeMiner(data_dir=temp_data_dir)
    
    def test_miner_initialization(self, miner):
        """Test miner initialization."""
        assert miner.data_dir.exists()
        assert len(miner.knowledge_entries) == 7  # All knowledge types
        assert miner.session_stats['total_extracted'] == 0
    
    def test_generate_entry_id(self, miner):
        """Test entry ID generation."""
        id1 = miner._generate_entry_id("https://test1.com", "Title1")
        id2 = miner._generate_entry_id("https://test2.com", "Title2")
        id3 = miner._generate_entry_id("https://test1.com", "Title1")
        
        assert id1 != id2
        assert id1 == id3  # Same source and title should generate same ID
        assert len(id1) == 12  # MD5 hash truncated to 12 chars
    
    def test_classify_file_knowledge_type(self, miner):
        """Test file knowledge type classification."""
        # Quest logic patterns
        assert miner._classify_file_knowledge_type("quest_file.txt", "quests/quest_logic.py") == KnowledgeType.QUEST_LOGIC
        assert miner._classify_file_knowledge_type("mission.py", "src/missions/") == KnowledgeType.QUEST_LOGIC
        
        # Crafting patterns
        assert miner._classify_file_knowledge_type("crafting.py", "crafting/recipes/") == KnowledgeType.CRAFTING_STATS
        assert miner._classify_file_knowledge_type("manufacture.txt", "data/manufacture/") == KnowledgeType.CRAFTING_STATS
        
        # Combat patterns
        assert miner._classify_file_knowledge_type("combat.py", "combat/weapons/") == KnowledgeType.COMBAT_DATA
        assert miner._classify_file_knowledge_type("armor.txt", "data/armor/") == KnowledgeType.COMBAT_DATA
        
        # Unknown patterns
        assert miner._classify_file_knowledge_type("unknown.txt", "random/path/") is None
    
    def test_extract_quest_logic(self, miner):
        """Test quest logic extraction."""
        content = "Quest ID 12345, Mission Type: Escort, Reward: 500 credits, Prerequisite: Level 10"
        result = miner._extract_quest_logic(content, "quest_file.txt")
        
        assert result['method'] == 'quest_logic_extraction'
        assert result['confidence'] == 0.9  # Pattern matched
        assert 'pattern_matched' in result['tags']
        assert len(result['content']) <= 2000  # Content limited
    
    def test_extract_crafting_stats(self, miner):
        """Test crafting stats extraction."""
        content = "Craft Level 5, Recipe: Advanced Armor, Resource: Durasteel, Quality: 85"
        result = miner._extract_crafting_stats(content, "crafting.txt")
        
        assert result['method'] == 'crafting_stats_extraction'
        assert result['confidence'] == 0.9  # Pattern matched
        assert 'pattern_matched' in result['tags']
    
    def test_extract_combat_data(self, miner):
        """Test combat data extraction."""
        content = "Damage: 150, Weapon: Rifle, Armor: Composite, Attack: Ranged"
        result = miner._extract_combat_data(content, "combat.txt")
        
        assert result['method'] == 'combat_data_extraction'
        assert result['confidence'] == 0.9  # Pattern matched
        assert 'pattern_matched' in result['tags']
    
    @patch('requests.get')
    def test_crawl_github_repos(self, mock_get, miner):
        """Test GitHub repository crawling."""
        # Mock GitHub API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'type': 'file',
                'name': 'quest_logic.py',
                'path': 'quests/quest_logic.py',
                'html_url': 'https://github.com/test/quest_logic.py',
                'download_url': 'https://raw.githubusercontent.com/test/quest_logic.py',
                'size': 1024,
                'sha': 'abc123'
            }
        ]
        mock_get.return_value = mock_response
        
        # Mock file content response
        mock_content_response = Mock()
        mock_content_response.status_code = 200
        mock_content_response.text = "Quest ID 12345, Mission Type: Escort"
        mock_get.side_effect = [mock_response, mock_content_response]
        
        entries = miner.crawl_github_repos()
        
        assert len(entries) > 0
        assert entries[0].knowledge_type == KnowledgeType.QUEST_LOGIC
        assert entries[0].source_type == SourceType.GITHUB_REPO
    
    def test_crawl_forum_posts(self, miner):
        """Test forum posts crawling."""
        entries = miner.crawl_forum_posts()
        
        assert len(entries) > 0
        assert all(entry.source_type == SourceType.FORUM_POST for entry in entries)
    
    def test_run_full_crawl(self, miner):
        """Test full crawl execution."""
        with patch.object(miner, 'crawl_github_repos') as mock_github:
            with patch.object(miner, 'crawl_forum_posts') as mock_forum:
                mock_github.return_value = []
                mock_forum.return_value = []
                
                stats = miner.run_full_crawl()
                
                assert 'total_extracted' in stats
                assert 'duration_seconds' in stats
                assert 'by_type' in stats
                assert 'by_source' in stats
    
    def test_search_knowledge(self, miner):
        """Test knowledge search functionality."""
        # Add some test entries
        test_entry = KnowledgeEntry(
            id="test123",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://test.com",
            title="Test Quest",
            content="This is a test quest with specific content",
            metadata={},
            extracted_at=datetime.now(),
            confidence_score=0.8,
            tags=["test", "quest"]
        )
        miner.knowledge_entries[KnowledgeType.QUEST_LOGIC] = [test_entry]
        
        # Search by title
        results = miner.search_knowledge("Test Quest")
        assert len(results) == 1
        
        # Search by content
        results = miner.search_knowledge("specific content")
        assert len(results) == 1
        
        # Search by tag
        results = miner.search_knowledge("quest")
        assert len(results) == 1
        
        # Search with no results
        results = miner.search_knowledge("nonexistent")
        assert len(results) == 0


class TestMTGKnowledgeIntegration:
    """Test the MTGKnowledgeIntegration class."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def integration(self, temp_data_dir):
        """Create a MTGKnowledgeIntegration instance for testing."""
        return MTGKnowledgeIntegration(data_dir=temp_data_dir)
    
    def test_integration_initialization(self, integration):
        """Test integration initialization."""
        assert integration.data_dir.exists()
        assert len(integration.integrations) == 0
        assert len(integration.knowledge_layer) == 0
        assert len(integration.integration_mappings) == 7  # All knowledge types
    
    def test_integration_mappings(self, integration):
        """Test integration mappings configuration."""
        mapping = integration.integration_mappings[KnowledgeType.QUEST_LOGIC]
        assert mapping['target_system'] == 'quest_engine'
        assert mapping['integration_method'] == 'quest_logic_integration'
        assert mapping['confidence_threshold'] == 0.7
        
        mapping = integration.integration_mappings[KnowledgeType.CRAFTING_STATS]
        assert mapping['target_system'] == 'crafting_system'
        assert mapping['confidence_threshold'] == 0.8
    
    def test_process_quest_logic(self, integration):
        """Test quest logic processing."""
        entry = KnowledgeEntry(
            id="test123",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://test.com",
            title="Test Quest",
            content="Quest ID 12345, Mission Type: Escort, Reward: 500, Prerequisite: Level 10",
            metadata={},
            extracted_at=datetime.now(),
            confidence_score=0.8
        )
        
        result = integration._process_quest_logic(entry)
        
        assert 'quest_patterns' in result
        assert 'mission_types' in result
        assert 'reward_patterns' in result
        assert 'prerequisite_patterns' in result
        assert '12345' in result['quest_patterns']
        assert 'Escort' in result['mission_types']
    
    def test_process_crafting_stats(self, integration):
        """Test crafting stats processing."""
        entry = KnowledgeEntry(
            id="test123",
            knowledge_type=KnowledgeType.CRAFTING_STATS,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://test.com",
            title="Test Crafting",
            content="Craft Level 5, Recipe: Advanced Armor, Resource: Durasteel, Quality: 85",
            metadata={},
            extracted_at=datetime.now(),
            confidence_score=0.8
        )
        
        result = integration._process_crafting_stats(entry)
        
        assert 'craft_levels' in result
        assert 'recipe_patterns' in result
        assert 'resource_patterns' in result
        assert 'quality_patterns' in result
        assert '5' in result['craft_levels']
        assert 'Advanced' in result['recipe_patterns']
    
    def test_integrate_knowledge_entry(self, integration):
        """Test knowledge entry integration."""
        entry = KnowledgeEntry(
            id="test123",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://test.com",
            title="Test Quest",
            content="Quest ID 12345, Mission Type: Escort",
            metadata={},
            extracted_at=datetime.now(),
            confidence_score=0.8
        )
        
        result = integration.integrate_knowledge_entry(entry)
        
        assert result is not None
        assert result.status == IntegrationStatus.INTEGRATED
        assert result.source_entry_id == entry.id
        assert result.target_system == 'quest_engine'
        assert result.confidence_score == 0.8
    
    def test_integrate_knowledge_entry_low_confidence(self, integration):
        """Test knowledge entry integration with low confidence."""
        entry = KnowledgeEntry(
            id="test123",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://test.com",
            title="Test Quest",
            content="Quest ID 12345",
            metadata={},
            extracted_at=datetime.now(),
            confidence_score=0.5  # Below threshold
        )
        
        result = integration.integrate_knowledge_entry(entry)
        
        assert result is None  # Should be rejected due to low confidence
    
    def test_run_full_integration(self, integration):
        """Test full integration execution."""
        with patch('core.mtg_knowledge_miner.mtg_knowledge_miner.get_all_knowledge') as mock_get:
            mock_get.return_value = {}
            
            stats = integration.run_full_integration()
            
            assert 'total_integrated' in stats
            assert 'total_failed' in stats
            assert 'duration_seconds' in stats
            assert 'success_rate' in stats
    
    def test_get_integration_stats(self, integration):
        """Test integration statistics."""
        stats = integration.get_integration_stats()
        
        assert 'total_integrations' in stats
        assert 'successful_integrations' in stats
        assert 'failed_integrations' in stats
        assert 'success_rate' in stats
        assert 'knowledge_layer_systems' in stats
    
    def test_search_knowledge_layer(self, integration):
        """Test knowledge layer search."""
        # Add some test data to knowledge layer
        integration.knowledge_layer['quest_engine'] = {
            'data': {
                'quest_patterns': ['12345', '67890'],
                'mission_types': ['Escort', 'Defend']
            }
        }
        
        # Search for specific pattern
        results = integration.search_knowledge_layer('12345')
        assert 'quest_engine' in results
        assert 'quest_patterns' in results['quest_engine']
        assert '12345' in results['quest_engine']['quest_patterns']
        
        # Search by system
        results = integration.search_knowledge_layer('Escort', 'quest_engine')
        assert 'quest_engine' in results
        assert 'mission_types' in results['quest_engine']


class TestIntegrationWorkflow:
    """Test the complete integration workflow."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_full_workflow(self, temp_data_dir):
        """Test the complete MTG knowledge mining and integration workflow."""
        # Create miner and integration instances
        miner = MTGKnowledgeMiner(data_dir=temp_data_dir)
        integration = MTGKnowledgeIntegration(data_dir=temp_data_dir)
        
        # Create test knowledge entry
        entry = KnowledgeEntry(
            id="workflow_test",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://github.com/test/workflow",
            title="Workflow Test Quest",
            content="Quest ID 99999, Mission Type: Test, Reward: 1000, Prerequisite: Level 20",
            metadata={"test": "workflow"},
            extracted_at=datetime.now(),
            confidence_score=0.9,
            tags=["workflow", "test"]
        )
        
        # Add entry to miner
        miner.knowledge_entries[KnowledgeType.QUEST_LOGIC] = [entry]
        
        # Integrate the entry
        integration_result = integration.integrate_knowledge_entry(entry)
        
        assert integration_result is not None
        assert integration_result.status == IntegrationStatus.INTEGRATED
        
        # Check knowledge layer
        knowledge_layer = integration.get_knowledge_layer()
        assert 'quest_engine' in knowledge_layer
        assert 'data' in knowledge_layer['quest_engine']
        
        # Check that patterns were extracted
        quest_data = knowledge_layer['quest_engine']['data']
        assert 'quest_patterns' in quest_data
        assert '99999' in quest_data['quest_patterns']
        assert 'mission_types' in quest_data
        assert 'Test' in quest_data['mission_types']


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_invalid_knowledge_type(self, temp_data_dir):
        """Test handling of invalid knowledge types."""
        miner = MTGKnowledgeMiner(data_dir=temp_data_dir)
        
        # Test with unknown knowledge type
        result = miner._extract_knowledge_from_content("test content", "test.txt", "UNKNOWN_TYPE")
        assert result is None
    
    def test_network_error_handling(self, temp_data_dir):
        """Test handling of network errors during crawling."""
        miner = MTGKnowledgeMiner(data_dir=temp_data_dir)
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            entries = miner.crawl_github_repos()
            assert len(entries) == 0
            assert len(miner.session_stats['errors']) > 0
    
    def test_file_processing_error(self, temp_data_dir):
        """Test handling of file processing errors."""
        miner = MTGKnowledgeMiner(data_dir=temp_data_dir)
        
        # Test with invalid file item
        result = miner._extract_from_github_file({}, "https://test.com", "test_repo")
        assert result is None
    
    def test_integration_error_handling(self, temp_data_dir):
        """Test handling of integration errors."""
        integration = MTGKnowledgeIntegration(data_dir=temp_data_dir)
        
        # Test with invalid entry
        result = integration.integrate_knowledge_entry(None)
        assert result is None


class TestPerformance:
    """Test performance aspects."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_large_dataset_handling(self, temp_data_dir):
        """Test handling of large datasets."""
        miner = MTGKnowledgeMiner(data_dir=temp_data_dir)
        
        # Create many test entries
        entries = []
        for i in range(100):
            entry = KnowledgeEntry(
                id=f"test_{i}",
                knowledge_type=KnowledgeType.QUEST_LOGIC,
                source_type=SourceType.GITHUB_REPO,
                source_url=f"https://test{i}.com",
                title=f"Test Quest {i}",
                content=f"Quest ID {i}, Mission Type: Test",
                metadata={},
                extracted_at=datetime.now(),
                confidence_score=0.8
            )
            entries.append(entry)
        
        miner.knowledge_entries[KnowledgeType.QUEST_LOGIC] = entries
        
        # Test search performance
        start_time = datetime.now()
        results = miner.search_knowledge("Test")
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0  # Should complete within 1 second
        assert len(results) > 0
    
    def test_memory_usage(self, temp_data_dir):
        """Test memory usage with large content."""
        miner = MTGKnowledgeMiner(data_dir=temp_data_dir)
        
        # Create entry with large content
        large_content = "x" * 10000  # 10KB content
        entry = KnowledgeEntry(
            id="large_test",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://test.com",
            title="Large Test",
            content=large_content,
            metadata={},
            extracted_at=datetime.now(),
            confidence_score=0.8
        )
        
        # Process the entry
        result = miner._extract_quest_logic(entry.content, "large_test.txt")
        
        # Check that content was limited
        assert len(result['content']) <= 2000


if __name__ == "__main__":
    pytest.main([__file__]) 