#!/usr/bin/env python3
"""Test script for Batch 064 - Discord Alert: Advanced Combat/Build Stats.

This test script validates all aspects of the Discord alerts system including:
- Combat stats tracking and performance analysis
- Build analysis and skill point ROI calculations
- Discord integration and alert formatting
- Performance analyzer coordination
- Integration with existing combat and build systems
"""

import json
import time
import random
import tempfile
import shutil
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

from modules.discord_alerts.combat_stats_tracker import CombatStatsTracker
from modules.discord_alerts.build_analyzer import BuildAnalyzer
from modules.discord_alerts.discord_notifier import DiscordNotifier
from modules.discord_alerts.performance_analyzer import PerformanceAnalyzer

class TestCombatStatsTracker:
    """Test suite for combat stats tracker functionality."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_results = []
        self.temp_dir = None
        
    def setup(self):
        """Setup test environment."""
        print("Setting up test environment...")
        
        # Create temporary directory for test logs
        self.temp_dir = tempfile.mkdtemp(prefix="discord_alerts_test_")
        
        # Override log directory for tests
        import modules.discord_alerts.combat_stats_tracker
        modules.discord_alerts.combat_stats_tracker.Path = lambda x: Path(self.temp_dir) / x
        
        print(f"Test directory: {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print("Cleaned up test directory")
    
    def run_test(self, test_name: str, test_func):
        """Run a test and record results."""
        print(f"\n--- Running Test: {test_name} ---")
        
        try:
            result = test_func()
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "message": "Test completed successfully"
            })
            print(f"✓ {test_name}: PASS")
            return result
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "message": str(e)
            })
            print(f"✗ {test_name}: FAIL - {e}")
            return None
    
    def test_combat_stats_tracker_initialization(self):
        """Test combat stats tracker initialization."""
        tracker = CombatStatsTracker(session_id="test_session")
        
        assert tracker.session_id == "test_session"
        assert tracker.total_damage == 0
        assert tracker.total_kills == 0
        assert len(tracker.combat_sessions) == 0
        assert tracker.current_session is None
        
        return tracker
    
    def test_combat_session_tracking(self):
        """Test combat session tracking functionality."""
        tracker = CombatStatsTracker(session_id="test_session")
        
        # Start combat session
        session_id = tracker.start_combat_session("Stormtrooper", 5)
        assert session_id is not None
        assert tracker.current_session is not None
        assert tracker.current_session.enemy_type == "Stormtrooper"
        assert tracker.current_session.enemy_level == 5
        
        # Record skill usage
        tracker.record_skill_usage("Rifle Shot", 25, "Stormtrooper", 1.5, "combat")
        assert tracker.current_session.total_damage == 25
        assert tracker.total_damage == 25
        
        # End combat session
        session_summary = tracker.end_combat_session("victory", 0)
        assert session_summary is not None
        assert tracker.current_session is None
        assert len(tracker.combat_sessions) == 1
        
        return tracker
    
    def test_skill_usage_tracking(self):
        """Test skill usage tracking functionality."""
        tracker = CombatStatsTracker(session_id="test_session")
        
        # Start combat session
        tracker.start_combat_session("Stormtrooper", 5)
        
        # Record multiple skill usages
        skills_data = [
            ("Rifle Shot", 25, "combat"),
            ("Pistol Shot", 15, "combat"),
            ("Heal", 0, "support"),
            ("Sniper Shot", 40, "combat")
        ]
        
        for skill_name, damage, skill_line in skills_data:
            tracker.record_skill_usage(skill_name, damage, "Stormtrooper", 2.0, skill_line)
        
        # Check skill usage tracking
        assert len(tracker.skills_usage) == 4
        assert tracker.skills_usage["Rifle Shot"].usage_count == 1
        assert tracker.skills_usage["Rifle Shot"].total_damage == 25
        assert tracker.skills_usage["Heal"].skill_line == "support"
        
        # Check skill line uptime
        assert tracker.skill_line_uptime["combat"] > 0
        assert tracker.skill_line_uptime["support"] > 0
        
        return tracker
    
    def test_enemy_kill_tracking(self):
        """Test enemy kill tracking functionality."""
        tracker = CombatStatsTracker(session_id="test_session")
        
        # Record enemy kills
        tracker.record_enemy_kill("Stormtrooper", 100)
        tracker.record_enemy_kill("Stormtrooper", 80)
        tracker.record_enemy_kill("Imperial Officer", 150)
        
        assert tracker.total_kills == 3
        assert tracker.kills_by_enemy_type["Stormtrooper"] == 2
        assert tracker.kills_by_enemy_type["Imperial Officer"] == 1
        assert tracker.damage_by_enemy_type["Stormtrooper"] == 180
        assert tracker.damage_by_enemy_type["Imperial Officer"] == 150
        
        return tracker
    
    def test_performance_summary_generation(self):
        """Test performance summary generation."""
        tracker = CombatStatsTracker(session_id="test_session")
        
        # Simulate combat session
        tracker.start_combat_session("Stormtrooper", 5)
        tracker.record_skill_usage("Rifle Shot", 25, "Stormtrooper", 1.5, "combat")
        tracker.record_skill_usage("Pistol Shot", 15, "Stormtrooper", 1.0, "combat")
        tracker.record_enemy_kill("Stormtrooper", 40)
        tracker.end_combat_session("victory", 0)
        
        # Get performance summary
        summary = tracker.get_performance_summary()
        
        assert summary.total_damage == 40
        assert summary.total_kills == 1
        assert summary.average_dps > 0
        assert len(summary.most_used_skills) > 0
        assert len(summary.least_used_skills) > 0
        assert summary.efficiency_score > 0
        
        return summary
    
    def test_skill_analysis_generation(self):
        """Test detailed skill analysis generation."""
        tracker = CombatStatsTracker(session_id="test_session")
        
        # Simulate combat session with multiple skills
        tracker.start_combat_session("Stormtrooper", 5)
        
        skills_data = [
            ("Rifle Shot", 25, "combat"),
            ("Rifle Shot", 30, "combat"),
            ("Pistol Shot", 15, "combat"),
            ("Heal", 0, "support"),
            ("Sniper Shot", 40, "combat")
        ]
        
        for skill_name, damage, skill_line in skills_data:
            tracker.record_skill_usage(skill_name, damage, "Stormtrooper", 2.0, skill_line)
        
        tracker.end_combat_session("victory", 0)
        
        # Get skill analysis
        analysis = tracker.get_skill_analysis()
        
        assert "skill_usage" in analysis
        assert "skill_line_analysis" in analysis
        assert "effectiveness_ranking" in analysis
        
        # Check skill usage data
        skill_usage = analysis["skill_usage"]
        assert "Rifle Shot" in skill_usage
        assert skill_usage["Rifle Shot"]["usage_count"] == 2
        assert skill_usage["Rifle Shot"]["total_damage"] == 55
        
        # Check effectiveness ranking
        effectiveness = analysis["effectiveness_ranking"]
        assert len(effectiveness) > 0
        
        return analysis
    
    def test_session_data_saving(self):
        """Test session data saving functionality."""
        tracker = CombatStatsTracker(session_id="test_session")
        
        # Simulate combat session
        tracker.start_combat_session("Stormtrooper", 5)
        tracker.record_skill_usage("Rifle Shot", 25, "Stormtrooper", 1.5, "combat")
        tracker.record_enemy_kill("Stormtrooper", 25)
        tracker.end_combat_session("victory", 0)
        
        # Save session data
        saved_file = tracker.save_session_data()
        
        assert Path(saved_file).exists()
        
        # Load and verify saved data
        with open(saved_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["session_id"] == "test_session"
        assert saved_data["total_damage"] == 25
        assert saved_data["total_kills"] == 1
        assert "combat_sessions" in saved_data
        assert "skill_usage" in saved_data
        
        return saved_file
    
    def test_session_end_summary(self):
        """Test session end summary generation."""
        tracker = CombatStatsTracker(session_id="test_session")
        
        # Simulate multiple combat sessions
        for i in range(3):
            tracker.start_combat_session(f"Enemy_{i}", i + 1)
            tracker.record_skill_usage("Rifle Shot", 25 + i * 5, f"Enemy_{i}", 1.5, "combat")
            tracker.record_enemy_kill(f"Enemy_{i}", 25 + i * 5)
            tracker.end_combat_session("victory", 0)
        
        # End session and get summary
        final_summary = tracker.end_session()
        
        assert final_summary["session_id"] == "test_session"
        assert final_summary["total_damage"] > 0
        assert final_summary["total_kills"] == 3
        assert "performance_summary" in final_summary
        assert "skill_analysis" in final_summary
        assert "saved_file" in final_summary
        
        return final_summary


class TestBuildAnalyzer:
    """Test suite for build analyzer functionality."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_results = []
        self.temp_dir = None
        
    def setup(self):
        """Setup test environment."""
        print("Setting up test environment...")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="build_analyzer_test_")
        
        # Create test build data
        self.test_build_data = {
            "build_summary": "Rifleman + Medic | Weapons: rifle, pistol | Combat Style: Hybrid",
            "abilities_granted": ["Rifle Shot", "Pistol Shot", "Heal", "Cure Poison", "Sniper Shot"],
            "profession_boxes": ["rifleman", "medic"],
            "weapons_supported": ["rifle", "pistol"],
            "combat_style": "hybrid",
            "minimum_attack_distance": 3
        }
        
        # Save test build file
        self.test_build_file = Path(self.temp_dir) / "test_build.json"
        with open(self.test_build_file, 'w') as f:
            json.dump(self.test_build_data, f, indent=2)
        
        print(f"Test directory: {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print("Cleaned up test directory")
    
    def run_test(self, test_name: str, test_func):
        """Run a test and record results."""
        print(f"\n--- Running Test: {test_name} ---")
        
        try:
            result = test_func()
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "message": "Test completed successfully"
            })
            print(f"✓ {test_name}: PASS")
            return result
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "message": str(e)
            })
            print(f"✗ {test_name}: FAIL - {e}")
            return None
    
    def test_build_analyzer_initialization(self):
        """Test build analyzer initialization."""
        analyzer = BuildAnalyzer()
        
        assert analyzer.current_build is None
        assert analyzer.build_data == {}
        assert len(analyzer.skill_point_costs) > 0
        assert len(analyzer.skill_lines) > 0
        
        return analyzer
    
    def test_build_loading_from_file(self):
        """Test loading build from file."""
        analyzer = BuildAnalyzer()
        
        # Load build from test file
        build_data = analyzer.load_build_from_file(str(self.test_build_file))
        
        assert build_data is not None
        assert analyzer.current_build is not None
        assert analyzer.current_build["build_summary"] == self.test_build_data["build_summary"]
        assert len(analyzer.current_build["abilities_granted"]) == 5
        
        return analyzer
    
    @patch('modules.discord_alerts.build_analyzer.SkillCalculatorParser')
    def test_build_loading_from_url(self, mock_parser):
        """Test loading build from URL."""
        analyzer = BuildAnalyzer()
        
        # Mock the parser
        mock_parser_instance = Mock()
        mock_parser_instance.parse_skill_calculator_link.return_value = self.test_build_data
        mock_parser.return_value = mock_parser_instance
        
        # Load build from URL
        build_data = analyzer.load_build_from_link("https://swgr.org/skill-calculator/test")
        
        assert build_data is not None
        assert analyzer.current_build is not None
        assert analyzer.current_build["build_summary"] == self.test_build_data["build_summary"]
        
        return analyzer
    
    def test_skill_point_roi_analysis(self):
        """Test skill point ROI analysis."""
        analyzer = BuildAnalyzer()
        analyzer.load_build_from_file(str(self.test_build_file))
        
        # Create test combat data
        combat_data = {
            "skill_usage": {
                "Rifle Shot": {"total_damage": 500, "usage_count": 10},
                "Pistol Shot": {"total_damage": 300, "usage_count": 8},
                "Heal": {"total_damage": 0, "usage_count": 5},
                "Sniper Shot": {"total_damage": 800, "usage_count": 4}
            }
        }
        
        # Analyze ROI
        roi_analysis = analyzer.analyze_skill_point_roi(combat_data)
        
        assert len(roi_analysis) == 4
        assert roi_analysis[0].skill_name in ["Rifle Shot", "Pistol Shot", "Sniper Shot", "Heal"]
        assert all(hasattr(roi, 'roi_score') for roi in roi_analysis)
        assert all(hasattr(roi, 'efficiency_rating') for roi in roi_analysis)
        
        return roi_analysis
    
    def test_build_efficiency_analysis(self):
        """Test build efficiency analysis."""
        analyzer = BuildAnalyzer()
        analyzer.load_build_from_file(str(self.test_build_file))
        
        # Create test combat data
        combat_data = {
            "skill_usage": {
                "Rifle Shot": {"total_damage": 500, "usage_count": 10},
                "Pistol Shot": {"total_damage": 300, "usage_count": 8},
                "Heal": {"total_damage": 0, "usage_count": 5},
                "Sniper Shot": {"total_damage": 800, "usage_count": 4}
            },
            "session_duration": 300.0
        }
        
        # Analyze build efficiency
        build_analysis = analyzer.analyze_build_efficiency(combat_data)
        
        assert build_analysis is not None
        assert build_analysis.build_name == self.test_build_data["build_summary"]
        assert build_analysis.total_skill_points > 0
        assert build_analysis.skills_analyzed == 4
        assert build_analysis.average_roi > 0
        assert len(build_analysis.most_efficient_skills) > 0
        assert len(build_analysis.least_efficient_skills) > 0
        assert len(build_analysis.optimization_recommendations) > 0
        
        return build_analysis
    
    def test_skill_line_performance_analysis(self):
        """Test skill line performance analysis."""
        analyzer = BuildAnalyzer()
        analyzer.load_build_from_file(str(self.test_build_file))
        
        # Create test combat data with skill line analysis
        combat_data = {
            "skill_usage": {
                "Rifle Shot": {"total_damage": 500, "usage_count": 10},
                "Pistol Shot": {"total_damage": 300, "usage_count": 8},
                "Heal": {"total_damage": 0, "usage_count": 5}
            },
            "skill_line_analysis": {
                "combat": {
                    "skills_in_line": ["Rifle Shot", "Pistol Shot"],
                    "uptime_percentage": 60.0
                },
                "support": {
                    "skills_in_line": ["Heal"],
                    "uptime_percentage": 20.0
                }
            },
            "session_duration": 300.0
        }
        
        # Analyze skill line performance
        skill_line_analysis = analyzer.analyze_skill_line_performance(combat_data)
        
        assert len(skill_line_analysis) > 0
        assert all(hasattr(analysis, 'skill_line') for analysis in skill_line_analysis)
        assert all(hasattr(analysis, 'total_skill_points') for analysis in skill_line_analysis)
        assert all(hasattr(analysis, 'efficiency_score') for analysis in skill_line_analysis)
        
        return skill_line_analysis


