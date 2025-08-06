#!/usr/bin/env python3
"""
Test suite for Batch 176 - Seasonal Bounty Leaderboard Reset System
Comprehensive testing of auto-reset, archiving, and MVP highlighting features
"""

import os
import sys
import json
import tempfile
import shutil
import unittest
import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.reset_bounty_leaderboard import (
    SeasonalBountyLeaderboard, 
    BountyHunter, 
    SeasonStats
)


class TestBountyHunter(unittest.TestCase):
    """Test BountyHunter dataclass functionality"""
    
    def test_bounty_hunter_creation(self):
        """Test creating a bounty hunter"""
        hunter = BountyHunter(
            name="TestHunter",
            guild="TestGuild",
            kills=5,
            deaths=2,
            total_bounty=15000,
            specializations=["jedi_hunter", "marksman"]
        )
        
        self.assertEqual(hunter.name, "TestHunter")
        self.assertEqual(hunter.guild, "TestGuild")
        self.assertEqual(hunter.kills, 5)
        self.assertEqual(hunter.deaths, 2)
        self.assertEqual(hunter.total_bounty, 15000)
        self.assertEqual(hunter.specializations, ["jedi_hunter", "marksman"])
    
    def test_kd_ratio_calculation(self):
        """Test K/D ratio calculation"""
        # Hunter with kills and deaths
        hunter1 = BountyHunter(name="Hunter1", guild="Guild1", kills=10, deaths=2)
        self.assertEqual(hunter1.kd_ratio, 5.0)
        
        # Hunter with no deaths
        hunter2 = BountyHunter(name="Hunter2", guild="Guild2", kills=5, deaths=0)
        self.assertEqual(hunter2.kd_ratio, 5.0)
        
        # Hunter with no kills
        hunter3 = BountyHunter(name="Hunter3", guild="Guild3", kills=0, deaths=0)
        self.assertEqual(hunter3.kd_ratio, 0.0)
        
        # Hunter with kills but no deaths
        hunter4 = BountyHunter(name="Hunter4", guild="Guild4", kills=3, deaths=0)
        self.assertEqual(hunter4.kd_ratio, 3.0)
    
    def test_average_bounty_calculation(self):
        """Test average bounty calculation"""
        # Hunter with kills
        hunter1 = BountyHunter(name="Hunter1", guild="Guild1", kills=4, total_bounty=12000)
        self.assertEqual(hunter1.average_bounty, 3000.0)
        
        # Hunter with no kills
        hunter2 = BountyHunter(name="Hunter2", guild="Guild2", kills=0, total_bounty=0)
        self.assertEqual(hunter2.average_bounty, 0.0)
    
    def test_default_specializations(self):
        """Test default specializations initialization"""
        hunter = BountyHunter(name="TestHunter", guild="TestGuild")
        self.assertEqual(hunter.specializations, [])


class TestSeasonStats(unittest.TestCase):
    """Test SeasonStats dataclass functionality"""
    
    def test_season_stats_creation(self):
        """Test creating season stats"""
        stats = SeasonStats(
            total_kills=100,
            total_deaths=50,
            total_bounty=300000,
            active_hunters=10,
            average_kills=10.0,
            average_kd=2.0,
            top_guild="TopGuild",
            mvp_hunter="MVPHunter"
        )
        
        self.assertEqual(stats.total_kills, 100)
        self.assertEqual(stats.total_deaths, 50)
        self.assertEqual(stats.total_bounty, 300000)
        self.assertEqual(stats.active_hunters, 10)
        self.assertEqual(stats.average_kills, 10.0)
        self.assertEqual(stats.average_kd, 2.0)
        self.assertEqual(stats.top_guild, "TopGuild")
        self.assertEqual(stats.mvp_hunter, "MVPHunter")
    
    def test_default_season_stats(self):
        """Test default season stats values"""
        stats = SeasonStats()
        
        self.assertEqual(stats.total_kills, 0)
        self.assertEqual(stats.total_deaths, 0)
        self.assertEqual(stats.total_bounty, 0)
        self.assertEqual(stats.active_hunters, 0)
        self.assertEqual(stats.average_kills, 0.0)
        self.assertEqual(stats.average_kd, 0.0)
        self.assertIsNone(stats.top_guild)
        self.assertIsNone(stats.mvp_hunter)


