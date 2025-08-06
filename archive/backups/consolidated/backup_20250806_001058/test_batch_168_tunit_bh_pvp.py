#!/usr/bin/env python3
"""
Test Batch 168 - T-Unit (BH) PvP Phase 2

This test suite validates the T-Unit BH PvP Phase 2 functionality including:
- Target acquisition from mission terminal → triangulation heuristics
- Range & LoS management; burst windows; escape path on counter-gank
- Strict safety checks: disable in high-risk policy, cooldowns between hunts
- Logs integrate with Seasonal BH Leaderboard (Batch 144)
"""

import json
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the T-Unit BH PvP mode
from modes.tunit_bh_pvp import (
    TUnitBHPvP, PvPTarget, HuntSession, PvPTargetType, 
    HuntStatus, SafetyLevel, run_tunit_bh_pvp
)


class TestTUnitBHPvP:
    """Test the TUnitBHPvP class."""
    
    @pytest.fixture
    def tunit_bh_pvp(self):
        """Create a TUnitBHPvP instance for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary config file
            config_path = Path(temp_dir) / "tunit_policy.json"
            config = {
                "enabled": True,
                "opt_in_required": True,
                "safety_settings": {
                    "max_risk_level": "caution",
                    "cooldown_between_hunts": 300,
                    "max_hunt_duration": 1800,
                    "emergency_escape_threshold": 0.8,
                    "disable_in_high_risk": True,
                    "high_risk_zones": ["gcw_hotspots", "crowded_areas"],
                    "safe_zone_radius": 200,
                    "escape_path_length": 3
                },
                "target_acquisition": {
                    "mission_terminal_enabled": True,
                    "triangulation_heuristics": True,
                    "max_tracking_distance": 5000,
                    "min_target_confidence": 0.7,
                    "target_refresh_interval": 60
                },
                "combat_settings": {
                    "range_management": True,
                    "line_of_sight_check": True,
                    "burst_window_duration": 30,
                    "burst_window_cooldown": 120,
                    "escape_path_planning": True,
                    "counter_gank_response": True
                },
                "logging_settings": {
                    "integrate_with_leaderboard": True,
                    "log_hunt_details": True,
                    "log_safety_checks": True,
                    "log_triangulation_data": True,
                    "leaderboard_batch_144": True
                },
                "discord_alerts": {
                    "enabled": True,
                    "alert_types": ["hunt_start", "hunt_complete", "safety_alert"],
                    "include_risk_level": True,
                    "include_rewards": True
                }
            }
            with config_path.open("w") as f:
                json.dump(config, f)
            
            # Create temporary target signals file
            signals_path = Path(temp_dir) / "data" / "bh"
            signals_path.mkdir(parents=True)
            signals_file = signals_path / "target_signals.json"
            signals_data = {
                "signal_patterns": {
                    "overt_player": {
                        "confidence_threshold": 0.8,
                        "refresh_rate": 30,
                        "location_accuracy": 0.9
                    },
                    "tef_flagged": {
                        "confidence_threshold": 0.7,
                        "refresh_rate": 45,
                        "location_accuracy": 0.8
                    }
                },
                "triangulation_heuristics": {
                    "max_distance": 5000,
                    "min_confidence": 0.7,
                    "location_update_interval": 30,
                    "path_prediction": True,
                    "zone_analysis": True
                }
            }
            with signals_file.open("w") as f:
                json.dump(signals_data, f)
            
            # Create TUnitBHPvP instance
            tunit = TUnitBHPvP(
                config_file=str(config_path),
                target_signals_file=str(signals_file)
            )
            yield tunit
    
    def test_initialization(self, tunit_bh_pvp):
        """Test TUnitBHPvP initialization."""
        assert tunit_bh_pvp is not None
        assert tunit_bh_pvp.config is not None
        assert tunit_bh_pvp.target_signals is not None
        assert tunit_bh_pvp.active_hunt is None
        assert len(tunit_bh_pvp.hunt_history) == 0
        assert tunit_bh_pvp.safety_level == SafetyLevel.SAFE
    
    def test_is_enabled_default_disabled(self, tunit_bh_pvp):
        """Test that mode is disabled by default."""
        # Default config has enabled: False
        tunit_bh_pvp.config["enabled"] = False
        assert tunit_bh_pvp.is_enabled() is False
    
    def test_is_enabled_when_enabled(self, tunit_bh_pvp):
        """Test that mode is enabled when configured."""
        tunit_bh_pvp.config["enabled"] = True
        tunit_bh_pvp.safety_level = SafetyLevel.SAFE
        assert tunit_bh_pvp.is_enabled() is True
    
    def test_is_enabled_cooldown_active(self, tunit_bh_pvp):
        """Test that mode is disabled during cooldown."""
        tunit_bh_pvp.config["enabled"] = True
        tunit_bh_pvp.safety_level = SafetyLevel.SAFE
        tunit_bh_pvp.cooldown_until = datetime.now() + timedelta(minutes=5)
        assert tunit_bh_pvp.is_enabled() is False
    
    def test_is_enabled_high_risk(self, tunit_bh_pvp):
        """Test that mode is disabled in high risk situations."""
        tunit_bh_pvp.config["enabled"] = True
        tunit_bh_pvp.safety_level = SafetyLevel.DANGER
        assert tunit_bh_pvp.is_enabled() is False
    
    def test_assess_safety_level_safe(self, tunit_bh_pvp):
        """Test safety level assessment for safe conditions."""
        with patch.object(tunit_bh_pvp, '_scan_nearby_players', return_value=[]):
            with patch.object(tunit_bh_pvp, '_assess_zone_risk', return_value=0.2):
                with patch.object(tunit_bh_pvp, '_has_recent_pvp_activity', return_value=False):
                    safety_level = tunit_bh_pvp.assess_safety_level()
                    assert safety_level == SafetyLevel.SAFE
    
    def test_assess_safety_level_caution(self, tunit_bh_pvp):
        """Test safety level assessment for caution conditions."""
        with patch.object(tunit_bh_pvp, '_scan_nearby_players', return_value=[{"hostile": False}] * 6):
            with patch.object(tunit_bh_pvp, '_assess_zone_risk', return_value=0.5):
                with patch.object(tunit_bh_pvp, '_has_recent_pvp_activity', return_value=False):
                    safety_level = tunit_bh_pvp.assess_safety_level()
                    assert safety_level == SafetyLevel.CAUTION
    
    def test_assess_safety_level_danger(self, tunit_bh_pvp):
        """Test safety level assessment for danger conditions."""
        with patch.object(tunit_bh_pvp, '_scan_nearby_players', return_value=[{"hostile": True}] * 8):
            with patch.object(tunit_bh_pvp, '_assess_zone_risk', return_value=0.8):
                with patch.object(tunit_bh_pvp, '_has_recent_pvp_activity', return_value=True):
                    safety_level = tunit_bh_pvp.assess_safety_level()
                    assert safety_level == SafetyLevel.DANGER
    
    def test_acquire_targets_from_terminal(self, tunit_bh_pvp):
        """Test target acquisition from terminal text."""
        terminal_text = """
        OvertPlayer 100,200 1500m 1000c
        TEFTarget 300,400 2000m 1500c
        EnemyPlayer 500,600 2500m 2000c
        """
        
        targets = tunit_bh_pvp.acquire_targets_from_terminal(terminal_text)
        
        assert len(targets) == 3
        assert targets[0].name == "OvertPlayer"
        assert targets[0].target_type == PvPTargetType.OVERT
        assert targets[1].name == "TEFTarget"
        assert targets[1].target_type == PvPTargetType.TEF_FLAGGED
        assert targets[2].name == "EnemyPlayer"
        assert targets[2].target_type == PvPTargetType.FACTION_ENEMY
    
    def test_parse_terminal_text(self, tunit_bh_pvp):
        """Test terminal text parsing."""
        terminal_text = "OvertPlayer 100,200 1500m 1000c"
        targets = tunit_bh_pvp._parse_terminal_text(terminal_text)
        
        assert len(targets) == 1
        assert targets[0]["name"] == "OvertPlayer"
        assert targets[0]["coordinates"] == [100, 200]
        assert targets[0]["distance"] == 1500
        assert targets[0]["reward_credits"] == 1000
    
    def test_extract_target_data_valid(self, tunit_bh_pvp):
        """Test valid target data extraction."""
        line = "OvertPlayer 100,200 1500m 1000c"
        target_data = tunit_bh_pvp._extract_target_data(line)
        
        assert target_data is not None
        assert target_data["name"] == "OvertPlayer"
        assert target_data["coordinates"] == [100, 200]
        assert target_data["distance"] == 1500
        assert target_data["reward_credits"] == 1000
    
    def test_extract_target_data_invalid(self, tunit_bh_pvp):
        """Test invalid target data extraction."""
        line = "Invalid line format"
        target_data = tunit_bh_pvp._extract_target_data(line)
        
        assert target_data is None
    
    def test_apply_triangulation_heuristics(self, tunit_bh_pvp):
        """Test triangulation heuristics application."""
        target_data = {
            "name": "OvertPlayer",
            "coordinates": [100, 200],
            "distance": 1500,
            "reward_credits": 1000
        }
        
        triangulated_location = tunit_bh_pvp._apply_triangulation_heuristics(target_data)
        
        assert triangulated_location is not None
        assert "coordinates" in triangulated_location
        assert "confidence" in triangulated_location
        assert "triangulation" in triangulated_location
    
    def test_determine_target_type(self, tunit_bh_pvp):
        """Test target type determination."""
        # Test overt player
        target_data = {"name": "OvertPlayer"}
        target_type = tunit_bh_pvp._determine_target_type(target_data)
        assert target_type == PvPTargetType.OVERT
        
        # Test TEF flagged
        target_data = {"name": "TEFTarget"}
        target_type = tunit_bh_pvp._determine_target_type(target_data)
        assert target_type == PvPTargetType.TEF_FLAGGED
        
        # Test faction enemy
        target_data = {"name": "EnemyPlayer"}
        target_type = tunit_bh_pvp._determine_target_type(target_data)
        assert target_type == PvPTargetType.FACTION_ENEMY
        
        # Test GCW target
        target_data = {"name": "GCWTarget"}
        target_type = tunit_bh_pvp._determine_target_type(target_data)
        assert target_type == PvPTargetType.GCW_TARGET
        
        # Test regular player
        target_data = {"name": "RegularPlayer"}
        target_type = tunit_bh_pvp._determine_target_type(target_data)
        assert target_type == PvPTargetType.PLAYER
    
    def test_assess_target_risk(self, tunit_bh_pvp):
        """Test target risk assessment."""
        # Low risk target
        target_data = {
            "name": "LowRiskTarget",
            "distance": 1000,
            "reward_credits": 500
        }
        risk_level = tunit_bh_pvp._assess_target_risk(target_data)
        assert risk_level in [SafetyLevel.SAFE, SafetyLevel.CAUTION]
        
        # High risk target
        target_data = {
            "name": "OvertPlayer",
            "distance": 4000,
            "reward_credits": 2500
        }
        risk_level = tunit_bh_pvp._assess_target_risk(target_data)
        assert risk_level in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]
    
    def test_start_hunt_success(self, tunit_bh_pvp):
        """Test successful hunt start."""
        tunit_bh_pvp.config["enabled"] = True
        tunit_bh_pvp.safety_level = SafetyLevel.SAFE
        
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        success = tunit_bh_pvp.start_hunt(target)
        assert success is True
        assert tunit_bh_pvp.active_hunt is not None
        assert tunit_bh_pvp.active_hunt.target == target
        assert tunit_bh_pvp.active_hunt.status == HuntStatus.SEARCHING
    
    def test_start_hunt_disabled(self, tunit_bh_pvp):
        """Test hunt start when mode is disabled."""
        tunit_bh_pvp.config["enabled"] = False
        
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        success = tunit_bh_pvp.start_hunt(target)
        assert success is False
        assert tunit_bh_pvp.active_hunt is None
    
    def test_start_hunt_already_active(self, tunit_bh_pvp):
        """Test hunt start when hunt already active."""
        tunit_bh_pvp.config["enabled"] = True
        tunit_bh_pvp.safety_level = SafetyLevel.SAFE
        
        # Start first hunt
        target1 = PvPTarget(
            name="TestTarget1",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        success1 = tunit_bh_pvp.start_hunt(target1)
        assert success1 is True
        
        # Try to start second hunt
        target2 = PvPTarget(
            name="TestTarget2",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [300, 400]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        success2 = tunit_bh_pvp.start_hunt(target2)
        assert success2 is False
    
    def test_manage_range_and_los(self, tunit_bh_pvp):
        """Test range and line of sight management."""
        # Setup active hunt
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        tunit_bh_pvp.active_hunt = HuntSession(
            target=target,
            start_time=datetime.now(),
            status=HuntStatus.SEARCHING,
            current_location={"coordinates": [50, 100]}
        )
        
        range_data = tunit_bh_pvp.manage_range_and_los()
        
        assert "status" in range_data
        assert "action" in range_data
        assert "current_distance" in range_data
        assert "optimal_range" in range_data
        assert "line_of_sight" in range_data
    
    def test_manage_range_and_los_no_hunt(self, tunit_bh_pvp):
        """Test range management when no active hunt."""
        range_data = tunit_bh_pvp.manage_range_and_los()
        
        assert range_data["status"] == "no_active_hunt"
    
    def test_manage_burst_windows(self, tunit_bh_pvp):
        """Test burst window management."""
        # Setup active hunt
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        tunit_bh_pvp.active_hunt = HuntSession(
            target=target,
            start_time=datetime.now(),
            status=HuntStatus.SEARCHING,
            current_location={"coordinates": [50, 100]}
        )
        
        burst_data = tunit_bh_pvp.manage_burst_windows()
        
        assert "status" in burst_data
        assert "available_bursts" in burst_data
        assert "can_create_burst" in burst_data
        assert "total_bursts" in burst_data
    
    def test_manage_burst_windows_no_hunt(self, tunit_bh_pvp):
        """Test burst window management when no active hunt."""
        burst_data = tunit_bh_pvp.manage_burst_windows()
        
        assert burst_data["status"] == "no_active_hunt"
    
    def test_handle_counter_gank(self, tunit_bh_pvp):
        """Test counter-gank handling."""
        # Setup active hunt
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        tunit_bh_pvp.active_hunt = HuntSession(
            target=target,
            start_time=datetime.now(),
            status=HuntStatus.SEARCHING,
            current_location={"coordinates": [50, 100]}
        )
        
        counter_gank_data = tunit_bh_pvp.handle_counter_gank()
        
        assert "status" in counter_gank_data
        assert "counter_gank_detected" in counter_gank_data
    
    def test_handle_counter_gank_no_hunt(self, tunit_bh_pvp):
        """Test counter-gank handling when no active hunt."""
        counter_gank_data = tunit_bh_pvp.handle_counter_gank()
        
        assert counter_gank_data["status"] == "no_active_hunt"
    
    def test_complete_hunt_success(self, tunit_bh_pvp):
        """Test successful hunt completion."""
        # Setup active hunt
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        tunit_bh_pvp.active_hunt = HuntSession(
            target=target,
            start_time=datetime.now(),
            status=HuntStatus.SEARCHING,
            current_location={"coordinates": [50, 100]}
        )
        
        success = tunit_bh_pvp.complete_hunt(success=True)
        
        assert success is True
        assert tunit_bh_pvp.active_hunt is None
        assert len(tunit_bh_pvp.hunt_history) == 1
        assert tunit_bh_pvp.hunt_history[0].status == HuntStatus.COMPLETED
        assert tunit_bh_pvp.cooldown_until is not None
    
    def test_complete_hunt_failure(self, tunit_bh_pvp):
        """Test failed hunt completion."""
        # Setup active hunt
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        tunit_bh_pvp.active_hunt = HuntSession(
            target=target,
            start_time=datetime.now(),
            status=HuntStatus.SEARCHING,
            current_location={"coordinates": [50, 100]}
        )
        
        success = tunit_bh_pvp.complete_hunt(success=False)
        
        assert success is True
        assert tunit_bh_pvp.active_hunt is None
        assert len(tunit_bh_pvp.hunt_history) == 1
        assert tunit_bh_pvp.hunt_history[0].status == HuntStatus.FAILED
    
    def test_complete_hunt_no_active_hunt(self, tunit_bh_pvp):
        """Test hunt completion when no active hunt."""
        success = tunit_bh_pvp.complete_hunt(success=True)
        
        assert success is False
    
    @patch('modes.tunit_bh_pvp.send_discord_alert')
    def test_send_hunt_alert(self, mock_send_alert, tunit_bh_pvp):
        """Test Discord alert sending."""
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        tunit_bh_pvp._send_hunt_alert("hunt_start", target)
        
        mock_send_alert.assert_called_once()
    
    def test_get_current_location(self, tunit_bh_pvp):
        """Test current location retrieval."""
        location = tunit_bh_pvp._get_current_location()
        
        assert "planet" in location
        assert "city" in location
        assert "coordinates" in location
        assert "zone" in location
    
    def test_scan_nearby_players(self, tunit_bh_pvp):
        """Test nearby player scanning."""
        players = tunit_bh_pvp._scan_nearby_players()
        
        assert isinstance(players, list)
        for player in players:
            assert "name" in player
            assert "distance" in player
            assert "hostile" in player
    
    def test_assess_zone_risk(self, tunit_bh_pvp):
        """Test zone risk assessment."""
        location = {"coordinates": [100, 200]}
        risk = tunit_bh_pvp._assess_zone_risk(location)
        
        assert isinstance(risk, float)
        assert 0.0 <= risk <= 1.0
    
    def test_has_recent_pvp_activity(self, tunit_bh_pvp):
        """Test recent PvP activity detection."""
        activity = tunit_bh_pvp._has_recent_pvp_activity()
        
        assert isinstance(activity, bool)


class TestPvPTarget:
    """Test the PvPTarget dataclass."""
    
    def test_pvp_target_creation(self):
        """Test PvPTarget creation."""
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        assert target.name == "TestTarget"
        assert target.target_type == PvPTargetType.OVERT
        assert target.location == {"coordinates": [100, 200]}
        assert target.difficulty == "medium"
        assert target.reward_credits == 1000
        assert target.risk_level == SafetyLevel.CAUTION
        assert isinstance(target.last_seen, datetime)
        assert isinstance(target.triangulation_data, dict)
        assert isinstance(target.engagement_history, list)


class TestHuntSession:
    """Test the HuntSession dataclass."""
    
    def test_hunt_session_creation(self):
        """Test HuntSession creation."""
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        session = HuntSession(
            target=target,
            start_time=datetime.now(),
            status=HuntStatus.SEARCHING,
            current_location={"coordinates": [50, 100]}
        )
        
        assert session.target == target
        assert isinstance(session.start_time, datetime)
        assert session.status == HuntStatus.SEARCHING
        assert session.current_location == {"coordinates": [50, 100]}
        assert isinstance(session.escape_path, list)
        assert isinstance(session.burst_windows, list)
        assert isinstance(session.safety_checks, list)
        assert session.cooldown_end is None


class TestSafetyLevel:
    """Test the SafetyLevel enum."""
    
    def test_safety_level_values(self):
        """Test SafetyLevel enum values."""
        assert SafetyLevel.SAFE.value == "safe"
        assert SafetyLevel.CAUTION.value == "caution"
        assert SafetyLevel.DANGER.value == "danger"
        assert SafetyLevel.CRITICAL.value == "critical"
    
    def test_safety_level_comparison(self):
        """Test SafetyLevel comparison."""
        assert SafetyLevel.SAFE < SafetyLevel.CAUTION
        assert SafetyLevel.CAUTION < SafetyLevel.DANGER
        assert SafetyLevel.DANGER < SafetyLevel.CRITICAL


class TestPvPTargetType:
    """Test the PvPTargetType enum."""
    
    def test_target_type_values(self):
        """Test PvPTargetType enum values."""
        assert PvPTargetType.PLAYER.value == "player"
        assert PvPTargetType.OVERT.value == "overt"
        assert PvPTargetType.TEF_FLAGGED.value == "tef_flagged"
        assert PvPTargetType.FACTION_ENEMY.value == "faction_enemy"
        assert PvPTargetType.GCW_TARGET.value == "gcw_target"


class TestHuntStatus:
    """Test the HuntStatus enum."""
    
    def test_hunt_status_values(self):
        """Test HuntStatus enum values."""
        assert HuntStatus.SEARCHING.value == "searching"
        assert HuntStatus.TRACKING.value == "tracking"
        assert HuntStatus.ENGAGING.value == "engaging"
        assert HuntStatus.ESCAPING.value == "escaping"
        assert HuntStatus.COMPLETED.value == "completed"
        assert HuntStatus.FAILED.value == "failed"
        assert HuntStatus.ABORTED.value == "aborted"


class TestTUnitBHPvPIntegration:
    """Integration tests for TUnitBHPvP."""
    
    @pytest.fixture
    def tunit_bh_pvp(self):
        """Create a TUnitBHPvP instance for integration testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary config file
            config_path = Path(temp_dir) / "tunit_policy.json"
            config = {
                "enabled": True,
                "opt_in_required": True,
                "safety_settings": {
                    "max_risk_level": "caution",
                    "cooldown_between_hunts": 300,
                    "max_hunt_duration": 1800,
                    "emergency_escape_threshold": 0.8,
                    "disable_in_high_risk": True,
                    "high_risk_zones": ["gcw_hotspots", "crowded_areas"],
                    "safe_zone_radius": 200,
                    "escape_path_length": 3
                },
                "target_acquisition": {
                    "mission_terminal_enabled": True,
                    "triangulation_heuristics": True,
                    "max_tracking_distance": 5000,
                    "min_target_confidence": 0.7,
                    "target_refresh_interval": 60
                },
                "combat_settings": {
                    "range_management": True,
                    "line_of_sight_check": True,
                    "burst_window_duration": 30,
                    "burst_window_cooldown": 120,
                    "escape_path_planning": True,
                    "counter_gank_response": True
                },
                "logging_settings": {
                    "integrate_with_leaderboard": True,
                    "log_hunt_details": True,
                    "log_safety_checks": True,
                    "log_triangulation_data": True,
                    "leaderboard_batch_144": True
                },
                "discord_alerts": {
                    "enabled": True,
                    "alert_types": ["hunt_start", "hunt_complete", "safety_alert"],
                    "include_risk_level": True,
                    "include_rewards": True
                }
            }
            with config_path.open("w") as f:
                json.dump(config, f)
            
            # Create temporary target signals file
            signals_path = Path(temp_dir) / "data" / "bh"
            signals_path.mkdir(parents=True)
            signals_file = signals_path / "target_signals.json"
            signals_data = {
                "signal_patterns": {
                    "overt_player": {
                        "confidence_threshold": 0.8,
                        "refresh_rate": 30,
                        "location_accuracy": 0.9
                    },
                    "tef_flagged": {
                        "confidence_threshold": 0.7,
                        "refresh_rate": 45,
                        "location_accuracy": 0.8
                    }
                },
                "triangulation_heuristics": {
                    "max_distance": 5000,
                    "min_confidence": 0.7,
                    "location_update_interval": 30,
                    "path_prediction": True,
                    "zone_analysis": True
                }
            }
            with signals_file.open("w") as f:
                json.dump(signals_data, f)
            
            # Create TUnitBHPvP instance
            tunit = TUnitBHPvP(
                config_file=str(config_path),
                target_signals_file=str(signals_file)
            )
            yield tunit
    
    def test_full_hunt_cycle(self, tunit_bh_pvp):
        """Test a complete hunt cycle."""
        # 1. Check if enabled
        assert tunit_bh_pvp.is_enabled() is True
        
        # 2. Assess safety
        safety_level = tunit_bh_pvp.assess_safety_level()
        assert safety_level in [SafetyLevel.SAFE, SafetyLevel.CAUTION]
        
        # 3. Acquire targets
        terminal_text = "OvertPlayer 100,200 1500m 1000c"
        targets = tunit_bh_pvp.acquire_targets_from_terminal(terminal_text)
        assert len(targets) == 1
        
        # 4. Start hunt
        target = targets[0]
        success = tunit_bh_pvp.start_hunt(target)
        assert success is True
        assert tunit_bh_pvp.active_hunt is not None
        
        # 5. Manage range and LoS
        range_data = tunit_bh_pvp.manage_range_and_los()
        assert "status" in range_data
        
        # 6. Manage burst windows
        burst_data = tunit_bh_pvp.manage_burst_windows()
        assert "status" in burst_data
        
        # 7. Check for counter-gank
        counter_gank_data = tunit_bh_pvp.handle_counter_gank()
        assert "status" in counter_gank_data
        
        # 8. Complete hunt
        completion_success = tunit_bh_pvp.complete_hunt(success=True)
        assert completion_success is True
        assert tunit_bh_pvp.active_hunt is None
        assert len(tunit_bh_pvp.hunt_history) == 1
    
    def test_safety_integration(self, tunit_bh_pvp):
        """Test safety integration throughout the system."""
        # Test safety assessment
        safety_level = tunit_bh_pvp.assess_safety_level()
        assert safety_level in [SafetyLevel.SAFE, SafetyLevel.CAUTION, SafetyLevel.DANGER, SafetyLevel.CRITICAL]
        
        # Test that high risk disables mode
        tunit_bh_pvp.safety_level = SafetyLevel.CRITICAL
        assert tunit_bh_pvp.is_enabled() is False
        
        # Test that safe level enables mode
        tunit_bh_pvp.safety_level = SafetyLevel.SAFE
        tunit_bh_pvp.config["enabled"] = True
        assert tunit_bh_pvp.is_enabled() is True
    
    def test_leaderboard_integration(self, tunit_bh_pvp):
        """Test leaderboard integration."""
        # Setup active hunt
        target = PvPTarget(
            name="TestTarget",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        )
        
        tunit_bh_pvp.active_hunt = HuntSession(
            target=target,
            start_time=datetime.now(),
            status=HuntStatus.SEARCHING,
            current_location={"coordinates": [50, 100]}
        )
        
        # Complete hunt to trigger leaderboard integration
        success = tunit_bh_pvp.complete_hunt(success=True)
        assert success is True
        
        # Check that hunt was logged
        assert len(tunit_bh_pvp.hunt_history) == 1
        assert tunit_bh_pvp.hunt_history[0].status == HuntStatus.COMPLETED


