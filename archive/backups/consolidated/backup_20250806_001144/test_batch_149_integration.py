#!/usr/bin/env python3
"""
Batch 149 - Passive Player Data Collection Integration Tests

This test suite validates the passive player data collection system
for SWGDB intelligence gathering.

Test Coverage:
- Passive data collection functionality
- OCR-based player detection
- Guild, faction, title extraction
- NPC detection logic
- Data persistence and export
- SWGDB integration format
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
from core.passive_player_collector import PassivePlayerCollector, PassivePlayerData
from profession_logic.utils.logger import logger


class TestPassivePlayerCollector:
    """Test suite for passive player data collection system."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        data_dir = Path(temp_dir) / "data" / "encounters"
        data_dir.mkdir(parents=True, exist_ok=True)
        yield data_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def collector(self, temp_data_dir):
        """Create collector instance with temporary data file."""
        data_file = temp_data_dir / "players_seen.json"
        return PassivePlayerCollector(str(data_file))
    
    @pytest.fixture
    def sample_player_data(self):
        """Sample player data for testing."""
        return {
            "name": "TestPlayer",
            "guild": "Test Guild",
            "faction": "Imperial",
            "title": "Master",
            "location": "TestZone",
            "timestamp": datetime.now().isoformat()
        }
    
    def test_initialization(self, collector):
        """Test collector initialization."""
        assert collector is not None
        assert hasattr(collector, 'known_players')
        assert hasattr(collector, 'detection_regions')
        assert hasattr(collector, 'name_patterns')
        assert hasattr(collector, 'guild_patterns')
        assert hasattr(collector, 'faction_patterns')
        assert hasattr(collector, 'title_patterns')
    
    def test_load_existing_data_empty(self, collector):
        """Test loading data from empty file."""
        assert len(collector.known_players) == 0
    
    def test_load_existing_data_with_records(self, temp_data_dir):
        """Test loading data from existing file with records."""
        data_file = temp_data_dir / "players_seen.json"
        
        # Create sample data
        sample_data = [
            {
                "name": "TestPlayer1",
                "guild": "Test Guild",
                "faction": "Imperial",
                "title": "Master",
                "location": "TestZone",
                "timestamp": "2025-01-01T00:00:00",
                "encounter_count": 2,
                "possible_npc": False,
                "zones_seen": ["TestZone", "OtherZone"]
            }
        ]
        
        with open(data_file, 'w') as f:
            json.dump(sample_data, f)
        
        collector = PassivePlayerCollector(str(data_file))
        assert len(collector.known_players) == 1
        assert "TestPlayer1" in collector.known_players
    
    def test_save_data(self, collector, sample_player_data):
        """Test saving data to file."""
        # Add sample player
        player = PassivePlayerData(**sample_player_data)
        collector.known_players[player.name] = player
        
        # Save data
        collector._save_data()
        
        # Verify file was created
        assert collector.data_file.exists()
        
        # Load and verify data
        with open(collector.data_file, 'r') as f:
            saved_data = json.load(f)
        
        assert len(saved_data) == 1
        assert saved_data[0]["name"] == "TestPlayer"
    
    @patch('core.passive_player_collector.capture_screen')
    @patch('core.passive_player_collector.get_ocr_engine')
    def test_collect_passive_data(self, mock_ocr_engine, mock_capture_screen, collector):
        """Test passive data collection."""
        # Mock OCR engine
        mock_engine = Mock()
        mock_engine.extract_text.return_value = Mock(
            text="TestPlayer [Test Guild] Master Imperial",
            confidence=85.0
        )
        mock_ocr_engine.return_value = mock_engine
        
        # Mock screen capture
        mock_capture_screen.return_value = Mock()
        
        # Mock current location
        current_location = {
            "planet": "TestPlanet",
            "city": "TestCity",
            "coordinates": [100, 200]
        }
        
        # Collect data
        encounters = collector.collect_passive_data(current_location)
        
        # Verify encounters were collected
        assert len(encounters) > 0
        assert encounters[0].name == "TestPlayer"
    
    def test_extract_player_name(self, collector):
        """Test player name extraction."""
        # Test CamelCase names
        assert collector._extract_player_name("TestPlayer") == "TestPlayer"
        assert collector._extract_player_name("Player123") == "Player123"
        assert collector._extract_player_name("Player_Name") == "Player_Name"
        
        # Test filtering of common words
        assert collector._extract_player_name("The Player") is None
        assert collector._extract_player_name("And Player") is None
    
    def test_extract_guild(self, collector):
        """Test guild extraction."""
        # Test bracket format
        assert collector._extract_guild("Player [Test Guild]") == "Test Guild"
        assert collector._extract_guild("Player <Test Guild>") == "Test Guild"
        assert collector._extract_guild("Player Guild: TestGuild") == "TestGuild"
        
        # Test no guild
        assert collector._extract_guild("Player") is None
    
    def test_extract_faction(self, collector):
        """Test faction extraction."""
        # Test imperial
        assert collector._extract_faction("Player Imperial") == "imperial"
        assert collector._extract_faction("Player Empire") == "imperial"
        
        # Test rebel
        assert collector._extract_faction("Player Rebel") == "rebel"
        assert collector._extract_faction("Player Alliance") == "rebel"
        
        # Test neutral
        assert collector._extract_faction("Player Neutral") == "neutral"
        
        # Test no faction
        assert collector._extract_faction("Player") is None
    
    def test_extract_title(self, collector):
        """Test title extraction."""
        # Test two word titles
        assert collector._extract_title("Player Master Rifleman") == "Master Rifleman"
        assert collector._extract_title("Player Jedi Master") == "Jedi Master"
        
        # Test single word titles
        assert collector._extract_title("Player Warrior") == "Warrior"
        
        # Test filtering
        assert collector._extract_title("Player The Warrior") is None
    
    def test_update_known_player_new(self, collector):
        """Test updating known player with new player."""
        encounter = PassivePlayerData(
            name="NewPlayer",
            guild="New Guild",
            faction="Imperial",
            title="Master",
            location="TestZone"
        )
        
        collector._update_known_player(encounter)
        
        assert "NewPlayer" in collector.known_players
        player = collector.known_players["NewPlayer"]
        assert player.guild == "New Guild"
        assert player.faction == "Imperial"
        assert player.title == "Master"
        assert player.encounter_count == 1
    
    def test_update_known_player_existing(self, collector):
        """Test updating known player with existing player."""
        # Add initial player
        initial_player = PassivePlayerData(
            name="TestPlayer",
            guild="Old Guild",
            faction="Rebel",
            title="Apprentice",
            location="Zone1"
        )
        collector.known_players["TestPlayer"] = initial_player
        
        # Update with new encounter
        new_encounter = PassivePlayerData(
            name="TestPlayer",
            guild="New Guild",
            faction="Imperial",
            title="Master",
            location="Zone2"
        )
        
        collector._update_known_player(new_encounter)
        
        player = collector.known_players["TestPlayer"]
        assert player.encounter_count == 2
        assert player.guild == "Old Guild"  # Should not update existing guild
        assert player.faction == "Rebel"    # Should not update existing faction
        assert player.title == "Apprentice" # Should not update existing title
        assert len(player.zones_seen) == 2
        assert "Zone1" in player.zones_seen
        assert "Zone2" in player.zones_seen
    
    def test_npc_detection(self, collector):
        """Test NPC detection logic."""
        # Add player with multiple zones
        player = PassivePlayerData(
            name="PossibleNPC",
            guild="Test Guild",
            faction="Neutral",
            title="Trader",
            location="Zone1"
        )
        player.zones_seen = {"Zone1", "Zone2", "Zone3"}
        collector.known_players["PossibleNPC"] = player
        
        # Update with new encounter
        new_encounter = PassivePlayerData(
            name="PossibleNPC",
            guild="Test Guild",
            faction="Neutral",
            title="Trader",
            location="Zone4"
        )
        
        collector._update_known_player(new_encounter)
        
        player = collector.known_players["PossibleNPC"]
        assert player.possible_npc is True
        assert len(player.zones_seen) == 4
    
    def test_get_player_statistics(self, collector):
        """Test player statistics generation."""
        # Add sample players
        players = [
            PassivePlayerData(name="Player1", guild="Guild1", faction="Imperial", location="Zone1"),
            PassivePlayerData(name="Player2", guild="Guild1", faction="Imperial", location="Zone2"),
            PassivePlayerData(name="Player3", guild="Guild2", faction="Rebel", location="Zone3"),
        ]
        
        for player in players:
            collector.known_players[player.name] = player
        
        stats = collector.get_player_statistics()
        
        assert stats["total_players"] == 3
        assert stats["total_encounters"] == 3
        assert stats["guilds"]["Guild1"] == 2
        assert stats["guilds"]["Guild2"] == 1
        assert stats["factions"]["imperial"] == 2
        assert stats["factions"]["rebel"] == 1
    
    def test_export_for_swgdb(self, collector):
        """Test SWGDB export format."""
        # Add sample player
        player = PassivePlayerData(
            name="TestPlayer",
            guild="Test Guild",
            faction="Imperial",
            title="Master",
            location="TestZone"
        )
        collector.known_players["TestPlayer"] = player
        
        export_data = collector.export_for_swgdb()
        
        assert "players" in export_data
        assert "statistics" in export_data
        assert "export_timestamp" in export_data
        
        assert len(export_data["players"]) == 1
        player_data = export_data["players"][0]
        assert player_data["name"] == "TestPlayer"
        assert player_data["guild"] == "Test Guild"
        assert player_data["faction"] == "Imperial"
        assert player_data["title"] == "Master"
        assert player_data["encounter_count"] == 1
        assert player_data["possible_npc"] is False
    
    def test_parse_player_text(self, collector):
        """Test parsing player information from text."""
        text = "TestPlayer [Test Guild] Master Imperial"
        current_zone = "TestZone"
        
        players = collector._parse_player_text(text, current_zone)
        
        assert len(players) == 1
        player_data = players[0]
        assert player_data["name"] == "TestPlayer"
        assert player_data["guild"] == "Test Guild"
        assert player_data["title"] == "Master"
        assert player_data["faction"] == "imperial"
    
    def test_extract_player_info(self, collector):
        """Test extracting player information from text line."""
        # Test complete player info
        text = "TestPlayer [Test Guild] Master Imperial"
        player_data = collector._extract_player_info(text)
        
        assert player_data is not None
        assert player_data["name"] == "TestPlayer"
        assert player_data["guild"] == "Test Guild"
        assert player_data["title"] == "Master"
        assert player_data["faction"] == "imperial"
        
        # Test minimal player info
        text = "TestPlayer"
        player_data = collector._extract_player_info(text)
        
        assert player_data is not None
        assert player_data["name"] == "TestPlayer"
        assert player_data.get("guild") is None
        assert player_data.get("faction") is None
        assert player_data.get("title") is None
    
    def test_cleanup(self, collector, sample_player_data):
        """Test cleanup functionality."""
        # Add sample data
        player = PassivePlayerData(**sample_player_data)
        collector.known_players[player.name] = player
        
        # Perform cleanup
        collector.cleanup()
        
        # Verify data was saved
        assert collector.data_file.exists()


