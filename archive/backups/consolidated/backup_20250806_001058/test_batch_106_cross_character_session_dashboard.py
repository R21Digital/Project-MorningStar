#!/usr/bin/env python3
"""
Tests for Batch 106 - Cross-Character Session Dashboard

This test suite covers:
- Authentication and authorization
- Session data loading and aggregation
- Cross-character summary generation
- Export functionality
- Sync management
- Dashboard integration

Usage:
    python -m pytest test_batch_106_cross_character_session_dashboard.py -v
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

from core.cross_character_session_dashboard import (
    CrossCharacterSessionDashboard,
    CrossCharacterSessionSummary,
    CharacterSessionData,
    SessionSyncStatus
)
from core.steam_discord_bridge import AuthStatus


class TestCrossCharacterSessionDashboard:
    """Test suite for CrossCharacterSessionDashboard."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_dir = tempfile.mkdtemp()
        sessions_dir = Path(temp_dir) / "sessions"
        multi_character_dir = Path(temp_dir) / "multi_character"
        
        sessions_dir.mkdir(parents=True)
        multi_character_dir.mkdir(parents=True)
        
        yield {
            'temp_dir': temp_dir,
            'sessions_dir': sessions_dir,
            'multi_character_dir': multi_character_dir
        }
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_session_data(self):
        """Create sample session data for testing."""
        return {
            "session_id": "test_session_001",
            "character_name": "TestCharacter",
            "server": "TestServer",
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "duration_minutes": 120.0,
            "mode": "medic",
            "summary": {
                "total_xp_gained": 15000,
                "total_credits_earned": 50000,
                "total_quests_completed": 5,
                "total_locations_visited": 8,
                "total_player_encounters": 3,
                "total_communication_events": 2,
                "total_afk_time_minutes": 10.0,
                "total_stuck_events": 1,
                "active_time_minutes": 110.0,
                "credits_per_hour": 25000.0,
                "xp_per_hour": 7500.0
            },
            "events": [
                {
                    "event_type": "whisper",
                    "timestamp": datetime.now().isoformat(),
                    "sender": "Player1",
                    "message": "Hello there!"
                },
                {
                    "event_type": "quest_complete",
                    "timestamp": datetime.now().isoformat(),
                    "quest_name": "Test Quest",
                    "xp_reward": 3000
                }
            ]
        }
    
    @pytest.fixture
    def sample_multi_character_data(self):
        """Create sample multi-character data for testing."""
        return {
            "accounts": [
                {
                    "account_id": "acc_001",
                    "discord_id": "123456789",
                    "account_name": "TestAccount",
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            ],
            "characters": [
                {
                    "character_id": "char_001",
                    "account_id": "acc_001",
                    "character_name": "TestCharacter",
                    "server": "TestServer",
                    "profession": "Medic",
                    "level": 45,
                    "is_main": True,
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "character_id": "char_002",
                    "account_id": "acc_001",
                    "character_name": "TestCharacter2",
                    "server": "TestServer",
                    "profession": "Rifleman",
                    "level": 32,
                    "is_main": False,
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            ],
            "sync_settings": {
                "123456789": {
                    "session_sync_enabled": True,
                    "enabled_at": datetime.now().isoformat()
                }
            }
        }
    
    @pytest.fixture
    def dashboard(self, temp_dirs):
        """Create dashboard instance with temporary directories."""
        return CrossCharacterSessionDashboard(
            sessions_dir=str(temp_dirs['sessions_dir']),
            multi_character_dir=str(temp_dirs['multi_character_dir'])
        )
    
    def test_dashboard_initialization(self, dashboard):
        """Test dashboard initialization."""
        assert dashboard is not None
        assert dashboard.sessions_dir.exists()
        assert dashboard.multi_character_dir.exists()
    
    def test_check_discord_auth_no_bridge(self, dashboard):
        """Test Discord auth check when no identity bridge is available."""
        result = dashboard.check_discord_auth("123456789")
        assert result is False
    
    @patch('core.cross_character_session_dashboard.IdentityBridge')
    def test_check_discord_auth_with_bridge(self, mock_bridge_class, dashboard):
        """Test Discord auth check with identity bridge."""
        # Mock the identity bridge
        mock_bridge = Mock()
        mock_identity = Mock()
        mock_identity.auth_status = AuthStatus.AUTHENTICATED
        mock_bridge.get_linked_identity.return_value = mock_identity
        mock_bridge_class.return_value = mock_bridge
        
        dashboard.identity_bridge = mock_bridge
        
        result = dashboard.check_discord_auth("123456789")
        assert result is True
        
        # Test with non-authenticated user
        mock_identity.auth_status = AuthStatus.PENDING
        result = dashboard.check_discord_auth("123456789")
        assert result is False
    
    def test_check_session_sync_enabled_no_file(self, dashboard):
        """Test session sync check when no sync file exists."""
        result = dashboard.check_session_sync_enabled("123456789")
        assert result is False
    
    def test_check_session_sync_enabled_with_file(self, dashboard, sample_multi_character_data):
        """Test session sync check with sync file."""
        # Create sync settings file
        sync_file = dashboard.multi_character_dir / "sync_settings.json"
        with open(sync_file, 'w', encoding='utf-8') as f:
            json.dump(sample_multi_character_data["sync_settings"], f)
        
        result = dashboard.check_session_sync_enabled("123456789")
        assert result is True
        
        # Test with non-existent user
        result = dashboard.check_session_sync_enabled("999999999")
        assert result is False
    
    def test_get_user_characters_no_files(self, dashboard):
        """Test getting user characters when no files exist."""
        characters = dashboard.get_user_characters("123456789")
        assert characters == []
    
    def test_get_user_characters_with_files(self, dashboard, sample_multi_character_data):
        """Test getting user characters with data files."""
        # Create accounts file
        accounts_file = dashboard.multi_character_dir / "accounts.json"
        with open(accounts_file, 'w', encoding='utf-8') as f:
            json.dump(sample_multi_character_data["accounts"], f)
        
        # Create characters file
        characters_file = dashboard.multi_character_dir / "characters.json"
        with open(characters_file, 'w', encoding='utf-8') as f:
            json.dump(sample_multi_character_data["characters"], f)
        
        characters = dashboard.get_user_characters("123456789")
        assert len(characters) == 2
        assert characters[0]["character_name"] == "TestCharacter"
        assert characters[1]["character_name"] == "TestCharacter2"
    
    def test_load_character_sessions_no_sessions(self, dashboard):
        """Test loading character sessions when no sessions exist."""
        sessions = dashboard.load_character_sessions("TestCharacter", "TestServer")
        assert sessions == []
    
    def test_load_character_sessions_with_sessions(self, dashboard, sample_session_data):
        """Test loading character sessions with session data."""
        # Create session file
        session_file = dashboard.sessions_dir / "session_001.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(sample_session_data, f)
        
        sessions = dashboard.load_character_sessions("TestCharacter", "TestServer")
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "test_session_001"
        assert sessions[0]["character_name"] == "TestCharacter"
    
    def test_calculate_character_stats_empty_sessions(self, dashboard):
        """Test calculating character stats with empty sessions."""
        stats = dashboard.calculate_character_stats([])
        assert stats.character_name == ""
        assert stats.server == ""
        assert stats.total_xp_gained == 0
        assert stats.total_credits_earned == 0
        assert stats.total_quests_completed == 0
    
    def test_calculate_character_stats_with_sessions(self, dashboard, sample_session_data):
        """Test calculating character stats with session data."""
        sessions = [sample_session_data]
        stats = dashboard.calculate_character_stats(sessions)
        
        assert stats.character_name == "TestCharacter"
        assert stats.server == "TestServer"
        assert stats.total_xp_gained == 15000
        assert stats.total_credits_earned == 50000
        assert stats.total_quests_completed == 5
        assert stats.total_locations_visited == 8
        assert stats.total_whisper_encounters == 1  # One whisper event
        assert stats.total_duration_hours == 2.0
        assert stats.mode_history == {"medic": 1}
    
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.check_discord_auth')
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.check_session_sync_enabled')
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.get_user_characters')
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.load_character_sessions')
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.calculate_character_stats')
    def test_get_cross_character_summary_success(self, mock_calc_stats, mock_load_sessions, 
                                                mock_get_chars, mock_sync_enabled, mock_auth, 
                                                dashboard, sample_session_data):
        """Test successful cross-character summary generation."""
        # Mock all dependencies
        mock_auth.return_value = True
        mock_sync_enabled.return_value = True
        mock_get_chars.return_value = [
            {"character_name": "TestCharacter", "server": "TestServer"}
        ]
        mock_load_sessions.return_value = [sample_session_data]
        
        mock_stats = CharacterSessionData(
            character_name="TestCharacter",
            server="TestServer",
            sessions=[sample_session_data],
            total_xp_gained=15000,
            total_credits_earned=50000,
            total_quests_completed=5,
            total_locations_visited=8,
            total_whisper_encounters=1,
            total_duration_hours=2.0,
            mode_history={"medic": 1},
            last_session=sample_session_data
        )
        mock_calc_stats.return_value = mock_stats
        
        summary = dashboard.get_cross_character_summary("123456789")
        
        assert summary is not None
        assert summary.total_sessions == 1
        assert summary.total_xp_gained == 15000
        assert summary.total_credits_earned == 50000
        assert summary.total_quests_completed == 5
        assert summary.characters_played == ["TestCharacter"]
        assert summary.mode_history == {"medic": 1}
    
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.check_discord_auth')
    def test_get_cross_character_summary_no_auth(self, mock_auth, dashboard):
        """Test cross-character summary when user is not authenticated."""
        mock_auth.return_value = False
        
        summary = dashboard.get_cross_character_summary("123456789")
        assert summary is None
    
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.check_discord_auth')
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.check_session_sync_enabled')
    def test_get_cross_character_summary_no_sync(self, mock_sync_enabled, mock_auth, dashboard):
        """Test cross-character summary when sync is not enabled."""
        mock_auth.return_value = True
        mock_sync_enabled.return_value = False
        
        summary = dashboard.get_cross_character_summary("123456789")
        assert summary is None
    
    def test_enable_session_sync(self, dashboard):
        """Test enabling session sync."""
        result = dashboard.enable_session_sync("123456789")
        assert result is True
        
        # Verify sync is enabled
        sync_enabled = dashboard.check_session_sync_enabled("123456789")
        assert sync_enabled is True
    
    def test_disable_session_sync(self, dashboard):
        """Test disabling session sync."""
        # First enable sync
        dashboard.enable_session_sync("123456789")
        
        # Then disable it
        result = dashboard.disable_session_sync("123456789")
        assert result is True
        
        # Verify sync is disabled
        sync_enabled = dashboard.check_session_sync_enabled("123456789")
        assert sync_enabled is False
    
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.get_cross_character_summary')
    def test_export_summary_json(self, mock_get_summary, dashboard):
        """Test JSON export functionality."""
        # Create mock summary
        mock_summary = CrossCharacterSessionSummary(
            total_sessions=1,
            total_xp_gained=15000,
            total_credits_earned=50000,
            total_quests_completed=5,
            total_locations_visited=8,
            total_whisper_encounters=1,
            total_duration_hours=2.0,
            average_xp_per_hour=7500.0,
            average_credits_per_hour=25000.0,
            characters_played=["TestCharacter"],
            mode_history={"medic": 1},
            recent_activity=[]
        )
        mock_get_summary.return_value = mock_summary
        
        export_data = dashboard.export_summary("123456789", "json")
        assert export_data is not None
        
        # Parse JSON to verify structure
        parsed_data = json.loads(export_data)
        assert parsed_data["total_sessions"] == 1
        assert parsed_data["total_xp_gained"] == 15000
        assert parsed_data["characters_played"] == ["TestCharacter"]
    
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.get_cross_character_summary')
    def test_export_summary_csv(self, mock_get_summary, dashboard):
        """Test CSV export functionality."""
        # Create mock summary
        mock_summary = CrossCharacterSessionSummary(
            total_sessions=1,
            total_xp_gained=15000,
            total_credits_earned=50000,
            total_quests_completed=5,
            total_locations_visited=8,
            total_whisper_encounters=1,
            total_duration_hours=2.0,
            average_xp_per_hour=7500.0,
            average_credits_per_hour=25000.0,
            characters_played=["TestCharacter"],
            mode_history={"medic": 1},
            recent_activity=[]
        )
        mock_get_summary.return_value = mock_summary
        
        export_data = dashboard.export_summary("123456789", "csv")
        assert export_data is not None
        
        # Verify CSV structure
        lines = export_data.split('\n')
        assert len(lines) >= 10  # Should have multiple lines
        assert "Metric,Value" in lines[0]
        assert "Total Sessions,1" in lines[1]
        assert "Total XP Gained,15000" in lines[2]
    
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.get_cross_character_summary')
    def test_export_summary_invalid_format(self, mock_get_summary, dashboard):
        """Test export with invalid format."""
        mock_get_summary.return_value = Mock()
        
        export_data = dashboard.export_summary("123456789", "invalid")
        assert export_data is None
    
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.get_cross_character_summary')
    def test_export_summary_no_data(self, mock_get_summary, dashboard):
        """Test export when no summary data is available."""
        mock_get_summary.return_value = None
        
        export_data = dashboard.export_summary("123456789", "json")
        assert export_data is None


class TestCrossCharacterSessionSummary:
    """Test suite for CrossCharacterSessionSummary dataclass."""
    
    def test_summary_creation(self):
        """Test creating a CrossCharacterSessionSummary instance."""
        summary = CrossCharacterSessionSummary(
            total_sessions=5,
            total_xp_gained=50000,
            total_credits_earned=150000,
            total_quests_completed=25,
            total_locations_visited=40,
            total_whisper_encounters=10,
            total_duration_hours=10.0,
            average_xp_per_hour=5000.0,
            average_credits_per_hour=15000.0,
            characters_played=["Char1", "Char2"],
            mode_history={"medic": 3, "quest": 2},
            recent_activity=[]
        )
        
        assert summary.total_sessions == 5
        assert summary.total_xp_gained == 50000
        assert summary.total_credits_earned == 150000
        assert summary.characters_played == ["Char1", "Char2"]
        assert summary.mode_history == {"medic": 3, "quest": 2}


class TestCharacterSessionData:
    """Test suite for CharacterSessionData dataclass."""
    
    def test_character_data_creation(self):
        """Test creating a CharacterSessionData instance."""
        char_data = CharacterSessionData(
            character_name="TestChar",
            server="TestServer",
            sessions=[],
            total_xp_gained=25000,
            total_credits_earned=75000,
            total_quests_completed=15,
            total_locations_visited=20,
            total_whisper_encounters=5,
            total_duration_hours=5.0,
            mode_history={"medic": 2, "quest": 1},
            last_session=None
        )
        
        assert char_data.character_name == "TestChar"
        assert char_data.server == "TestServer"
        assert char_data.total_xp_gained == 25000
        assert char_data.total_credits_earned == 75000
        assert char_data.mode_history == {"medic": 2, "quest": 1}


class TestSessionSyncStatus:
    """Test suite for SessionSyncStatus enum."""
    
    def test_enum_values(self):
        """Test SessionSyncStatus enum values."""
        assert SessionSyncStatus.ENABLED == "enabled"
        assert SessionSyncStatus.DISABLED == "disabled"
        assert SessionSyncStatus.PENDING == "pending"


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.fixture
    def complete_setup(self, temp_dirs):
        """Set up complete test environment."""
        dashboard = CrossCharacterSessionDashboard(
            sessions_dir=str(temp_dirs['sessions_dir']),
            multi_character_dir=str(temp_dirs['multi_character_dir'])
        )
        
        # Create sample data
        sample_data = {
            "accounts": [{"account_id": "acc_001", "discord_id": "123456789"}],
            "characters": [
                {"character_id": "char_001", "account_id": "acc_001", 
                 "character_name": "TestChar", "server": "TestServer"}
            ],
            "sync_settings": {"123456789": {"session_sync_enabled": True}},
            "sessions": [
                {
                    "session_id": "session_001",
                    "character_name": "TestChar",
                    "server": "TestServer",
                    "mode": "medic",
                    "summary": {"total_xp_gained": 15000, "total_credits_earned": 50000}
                }
            ]
        }
        
        # Create files
        accounts_file = dashboard.multi_character_dir / "accounts.json"
        with open(accounts_file, 'w') as f:
            json.dump(sample_data["accounts"], f)
        
        characters_file = dashboard.multi_character_dir / "characters.json"
        with open(characters_file, 'w') as f:
            json.dump(sample_data["characters"], f)
        
        sync_file = dashboard.multi_character_dir / "sync_settings.json"
        with open(sync_file, 'w') as f:
            json.dump(sample_data["sync_settings"], f)
        
        session_file = dashboard.sessions_dir / "session_001.json"
        with open(session_file, 'w') as f:
            json.dump(sample_data["sessions"][0], f)
        
        return dashboard, sample_data
    
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.check_discord_auth')
    @patch('core.cross_character_session_dashboard.CrossCharacterSessionDashboard.check_session_sync_enabled')
    def test_complete_workflow(self, mock_sync_enabled, mock_auth, complete_setup):
        """Test the complete workflow from data loading to summary generation."""
        dashboard, sample_data = complete_setup
        
        # Mock authentication
        mock_auth.return_value = True
        mock_sync_enabled.return_value = True
        
        # Test the complete workflow
        characters = dashboard.get_user_characters("123456789")
        assert len(characters) == 1
        assert characters[0]["character_name"] == "TestChar"
        
        sessions = dashboard.load_character_sessions("TestChar", "TestServer")
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "session_001"
        
        char_stats = dashboard.calculate_character_stats(sessions)
        assert char_stats.character_name == "TestChar"
        assert char_stats.total_xp_gained == 15000
        assert char_stats.total_credits_earned == 50000
        
        summary = dashboard.get_cross_character_summary("123456789")
        assert summary is not None
        assert summary.total_sessions == 1
        assert summary.total_xp_gained == 15000
        assert summary.characters_played == ["TestChar"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 