class TestConfigurationLoading:
    """Test configuration loading functionality."""
    
    def test_default_config_loading(self):
        """Test loading of default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create TUnitBHPvP without config file
            config_path = Path(temp_dir) / "nonexistent_config.json"
            signals_path = Path(temp_dir) / "nonexistent_signals.json"
            
            tunit = TUnitBHPvP(
                config_file=str(config_path),
                target_signals_file=str(signals_path)
            )
            
            # Should load default config
            assert tunit.config is not None
            assert "enabled" in tunit.config
            assert "safety_settings" in tunit.config
            assert "target_acquisition" in tunit.config
            assert "combat_settings" in tunit.config
            assert "logging_settings" in tunit.config
            assert "discord_alerts" in tunit.config
    
    def test_custom_config_loading(self):
        """Test loading of custom configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create custom config file
            config_path = Path(temp_dir) / "custom_config.json"
            config = {
                "enabled": True,
                "opt_in_required": False,
                "safety_settings": {
                    "max_risk_level": "danger",
                    "cooldown_between_hunts": 600
                }
            }
            with config_path.open("w") as f:
                json.dump(config, f)
            
            # Create custom signals file
            signals_path = Path(temp_dir) / "custom_signals.json"
            signals = {
                "signal_patterns": {
                    "custom_target": {
                        "confidence_threshold": 0.9,
                        "refresh_rate": 20
                    }
                }
            }
            with signals_path.open("w") as f:
                json.dump(signals, f)
            
            tunit = TUnitBHPvP(
                config_file=str(config_path),
                target_signals_file=str(signals_path)
            )
            
            # Should load custom config
            assert tunit.config["enabled"] is True
            assert tunit.config["opt_in_required"] is False
            assert tunit.config["safety_settings"]["max_risk_level"] == "danger"
            assert tunit.config["safety_settings"]["cooldown_between_hunts"] == 600
            
            # Should load custom signals
            assert "custom_target" in tunit.target_signals["signal_patterns"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 