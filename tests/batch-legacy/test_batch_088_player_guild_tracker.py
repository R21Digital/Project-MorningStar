#!/usr/bin/env python3
"""
Test suite for Batch 088 - Guild Tracker + Player Lookup Tool

This test suite covers:
1. Player and Guild data structures
2. Search and lookup functionality
3. Statistics and reporting
4. Web interface integration
5. API endpoints
"""

import json
import logging
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.player_guild_tracker import (
    PlayerGuildTracker, PlayerData, GuildMemberData, 
    EnhancedGuildData, PlayerSearchResult, GuildSearchResult,
    PlayerStatus, ProfessionType
)

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class TestPlayerData(unittest.TestCase):
    """Test PlayerData dataclass functionality."""
    
    def test_player_data_creation(self):
        """Test creating a PlayerData instance."""
        player = PlayerData(
            name="TestPlayer",
            title="Master",
            profession="commando",
            level=90,
            faction="rebel"
        )
        
        self.assertEqual(player.name, "TestPlayer")
        self.assertEqual(player.title, "Master")
        self.assertEqual(player.profession, "commando")
        self.assertEqual(player.level, 90)
        self.assertEqual(player.faction, "rebel")
        self.assertEqual(player.status, "unknown")  # default value
        self.assertEqual(player.achievements, [])  # default empty list
        self.assertEqual(player.skills, {})  # default empty dict
        self.assertEqual(player.equipment, {})  # default empty dict
    
    def test_player_data_with_optional_fields(self):
        """Test PlayerData with all optional fields."""
        player = PlayerData(
            name="TestPlayer",
            title="Master",
            guild="TestGuild",
            guild_tag="TEST",
            profession="commando",
            profession_type="combat",
            level=90,
            faction="rebel",
            city="TestCity",
            planet="naboo",
            location="Test Location",
            last_seen=datetime.now().isoformat(),
            status="online",
            playtime_hours=1000,
            achievements=["Achievement1", "Achievement2"],
            skills={"Skill1": 4000, "Skill2": 4000},
            equipment={"Weapon": "Test Weapon", "Armor": "Test Armor"},
            notes="Test notes"
        )
        
        self.assertEqual(player.name, "TestPlayer")
        self.assertEqual(player.guild, "TestGuild")
        self.assertEqual(player.guild_tag, "TEST")
        self.assertEqual(len(player.achievements), 2)
        self.assertEqual(len(player.skills), 2)
        self.assertEqual(len(player.equipment), 2)
        self.assertEqual(player.notes, "Test notes")


class TestGuildMemberData(unittest.TestCase):
    """Test GuildMemberData dataclass functionality."""
    
    def test_guild_member_data_creation(self):
        """Test creating a GuildMemberData instance."""
        member = GuildMemberData(
            name="TestMember",
            rank="Officer",
            profession="commando",
            level=85
        )
        
        self.assertEqual(member.name, "TestMember")
        self.assertEqual(member.rank, "Officer")
        self.assertEqual(member.profession, "commando")
        self.assertEqual(member.level, 85)
        self.assertIsNone(member.join_date)
        self.assertIsNone(member.last_active)
        self.assertIsNone(member.contribution)


class TestEnhancedGuildData(unittest.TestCase):
    """Test EnhancedGuildData dataclass functionality."""
    
    def test_guild_data_creation(self):
        """Test creating an EnhancedGuildData instance."""
        guild = EnhancedGuildData(
            name="Test Guild",
            tag="TEST",
            faction="rebel",
            leader="TestLeader",
            members_total=10,
            members_active=8,
            active_percentage=80.0
        )
        
        self.assertEqual(guild.name, "Test Guild")
        self.assertEqual(guild.tag, "TEST")
        self.assertEqual(guild.faction, "rebel")
        self.assertEqual(guild.leader, "TestLeader")
        self.assertEqual(guild.members_total, 10)
        self.assertEqual(guild.members_active, 8)
        self.assertEqual(guild.active_percentage, 80.0)
        self.assertEqual(guild.members, [])  # default empty list
        self.assertEqual(guild.territories, [])  # default empty list
        self.assertEqual(guild.achievements, [])  # default empty list