class TestDiscordNotifier:
    """Test suite for Discord notifier functionality."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_results = []
        
    def run_test(self, test_name: str, test_func):
        """Run a test and record results."""
        print(f"\n--- Running Test: {test_name} ---")
        
        try:
            result = test_func()
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "message": "Test completed successfully"
            })
            print(f"✓ {test_name}: PASS")
            return result
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "message": str(e)
            })
            print(f"✗ {test_name}: FAIL - {e}")
            return None
    
    def test_discord_notifier_initialization(self):
        """Test Discord notifier initialization."""
        notifier = DiscordNotifier(webhook_url="test_url")
        
        assert notifier.webhook_url == "test_url"
        assert notifier.max_embed_fields == 25
        assert notifier.max_field_length == 1024
        
        return notifier
    
    def test_performance_embed_creation(self):
        """Test performance embed creation."""
        notifier = DiscordNotifier()
        
        # Create test performance data
        performance_data = {
            "session_id": "test_session",
            "performance_summary": {
                "total_damage": 1500,
                "total_kills": 5,
                "session_duration": 300.0,
                "average_dps": 5.0,
                "most_used_skills": [("Rifle Shot", 10), ("Pistol Shot", 8)],
                "least_used_skills": [("Heal", 2), ("Sniper Shot", 1)],
                "skill_line_uptime": {"combat": 70.0, "support": 30.0},
                "efficiency_score": 75.5
            }
        }
        
        # Create embed
        embed = notifier._create_performance_embed(performance_data)
        
        assert embed.title == "⚔️ Combat Performance Report"
        assert embed.description == "Session: test_session"
        assert len(embed.fields) > 0
        
        return embed
    
    def test_build_analysis_embed_creation(self):
        """Test build analysis embed creation."""
        notifier = DiscordNotifier()
        
        # Create test build analysis data
        build_analysis = {
            "build_name": "Rifleman + Medic Hybrid",
            "total_skill_points": 128,
            "skills_analyzed": 4,
            "average_roi": 450.5,
            "build_efficiency_score": 78.5,
            "most_efficient_skills": [
            ],
            "least_efficient_skills": [
            ],
            "unused_skills": ["Cure Poison"],
            "optimization_recommendations": [
                "Consider using 1 unused skills from your build",
                "Build efficiency is good - minor optimizations only"
            ]
        }
        
        # Create embed
        embed = notifier._create_build_analysis_embed(build_analysis)
        
        assert embed.title == "🔧 Build Analysis Report"
        assert embed.description == "Rifleman + Medic Hybrid"
        assert len(embed.fields) > 0
        
        return embed
    
    def test_simple_alert_sending(self):
        """Test simple alert sending."""
        notifier = DiscordNotifier()
        
        # Test with mock webhook
        with patch('modules.discord_alerts.discord_notifier.discord.SyncWebhook') as mock_webhook:
            mock_webhook_instance = Mock()
            mock_webhook.from_url.return_value = mock_webhook_instance
            
            success = notifier.send_simple_alert("Test Alert", "This is a test message")
            
            # Should fail without proper webhook URL, but not crash
            assert isinstance(success, bool)
        
        return True


class TestPerformanceAnalyzer:
    """Test suite for performance analyzer functionality."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_results = []
        self.temp_dir = None
        
    def setup(self):
        """Setup test environment."""
        print("Setting up test environment...")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="performance_analyzer_test_")
        
        print(f"Test directory: {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print("Cleaned up test directory")
    
    def run_test(self, test_name: str, test_func):
        """Run a test and record results."""
        print(f"\n--- Running Test: {test_name} ---")
        
        try:
            result = test_func()
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "message": "Test completed successfully"
            })
            print(f"✓ {test_name}: PASS")
            return result
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "message": str(e)
            })
            print(f"✗ {test_name}: FAIL - {e}")
            return None
    
    def test_performance_analyzer_initialization(self):
        """Test performance analyzer initialization."""
        analyzer = PerformanceAnalyzer()
        
        assert analyzer.combat_tracker is not None
        assert analyzer.build_analyzer is not None
        assert analyzer.discord_notifier is not None
        assert analyzer.auto_discord_alerts is True
        assert analyzer.save_reports is True
        
        return analyzer
    
    def test_analysis_session_management(self):
        """Test analysis session management."""
        analyzer = PerformanceAnalyzer()
        
        # Start analysis session
        session_id = analyzer.start_analysis_session("test_session")
        assert session_id == "test_session"
        
        # Check status
        status = analyzer.get_analysis_status()
        assert status["session_active"] is False  # No active combat session
        assert status["build_loaded"] is False
        assert status["discord_configured"] is False
        
        return analyzer
    
    def test_combat_event_recording(self):
        """Test combat event recording."""
        analyzer = PerformanceAnalyzer()
        analyzer.start_analysis_session("test_session")
        
        # Record combat events
        analyzer.record_combat_event("combat_start", enemy_type="Stormtrooper", enemy_level=5)
        analyzer.record_combat_event("skill_usage", skill_name="Rifle Shot", damage_dealt=25, 
                                   target="Stormtrooper", cooldown=1.5, skill_line="combat")
        analyzer.record_combat_event("enemy_kill", enemy_type="Stormtrooper", damage_dealt=25)
        analyzer.record_combat_event("combat_end", result="victory", enemy_hp_remaining=0)
        
        # Check status
        status = analyzer.get_analysis_status()
        assert status["total_damage"] == 25
        assert status["total_kills"] == 1
        
        return analyzer
    
    def test_build_loading_for_analysis(self):
        """Test build loading for analysis."""
        analyzer = PerformanceAnalyzer()
        
        # Create test build file
        test_build_file = Path(self.temp_dir) / "test_build.json"
        test_build_data = {
            "build_summary": "Test Build",
            "abilities_granted": ["Rifle Shot", "Pistol Shot", "Heal"]
        }
        
        with open(test_build_file, 'w') as f:
            json.dump(test_build_data, f, indent=2)
        
        # Load build
        success = analyzer.load_build_for_analysis(build_file=str(test_build_file))
        assert success is True
        
        # Check status
        status = analyzer.get_analysis_status()
        assert status["build_loaded"] is True
        
        return analyzer
    
    def test_comprehensive_report_generation(self):
        """Test comprehensive report generation."""
        analyzer = PerformanceAnalyzer()
        analyzer.start_analysis_session("test_session")
        
        # Simulate combat session
        analyzer.record_combat_event("combat_start", enemy_type="Stormtrooper", enemy_level=5)
        analyzer.record_combat_event("skill_usage", skill_name="Rifle Shot", damage_dealt=25, 
                                   target="Stormtrooper", cooldown=1.5, skill_line="combat")
        analyzer.record_combat_event("enemy_kill", enemy_type="Stormtrooper", damage_dealt=25)
        analyzer.record_combat_event("combat_end", result="victory", enemy_hp_remaining=0)
        
        # Generate report
        report = analyzer.generate_comprehensive_report()
        
        assert report.session_id == "test_session"
        assert report.combat_performance is not None
        assert report.build_analysis is None  # No build loaded
        assert len(report.recommendations) > 0
        assert isinstance(report.discord_sent, bool)
        
        return report
    
    def test_session_performance_analysis(self):
        """Test session performance analysis."""
        analyzer = PerformanceAnalyzer()
        
        # Create test session data
        session_data = {
            "session_id": "test_session",
            "performance_summary": {
                "total_damage": 1500,
                "total_kills": 5,
                "session_duration": 300.0,
                "average_dps": 5.0,
                "efficiency_score": 75.5
            },
            "skill_analysis": {
                "skill_usage": {
                    "Rifle Shot": {"total_damage": 800, "usage_count": 10},
                    "Pistol Shot": {"total_damage": 400, "usage_count": 8},
                    "Heal": {"total_damage": 0, "usage_count": 3}
                }
            }
        }
        
        # Analyze session
        analysis = analyzer.analyze_session_performance(session_data)
        
        assert analysis["combat_performance"] == session_data
        assert analysis["build_analysis"] is None
        assert len(analysis["recommendations"]) > 0
        
        return analysis
    
    def test_discord_integration_test(self):
        """Test Discord integration."""
        analyzer = PerformanceAnalyzer()
        
        # Test Discord integration (should fail without proper configuration)
        success = analyzer.test_discord_integration()
        assert isinstance(success, bool)
        
        return success


