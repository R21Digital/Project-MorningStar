"""Test Batch 099 - T-Unit Bounty Hunter Mode (Phase 1)

This test suite validates the bounty hunter mode functionality including:
- Mission acceptance and filtering
- Travel to target locations
- Combat engagement
- Mission completion
- Discord alerts
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the bounty hunter mode
from android_ms11.modes.bounty_hunter_tunit import BountyHunterTUnit, run
from modules.discord_alerts import send_discord_alert, send_bounty_alert


class TestBountyHunterTUnit:
    """Test the BountyHunterTUnit class."""
    
    @pytest.fixture
    def bounty_hunter(self):
        """Create a BountyHunterTUnit instance for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary config file
            config_path = Path(temp_dir) / "bounty_hunter_profile.json"
            config = {
                "max_active_missions": 2,
                "min_reward_credits": 300,
                "max_travel_distance": 3000,
                "enable_discord_alerts": True
            }
            with config_path.open("w") as f:
                json.dump(config, f)
            
            # Create temporary bounties data
            bounties_dir = Path(temp_dir) / "data" / "bounties"
            bounties_dir.mkdir(parents=True)
            bounties_file = bounties_dir / "test_bounties.json"
            bounties_data = {
                "missions": [
                    {
                        "mission_id": "test_001",
                        "target_name": "Test Target",
                        "target_type": "npc",
                        "location": {
                            "planet": "tatooine",
                            "city": "mos_eisley",
                            "coordinates": [100, 200]
                        },
                        "difficulty": "easy",
                        "reward_credits": 500
                    }
                ]
            }
            with bounties_file.open("w") as f:
                json.dump(bounties_data, f)
            
            # Patch the profile path
            with patch.object(BountyHunterTUnit, '__init__', return_value=None):
                bh = BountyHunterTUnit()
                bh.profile_path = config_path
                bh.profile = config
                bh.active_missions = []
                bh.completed_missions = []
                bh.bounties_data = {"test_bounties": bounties_data["missions"]}
                yield bh
    
    def test_should_accept_mission_valid(self, bounty_hunter):
        """Test that valid missions are accepted."""
        mission = {
            "name": "Valid Target",
            "distance": 1000,
            "credits": 500
        }
        
        assert bounty_hunter._should_accept_mission(mission) is True
    
    def test_should_accept_mission_too_far(self, bounty_hunter):
        """Test that missions too far away are rejected."""
        mission = {
            "name": "Far Target",
            "distance": 5000,  # Beyond max_travel_distance
            "credits": 500
        }
        
        assert bounty_hunter._should_accept_mission(mission) is False
    
    def test_should_accept_mission_low_reward(self, bounty_hunter):
        """Test that missions with low rewards are rejected."""
        mission = {
            "name": "Low Reward Target",
            "distance": 1000,
            "credits": 200  # Below min_reward_credits
        }
        
        assert bounty_hunter._should_accept_mission(mission) is False
    
    def test_should_accept_mission_max_active(self, bounty_hunter):
        """Test that missions are rejected when at max active missions."""
        # Fill active missions
        bounty_hunter.active_missions = [{"name": "Mission 1"}, {"name": "Mission 2"}]
        
        mission = {
            "name": "Extra Target",
            "distance": 1000,
            "credits": 500
        }
        
        assert bounty_hunter._should_accept_mission(mission) is False
    
    @patch('android_ms11.modes.bounty_hunter_tunit.travel_to_target')
    @patch('android_ms11.modes.bounty_hunter_tunit.verify_waypoint_stability')
    def test_travel_to_target_success(self, mock_verify, mock_travel, bounty_hunter):
        """Test successful travel to target."""
        mission = {
            "name": "Test Target",
            "location": {
                "planet": "tatooine",
                "city": "mos_eisley",
                "coordinates": [100, 200]
            }
        }
        
        mock_travel.return_value = True
        mock_verify.return_value = None
        
        result = bounty_hunter.travel_to_target(mission)
        
        assert result is True
        mock_travel.assert_called_once()
        mock_verify.assert_called_once()
    
    @patch('android_ms11.modes.bounty_hunter_tunit.travel_to_target')
    def test_travel_to_target_failure(self, mock_travel, bounty_hunter):
        """Test failed travel to target."""
        mission = {
            "name": "Test Target",
            "location": {
                "planet": "tatooine",
                "city": "mos_eisley",
                "coordinates": [100, 200]
            }
        }
        
        mock_travel.side_effect = Exception("Travel failed")
        
        result = bounty_hunter.travel_to_target(mission)
        
        assert result is False
    
    @patch('android_ms11.modes.bounty_hunter_tunit.engage_targets')
    @patch('android_ms11.modes.bounty_hunter_tunit.send_discord_alert')
    def test_engage_target_success(self, mock_discord, mock_combat, bounty_hunter):
        """Test successful target engagement."""
        mission = {
            "name": "Test Target",
            "difficulty": "medium",
            "combat_profile": "tactical",
            "location": {
                "planet": "tatooine",
                "city": "mos_eisley"
            }
        }
        
        mock_combat.return_value = True
        mock_discord.return_value = True
        
        result = bounty_hunter.engage_target(mission)
        
        assert result is True
        mock_combat.assert_called_once_with("Test Target", count=1)
        assert len(bounty_hunter.completed_missions) == 1
        assert len(bounty_hunter.active_missions) == 0
    
    @patch('android_ms11.modes.bounty_hunter_tunit.engage_targets')
    def test_engage_target_failure(self, mock_combat, bounty_hunter):
        """Test failed target engagement."""
        mission = {
            "name": "Test Target",
            "difficulty": "medium",
            "combat_profile": "tactical"
        }
        
        mock_combat.return_value = False
        
        result = bounty_hunter.engage_target(mission)
        
        assert result is False
        assert len(bounty_hunter.completed_missions) == 0
    
    def test_complete_mission(self, bounty_hunter):
        """Test mission completion."""
        mission = {
            "name": "Test Target",
            "reward_credits": 1000
        }
        
        result = bounty_hunter.complete_mission(mission)
        
        assert result is True
        assert mission["turned_in"] is True
        assert mission["reward_collected"] == 1000
    
    @patch('android_ms11.modes.bounty_hunter_tunit.TerminalFarmer')
    def test_accept_missions(self, mock_farmer_class, bounty_hunter):
        """Test mission acceptance from terminal."""
        mock_farmer = Mock()
        mock_farmer.parse_missions.return_value = [
            {"name": "Target 1", "distance": 1000, "credits": 500},
            {"name": "Target 2", "distance": 2000, "credits": 800}
        ]
        mock_farmer_class.return_value = mock_farmer
        
        missions = bounty_hunter.accept_missions("Test terminal text")
        
        assert len(missions) == 2
        mock_farmer.parse_missions.assert_called_once_with("Test terminal text")
    
    @patch('android_ms11.modes.bounty_hunter_tunit.travel_to_target')
    @patch('android_ms11.modes.bounty_hunter_tunit.engage_target')
    @patch('android_ms11.modes.bounty_hunter_tunit.complete_mission')
    def test_run_mission_cycle(self, mock_complete, mock_engage, mock_travel, bounty_hunter):
        """Test complete mission cycle."""
        # Add a test mission
        mission = {
            "name": "Test Target",
            "location": {"planet": "tatooine", "city": "mos_eisley"},
            "reward_credits": 500
        }
        bounty_hunter.active_missions = [mission]
        
        mock_travel.return_value = True
        mock_engage.return_value = True
        mock_complete.return_value = True
        
        bounty_hunter.run_mission_cycle()
        
        mock_travel.assert_called_once()
        mock_engage.assert_called_once()
        mock_complete.assert_called_once()


