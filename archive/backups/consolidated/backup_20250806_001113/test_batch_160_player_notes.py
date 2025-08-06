#!/usr/bin/env python3
"""
Batch 160 - Player Notes System Tests

Comprehensive test suite for the player notes system including:
- PlayerNote dataclass tests
- PlayerNotesCollector functionality tests
- PlayerNotesIntegration tests
- Data persistence tests
- Global helper function tests
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.player_notes_collector import (
    PlayerNote, PlayerNotesCollector, get_player_notes_collector, add_player_encounter
)
from core.player_notes_integration import (
    PlayerEncounterEvent, PlayerNotesIntegration, get_player_notes_integration
)


class TestPlayerNote(unittest.TestCase):
    """Test the PlayerNote dataclass."""
    
    def test_player_note_creation(self):
        """Test creating a PlayerNote instance."""
        player = PlayerNote(
            player_name="TestPlayer",
            guild_tag="TestGuild",
            race="human",
            faction="neutral",
            title="Warrior"
        )
        
        self.assertEqual(player.player_name, "TestPlayer")
        self.assertEqual(player.guild_tag, "TestGuild")
        self.assertEqual(player.race, "human")
        self.assertEqual(player.faction, "neutral")
        self.assertEqual(player.title, "Warrior")
        self.assertEqual(player.encounter_count, 1)
        self.assertIsInstance(player.first_seen, str)
        self.assertIsInstance(player.last_seen, str)
        self.assertEqual(player.locations, [])
        self.assertIsNone(player.notes)
    
    def test_player_note_post_init(self):
        """Test PlayerNote __post_init__ method."""
        player = PlayerNote(player_name="TestPlayer")
        
        # Check that timestamps are set
        self.assertIsNotNone(player.first_seen)
        self.assertIsNotNone(player.last_seen)
        
        # Check that locations is initialized as empty list
        self.assertEqual(player.locations, [])
        
        # Check that encounter_count defaults to 1
        self.assertEqual(player.encounter_count, 1)


class TestPlayerNotesCollector(unittest.TestCase):
    """Test the PlayerNotesCollector class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_file = Path(self.temp_dir) / "test_players_seen.json"
        self.collector = PlayerNotesCollector(str(self.test_data_file))
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_data_file.exists():
            self.test_data_file.unlink()
        Path(self.temp_dir).rmdir()
    
    def test_collector_initialization(self):
        """Test collector initialization."""
        self.assertEqual(self.collector.data_file, self.test_data_file)
        self.assertEqual(len(self.collector.players), 0)
    
    def test_add_new_player(self):
        """Test adding a new player."""
        success = self.collector.add_player_encounter(
            player_name="NewPlayer",
            guild_tag="TestGuild",
            race="human",
            faction="neutral"
        )
        
        self.assertTrue(success)
        self.assertEqual(len(self.collector.players), 1)
        
        player = self.collector.players["NewPlayer"]
        self.assertEqual(player.player_name, "NewPlayer")
        self.assertEqual(player.guild_tag, "TestGuild")
        self.assertEqual(player.race, "human")
        self.assertEqual(player.faction, "neutral")
        self.assertEqual(player.encounter_count, 1)
    
    def test_update_existing_player(self):
        """Test updating an existing player."""
        # Add initial player
        self.collector.add_player_encounter(
            player_name="TestPlayer",
            guild_tag="OldGuild",
            race="human"
        )
        
        # Update player with new information
        success = self.collector.add_player_encounter(
            player_name="TestPlayer",
            guild_tag="NewGuild",
            race="human",
            faction="rebel",
            title="Warrior"
        )
        
        self.assertTrue(success)
        self.assertEqual(len(self.collector.players), 1)
        
        player = self.collector.players["TestPlayer"]
        self.assertEqual(player.guild_tag, "NewGuild")  # Updated
        self.assertEqual(player.faction, "rebel")  # New
        self.assertEqual(player.title, "Warrior")  # New
        self.assertEqual(player.encounter_count, 2)  # Incremented
    
    def test_add_player_with_location(self):
        """Test adding a player with location information."""
        location = {
            "planet": "Corellia",
            "city": "Coronet",
            "coordinates": [200, 400]
        }
        
        success = self.collector.add_player_encounter(
            player_name="TestPlayer",
            location=location
        )
        
        self.assertTrue(success)
        player = self.collector.players["TestPlayer"]
        self.assertEqual(len(player.locations), 1)
        self.assertIn("timestamp", player.locations[0])
        self.assertEqual(player.locations[0]["planet"], "Corellia")
    
    def test_get_player_info(self):
        """Test getting player information."""
        self.collector.add_player_encounter(
            player_name="TestPlayer",
            guild_tag="TestGuild"
        )
        
        player = self.collector.get_player_info("TestPlayer")
        self.assertIsNotNone(player)
        self.assertEqual(player.player_name, "TestPlayer")
        self.assertEqual(player.guild_tag, "TestGuild")
        
        # Test non-existent player
        player = self.collector.get_player_info("NonExistentPlayer")
        self.assertIsNone(player)
    
    def test_get_players_by_guild(self):
        """Test filtering players by guild."""
        self.collector.add_player_encounter("Player1", guild_tag="GuildA")
        self.collector.add_player_encounter("Player2", guild_tag="GuildB")
        self.collector.add_player_encounter("Player3", guild_tag="GuildA")
        
        guild_a_players = self.collector.get_players_by_guild("GuildA")
        self.assertEqual(len(guild_a_players), 2)
        
        guild_b_players = self.collector.get_players_by_guild("GuildB")
        self.assertEqual(len(guild_b_players), 1)
    
    def test_get_players_by_faction(self):
        """Test filtering players by faction."""
        self.collector.add_player_encounter("Player1", faction="rebel")
        self.collector.add_player_encounter("Player2", faction="imperial")
        self.collector.add_player_encounter("Player3", faction="rebel")
        
        rebel_players = self.collector.get_players_by_faction("rebel")
        self.assertEqual(len(rebel_players), 2)
        
        imperial_players = self.collector.get_players_by_faction("imperial")
        self.assertEqual(len(imperial_players), 1)
    
    def test_get_players_by_race(self):
        """Test filtering players by race."""
        self.collector.add_player_encounter("Player1", race="human")
        self.collector.add_player_encounter("Player2", race="zabrak")
        self.collector.add_player_encounter("Player3", race="human")
        
        human_players = self.collector.get_players_by_race("human")
        self.assertEqual(len(human_players), 2)
        
        zabrak_players = self.collector.get_players_by_race("zabrak")
        self.assertEqual(len(zabrak_players), 1)
    
    def test_get_statistics(self):
        """Test statistics generation."""
        self.collector.add_player_encounter("Player1", guild_tag="GuildA", faction="rebel", race="human")
        self.collector.add_player_encounter("Player2", guild_tag="GuildA", faction="rebel", race="zabrak")
        self.collector.add_player_encounter("Player3", guild_tag="GuildB", faction="imperial", race="human")
        
        stats = self.collector.get_statistics()
        
        self.assertEqual(stats["total_players"], 3)
        self.assertEqual(stats["total_encounters"], 3)
        self.assertEqual(stats["guilds"]["GuildA"], 2)
        self.assertEqual(stats["guilds"]["GuildB"], 1)
        self.assertEqual(stats["factions"]["rebel"], 2)
        self.assertEqual(stats["factions"]["imperial"], 1)
        self.assertEqual(stats["races"]["human"], 2)
        self.assertEqual(stats["races"]["zabrak"], 1)
    
    def test_export_data_json(self):
        """Test JSON data export."""
        self.collector.add_player_encounter("TestPlayer", guild_tag="TestGuild")
        
        export_file = self.collector.export_data(format="json")
        
        self.assertTrue(Path(export_file).exists())
        
        # Verify exported data
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        self.assertIn("TestPlayer", exported_data)
        self.assertEqual(exported_data["TestPlayer"]["guild_tag"], "TestGuild")
        
        # Clean up
        Path(export_file).unlink()
    
    def test_export_data_csv(self):
        """Test CSV data export."""
        self.collector.add_player_encounter("TestPlayer", guild_tag="TestGuild", race="human")
        
        export_file = self.collector.export_data(format="csv")
        
        self.assertTrue(Path(export_file).exists())
        
        # Verify CSV content
        with open(export_file, 'r') as f:
            lines = f.readlines()
        
        self.assertGreater(len(lines), 1)  # Header + data
        self.assertIn("TestPlayer", lines[1])
        self.assertIn("TestGuild", lines[1])
        
        # Clean up
        Path(export_file).unlink()
    
    def test_cleanup_old_data(self):
        """Test cleanup of old data."""
        # Add a player with old timestamp
        player = PlayerNote(player_name="OldPlayer")
        player.last_seen = (datetime.now() - timedelta(days=2)).isoformat()
        self.collector.players["OldPlayer"] = player
        
        # Add a player with recent timestamp
        player = PlayerNote(player_name="RecentPlayer")
        player.last_seen = datetime.now().isoformat()
        self.collector.players["RecentPlayer"] = player
        
        # Cleanup data older than 1 day
        removed_count = self.collector.cleanup_old_data(days_old=1)
        
        self.assertEqual(removed_count, 1)
        self.assertNotIn("OldPlayer", self.collector.players)
        self.assertIn("RecentPlayer", self.collector.players)


