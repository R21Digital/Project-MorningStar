#!/usr/bin/env python3
"""
Test Suite for Batch 180 - RLS Farming Mode

This test suite covers:
- Target selection and cooldown management
- Travel and group management
- Loot tracking and priority system
- Statistics and reporting
- Configuration loading and validation
- Error handling and edge cases

Run with: pytest test_batch_180_rls_farming.py -v
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional

# Import the RLS farming mode
try:
    from core.modes.rare_loot_farm import RLSFarmingMode, run_rls_farming_mode
except ImportError as e:
    pytest.skip(f"RLS farming mode not available: {e}", allow_module_level=True)


class TestRLSFarmingMode:
    """Test suite for RLS Farming Mode."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory for testing."""
        temp_dir = tempfile.mkdtemp()
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir()
        
        # Create test loot targets config
        test_config = {
            "targets": [
                {
                    "id": "ig88",
                    "name": "IG-88",
                    "planet": "Lok",
                    "zone": "Imperial Research Facility",
                    "level": 90,
                    "cooldown_hours": 24,
                    "loot_priority": ["IG-88's Head", "Assassin Droid Parts"],
                    "notes": "Legendary bounty hunter droid",
                    "coordinates": [500, 300],
                    "spawn_conditions": "any_time",
                    "rarity": "legendary"
                },
                {
                    "id": "crystal_snake",
                    "name": "Crystal Snake",
                    "planet": "Dantooine",
                    "zone": "Force Crystal Cave",
                    "level": 85,
                    "cooldown_hours": 12,
                    "loot_priority": ["Crystal Snake Necklace", "Force Crystals"],
                    "notes": "Crystal-infused serpent",
                    "coordinates": [300, 250],
                    "spawn_conditions": "any_time",
                    "rarity": "epic"
                }
            ],
            "settings": {
                "farming_interval": 30,
                "discord_alerts_enabled": True,
                "cooldown_tracking": True
            }
        }
        
        with open(config_dir / "loot_targets.json", 'w') as f:
            json.dump(test_config, f)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        data_dir = Path(temp_dir) / "data" / "rls_farming_sessions"
        data_dir.mkdir(parents=True)
        
        # Create test session data
        test_sessions = [
            {
                "target": {
                    "id": "ig88",
                    "name": "IG-88",
                    "planet": "Lok",
                    "zone": "Imperial Research Facility"
                },
                "start_time": "2025-01-04T10:00:00",
                "end_time": "2025-01-04T10:15:00",
                "duration_seconds": 900,
                "solo_mode": False,
                "success": True,
                "loot_log": [
                    {
                        "name": "IG-88's Head",
                        "target": "IG-88",
                        "rarity": "legendary",
                        "value": 15000,
                        "is_rare": True,
                        "is_priority": True,
                        "timestamp": "2025-01-04T10:10:00",
                        "location": "Lok - Imperial Research Facility"
                    }
                ],
                "combat_log": []
            }
        ]
        
        for i, session in enumerate(test_sessions):
            with open(data_dir / f"test_session_{i+1}.json", 'w') as f:
                json.dump(session, f)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def farming_mode(self, temp_config_dir, temp_data_dir):
        """Create RLS farming mode instance for testing."""
        with patch('core.modes.rare_loot_farm.Path') as mock_path:
            # Mock config path
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.__truediv__.return_value = Path(temp_config_dir) / "config" / "loot_targets.json"
            
            # Mock data path
            mock_path.return_value.glob.return_value = [
                Path(temp_data_dir) / "data" / "rls_farming_sessions" / "test_session_1.json"
            ]
            
            mode = RLSFarmingMode()
            return mode
    
    def test_initialization(self, farming_mode):
        """Test RLS farming mode initialization."""
        assert farming_mode is not None
        assert hasattr(farming_mode, 'rls_targets')
        assert hasattr(farming_mode, 'cooldown_tracker')
        assert hasattr(farming_mode, 'rare_drops_found')
        assert len(farming_mode.rls_targets) > 0
    
    def test_load_loot_targets(self, farming_mode):
        """Test loading loot targets configuration."""
        targets = farming_mode.loot_targets
        assert "targets" in targets
        assert "settings" in targets
        assert len(targets["targets"]) > 0
    
    def test_load_farming_sessions(self, farming_mode):
        """Test loading farming sessions data."""
        sessions = farming_mode.farming_sessions
        assert isinstance(sessions, list)
        assert len(sessions) > 0
    
    def test_check_cooldowns(self, farming_mode):
        """Test cooldown checking functionality."""
        cooldown_status = farming_mode.check_cooldowns()
        
        assert isinstance(cooldown_status, dict)
        assert len(cooldown_status) > 0
        
        # Check structure of cooldown status
        for target_id, status in cooldown_status.items():
            assert "available" in status
            assert "hours_remaining" in status
            assert isinstance(status["available"], bool)
            assert isinstance(status["hours_remaining"], (int, float))
    
    def test_select_farming_target(self, farming_mode):
        """Test target selection functionality."""
        # Test with no priority target
        target = farming_mode.select_farming_target()
        if target:
            assert "id" in target
            assert "name" in target
            assert "planet" in target
            assert "zone" in target
            assert "level" in target
        
        # Test with specific priority target
        target = farming_mode.select_farming_target("ig88")
        if target:
            assert target["id"] == "ig88"
            assert target["name"] == "IG-88"
    
    def test_select_farming_target_no_available(self, farming_mode):
        """Test target selection when no targets are available."""
        # Mock all targets on cooldown
        farming_mode.cooldown_tracker = {
            "ig88": datetime.now(),
            "crystal_snake": datetime.now()
        }
        
        target = farming_mode.select_farming_target()
        assert target is None
    
    def test_travel_to_target(self, farming_mode):
        """Test travel functionality."""
        target = {
            "name": "Test Target",
            "planet": "Test Planet",
            "zone": "Test Zone",
            "coordinates": [100, 200]
        }
        
        # Test with travel manager available
        with patch('core.modes.rare_loot_farm.travel_manager') as mock_travel:
            mock_travel.travel_to_location.return_value = True
            result = farming_mode.travel_to_target(target)
            assert result is True
        
        # Test without travel manager
        with patch('core.modes.rare_loot_farm.travel_manager', None):
            result = farming_mode.travel_to_target(target)
            assert result is False
    
    def test_join_or_create_group(self, farming_mode):
        """Test group management functionality."""
        target = {
            "name": "Test Target",
            "planet": "Test Planet",
            "zone": "Test Zone"
        }
        
        # Test group creation
        result = farming_mode.join_or_create_group(target)
        assert result is True
    
    def test_farm_target(self, farming_mode):
        """Test complete farming session."""
        target = {
            "id": "test_target",
            "name": "Test Target",
            "planet": "Test Planet",
            "zone": "Test Zone",
            "coordinates": [100, 200],
            "loot_priority": ["Test Item"],
            "rarity": "epic"
        }
        
        # Mock travel and combat
        with patch.object(farming_mode, 'travel_to_target', return_value=True), \
             patch.object(farming_mode, 'join_or_create_group', return_value=True), \
             patch.object(farming_mode, '_execute_farming_cycle') as mock_farm:
            
            mock_farm.return_value = {
                "success": True,
                "loot_found": ["Test Item", "Common Trophy"],
                "combat_events": [
                    {"type": "combat_start", "time": datetime.now().isoformat()},
                    {"type": "target_defeated", "time": datetime.now().isoformat()}
                ]
            }
            
            result = farming_mode.farm_target(target, solo_mode=False)
            
            assert result["success"] is True
            assert "session" in result
            assert "loot_found" in result
            assert "combat_events" in result
    
    def test_process_loot_item(self, farming_mode):
        """Test loot item processing."""
        target = {
            "name": "Test Target",
            "loot_priority": ["Priority Item"],
            "rarity": "legendary"
        }
        
        # Test priority item
        loot = farming_mode._process_loot_item("Priority Item", target)
        assert loot["is_priority"] is True
        assert loot["is_rare"] is True
        assert loot["rarity"] in ["epic", "legendary"]
        
        # Test common item
        loot = farming_mode._process_loot_item("Common Item", target)
        assert loot["is_priority"] is False
        assert loot["rarity"] == "common"
    
    def test_get_farming_stats(self, farming_mode):
        """Test statistics generation."""
        stats = farming_mode.get_farming_stats()
        
        assert "total_sessions" in stats
        assert "total_loot" in stats
        assert "total_rare_drops" in stats
        assert "success_rate" in stats
        assert "average_duration_minutes" in stats
        assert "kill_count" in stats
        assert "target_stats" in stats
        assert "cooldown_status" in stats
        
        assert isinstance(stats["total_sessions"], int)
        assert isinstance(stats["total_loot"], int)
        assert isinstance(stats["success_rate"], (int, float))
    
    def test_export_farming_report(self, farming_mode):
        """Test farming report export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('core.modes.rare_loot_farm.Path') as mock_path:
                mock_path.return_value.mkdir.return_value = None
                mock_path.return_value.__truediv__.return_value = Path(temp_dir) / "report.json"
                
                report_path = farming_mode.export_farming_report()
                assert isinstance(report_path, str)
                assert report_path.endswith(".json")
    
    def test_save_farming_session(self, farming_mode):
        """Test session saving functionality."""
        session_data = {
            "target": {"name": "Test Target"},
            "start_time": datetime.now().isoformat(),
            "loot_log": [],
            "combat_log": []
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('core.modes.rare_loot_farm.Path') as mock_path:
                mock_path.return_value.mkdir.return_value = None
                mock_path.return_value.__truediv__.return_value = Path(temp_dir) / "session.json"
                
                result = farming_mode._save_farming_session(session_data)
                assert isinstance(result, str)
    
    def test_mock_farming_cycle(self, farming_mode):
        """Test mock farming cycle for testing."""
        target = {
            "name": "Test Target",
            "loot_priority": ["Priority Item", "Rare Item"]
        }
        
        result = farming_mode._mock_farming_cycle(target)
        
        assert result["success"] is True
        assert "loot_found" in result
        assert "combat_events" in result
        assert len(result["loot_found"]) > 0
        assert len(result["combat_events"]) > 0
    
    def test_get_recent_drops_for_target(self, farming_mode):
        """Test recent drops retrieval for specific target."""
        target_id = "ig88"
        recent_drops = farming_mode._get_recent_drops_for_target(target_id)
        
        assert isinstance(recent_drops, list)
        # Should find drops from test session data
        assert len(recent_drops) > 0
    
    def test_select_best_target(self, farming_mode):
        """Test best target selection algorithm."""
        available_targets = ["ig88", "crystal_snake"]
        
        best_target = farming_mode._select_best_target(available_targets)
        
        assert best_target in available_targets
    
    def test_select_best_target_empty(self, farming_mode):
        """Test best target selection with no available targets."""
        best_target = farming_mode._select_best_target([])
        assert best_target is None


class TestRLSFarmingModeIntegration:
    """Integration tests for RLS farming mode."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock external dependencies."""
        with patch('core.modes.rare_loot_farm.travel_manager') as mock_travel, \
             patch('core.modes.rare_loot_farm.combat_manager') as mock_combat, \
             patch('core.modes.rare_loot_farm.DiscordAlertManager') as mock_discord:
            
            mock_travel.travel_to_location.return_value = True
            mock_combat.engage_target.return_value = {
                "success": True,
                "loot_found": ["Test Item"],
                "combat_events": []
            }
            mock_discord.return_value.send_alert.return_value = None
            
            yield {
                "travel": mock_travel,
                "combat": mock_combat,
                "discord": mock_discord
            }
    
    def test_full_farming_cycle(self, mock_dependencies):
        """Test complete farming cycle with mocked dependencies."""
        mode = RLSFarmingMode()
        
        target = {
            "id": "test_target",
            "name": "Test Target",
            "planet": "Test Planet",
            "zone": "Test Zone",
            "coordinates": [100, 200],
            "loot_priority": ["Priority Item"],
            "rarity": "epic"
        }
        
        result = mode.farm_target(target, solo_mode=False)
        
        assert result["success"] is True
        assert "session" in result
        assert "loot_found" in result
        
        # Verify travel was called
        mock_dependencies["travel"].travel_to_location.assert_called_once()
        
        # Verify combat was called
        mock_dependencies["combat"].engage_target.assert_called_once()
    
    def test_discord_alert_sending(self, mock_dependencies):
        """Test Discord alert sending for rare loot."""
        mode = RLSFarmingMode()
        
        loot_info = {
            "name": "Rare Item",
            "rarity": "epic",
            "target": "Test Target",
            "value": 5000,
            "location": "Test Location",
            "timestamp": datetime.now().isoformat(),
            "is_priority": True
        }
        
        mode._send_discord_alert(loot_info)
        
        # Verify Discord alert was sent
        mock_dependencies["discord"].return_value.send_alert.assert_called_once()


