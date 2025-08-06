#!/usr/bin/env python3
"""
Tests for Batch 107 - AI Tactical Engine (PvE & PvP Fight Decisions)

This test suite covers:
- Engine initialization and data loading
- Combat log analysis and learning
- Tactical recommendations
- Combat metrics calculation
- Session synchronization
- Report export functionality
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from core.combat_tactics_engine import (
    CombatTacticsEngine,
    CombatEvent,
    CombatSession,
    CombatResult,
    TacticalAction,
    WeaponEnemyResist,
    TacticalInsight,
    CombatMetrics
)


class TestCombatTacticsEngine:
    """Test the CombatTacticsEngine class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_dir = tempfile.mkdtemp()
        combat_logs_dir = Path(temp_dir) / "combat_logs"
        tactics_data_dir = Path(temp_dir) / "tactics_data"
        session_logs_dir = Path(temp_dir) / "session_logs"
        
        combat_logs_dir.mkdir()
        tactics_data_dir.mkdir()
        session_logs_dir.mkdir()
        
        yield {
            'temp_dir': temp_dir,
            'combat_logs_dir': combat_logs_dir,
            'tactics_data_dir': tactics_data_dir,
            'session_logs_dir': session_logs_dir
        }
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_combat_data(self):
        """Create sample combat data for testing."""
        return {
            "session_id": "test_session_001",
            "start_time": "2025-08-01T12:00:00.000000",
            "end_time": "2025-08-01T12:01:00.000000",
            "duration": 60.0,
            "events": [
                {
                    "event_type": "ability_use",
                    "timestamp": "2025-08-01T12:00:10.000000",
                    "ability_name": "rifle_shot",
                    "target": "stormtrooper",
                    "damage_dealt": 200,
                    "damage_type": "physical",
                    "success": True,
                    "enemy_type": "stormtrooper",
                    "xp_gained": 150,
                    "player_health": 100,
                    "target_health": 100
                },
                {
                    "event_type": "ability_use",
                    "timestamp": "2025-08-01T12:00:20.000000",
                    "ability_name": "headshot",
                    "target": "stormtrooper",
                    "damage_dealt": 400,
                    "damage_type": "physical",
                    "success": True,
                    "enemy_type": "stormtrooper",
                    "xp_gained": 250,
                    "player_health": 80,
                    "target_health": 40
                },
                {
                    "event_type": "enemy_killed",
                    "timestamp": "2025-08-01T12:00:30.000000",
                    "enemy_type": "stormtrooper",
                    "xp_gained": 500,
                    "player_health": 80,
                    "target_health": 0
                }
            ],
            "result": "victory",
            "player_build": {
                "weapon_type": "rifle",
                "role": "rifleman"
            },
            "enemy_type": "stormtrooper",
            "tactics_used": ["opening_burst"],
            "success_rate": 0.8,
            "damage_efficiency": 1.2
        }
    
    @pytest.fixture
    def engine(self, temp_dirs):
        """Create a CombatTacticsEngine instance for testing."""
        return CombatTacticsEngine(
            combat_logs_dir=str(temp_dirs['combat_logs_dir']),
            tactics_data_dir=str(temp_dirs['tactics_data_dir']),
            session_logs_dir=str(temp_dirs['session_logs_dir'])
        )
    
    def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine.combat_logs_dir.exists()
        assert engine.tactics_data_dir.exists()
        assert engine.session_logs_dir.exists()
        assert len(engine.weapon_resist_data) == 0
        assert len(engine.tactical_insights) == 0
        assert len(engine.combat_sessions) == 0
        assert engine.metrics is None
    
    def test_load_weapon_resist_data(self, engine, temp_dirs):
        """Test loading weapon resistance data."""
        # Create sample weapon resist data
        resist_data = {
            "rifle_stormtrooper": {
                "weapon_type": "rifle",
                "enemy_type": "stormtrooper",
                "effectiveness": 0.8,
                "sample_size": 10,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        resist_file = temp_dirs['tactics_data_dir'] / "weapon_resist_data.json"
        with open(resist_file, 'w', encoding='utf-8') as f:
            json.dump(resist_data, f, indent=2)
        
        # Reload data
        engine._load_weapon_resist_data()
        
        assert len(engine.weapon_resist_data) == 1
        assert "rifle_stormtrooper" in engine.weapon_resist_data
        resist = engine.weapon_resist_data["rifle_stormtrooper"]
        assert resist.weapon_type == "rifle"
        assert resist.enemy_type == "stormtrooper"
        assert resist.effectiveness == 0.8
    
    def test_save_weapon_resist_data(self, engine, temp_dirs):
        """Test saving weapon resistance data."""
        # Add sample data
        engine.weapon_resist_data["test_key"] = WeaponEnemyResist(
            weapon_type="pistol",
            enemy_type="imperial_officer",
            effectiveness=0.6,
            sample_size=5,
            last_updated=datetime.now().isoformat()
        )
        
        # Save data
        engine._save_weapon_resist_data()
        
        # Verify file was created
        resist_file = temp_dirs['tactics_data_dir'] / "weapon_resist_data.json"
        assert resist_file.exists()
        
        # Verify data was saved correctly
        with open(resist_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "test_key" in data
        assert data["test_key"]["weapon_type"] == "pistol"
        assert data["test_key"]["enemy_type"] == "imperial_officer"
    
    def test_load_tactical_insights(self, engine, temp_dirs):
        """Test loading tactical insights."""
        # Create sample tactical insights
        insights_data = {
            "opening_stormtrooper_rifle": {
                "enemy_type": "stormtrooper",
                "player_build": "rifle",
                "situation": "opening",
                "best_action": "aggressive",
                "success_rate": 0.8,
                "confidence": 0.8,
                "sample_size": 10,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        insights_file = temp_dirs['tactics_data_dir'] / "tactical_insights.json"
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights_data, f, indent=2)
        
        # Reload data
        engine._load_tactical_insights()
        
        assert len(engine.tactical_insights) == 1
        assert "opening_stormtrooper_rifle" in engine.tactical_insights
        insight = engine.tactical_insights["opening_stormtrooper_rifle"]
        assert insight.enemy_type == "stormtrooper"
        assert insight.player_build == "rifle"
        assert insight.best_action == TacticalAction.AGGRESSIVE
    
    def test_load_combat_sessions(self, engine, temp_dirs, sample_combat_data):
        """Test loading combat sessions."""
        # Create sample combat log
        log_file = temp_dirs['combat_logs_dir'] / "combat_stats_test_001.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(sample_combat_data, f, indent=2)
        
        # Reload sessions
        engine._load_combat_sessions()
        
        assert len(engine.combat_sessions) == 1
        session = engine.combat_sessions[0]
        assert session.session_id == "test_session_001"
        assert session.result == CombatResult.VICTORY
        assert len(session.events) == 3
    
    def test_classify_weapon_type(self, engine):
        """Test weapon type classification."""
        assert engine._classify_weapon_type("rifle_shot") == "rifle"
        assert engine._classify_weapon_type("pistol_blast") == "pistol"
        assert engine._classify_weapon_type("sword_slash") == "melee"
        assert engine._classify_weapon_type("grenade_throw") == "explosive"
        assert engine._classify_weapon_type("heal_self") == "support"
        assert engine._classify_weapon_type("unknown_ability") == "unknown"
    
    def test_classify_player_build(self, engine):
        """Test player build classification."""
        build1 = {"weapon_type": "rifle", "role": "rifleman"}
        build2 = {"role": "medic"}
        build3 = {}
        
        assert engine._classify_player_build(build1) == "rifle"
        assert engine._classify_player_build(build2) == "medic"
        assert engine._classify_player_build(build3) == "unknown"
    
    def test_classify_tactic(self, engine):
        """Test tactic classification."""
        assert engine._classify_tactic("heal_self") == "heal"
        assert engine._classify_tactic("shield_block") == "defensive"
        assert engine._classify_tactic("burst_fire") == "burst"
        assert engine._classify_tactic("flee_escape") == "flee"
        assert engine._classify_tactic("debuff_enemy") == "debuff"
        assert engine._classify_tactic("attack_enemy") == "attack"
    
    def test_map_tactic_to_action(self, engine):
        """Test mapping tactics to actions."""
        assert engine._map_tactic_to_action("heal") == TacticalAction.HEAL
        assert engine._map_tactic_to_action("defensive") == TacticalAction.DEFENSIVE
        assert engine._map_tactic_to_action("burst") == TacticalAction.BURST
        assert engine._map_tactic_to_action("flee") == TacticalAction.FLEE
        assert engine._map_tactic_to_action("debuff") == TacticalAction.OPEN_DEBUFF
        assert engine._map_tactic_to_action("attack") == TacticalAction.AGGRESSIVE
        assert engine._map_tactic_to_action("unknown") == TacticalAction.AGGRESSIVE
    
    def test_analyze_combat_logs(self, engine, temp_dirs, sample_combat_data):
        """Test combat log analysis."""
        # Create sample combat log
        log_file = temp_dirs['combat_logs_dir'] / "combat_stats_test_001.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(sample_combat_data, f, indent=2)
        
        # Reload sessions and analyze
        engine._load_combat_sessions()
        engine.analyze_combat_logs()
        
        # Check that weapon resistance data was created
        assert len(engine.weapon_resist_data) > 0
        
        # Check that tactical insights were created
        assert len(engine.tactical_insights) > 0
    
    def test_get_optimal_action_with_insight(self, engine):
        """Test getting optimal action when tactical insight exists."""
        # Add a tactical insight
        engine.tactical_insights["opening_stormtrooper_rifle"] = TacticalInsight(
            enemy_type="stormtrooper",
            player_build="rifle",
            situation="opening",
            best_action=TacticalAction.BURST,
            success_rate=0.8,
            confidence=0.8,
            sample_size=10,
            last_updated=datetime.now().isoformat()
        )
        
        action = engine.get_optimal_action(
            enemy_type="stormtrooper",
            player_build={"weapon_type": "rifle"},
            situation="opening"
        )
        
        assert action == TacticalAction.BURST
    
    def test_get_optimal_action_with_weapon_resist(self, engine):
        """Test getting optimal action based on weapon resistance."""
        # Add weapon resistance data
        engine.weapon_resist_data["rifle_stormtrooper"] = WeaponEnemyResist(
            weapon_type="rifle",
            enemy_type="stormtrooper",
            effectiveness=0.8,
            sample_size=10,
            last_updated=datetime.now().isoformat()
        )
        
        action = engine.get_optimal_action(
            enemy_type="stormtrooper",
            player_build={"weapon_type": "rifle"}
        )
        
        assert action == TacticalAction.AGGRESSIVE
    
    def test_get_optimal_action_fallback(self, engine):
        """Test getting optimal action with fallback logic."""
        action = engine.get_optimal_action(
            enemy_type="unknown",
            player_build={},
            player_health=25,
            target_health=100
        )
        
        # Should fall back to heal for low health
        assert action == TacticalAction.HEAL
    
    def test_get_combat_metrics(self, engine, temp_dirs, sample_combat_data):
        """Test combat metrics calculation."""
        # Create sample combat log
        log_file = temp_dirs['combat_logs_dir'] / "combat_stats_test_001.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(sample_combat_data, f, indent=2)
        
        # Reload sessions and analyze
        engine._load_combat_sessions()
        engine.analyze_combat_logs()
        
        # Get metrics
        metrics = engine.get_combat_metrics()
        
        assert metrics.total_combats == 1
        assert metrics.victories == 1
        assert metrics.defeats == 0
        assert metrics.avg_damage_dealt > 0
        assert isinstance(metrics.most_effective_weapons, list)
        assert isinstance(metrics.most_effective_tactics, list)
        assert isinstance(metrics.enemy_type_performance, dict)
    
    def test_sync_to_user_sessions(self, engine, temp_dirs):
        """Test syncing tactical data to user sessions."""
        # Create sample session file
        session_data = {
            "session_id": "test_session",
            "discord_id": "test_user_123",
            "start_time": "2025-08-01T12:00:00.000000",
            "end_time": "2025-08-01T13:00:00.000000"
        }
        
        session_file = temp_dirs['session_logs_dir'] / "session_test_001.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        
        # Add some metrics data
        engine.metrics = CombatMetrics(
            total_combats=10,
            victories=8,
            defeats=2,
            avg_damage_dealt=200.0,
            avg_damage_taken=150.0,
            avg_combat_duration=30.0,
            most_effective_weapons=[("rifle", 0.8)],
            most_effective_tactics=[("aggressive", 0.8)],
            enemy_type_performance={"stormtrooper": 0.8}
        )
        
        # Sync data
        success = engine.sync_to_user_sessions("test_user_123")
        
        assert success
        
        # Verify session was updated
        with open(session_file, 'r', encoding='utf-8') as f:
            updated_session = json.load(f)
        
        assert 'tactical_metrics' in updated_session
        tactical_metrics = updated_session['tactical_metrics']
        assert tactical_metrics['total_combats'] == 10
        assert tactical_metrics['victory_rate'] == 0.8
        assert tactical_metrics['most_effective_weapon'] == "rifle"
    
    def test_export_tactical_report_json(self, engine, temp_dirs):
        """Test exporting tactical report in JSON format."""
        # Add some data
        engine.weapon_resist_data["test_key"] = WeaponEnemyResist(
            weapon_type="pistol",
            enemy_type="imperial_officer",
            effectiveness=0.6,
            sample_size=5,
            last_updated=datetime.now().isoformat()
        )
        
        engine.metrics = CombatMetrics(
            total_combats=5,
            victories=4,
            defeats=1,
            avg_damage_dealt=150.0,
            avg_damage_taken=100.0,
            avg_combat_duration=25.0,
            most_effective_weapons=[("pistol", 0.6)],
            most_effective_tactics=[("defensive", 0.7)],
            enemy_type_performance={"imperial_officer": 0.8}
        )
        
        # Export report
        report_path = engine.export_tactical_report(format='json')
        
        assert Path(report_path).exists()
        
        # Verify report content
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        assert 'weapon_resistance_data' in report_data
        assert 'combat_metrics' in report_data
        assert report_data['combat_metrics']['total_combats'] == 5
    
    def test_export_tactical_report_txt(self, engine, temp_dirs):
        """Test exporting tactical report in text format."""
        # Add some data
        engine.metrics = CombatMetrics(
            total_combats=3,
            victories=2,
            defeats=1,
            avg_damage_dealt=120.0,
            avg_damage_taken=80.0,
            avg_combat_duration=20.0,
            most_effective_weapons=[("rifle", 0.7)],
            most_effective_tactics=[("aggressive", 0.6)],
            enemy_type_performance={"stormtrooper": 0.7}
        )
        
        # Export report
        report_path = engine.export_tactical_report(format='txt')
        
        assert Path(report_path).exists()
        
        # Verify report content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "AI Tactical Engine Report" in content
        assert "Total Combat Sessions: 3" in content
        assert "Victory Rate: 66.7%" in content
    
    def test_export_tactical_report_invalid_format(self, engine):
        """Test exporting tactical report with invalid format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            engine.export_tactical_report(format='invalid')
    
    def test_has_low_health_events(self, engine):
        """Test low health event detection."""
        # Create session with low health events
        events = [
            CombatEvent(
                timestamp="2025-08-01T12:00:00.000000",
                event_type="ability_use",
                player_health=25
            )
        ]
        
        session = CombatSession(
            session_id="test",
            start_time="2025-08-01T12:00:00.000000",
            end_time="2025-08-01T12:01:00.000000",
            duration=60.0,
            events=events,
            result=CombatResult.VICTORY,
            player_build={},
            enemy_type="test",
            tactics_used=[],
            success_rate=0.8,
            damage_efficiency=1.0
        )
        
        assert engine._has_low_health_events(session)
    
    def test_has_high_damage_events(self, engine):
        """Test high damage event detection."""
        # Create session with high damage events
        events = [
            CombatEvent(
                timestamp="2025-08-01T12:00:00.000000",
                event_type="ability_use",
                damage_taken=150
            )
        ]
        
        session = CombatSession(
            session_id="test",
            start_time="2025-08-01T12:00:00.000000",
            end_time="2025-08-01T12:01:00.000000",
            duration=60.0,
            events=events,
            result=CombatResult.VICTORY,
            player_build={},
            enemy_type="test",
            tactics_used=[],
            success_rate=0.8,
            damage_efficiency=1.0
        )
        
        assert engine._has_high_damage_events(session)


class TestCombatEvent:
    """Test the CombatEvent dataclass."""
    
    def test_combat_event_creation(self):
        """Test creating a CombatEvent."""
        event = CombatEvent(
            timestamp="2025-08-01T12:00:00.000000",
            event_type="ability_use",
            ability_name="rifle_shot",
            target="stormtrooper",
            damage_dealt=200,
            damage_type="physical",
            success=True,
            enemy_type="stormtrooper",
            xp_gained=150,
            player_health=100,
            target_health=100
        )
        
        assert event.timestamp == "2025-08-01T12:00:00.000000"
        assert event.event_type == "ability_use"
        assert event.ability_name == "rifle_shot"
        assert event.damage_dealt == 200
        assert event.success is True


class TestCombatSession:
    """Test the CombatSession dataclass."""
    
    def test_combat_session_creation(self):
        """Test creating a CombatSession."""
        events = [
            CombatEvent(
                timestamp="2025-08-01T12:00:00.000000",
                event_type="ability_use",
                ability_name="rifle_shot"
            )
        ]
        
        session = CombatSession(
            session_id="test_session",
            start_time="2025-08-01T12:00:00.000000",
            end_time="2025-08-01T12:01:00.000000",
            duration=60.0,
            events=events,
            result=CombatResult.VICTORY,
            player_build={"weapon_type": "rifle"},
            enemy_type="stormtrooper",
            tactics_used=["opening_burst"],
            success_rate=0.8,
            damage_efficiency=1.2
        )
        
        assert session.session_id == "test_session"
        assert session.result == CombatResult.VICTORY
        assert len(session.events) == 1
        assert session.success_rate == 0.8


class TestWeaponEnemyResist:
    """Test the WeaponEnemyResist dataclass."""
    
    def test_weapon_enemy_resist_creation(self):
        """Test creating a WeaponEnemyResist."""
        resist = WeaponEnemyResist(
            weapon_type="rifle",
            enemy_type="stormtrooper",
            effectiveness=0.8,
            sample_size=10,
            last_updated=datetime.now().isoformat()
        )
        
        assert resist.weapon_type == "rifle"
        assert resist.enemy_type == "stormtrooper"
        assert resist.effectiveness == 0.8
        assert resist.sample_size == 10


class TestTacticalInsight:
    """Test the TacticalInsight dataclass."""
    
    def test_tactical_insight_creation(self):
        """Test creating a TacticalInsight."""
        insight = TacticalInsight(
            enemy_type="stormtrooper",
            player_build="rifle",
            situation="opening",
            best_action=TacticalAction.BURST,
            success_rate=0.8,
            confidence=0.8,
            sample_size=10,
            last_updated=datetime.now().isoformat()
        )
        
        assert insight.enemy_type == "stormtrooper"
        assert insight.player_build == "rifle"
        assert insight.best_action == TacticalAction.BURST
        assert insight.success_rate == 0.8


class TestCombatMetrics:
    """Test the CombatMetrics dataclass."""
    
    def test_combat_metrics_creation(self):
        """Test creating CombatMetrics."""
        metrics = CombatMetrics(
            total_combats=10,
            victories=8,
            defeats=2,
            avg_damage_dealt=200.0,
            avg_damage_taken=150.0,
            avg_combat_duration=30.0,
            most_effective_weapons=[("rifle", 0.8)],
            most_effective_tactics=[("aggressive", 0.8)],
            enemy_type_performance={"stormtrooper": 0.8}
        )
        
        assert metrics.total_combats == 10
        assert metrics.victories == 8
        assert metrics.defeats == 2
        assert metrics.avg_damage_dealt == 200.0
        assert len(metrics.most_effective_weapons) == 1
        assert len(metrics.most_effective_tactics) == 1


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.fixture
    def complete_setup(self, temp_dirs):
        """Set up complete test environment."""
        # Create sample combat log
        sample_data = {
            "session_id": "integration_test_001",
            "start_time": "2025-08-01T12:00:00.000000",
            "end_time": "2025-08-01T12:01:00.000000",
            "duration": 60.0,
            "events": [
                {
                    "event_type": "ability_use",
                    "timestamp": "2025-08-01T12:00:10.000000",
                    "ability_name": "rifle_shot",
                    "target": "stormtrooper",
                    "damage_dealt": 200,
                    "damage_type": "physical",
                    "success": True,
                    "enemy_type": "stormtrooper",
                    "xp_gained": 150,
                    "player_health": 100,
                    "target_health": 100
                }
            ],
            "result": "victory",
            "player_build": {"weapon_type": "rifle", "role": "rifleman"},
            "enemy_type": "stormtrooper",
            "tactics_used": ["opening_burst"],
            "success_rate": 0.8,
            "damage_efficiency": 1.2
        }
        
        log_file = temp_dirs['combat_logs_dir'] / "combat_stats_integration_001.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2)
        
        # Create sample session
        session_data = {
            "session_id": "integration_session",
            "discord_id": "integration_user_123",
            "start_time": "2025-08-01T12:00:00.000000",
            "end_time": "2025-08-01T12:01:00.000000"
        }
        
        session_file = temp_dirs['session_logs_dir'] / "session_integration_001.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        
        return temp_dirs
    
    def test_complete_workflow(self, complete_setup):
        """Test the complete workflow from initialization to recommendations."""
        engine = CombatTacticsEngine(
            combat_logs_dir=str(complete_setup['combat_logs_dir']),
            tactics_data_dir=str(complete_setup['tactics_data_dir']),
            session_logs_dir=str(complete_setup['session_logs_dir'])
        )
        
        # Load and analyze data
        engine._load_combat_sessions()
        engine.analyze_combat_logs()
        
        # Get recommendations
        action = engine.get_optimal_action(
            enemy_type="stormtrooper",
            player_build={"weapon_type": "rifle"},
            situation="opening"
        )
        
        # Verify we got a valid action
        assert action in TacticalAction
        
        # Get metrics
        metrics = engine.get_combat_metrics()
        assert metrics.total_combats == 1
        assert metrics.victories == 1
        
        # Sync to sessions
        success = engine.sync_to_user_sessions("integration_user_123")
        assert success
        
        # Export report
        report_path = engine.export_tactical_report(format='json')
        assert Path(report_path).exists()
        
        print(f"[INTEGRATION] Complete workflow test passed")
        print(f"[INTEGRATION] Recommended action: {action.value}")
        print(f"[INTEGRATION] Total combats: {metrics.total_combats}")
        print(f"[INTEGRATION] Report exported: {report_path}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 