class TestPlayerNotesIntegration(unittest.TestCase):
    """Test the PlayerNotesIntegration class."""
    
    def setUp(self):
        """Set up test environment."""
        self.integration = PlayerNotesIntegration()
    
    def test_integration_initialization(self):
        """Test integration initialization."""
        self.assertIsNotNone(self.integration.player_notes_collector)
        self.assertEqual(len(self.integration.session_encounters), 0)
    
    def test_record_player_encounter(self):
        """Test recording a player encounter."""
        success = self.integration.record_player_encounter(
            player_name="TestPlayer",
            guild_tag="TestGuild",
            race="human",
            faction="neutral",
            location={"planet": "Corellia", "city": "Coronet"}
        )
        
        self.assertTrue(success)
        self.assertEqual(len(self.integration.session_encounters), 1)
        
        encounter = self.integration.session_encounters[0]
        self.assertEqual(encounter.player_name, "TestPlayer")
        self.assertEqual(encounter.guild_tag, "TestGuild")
        self.assertEqual(encounter.race, "human")
        self.assertEqual(encounter.faction, "neutral")
    
    def test_get_session_statistics(self):
        """Test session statistics generation."""
        self.integration.record_player_encounter("Player1", guild_tag="GuildA", faction="rebel")
        self.integration.record_player_encounter("Player2", guild_tag="GuildA", faction="rebel")
        self.integration.record_player_encounter("Player3", guild_tag="GuildB", faction="imperial")
        
        stats = self.integration.get_session_statistics()
        
        self.assertEqual(stats["session_encounters"], 3)
        self.assertEqual(stats["unique_players"], 3)
        self.assertIn("GuildA", stats["guilds_encountered"])
        self.assertIn("GuildB", stats["guilds_encountered"])
        self.assertIn("rebel", stats["factions_encountered"])
        self.assertIn("imperial", stats["factions_encountered"])
    
    def test_get_players_by_guild_in_session(self):
        """Test filtering session players by guild."""
        self.integration.record_player_encounter("Player1", guild_tag="GuildA")
        self.integration.record_player_encounter("Player2", guild_tag="GuildA")
        self.integration.record_player_encounter("Player3", guild_tag="GuildB")
        
        guild_a_players = self.integration.get_players_by_guild_in_session("GuildA")
        self.assertEqual(len(guild_a_players), 2)
        
        guild_b_players = self.integration.get_players_by_guild_in_session("GuildB")
        self.assertEqual(len(guild_b_players), 1)
    
    def test_get_players_by_faction_in_session(self):
        """Test filtering session players by faction."""
        self.integration.record_player_encounter("Player1", faction="rebel")
        self.integration.record_player_encounter("Player2", faction="rebel")
        self.integration.record_player_encounter("Player3", faction="imperial")
        
        rebel_players = self.integration.get_players_by_faction_in_session("rebel")
        self.assertEqual(len(rebel_players), 2)
        
        imperial_players = self.integration.get_players_by_faction_in_session("imperial")
        self.assertEqual(len(imperial_players), 1)
    
    def test_export_session_data(self):
        """Test session data export."""
        self.integration.record_player_encounter("TestPlayer", guild_tag="TestGuild")
        
        session_data = self.integration.export_session_data()
        
        self.assertIn("encounters", session_data)
        self.assertIn("statistics", session_data)
        self.assertEqual(len(session_data["encounters"]), 1)
        self.assertEqual(session_data["encounters"][0]["player_name"], "TestPlayer")
    
    def test_clear_session_data(self):
        """Test clearing session data."""
        self.integration.record_player_encounter("TestPlayer")
        self.assertEqual(len(self.integration.session_encounters), 1)
        
        self.integration.clear_session_data()
        self.assertEqual(len(self.integration.session_encounters), 0)