class TestRLSFarmingModeErrorHandling:
    """Error handling tests for RLS farming mode."""
    
    def test_config_file_not_found(self):
        """Test handling of missing config file."""
        with patch('core.modes.rare_loot_farm.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            
            mode = RLSFarmingMode()
            assert mode.loot_targets == {"targets": [], "settings": {}}
    
    def test_session_file_corrupted(self):
        """Test handling of corrupted session files."""
        with patch('core.modes.rare_loot_farm.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.glob.return_value = ["corrupted_file.json"]
            
            # Mock file reading to raise exception
            with patch('builtins.open', side_effect=Exception("File corrupted")):
                mode = RLSFarmingMode()
                assert isinstance(mode.farming_sessions, list)
    
    def test_travel_failure(self):
        """Test handling of travel failures."""
        mode = RLSFarmingMode()
        
        target = {
            "name": "Test Target",
            "planet": "Test Planet",
            "zone": "Test Zone",
            "coordinates": [100, 200]
        }
        
        with patch('core.modes.rare_loot_farm.travel_manager') as mock_travel:
            mock_travel.travel_to_location.return_value = False
            
            result = mode.travel_to_target(target)
            assert result is False
    
    def test_combat_failure(self):
        """Test handling of combat failures."""
        mode = RLSFarmingMode()
        
        target = {
            "name": "Test Target",
            "loot_priority": ["Test Item"],
            "rarity": "epic"
        }
        
        with patch.object(mode, 'travel_to_target', return_value=True), \
             patch.object(mode, 'join_or_create_group', return_value=True), \
             patch.object(mode, '_execute_farming_cycle') as mock_farm:
            
            mock_farm.return_value = {
                "success": False,
                "error": "Combat failed"
            }
            
            result = mode.farm_target(target)
            assert result["success"] is False
            assert "error" in result


class TestRLSFarmingModeMainFunction:
    """Tests for the main run function."""
    
    def test_run_rls_farming_mode_success(self):
        """Test successful execution of main farming mode."""
        with patch('core.modes.rare_loot_farm.RLSFarmingMode') as mock_mode_class:
            mock_mode = Mock()
            mock_mode_class.return_value = mock_mode
            
            # Mock successful execution
            mock_mode.check_cooldowns.return_value = {
                "ig88": {"available": True, "hours_remaining": 0},
                "crystal_snake": {"available": True, "hours_remaining": 0}
            }
            mock_mode.select_farming_target.return_value = {
                "id": "ig88",
                "name": "IG-88",
                "planet": "Lok",
                "zone": "Imperial Research Facility"
            }
            mock_mode.farm_target.return_value = {
                "success": True,
                "loot_found": ["Test Item"],
                "combat_events": []
            }
            mock_mode.get_farming_stats.return_value = {
                "total_sessions": 1,
                "total_loot": 1,
                "success_rate": 100.0
            }
            mock_mode.export_farming_report.return_value = "/path/to/report.json"
            
            result = run_rls_farming_mode(max_sessions=1)
            
            assert result["success"] is True
            assert result["sessions_completed"] == 1
            assert len(result["total_loot_found"]) == 1
    
    def test_run_rls_farming_mode_no_targets(self):
        """Test execution when no targets are available."""
        with patch('core.modes.rare_loot_farm.RLSFarmingMode') as mock_mode_class:
            mock_mode = Mock()
            mock_mode_class.return_value = mock_mode
            
            # Mock no available targets
            mock_mode.check_cooldowns.return_value = {
                "ig88": {"available": False, "hours_remaining": 12},
                "crystal_snake": {"available": False, "hours_remaining": 6}
            }
            
            result = run_rls_farming_mode(max_sessions=1)
            
            assert result["success"] is False
            assert "error" in result
            assert "No targets available" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 