class TestPlayerGuildTracker(unittest.TestCase):
    """Test PlayerGuildTracker functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = PlayerGuildTracker(data_dir=self.temp_dir)
        
        # Create test data
        self.test_player = PlayerData(
            name="TestPlayer",
            title="Master",
            profession="commando",
            level=90,
            faction="rebel",
            guild="TestGuild",
            guild_tag="TEST",
            city="TestCity",
            planet="naboo",
            last_seen=datetime.now().isoformat(),
            status="online"
        )
        
        self.test_guild = EnhancedGuildData(
            name="Test Guild",
            tag="TEST",
            faction="rebel",
            leader="TestLeader",
            members_total=10,
            members_active=8,
            active_percentage=80.0,
            description="Test guild description",
            city="TestCity",
            planet="naboo",
            last_updated=datetime.now().isoformat()
        )
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        self.assertIsNotNone(self.tracker)
        self.assertTrue(self.tracker.data_dir.exists())
        self.assertTrue((self.tracker.data_dir / "players").exists())
        self.assertTrue((self.tracker.data_dir / "guilds").exists())
    
    def test_save_and_load_player_data(self):
        """Test saving and loading player data."""
        # Save player data
        self.tracker._save_player_data(self.test_player)
        
        # Load player data
        loaded_player = self.tracker._load_player_data("TestPlayer")
        
        self.assertIsNotNone(loaded_player)
        self.assertEqual(loaded_player.name, self.test_player.name)
        self.assertEqual(loaded_player.profession, self.test_player.profession)
        self.assertEqual(loaded_player.level, self.test_player.level)
    
    def test_save_and_load_guild_data(self):
        """Test saving and loading guild data."""
        # Save guild data
        self.tracker._save_guild_data(self.test_guild)
        
        # Load guild data
        loaded_guild = self.tracker._load_guild_data("TEST")
        
        self.assertIsNotNone(loaded_guild)
        self.assertEqual(loaded_guild.name, self.test_guild.name)
        self.assertEqual(loaded_guild.tag, self.test_guild.tag)
        self.assertEqual(loaded_guild.faction, self.test_guild.faction)
    
    def test_get_player(self):
        """Test player lookup functionality."""
        # Save player data
        self.tracker._save_player_data(self.test_player)
        
        # Get player
        player = self.tracker.get_player("TestPlayer")
        
        self.assertIsNotNone(player)
        self.assertEqual(player.name, "TestPlayer")
    
    def test_get_guild(self):
        """Test guild lookup functionality."""
        # Save guild data
        self.tracker._save_guild_data(self.test_guild)
        
        # Get guild
        guild = self.tracker.get_guild("TEST")
        
        self.assertIsNotNone(guild)
        self.assertEqual(guild.name, "Test Guild")
    
    def test_search_players(self):
        """Test player search functionality."""
        # Save test player
        self.tracker._save_player_data(self.test_player)
        
        # Search for players
        results = self.tracker.search_players("commando")
        
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], PlayerSearchResult)
        self.assertEqual(results[0].player.name, "TestPlayer")
        self.assertGreater(results[0].relevance_score, 0)
    
    def test_search_guilds(self):
        """Test guild search functionality."""
        # Save test guild
        self.tracker._save_guild_data(self.test_guild)
        
        # Search for guilds
        results = self.tracker.search_guilds("rebel")
        
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], GuildSearchResult)
        self.assertEqual(results[0].guild.name, "Test Guild")
        self.assertGreater(results[0].relevance_score, 0)
    
    def test_get_online_players(self):
        """Test getting online players."""
        # Create online and offline players
        online_player = PlayerData(name="OnlinePlayer", status="online")
        offline_player = PlayerData(name="OfflinePlayer", status="offline")
        
        self.tracker._save_player_data(online_player)
        self.tracker._save_player_data(offline_player)
        
        # Get online players
        online_players = self.tracker.get_online_players()
        
        self.assertEqual(len(online_players), 1)
        self.assertEqual(online_players[0].name, "OnlinePlayer")
    
    def test_get_statistics(self):
        """Test statistics generation."""
        # Save test data
        self.tracker._save_player_data(self.test_player)
        self.tracker._save_guild_data(self.test_guild)
        
        # Get statistics
        stats = self.tracker.get_statistics()
        
        self.assertIn('total_players', stats)
        self.assertIn('online_players', stats)
        self.assertIn('total_guilds', stats)
        self.assertIn('active_guilds', stats)
        self.assertIn('profession_distribution', stats)
        self.assertIn('planet_distribution', stats)
        self.assertIn('faction_distribution', stats)
        self.assertIn('recent_activity', stats)
        
        self.assertEqual(stats['total_players'], 1)
        self.assertEqual(stats['online_players'], 1)
        self.assertEqual(stats['total_guilds'], 1)
        self.assertEqual(stats['active_guilds'], 1)
    
    def test_update_player_status(self):
        """Test updating player status."""
        # Create initial player
        player = PlayerData(name="StatusPlayer", status="offline")
        self.tracker._save_player_data(player)
        
        # Update status
        self.tracker.update_player_status("StatusPlayer", "online", "New Location")
        
        # Check updated player
        updated_player = self.tracker.get_player("StatusPlayer")
        self.assertEqual(updated_player.status, "online")
        self.assertEqual(updated_player.location, "New Location")
    
    def test_profession_mapping(self):
        """Test profession type mapping."""
        self.assertEqual(self.tracker._get_profession_type("commando"), "combat")
        self.assertEqual(self.tracker._get_profession_type("artisan"), "crafting")
        self.assertEqual(self.tracker._get_profession_type("doctor"), "social")
        self.assertEqual(self.tracker._get_profession_type("jedi"), "hybrid")
        self.assertEqual(self.tracker._get_profession_type("unknown"), "unknown")


class TestWebInterface(unittest.TestCase):
    """Test web interface integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = PlayerGuildTracker(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('core.player_guild_tracker.SWGTrackerIntegration')
    def test_dashboard_integration(self, mock_swgtracker):
        """Test dashboard integration."""
        # Mock SWGTracker integration
        mock_swgtracker.return_value.fetch_guilds.return_value = []
        
        # Test that tracker can be imported by dashboard
        try:
            from dashboard.app import player_guild_tracker
            self.assertIsNotNone(player_guild_tracker)
        except ImportError:
            # Dashboard might not be available in test environment
            pass


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoint functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = PlayerGuildTracker(data_dir=self.temp_dir)
        
        # Create test data
        self.test_player = PlayerData(
            name="APITestPlayer",
            profession="commando",
            level=90,
            faction="rebel"
        )
        self.tracker._save_player_data(self.test_player)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_player_search_api_simulation(self):
        """Simulate player search API functionality."""
        # Simulate API search
        results = self.tracker.search_players("commando")
        
        # Format as API response
        api_response = {
            'success': True,
            'results': [
                {
                    'player': {
                        'name': result.player.name,
                        'profession': result.player.profession,
                        'level': result.player.level,
                        'faction': result.player.faction
                    },
                    'relevance_score': result.relevance_score,
                    'match_reasons': result.match_reasons
                }
                for result in results
            ]
        }
        
        self.assertTrue(api_response['success'])
        self.assertGreater(len(api_response['results']), 0)
        self.assertIn('player', api_response['results'][0])
        self.assertIn('relevance_score', api_response['results'][0])
    
    def test_guild_search_api_simulation(self):
        """Simulate guild search API functionality."""
        # Create test guild
        test_guild = EnhancedGuildData(
            name="APITestGuild",
            tag="APITEST",
            faction="rebel",
            leader="TestLeader",
            members_total=10,
            members_active=8,
            active_percentage=80.0
        )
        self.tracker._save_guild_data(test_guild)
        
        # Simulate API search
        results = self.tracker.search_guilds("rebel")
        
        # Format as API response
        api_response = {
            'success': True,
            'results': [
                {
                    'guild': {
                        'name': result.guild.name,
                        'tag': result.guild.tag,
                        'faction': result.guild.faction,
                        'members_total': result.guild.members_total
                    },
                    'relevance_score': result.relevance_score,
                    'match_reasons': result.match_reasons
                }
                for result in results
            ]
        }
        
        self.assertTrue(api_response['success'])
        self.assertGreater(len(api_response['results']), 0)
        self.assertIn('guild', api_response['results'][0])
        self.assertIn('relevance_score', api_response['results'][0])


def run_integration_tests():
    """Run integration tests with live server."""
    logger.info("Running integration tests...")
    
    try:
        import requests
        
        # Test basic server response
        response = requests.get("http://127.0.0.1:8000/players", timeout=5)
        if response.status_code == 200:
            logger.info("✓ Player lookup page accessible")
        else:
            logger.warning(f"✗ Player lookup page returned {response.status_code}")
        
        response = requests.get("http://127.0.0.1:8000/guilds", timeout=5)
        if response.status_code == 200:
            logger.info("✓ Guild tracker page accessible")
        else:
            logger.warning(f"✗ Guild tracker page returned {response.status_code}")
        
        # Test API endpoints
        response = requests.get("http://127.0.0.1:8000/api/players?q=commando", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info("✓ Player search API working")
            else:
                logger.warning("✗ Player search API returned error")
        else:
            logger.warning(f"✗ Player search API returned {response.status_code}")
        
        response = requests.get("http://127.0.0.1:8000/api/guilds?q=rebel", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info("✓ Guild search API working")
            else:
                logger.warning("✗ Guild search API returned error")
        else:
            logger.warning(f"✗ Guild search API returned {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        logger.warning("✗ Server not running - skipping integration tests")
    except Exception as e:
        logger.error(f"✗ Integration test error: {e}")


if __name__ == "__main__":
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run integration tests if server is available
    run_integration_tests() 