class TestSeasonalBountyLeaderboard(unittest.TestCase):
    """Test SeasonalBountyLeaderboard functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "bounty"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize leaderboard with test directory
        self.leaderboard = SeasonalBountyLeaderboard(str(self.data_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_leaderboard_initialization(self):
        """Test leaderboard initialization"""
        self.assertIsNotNone(self.leaderboard)
        self.assertEqual(self.leaderboard.data_dir, self.data_dir)
        self.assertIsNotNone(self.leaderboard.current_season)
    
    def test_create_new_season(self):
        """Test creating a new season"""
        # Remove existing season file
        if self.leaderboard.current_file.exists():
            self.leaderboard.current_file.unlink()
        
        new_season = self.leaderboard._create_new_season()
        
        self.assertIn('season', new_season)
        self.assertIn('start_date', new_season)
        self.assertIn('status', new_season)
        self.assertEqual(new_season['status'], 'active')
        self.assertIn('hunters', new_season)
        self.assertIn('season_stats', new_season)
        self.assertIn('settings', new_season)
    
    def test_add_kill(self):
        """Test adding a kill"""
        success = self.leaderboard.add_kill("TestHunter", "TestGuild", 3000)
        self.assertTrue(success)
        
        # Check that hunter was added
        hunters = self.leaderboard.current_season.get('hunters', [])
        self.assertEqual(len(hunters), 1)
        
        hunter = hunters[0]
        self.assertEqual(hunter['name'], "TestHunter")
        self.assertEqual(hunter['guild'], "TestGuild")
        self.assertEqual(hunter['kills'], 1)
        self.assertEqual(hunter['total_bounty'], 3000)
    
    def test_add_death(self):
        """Test adding a death"""
        success = self.leaderboard.add_death("TestHunter", "TestGuild")
        self.assertTrue(success)
        
        # Check that hunter was added
        hunters = self.leaderboard.current_season.get('hunters', [])
        self.assertEqual(len(hunters), 1)
        
        hunter = hunters[0]
        self.assertEqual(hunter['name'], "TestHunter")
        self.assertEqual(hunter['guild'], "TestGuild")
        self.assertEqual(hunter['deaths'], 1)
    
    def test_get_or_create_hunter(self):
        """Test getting or creating a hunter"""
        # Create new hunter
        hunter1 = self.leaderboard._get_or_create_hunter("TestHunter", "TestGuild")
        self.assertEqual(hunter1.name, "TestHunter")
        self.assertEqual(hunter1.guild, "TestGuild")
        
        # Get existing hunter
        hunter2 = self.leaderboard._get_or_create_hunter("TestHunter", "TestGuild")
        self.assertEqual(hunter2.name, "TestHunter")
        self.assertEqual(hunter2.guild, "TestGuild")
        
        # Should be the same hunter
        self.assertEqual(hunter1.name, hunter2.name)
    
    def test_update_season_stats(self):
        """Test updating season statistics"""
        # Add some hunters
        self.leaderboard.add_kill("Hunter1", "Guild1", 3000)
        self.leaderboard.add_kill("Hunter1", "Guild1", 3000)
        self.leaderboard.add_death("Hunter1", "Guild1")
        
        self.leaderboard.add_kill("Hunter2", "Guild2", 3000)
        self.leaderboard.add_death("Hunter2", "Guild2")
        
        stats = self.leaderboard.current_season.get('season_stats', {})
        
        self.assertEqual(stats.get('total_kills'), 3)
        self.assertEqual(stats.get('total_deaths'), 2)
        self.assertEqual(stats.get('total_bounty'), 9000)
        self.assertEqual(stats.get('active_hunters'), 2)
    
    def test_get_current_leaderboard(self):
        """Test getting current leaderboard"""
        # Add hunters with different stats
        self.leaderboard.add_kill("Hunter1", "Guild1", 3000)
        self.leaderboard.add_kill("Hunter1", "Guild1", 3000)
        self.leaderboard.add_death("Hunter1", "Guild1")
        
        self.leaderboard.add_kill("Hunter2", "Guild2", 3000)
        self.leaderboard.add_kill("Hunter2", "Guild2", 3000)
        self.leaderboard.add_kill("Hunter2", "Guild2", 3000)
        
        leaderboard = self.leaderboard.get_current_leaderboard()
        
        self.assertEqual(len(leaderboard), 2)
        # Hunter2 should be first (more kills)
        self.assertEqual(leaderboard[0]['name'], "Hunter2")
        self.assertEqual(leaderboard[0]['kills'], 3)
        self.assertEqual(leaderboard[1]['name'], "Hunter1")
        self.assertEqual(leaderboard[1]['kills'], 2)
    
    def test_generate_mvp_highlights(self):
        """Test generating MVP highlights"""
        # Add hunters with different stats
        self.leaderboard.add_kill("MostKills", "Guild1", 3000)
        self.leaderboard.add_kill("MostKills", "Guild1", 3000)
        self.leaderboard.add_kill("MostKills", "Guild1", 3000)
        self.leaderboard.add_death("MostKills", "Guild1")  # Add a death to make K/D ratio 3.0
        
        self.leaderboard.add_kill("BestKD", "Guild2", 3000)
        self.leaderboard.add_kill("BestKD", "Guild2", 3000)
        # No deaths for BestKD - K/D ratio 2.0 (better than MostKills' 3.0)
        
        self.leaderboard.add_kill("HighestBounty", "Guild3", 10000)
        self.leaderboard.add_death("HighestBounty", "Guild3")
        
        mvp_highlights = self.leaderboard._generate_mvp_highlights()
        
        self.assertIn('most_kills', mvp_highlights)
        self.assertIn('best_kd_ratio', mvp_highlights)
        self.assertIn('highest_bounty', mvp_highlights)
        
        self.assertEqual(mvp_highlights['most_kills']['name'], "MostKills")
        self.assertEqual(mvp_highlights['best_kd_ratio']['name'], "BestKD")
        self.assertEqual(mvp_highlights['highest_bounty']['name'], "HighestBounty")
    
    def test_check_season_reset(self):
        """Test checking if season reset is needed"""
        # Mock current date to be reset day
        with patch('scripts.reset_bounty_leaderboard.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.datetime(2025, 1, 1, 12, 0, 0)
            
            # Should need reset on reset day
            needs_reset = self.leaderboard.check_season_reset()
            self.assertTrue(needs_reset)
        
        # Mock current date to not be reset day
        with patch('scripts.reset_bounty_leaderboard.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.datetime(2025, 1, 15, 12, 0, 0)
            
            # Should not need reset on non-reset day
            needs_reset = self.leaderboard.check_season_reset()
            self.assertFalse(needs_reset)
    
    def test_archive_current_season(self):
        """Test archiving current season"""
        # Add some hunters
        self.leaderboard.add_kill("TestHunter", "TestGuild", 3000)
        
        # Archive season
        success = self.leaderboard._archive_current_season()
        self.assertTrue(success)
        
        # Check that archive file was created
        archive_files = list(self.leaderboard.history_dir.glob("*.json"))
        self.assertEqual(len(archive_files), 1)
        
        # Check archive content
        with open(archive_files[0], 'r') as f:
            archive_data = json.load(f)
        
        self.assertIn('season_info', archive_data)
        self.assertIn('hunters', archive_data)
        self.assertIn('season_stats', archive_data)
        self.assertIn('mvp_highlights', archive_data)
    
    def test_get_season_history(self):
        """Test getting season history"""
        # Create a mock archive file
        archive_file = self.leaderboard.history_dir / "2025-01.json"
        archive_data = {
            'season_info': {
                'season': 1,
                'start_date': '2025-01-01',
                'end_date': '2025-01-31',
                'status': 'archived'
            },
            'hunters': [],
            'season_stats': {},
            'mvp_highlights': {}
        }
        
        with open(archive_file, 'w') as f:
            json.dump(archive_data, f)
        
        history = self.leaderboard.get_season_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['filename'], "2025-01.json")
    
    def test_perform_season_reset(self):
        """Test performing season reset"""
        # Add some hunters
        self.leaderboard.add_kill("TestHunter", "TestGuild", 3000)
        
        # Mock check_season_reset to return True
        with patch.object(self.leaderboard, 'check_season_reset', return_value=True):
            success = self.leaderboard.perform_season_reset()
            self.assertTrue(success)
            
            # Check that archive was created
            archive_files = list(self.leaderboard.history_dir.glob("*.json"))
            self.assertEqual(len(archive_files), 1)
            
            # Check that new season was created
            self.assertIn('season', self.leaderboard.current_season)
            self.assertEqual(self.leaderboard.current_season['status'], 'active')


class TestCommandLineInterface(unittest.TestCase):
    """Test command line interface functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "bounty"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    @patch('sys.argv', ['reset_bounty_leaderboard.py', '--check'])
    def test_check_command(self):
        """Test --check command"""
        from scripts.reset_bounty_leaderboard import main
        
        # Mock leaderboard to avoid file system dependencies
        with patch('scripts.reset_bounty_leaderboard.SeasonalBountyLeaderboard') as mock_class:
            mock_leaderboard = MagicMock()
            mock_leaderboard.check_season_reset.return_value = False
            mock_class.return_value = mock_leaderboard
            
            # Should not raise exception
            try:
                main()
            except SystemExit:
                pass
    
    @patch('sys.argv', ['reset_bounty_leaderboard.py', '--add-kill', 'TestHunter', 'TestGuild', '3000'])
    def test_add_kill_command(self):
        """Test --add-kill command"""
        from scripts.reset_bounty_leaderboard import main
        
        with patch('scripts.reset_bounty_leaderboard.SeasonalBountyLeaderboard') as mock_class:
            mock_leaderboard = MagicMock()
            mock_leaderboard.add_kill.return_value = True
            mock_class.return_value = mock_leaderboard
            
            try:
                main()
            except SystemExit:
                pass
            
            mock_leaderboard.add_kill.assert_called_once_with('TestHunter', 'TestGuild', 3000)
    
    @patch('sys.argv', ['reset_bounty_leaderboard.py', '--leaderboard'])
    def test_leaderboard_command(self):
        """Test --leaderboard command"""
        from scripts.reset_bounty_leaderboard import main
        
        with patch('scripts.reset_bounty_leaderboard.SeasonalBountyLeaderboard') as mock_class:
            mock_leaderboard = MagicMock()
            mock_leaderboard.get_current_leaderboard.return_value = [
                {'rank': 1, 'name': 'TestHunter', 'guild': 'TestGuild', 'kills': 5, 'deaths': 1, 'kd_ratio': 5.0, 'total_bounty': 15000}
            ]
            mock_class.return_value = mock_leaderboard
            
            try:
                main()
            except SystemExit:
                pass