class TestPassivePlayerData:
    """Test suite for PassivePlayerData dataclass."""
    
    def test_initialization(self):
        """Test PassivePlayerData initialization."""
        player = PassivePlayerData(
            name="TestPlayer",
            guild="Test Guild",
            faction="Imperial",
            title="Master",
            location="TestZone"
        )
        
        assert player.name == "TestPlayer"
        assert player.guild == "Test Guild"
        assert player.faction == "Imperial"
        assert player.title == "Master"
        assert player.location == "TestZone"
        assert player.encounter_count == 1
        assert player.possible_npc is False
        assert player.zones_seen == {"TestZone"}
        assert player.timestamp is not None
    
    def test_post_init_timestamp(self):
        """Test automatic timestamp generation."""
        player = PassivePlayerData(name="TestPlayer", location="TestZone")
        
        assert player.timestamp is not None
        # Verify it's a valid ISO format
        datetime.fromisoformat(player.timestamp)
    
    def test_post_init_zones_seen(self):
        """Test automatic zones_seen initialization."""
        player = PassivePlayerData(name="TestPlayer", location="TestZone")
        
        assert player.zones_seen == {"TestZone"}


def run_integration_tests():
    """Run integration tests for Batch 149."""
    print("\n" + "="*80)
    print("🧪 BATCH 149 - PASSIVE PLAYER COLLECTION INTEGRATION TESTS")
    print("="*80)
    
    # Create test instance
    test_instance = TestPassivePlayerCollector()
    
    # Run key tests
    test_results = []
    
    print("\n📋 Running Tests:")
    
    # Test initialization
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data" / "encounters"
            data_dir.mkdir(parents=True, exist_ok=True)
            collector = PassivePlayerCollector(str(data_dir / "players_seen.json"))
            test_instance.test_initialization(collector)
            print("✅ Initialization test passed")
            test_results.append(("Initialization", True))
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        test_results.append(("Initialization", False))
    
    # Test data extraction
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data" / "encounters"
            data_dir.mkdir(parents=True, exist_ok=True)
            collector = PassivePlayerCollector(str(data_dir / "players_seen.json"))
            
            # Test name extraction
            assert collector._extract_player_name("TestPlayer") == "TestPlayer"
            assert collector._extract_guild("Player [Test Guild]") == "Test Guild"
            assert collector._extract_faction("Player Imperial") == "imperial"
            assert collector._extract_title("Player Master Rifleman") == "Master Rifleman"
            
            print("✅ Data extraction tests passed")
            test_results.append(("Data Extraction", True))
    except Exception as e:
        print(f"❌ Data extraction tests failed: {e}")
        test_results.append(("Data Extraction", False))
    
    # Test player management
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data" / "encounters"
            data_dir.mkdir(parents=True, exist_ok=True)
            collector = PassivePlayerCollector(str(data_dir / "players_seen.json"))
            
            # Test new player
            encounter = PassivePlayerData(
                name="TestPlayer",
                guild="Test Guild",
                faction="Imperial",
                title="Master",
                location="TestZone"
            )
            collector._update_known_player(encounter)
            assert "TestPlayer" in collector.known_players
            
            # Test statistics
            stats = collector.get_player_statistics()
            assert stats["total_players"] == 1
            
            print("✅ Player management tests passed")
            test_results.append(("Player Management", True))
    except Exception as e:
        print(f"❌ Player management tests failed: {e}")
        test_results.append(("Player Management", False))
    
    # Test SWGDB export
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data" / "encounters"
            data_dir.mkdir(parents=True, exist_ok=True)
            collector = PassivePlayerCollector(str(data_dir / "players_seen.json"))
            
            # Add sample player
            encounter = PassivePlayerData(
                name="TestPlayer",
                guild="Test Guild",
                faction="Imperial",
                title="Master",
                location="TestZone"
            )
            collector._update_known_player(encounter)
            
            # Test export
            export_data = collector.export_for_swgdb()
            assert "players" in export_data
            assert "statistics" in export_data
            assert len(export_data["players"]) == 1
            
            print("✅ SWGDB export tests passed")
            test_results.append(("SWGDB Export", True))
    except Exception as e:
        print(f"❌ SWGDB export tests failed: {e}")
        test_results.append(("SWGDB Export", False))
    
    # Summary
    print("\n" + "-"*60)
    print("📊 TEST SUMMARY")
    print("-"*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Batch 149 integration is ready.")
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1) 