class TestGlobalFunctions(unittest.TestCase):
    """Test global helper functions."""
    
    def test_get_player_notes_collector(self):
        """Test global collector function."""
        collector = get_player_notes_collector()
        self.assertIsInstance(collector, PlayerNotesCollector)
    
    def test_add_player_encounter(self):
        """Test global add_player_encounter function."""
        success = add_player_encounter(
            player_name="TestPlayer",
            guild_tag="TestGuild",
            race="human"
        )
        self.assertTrue(success)
    
    def test_get_player_notes_integration(self):
        """Test global integration function."""
        integration = get_player_notes_integration()
        self.assertIsInstance(integration, PlayerNotesIntegration)


class TestDataPersistence(unittest.TestCase):
    """Test data persistence functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_file = Path(self.temp_dir) / "test_persistence.json"
        self.collector = PlayerNotesCollector(str(self.test_data_file))
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_data_file.exists():
            self.test_data_file.unlink()
        Path(self.temp_dir).rmdir()
    
    def test_data_persistence(self):
        """Test that data persists between collector instances."""
        # Add data with first collector
        self.collector.add_player_encounter("TestPlayer", guild_tag="TestGuild")
        
        # Create new collector instance
        new_collector = PlayerNotesCollector(str(self.test_data_file))
        
        # Verify data is loaded
        self.assertEqual(len(new_collector.players), 1)
        self.assertIn("TestPlayer", new_collector.players)
        
        player = new_collector.players["TestPlayer"]
        self.assertEqual(player.guild_tag, "TestGuild")
    
    def test_corrupted_data_handling(self):
        """Test handling of corrupted JSON data."""
        # Create corrupted JSON file
        with open(self.test_data_file, 'w') as f:
            f.write('{"invalid": json}')
        
        # Should handle corruption gracefully
        collector = PlayerNotesCollector(str(self.test_data_file))
        self.assertEqual(len(collector.players), 0)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 