class TestDataPersistence(unittest.TestCase):
    """Test data persistence functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "bounty"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_save_and_load_current_season(self):
        """Test saving and loading current season"""
        leaderboard = SeasonalBountyLeaderboard(str(self.data_dir))
        
        # Add some data
        leaderboard.add_kill("TestHunter", "TestGuild", 3000)
        
        # Create new leaderboard instance to test loading
        new_leaderboard = SeasonalBountyLeaderboard(str(self.data_dir))
        
        # Check that data was loaded correctly
        hunters = new_leaderboard.current_season.get('hunters', [])
        self.assertEqual(len(hunters), 1)
        self.assertEqual(hunters[0]['name'], "TestHunter")
    
    def test_archive_file_format(self):
        """Test archive file format"""
        leaderboard = SeasonalBountyLeaderboard(str(self.data_dir))
        
        # Add some data
        leaderboard.add_kill("TestHunter", "TestGuild", 3000)
        
        # Archive season
        leaderboard._archive_current_season()
        
        # Check archive file
        archive_files = list(leaderboard.history_dir.glob("*.json"))
        self.assertEqual(len(archive_files), 1)
        
        with open(archive_files[0], 'r') as f:
            archive_data = json.load(f)
        
        # Check required fields
        required_fields = ['season_info', 'hunters', 'season_stats', 'mvp_highlights']
        for field in required_fields:
            self.assertIn(field, archive_data)
        
        # Check season_info structure
        season_info = archive_data['season_info']
        self.assertIn('season', season_info)
        self.assertIn('start_date', season_info)
        self.assertIn('end_date', season_info)
        self.assertEqual(season_info['status'], 'archived')


class TestErrorHandling(unittest.TestCase):
    """Test error handling functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "bounty"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_invalid_bounty_value(self):
        """Test handling invalid bounty value"""
        leaderboard = SeasonalBountyLeaderboard(str(self.data_dir))
        
        # Should handle invalid bounty gracefully
        success = leaderboard.add_kill("TestHunter", "TestGuild", "invalid")
        self.assertFalse(success)
    
    def test_missing_data_directory(self):
        """Test handling missing data directory"""
        # Should create directory if it doesn't exist
        non_existent_dir = Path(self.test_dir) / "non_existent"
        leaderboard = SeasonalBountyLeaderboard(str(non_existent_dir))
        
        self.assertTrue(non_existent_dir.exists())
        self.assertTrue((non_existent_dir / "history").exists())
    
    def test_corrupted_season_file(self):
        """Test handling corrupted season file"""
        # Create corrupted season file
        season_file = self.data_dir / "current_season.json"
        with open(season_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle corrupted file gracefully
        leaderboard = SeasonalBountyLeaderboard(str(self.data_dir))
        self.assertIsNotNone(leaderboard.current_season)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 