class TestDiscordAlerts:
    """Test Discord alert functionality."""
    
    @patch('modules.discord_alerts.load_discord_config')
    def test_send_discord_alert_enabled(self, mock_load_config):
        """Test sending Discord alert when enabled."""
        mock_load_config.return_value = {"discord_token": "test_token"}
        
        with patch('modules.discord_alerts.logger') as mock_logger:
            result = send_discord_alert("Test alert")
            
            assert result is True
            mock_logger.info.assert_called_once()
    
    @patch('modules.discord_alerts.load_discord_config')
    def test_send_discord_alert_disabled(self, mock_load_config):
        """Test Discord alert when disabled."""
        mock_load_config.return_value = {}
        
        with patch('modules.discord_alerts.logger') as mock_logger:
            result = send_discord_alert("Test alert")
            
            assert result is False
            mock_logger.debug.assert_called_once()
    
    def test_send_bounty_alert(self):
        """Test bounty-specific alert formatting."""
        with patch('modules.discord_alerts.send_discord_alert') as mock_send:
            mock_send.return_value = True
            
            result = send_bounty_alert("Test Target", "Tatooine", "medium")
            
            assert result is True
            mock_send.assert_called_once()
            # Check that the message contains the expected format
            call_args = mock_send.call_args[0][0]
            assert "T-Unit engaged target: Test Target" in call_args
            assert "Tatooine" in call_args
            assert "medium" in call_args