class TestIntegration:
    """Integration tests for the complete Discord alerts system."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_results = []
        self.temp_dir = None
        
    def setup(self):
        """Setup test environment."""
        print("Setting up integration test environment...")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="integration_test_")
        
        print(f"Test directory: {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print("Cleaned up test directory")
    
    def run_test(self, test_name: str, test_func):
        """Run a test and record results."""
        print(f"\n--- Running Integration Test: {test_name} ---")
        
        try:
            result = test_func()
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "message": "Test completed successfully"
            })
            print(f"✓ {test_name}: PASS")
            return result
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "message": str(e)
            })
            print(f"✗ {test_name}: FAIL - {e}")
            return None
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Initialize performance analyzer
        analyzer = PerformanceAnalyzer()
        analyzer.start_analysis_session("integration_test")
        
        # Load test build
        test_build_file = Path(self.temp_dir) / "test_build.json"
        test_build_data = {
            "build_summary": "Rifleman + Medic Hybrid",
            "abilities_granted": ["Rifle Shot", "Pistol Shot", "Heal", "Sniper Shot"],
            "profession_boxes": ["rifleman", "medic"],
            "weapons_supported": ["rifle", "pistol"],
            "combat_style": "hybrid"
        }
        
        with open(test_build_file, 'w') as f:
            json.dump(test_build_data, f, indent=2)
        
        analyzer.load_build_for_analysis(build_file=str(test_build_file))
        
        # Simulate combat session
        combat_events = [
            ("combat_start", {"enemy_type": "Stormtrooper", "enemy_level": 5}),
            ("skill_usage", {"skill_name": "Rifle Shot", "damage_dealt": 25, 
                           "target": "Stormtrooper", "cooldown": 1.5, "skill_line": "combat"}),
            ("skill_usage", {"skill_name": "Pistol Shot", "damage_dealt": 15, 
                           "target": "Stormtrooper", "cooldown": 1.0, "skill_line": "combat"}),
            ("skill_usage", {"skill_name": "Heal", "damage_dealt": 0, 
                           "target": "Self", "cooldown": 2.0, "skill_line": "support"}),
            ("enemy_kill", {"enemy_type": "Stormtrooper", "damage_dealt": 40}),
            ("combat_end", {"result": "victory", "enemy_hp_remaining": 0})
        ]
        
        for event_type, event_data in combat_events:
            analyzer.record_combat_event(event_type, **event_data)
        
        # Generate comprehensive report
        report = analyzer.generate_comprehensive_report()
        
        # Verify report structure
        assert report.session_id == "integration_test"
        assert report.combat_performance is not None
        assert report.build_analysis is not None
        assert len(report.recommendations) > 0
        assert report.timestamp is not None
        
        # Verify combat performance data
        combat_data = report.combat_performance
        assert combat_data["total_damage"] == 40
        assert combat_data["total_kills"] == 1
        
        # Verify build analysis data
        build_data = report.build_analysis
        assert build_data["build_name"] == "Rifleman + Medic Hybrid"
        assert build_data["skills_analyzed"] == 3  # Rifle Shot, Pistol Shot, Heal
        
        return report
    
    def test_discord_alert_generation(self):
        """Test Discord alert generation with mock data."""
        # Create test performance data
        performance_data = {
            "session_id": "discord_test",
            "performance_summary": {
                "total_damage": 2500,
                "total_kills": 8,
                "session_duration": 600.0,
                "average_dps": 4.17,
                "most_used_skills": [("Rifle Shot", 15), ("Pistol Shot", 12), ("Sniper Shot", 5)],
                "least_used_skills": [("Heal", 3), ("Cure Poison", 1)],
                "skill_line_uptime": {"combat": 75.0, "support": 25.0},
                "efficiency_score": 82.5
            },
            "skill_analysis": {
                "skill_usage": {
                    "Rifle Shot": {"total_damage": 1200, "usage_count": 15, "average_damage": 80.0},
                    "Pistol Shot": {"total_damage": 800, "usage_count": 12, "average_damage": 66.7},
                    "Sniper Shot": {"total_damage": 500, "usage_count": 5, "average_damage": 100.0}
                }
            }
        }
        
        # Create test build analysis data
        build_analysis = {
            "build_name": "Rifleman + Medic Hybrid",
            "total_skill_points": 128,
            "skills_analyzed": 3,
            "average_roi": 520.5,
            "build_efficiency_score": 78.5,
            "most_efficient_skills": [
            ],
            "least_efficient_skills": [
            ],
            "unused_skills": ["Cure Poison"],
            "optimization_recommendations": [
                "Consider using 1 unused skills from your build",
                "Build efficiency is good - minor optimizations only"
            ]
        }
        
        # Test Discord notifier
        notifier = DiscordNotifier()
        
        # Create embeds
        performance_embed = notifier._create_performance_embed(performance_data)
        build_embed = notifier._create_build_analysis_embed(build_analysis)
        
        assert performance_embed.title == "⚔️ Combat Performance Report"
        assert build_embed.title == "🔧 Build Analysis Report"
        assert len(performance_embed.fields) > 0
        assert len(build_embed.fields) > 0
        
        return {
            "performance_embed": performance_embed,
            "build_embed": build_embed
        }


def run_tests():
    """Run all test suites."""
    print("🚀 Starting Batch 064 - Discord Alert Tests")
    print("=" * 60)
    
    # Initialize test suites
    combat_tests = TestCombatStatsTracker()
    build_tests = TestBuildAnalyzer()
    discord_tests = TestDiscordNotifier()
    performance_tests = TestPerformanceAnalyzer()
    integration_tests = TestIntegration()
    
    # Setup test environments
    combat_tests.setup()
    build_tests.setup()
    performance_tests.setup()
    integration_tests.setup()
    
    try:
        # Run combat stats tracker tests
        print("\n📊 Testing Combat Stats Tracker...")
        combat_tests.run_test("Initialization", combat_tests.test_combat_stats_tracker_initialization)
        combat_tests.run_test("Session Tracking", combat_tests.test_combat_session_tracking)
        combat_tests.run_test("Skill Usage Tracking", combat_tests.test_skill_usage_tracking)
        combat_tests.run_test("Enemy Kill Tracking", combat_tests.test_enemy_kill_tracking)
        combat_tests.run_test("Performance Summary", combat_tests.test_performance_summary_generation)
        combat_tests.run_test("Skill Analysis", combat_tests.test_skill_analysis_generation)
        combat_tests.run_test("Session Data Saving", combat_tests.test_session_data_saving)
        combat_tests.run_test("Session End Summary", combat_tests.test_session_end_summary)
        
        # Run build analyzer tests
        print("\n🔧 Testing Build Analyzer...")
        build_tests.run_test("Initialization", build_tests.test_build_analyzer_initialization)
        build_tests.run_test("Build Loading from File", build_tests.test_build_loading_from_file)
        build_tests.run_test("Build Loading from URL", build_tests.test_build_loading_from_url)
        build_tests.run_test("Skill Point ROI Analysis", build_tests.test_skill_point_roi_analysis)
        build_tests.run_test("Build Efficiency Analysis", build_tests.test_build_efficiency_analysis)
        build_tests.run_test("Skill Line Performance", build_tests.test_skill_line_performance_analysis)
        
        # Run Discord notifier tests
        print("\n📢 Testing Discord Notifier...")
        discord_tests.run_test("Initialization", discord_tests.test_discord_notifier_initialization)
        discord_tests.run_test("Performance Embed Creation", discord_tests.test_performance_embed_creation)
        discord_tests.run_test("Build Analysis Embed Creation", discord_tests.test_build_analysis_embed_creation)
        discord_tests.run_test("Simple Alert Sending", discord_tests.test_simple_alert_sending)
        
        # Run performance analyzer tests
        print("\n📈 Testing Performance Analyzer...")
        performance_tests.run_test("Initialization", performance_tests.test_performance_analyzer_initialization)
        performance_tests.run_test("Session Management", performance_tests.test_analysis_session_management)
        performance_tests.run_test("Combat Event Recording", performance_tests.test_combat_event_recording)
        performance_tests.run_test("Build Loading", performance_tests.test_build_loading_for_analysis)
        performance_tests.run_test("Comprehensive Report", performance_tests.test_comprehensive_report_generation)
        performance_tests.run_test("Session Analysis", performance_tests.test_session_performance_analysis)
        performance_tests.run_test("Discord Integration", performance_tests.test_discord_integration_test)
        
        # Run integration tests
        print("\n🔗 Testing Integration...")
        integration_tests.run_test("End-to-End Workflow", integration_tests.test_end_to_end_workflow)
        integration_tests.run_test("Discord Alert Generation", integration_tests.test_discord_alert_generation)
        
    finally:
        # Cleanup test environments
        combat_tests.teardown()
        build_tests.teardown()
        performance_tests.teardown()
        integration_tests.teardown()
    
    # Print test results
    print("\n" + "=" * 60)
    print("📋 Test Results Summary")
    print("=" * 60)
    
    all_results = (
        combat_tests.test_results + 
        build_tests.test_results + 
        discord_tests.test_results + 
        performance_tests.test_results + 
        integration_tests.test_results
    )
    
    passed = sum(1 for result in all_results if result["status"] == "PASS")
    failed = sum(1 for result in all_results if result["status"] == "FAIL")
    total = len(all_results)
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for result in all_results:
            if result["status"] == "FAIL":
                print(f"  - {result['test']}: {result['message']}")
    
    print("\n🎉 Batch 064 - Discord Alert Tests Complete!")
    return all_results


if __name__ == "__main__":
    run_tests() 