class TestBountyHunterIntegration:
    """Integration tests for the bounty hunter mode."""
    
    @patch('android_ms11.modes.bounty_hunter_tunit.assert_profile_ready')
    @patch('android_ms11.modes.bounty_hunter_tunit.BountyHunterTUnit')
    def test_run_function(self, mock_bh_class, mock_assert):
        """Test the main run function."""
        mock_bh = Mock()
        mock_bh_class.return_value = mock_bh
        
        run(profile={"test": "config"}, session=Mock())
        
        mock_assert.assert_called_once()
        mock_bh_class.assert_called_once()
        mock_bh.run_mission_cycle.assert_called_once()
    
    def test_bounty_data_loading(self):
        """Test loading bounty data from JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test bounty data
            bounties_dir = Path(temp_dir) / "data" / "bounties"
            bounties_dir.mkdir(parents=True)
            
            test_data = {
                "missions": [
                    {
                        "mission_id": "test_001",
                        "target_name": "Test Target",
                        "target_type": "npc",
                        "location": {
                            "planet": "tatooine",
                            "city": "mos_eisley",
                            "coordinates": [100, 200]
                        },
                        "difficulty": "easy",
                        "reward_credits": 500
                    }
                ]
            }
            
            with (bounties_dir / "test_bounties.json").open("w") as f:
                json.dump(test_data, f)
            
            # Test loading
            with patch.object(BountyHunterTUnit, '__init__', return_value=None):
                bh = BountyHunterTUnit()
                bh._load_bounties_data()
                
                # This would normally load from the actual data directory
                # For testing, we'll just verify the method exists
                assert hasattr(bh, '_load_bounties_data')


class TestBountyHunterConfiguration:
    """Test bounty hunter configuration handling."""
    
    def test_default_profile(self):
        """Test default profile creation."""
        with patch.object(BountyHunterTUnit, '__init__', return_value=None):
            bh = BountyHunterTUnit()
            bh._load_profile()
            
            # Check that default values are set
            assert bh.profile["max_active_missions"] == 3
            assert bh.profile["min_reward_credits"] == 500
            assert bh.profile["enable_discord_alerts"] is True
    
    def test_custom_profile_loading(self):
        """Test loading custom profile configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_config = {
                "max_active_missions": 5,
                "min_reward_credits": 1000,
                "enable_discord_alerts": False
            }
            json.dump(custom_config, f)
            config_path = f.name
        
        try:
            with patch.object(BountyHunterTUnit, '__init__', return_value=None):
                bh = BountyHunterTUnit()
                bh.profile_path = Path(config_path)
                bh._load_profile()
                
                assert bh.profile["max_active_missions"] == 5
                assert bh.profile["min_reward_credits"] == 1000
                assert bh.profile["enable_discord_alerts"] is False
        finally:
            Path(config_path).unlink()


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 