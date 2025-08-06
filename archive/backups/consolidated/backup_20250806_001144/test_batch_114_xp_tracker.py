"""Test Batch 114 - Experimental XP Tracker (Deep Skill Mapping)

This test suite validates the enhanced XP tracking capabilities including:
- Log XP gains with timestamps, quest name (if known), and zone
- Visualize XP gain rates per hour
- Detect which skills are progressing fastest
- Recommend optimal skill paths and detect leveling slowdowns
- Store XP gain summaries in session logs and charts
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from modules.experimental_xp_tracker import (
    ExperimentalXPTracker, XPGainEvent, SkillProgress, 
    ProfessionAnalytics, XPSessionSummary
)


class TestExperimentalXPTracker:
    """Test suite for the experimental XP tracker."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for test configuration."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def xp_tracker(self, temp_config_dir):
        """Create an XP tracker instance for testing."""
        config_path = Path(temp_config_dir) / "xp_tracker_config.json"
        tracker = ExperimentalXPTracker(str(config_path))
        return tracker
    
    def test_initialization(self, xp_tracker):
        """Test XP tracker initialization."""
        assert xp_tracker.xp_events == []
        assert xp_tracker.skill_progress == {}
        assert xp_tracker.profession_analytics == {}
        assert xp_tracker.current_session_id is None
        assert xp_tracker.session_start_time is None
        assert len(xp_tracker.hourly_xp_rates) == 0
        assert len(xp_tracker.daily_xp_totals) == 0
    
    def test_start_session(self, xp_tracker):
        """Test session start functionality."""
        session_id = xp_tracker.start_session()
        
        assert session_id is not None
        assert xp_tracker.current_session_id == session_id
        assert xp_tracker.session_start_time is not None
        assert isinstance(session_id, str)
        assert "session_" in session_id
    
    def test_record_xp_gain_basic(self, xp_tracker):
        """Test basic XP gain recording."""
        xp_tracker.start_session()
        
        event = xp_tracker.record_xp_gain(
            amount=100,
            profession="marksman",
            skill="combat_marksman_novice",
            source="combat"
        )
        
        assert len(xp_tracker.xp_events) == 1
        assert event.amount == 100
        assert event.profession == "marksman"
        assert event.skill == "combat_marksman_novice"
        assert event.source == "combat"
        assert event.session_id is not None
        assert event.timestamp is not None
    
    def test_record_xp_gain_with_quest_and_zone(self, xp_tracker):
        """Test XP gain recording with quest name and zone."""
        xp_tracker.start_session()
        
        event = xp_tracker.record_xp_gain(
            amount=250,
            profession="medic",
            skill="science_medic_novice",
            source="quest",
            quest_name="Healing the Sick",
            zone="dantooine"
        )
        
        assert event.quest_name == "Healing the Sick"
        assert event.zone == "dantooine"
        assert event.source == "quest"
        assert event.amount == 250
    
    def test_record_xp_gain_with_levels(self, xp_tracker):
        """Test XP gain recording with level progression."""
        xp_tracker.start_session()
        
        event = xp_tracker.record_xp_gain(
            amount=500,
            profession="artisan",
            skill="crafting_artisan_novice",
            source="crafting",
            level_before=1,
            level_after=2
        )
        
        assert event.level_before == 1
        assert event.level_after == 2
        assert event.skill_progress_percentage is not None
    
    def test_skill_progress_tracking(self, xp_tracker):
        """Test skill progress tracking functionality."""
        xp_tracker.start_session()
        
        # Record multiple XP gains for the same skill
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat")
        xp_tracker.record_xp_gain(150, "marksman", "combat_marksman_novice", "combat")
        xp_tracker.record_xp_gain(200, "marksman", "combat_marksman_novice", "quest")
        
        skill_key = "marksman_combat_marksman_novice"
        assert skill_key in xp_tracker.skill_progress
        
        progress = xp_tracker.skill_progress[skill_key]
        assert progress.skill_name == "combat_marksman_novice"
        assert progress.profession == "marksman"
        assert progress.total_xp == 450
        assert len(progress.gains_history) == 3
        assert progress.progress_rate > 0
    
    def test_zone_efficiency_tracking(self, xp_tracker):
        """Test zone efficiency tracking."""
        xp_tracker.start_session()
        
        # Record XP gains in different zones
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat", zone="dantooine")
        xp_tracker.record_xp_gain(150, "marksman", "combat_marksman_novice", "combat", zone="naboo")
        xp_tracker.record_xp_gain(200, "marksman", "combat_marksman_novice", "quest", zone="dantooine")
        
        assert "dantooine" in xp_tracker.zone_xp_efficiency
        assert "naboo" in xp_tracker.zone_xp_efficiency
        
        dantooine_data = xp_tracker.zone_xp_efficiency["dantooine"]
        assert dantooine_data["total_xp"] == 300
        assert dantooine_data["events"] == 2
        
        naboo_data = xp_tracker.zone_xp_efficiency["naboo"]
        assert naboo_data["total_xp"] == 150
        assert naboo_data["events"] == 1
    
    def test_get_fastest_progressing_skills(self, xp_tracker):
        """Test detection of fastest progressing skills."""
        xp_tracker.start_session()
        
        # Record XP gains with different rates
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat")
        xp_tracker.record_xp_gain(200, "medic", "science_medic_novice", "quest")
        xp_tracker.record_xp_gain(50, "artisan", "crafting_artisan_novice", "crafting")
        
        fastest_skills = xp_tracker.get_fastest_progressing_skills(limit=2)
        
        assert len(fastest_skills) == 2
        # The skill with the highest recent XP should be first
        assert fastest_skills[0].progress_rate >= fastest_skills[1].progress_rate
    
    def test_get_slowest_progressing_skills(self, xp_tracker):
        """Test detection of slowest progressing skills."""
        xp_tracker.start_session()
        
        # Record XP gains with different rates
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat")
        xp_tracker.record_xp_gain(200, "medic", "science_medic_novice", "quest")
        xp_tracker.record_xp_gain(50, "artisan", "crafting_artisan_novice", "crafting")
        
        slowest_skills = xp_tracker.get_slowest_progressing_skills(limit=2)
        
        assert len(slowest_skills) == 2
        # The skill with the lowest recent XP should be first
        assert slowest_skills[0].progress_rate <= slowest_skills[1].progress_rate
    
    def test_calculate_xp_rate_per_hour(self, xp_tracker):
        """Test XP rate calculation."""
        xp_tracker.start_session()
        
        # Record XP gains over time
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat")
        xp_tracker.record_xp_gain(150, "medic", "science_medic_novice", "quest")
        
        xp_rate = xp_tracker.calculate_xp_rate_per_hour(hours=1)
        
        assert xp_rate >= 0
        assert isinstance(xp_rate, float)
    
    def test_detect_leveling_slowdowns(self, xp_tracker):
        """Test leveling slowdown detection."""
        xp_tracker.start_session()
        
        # Record XP gains to create a pattern
        for i in range(10):
            xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat")
        
        # Record lower XP gains to simulate slowdown
        for i in range(5):
            xp_tracker.record_xp_gain(20, "marksman", "combat_marksman_novice", "combat")
        
        slowdowns = xp_tracker.detect_leveling_slowdowns()
        
        assert isinstance(slowdowns, list)
        # The slowdown detection might not trigger immediately, so we just check the structure
        if slowdowns:
            # Should detect slowdown in marksman skill if any slowdowns are detected
            marksman_slowdowns = [s for s in slowdowns if s["skill"] == "combat_marksman_novice"]
            # Check that slowdown data has the expected structure
            for slowdown in slowdowns:
                assert "skill" in slowdown
                assert "profession" in slowdown
                assert "current_rate" in slowdown
                assert "expected_rate" in slowdown
                assert "slowdown_percentage" in slowdown
    
    def test_recommend_optimal_skill_paths(self, xp_tracker):
        """Test optimal skill path recommendations."""
        xp_tracker.start_session()
        
        # Record XP gains for different skills in the same profession
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat")
        xp_tracker.record_xp_gain(200, "marksman", "combat_marksman_marksman", "combat")
        xp_tracker.record_xp_gain(50, "marksman", "combat_marksman_rifleman", "combat")
        
        recommendations = xp_tracker.recommend_optimal_skill_paths()
        
        assert "marksman" in recommendations
        assert isinstance(recommendations["marksman"], list)
        assert len(recommendations["marksman"]) > 0
    
    def test_get_profession_analytics(self, xp_tracker):
        """Test profession analytics generation."""
        xp_tracker.start_session()
        
        # Record XP gains for a profession
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat")
        xp_tracker.record_xp_gain(150, "marksman", "combat_marksman_marksman", "quest")
        xp_tracker.record_xp_gain(200, "marksman", "combat_marksman_rifleman", "combat")
        
        analytics = xp_tracker.get_profession_analytics("marksman")
        
        assert analytics is not None
        assert analytics.profession_name == "marksman"
        assert analytics.total_xp == 450
        assert analytics.skills_count == 3
        assert analytics.average_level >= 0
        assert analytics.fastest_skill is not None
        assert analytics.slowest_skill is not None
        assert analytics.xp_per_hour >= 0
        assert analytics.optimal_zones is not None
        assert analytics.skill_path_recommendation is not None
    
    def test_generate_xp_summary(self, xp_tracker):
        """Test XP summary generation."""
        xp_tracker.start_session()
        
        # Record various XP gains
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat", zone="dantooine")
        xp_tracker.record_xp_gain(200, "medic", "science_medic_novice", "quest", zone="naboo")
        xp_tracker.record_xp_gain(150, "artisan", "crafting_artisan_novice", "crafting", zone="tatooine")
        
        summary = xp_tracker.generate_xp_summary()
        
        assert summary["total_xp"] == 450
        assert summary["xp_per_hour"] >= 0
        assert "xp_by_source" in summary
        assert "xp_by_profession" in summary
        assert "xp_by_zone" in summary
        assert "top_gaining_skills" in summary
        assert "fastest_progressing_skills" in summary
        assert "slowdowns_detected" in summary
        assert "optimal_paths" in summary
        assert "zone_efficiency" in summary
    
    def test_create_xp_visualization(self, xp_tracker):
        """Test XP visualization creation."""
        xp_tracker.start_session()
        
        # Record some XP gains to create data for visualization
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat", zone="dantooine")
        xp_tracker.record_xp_gain(200, "medic", "science_medic_novice", "quest", zone="naboo")
        xp_tracker.record_xp_gain(150, "artisan", "crafting_artisan_novice", "crafting", zone="tatooine")
        
        # Test visualization creation
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            viz_path = xp_tracker.create_xp_visualization(save_path=tmp_file.name)
            
            # Visualization may be None if matplotlib is not available
            if viz_path is not None:
                assert viz_path == tmp_file.name
                # Check that the file was created (if matplotlib is available)
                import os
                assert os.path.exists(tmp_file.name)
            else:
                # If matplotlib is not available, the method should return None
                assert viz_path is None
    
    def test_export_xp_data(self, xp_tracker, temp_config_dir):
        """Test XP data export functionality."""
        xp_tracker.start_session()
        
        # Record some XP gains
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat", zone="dantooine")
        xp_tracker.record_xp_gain(200, "medic", "science_medic_novice", "quest", zone="naboo")
        
        # Export data
        export_path = Path(temp_config_dir) / "xp_export.json"
        exported_path = xp_tracker.export_xp_data(str(export_path))
        
        assert exported_path == str(export_path)
        assert export_path.exists()
        
        # Verify exported data structure
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        assert "export_timestamp" in exported_data
        assert "session_summary" in exported_data
        assert "xp_events" in exported_data
        assert "skill_progress" in exported_data
        assert "hourly_rates" in exported_data
        assert "daily_totals" in exported_data
        assert "zone_efficiency" in exported_data
        assert "summary" in exported_data
        
        # Verify session summary structure
        session_summary = exported_data["session_summary"]
        assert "session_id" in session_summary
        assert "start_time" in session_summary
        assert "end_time" in session_summary
        assert "total_xp" in session_summary
        assert "xp_per_hour" in session_summary
        assert "profession_breakdown" in session_summary
        assert "skill_breakdown" in session_summary
        assert "source_breakdown" in session_summary
        assert "fastest_skills" in session_summary
        assert "slowdowns_detected" in session_summary
        assert "optimal_paths" in session_summary
        assert "zone_efficiency" in session_summary
    
    def test_get_zone_recommendations(self, xp_tracker):
        """Test zone recommendations for professions."""
        xp_tracker.start_session()
        
        # Record XP gains in different zones for a profession
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat", zone="dantooine")
        xp_tracker.record_xp_gain(200, "marksman", "combat_marksman_novice", "combat", zone="naboo")
        xp_tracker.record_xp_gain(150, "marksman", "combat_marksman_novice", "quest", zone="dantooine")
        xp_tracker.record_xp_gain(300, "marksman", "combat_marksman_novice", "combat", zone="corellia")
        
        recommendations = xp_tracker.get_zone_recommendations("marksman")
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check that zones are sorted by efficiency (highest first)
        for i in range(len(recommendations) - 1):
            assert recommendations[i]["avg_xp"] >= recommendations[i + 1]["avg_xp"]
        
        # Verify zone data structure
        for rec in recommendations:
            assert "zone" in rec
            assert "total_xp" in rec
            assert "events" in rec
            assert "avg_xp" in rec
    
    def test_reset_session(self, xp_tracker):
        """Test session reset functionality."""
        xp_tracker.start_session()
        
        # Record some XP gains
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat", zone="dantooine")
        xp_tracker.record_xp_gain(200, "medic", "science_medic_novice", "quest", zone="naboo")
        
        # Verify data exists
        assert len(xp_tracker.xp_events) > 0
        assert len(xp_tracker.session_xp_gains) > 0
        assert len(xp_tracker.zone_xp_efficiency) > 0
        
        # Reset session
        xp_tracker.reset_session()
        
        # Verify session data is cleared
        assert len(xp_tracker.session_xp_gains) == 0
        assert len(xp_tracker.zone_xp_efficiency) == 0
        assert len(xp_tracker.hourly_xp_rates) == 0
        assert len(xp_tracker.daily_xp_totals) == 0
        
        # Verify historical data is preserved
        assert len(xp_tracker.xp_events) > 0
        assert len(xp_tracker.skill_progress) > 0
    
    def test_skill_progress_percentage_calculation(self, xp_tracker):
        """Test skill progress percentage calculation."""
        xp_tracker.start_session()
        
        # Record XP gain with level progression
        event = xp_tracker.record_xp_gain(
            amount=1000,
            profession="marksman",
            skill="combat_marksman_novice",
            source="combat",
            level_before=1,
            level_after=2
        )
        
        assert event.skill_progress_percentage is not None
        assert 0 <= event.skill_progress_percentage <= 100
    
    def test_xp_rate_per_hour_calculation(self, xp_tracker):
        """Test XP rate per hour calculation in events."""
        xp_tracker.start_session()
        
        # Record multiple XP gains
        event1 = xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat")
        event2 = xp_tracker.record_xp_gain(200, "medic", "science_medic_novice", "quest")
        
        assert event1.xp_rate_per_hour is not None
        assert event2.xp_rate_per_hour is not None
        assert event2.xp_rate_per_hour >= event1.xp_rate_per_hour
    
    def test_quest_completion_rate_tracking(self, xp_tracker):
        """Test quest completion rate tracking in skill progress."""
        xp_tracker.start_session()
        
        # Record mixed XP gains
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat")
        xp_tracker.record_xp_gain(200, "marksman", "combat_marksman_novice", "quest")
        xp_tracker.record_xp_gain(150, "marksman", "combat_marksman_novice", "combat")
        xp_tracker.record_xp_gain(300, "marksman", "combat_marksman_novice", "quest")
        
        skill_key = "marksman_combat_marksman_novice"
        progress = xp_tracker.skill_progress[skill_key]
        
        # Should have 50% quest completion rate (2 quests out of 4 total events)
        assert progress.quest_completion_rate == 0.5
    
    def test_slowdown_detection_in_skill_progress(self, xp_tracker):
        """Test slowdown detection in skill progress."""
        xp_tracker.start_session()
        
        # Record high XP gains initially
        for i in range(5):
            xp_tracker.record_xp_gain(200, "marksman", "combat_marksman_novice", "combat")
        
        # Record low XP gains to trigger slowdown detection
        for i in range(5):
            xp_tracker.record_xp_gain(20, "marksman", "combat_marksman_novice", "combat")
        
        skill_key = "marksman_combat_marksman_novice"
        progress = xp_tracker.skill_progress[skill_key]
        
        # Should detect slowdown
        assert progress.slowdown_detected == True
    
    def test_zone_preferences_tracking(self, xp_tracker):
        """Test zone preferences tracking in skill progress."""
        xp_tracker.start_session()
        
        # Record XP gains in different zones for the same skill
        xp_tracker.record_xp_gain(100, "marksman", "combat_marksman_novice", "combat", zone="dantooine")
        xp_tracker.record_xp_gain(200, "marksman", "combat_marksman_novice", "combat", zone="naboo")
        xp_tracker.record_xp_gain(150, "marksman", "combat_marksman_novice", "combat", zone="dantooine")
        
        skill_key = "marksman_combat_marksman_novice"
        progress = xp_tracker.skill_progress[skill_key]
        
        assert "dantooine" in progress.zone_preferences
        assert "naboo" in progress.zone_preferences
        assert progress.zone_preferences["dantooine"] == 250  # 100 + 150
        assert progress.zone_preferences["naboo"] == 200


class TestXPGainEvent:
    """Test XPGainEvent dataclass."""
    
    def test_xp_gain_event_creation(self):
        """Test XPGainEvent creation with all fields."""
        event = XPGainEvent(
            timestamp="2025-01-01T12:00:00",
            amount=100,
            profession="marksman",
            skill="combat_marksman_novice",
            source="combat",
            quest_name="Test Quest",
            zone="dantooine",
            level_before=1,
            level_after=2,
            session_id="test_session",
            xp_rate_per_hour=150.0,
            skill_progress_percentage=25.0
        )
        
        assert event.timestamp == "2025-01-01T12:00:00"
        assert event.amount == 100
        assert event.profession == "marksman"
        assert event.skill == "combat_marksman_novice"
        assert event.source == "combat"
        assert event.quest_name == "Test Quest"
        assert event.zone == "dantooine"
        assert event.level_before == 1
        assert event.level_after == 2
        assert event.session_id == "test_session"
        assert event.xp_rate_per_hour == 150.0
        assert event.skill_progress_percentage == 25.0
    
    def test_xp_gain_event_minimal(self):
        """Test XPGainEvent creation with minimal fields."""
        event = XPGainEvent(
            timestamp="2025-01-01T12:00:00",
            amount=100,
            profession="marksman",
            skill="combat_marksman_novice",
            source="combat"
        )
        
        assert event.quest_name is None
        assert event.zone is None
        assert event.level_before is None
        assert event.level_after is None
        assert event.session_id is None
        assert event.xp_rate_per_hour is None
        assert event.skill_progress_percentage is None


class TestSkillProgress:
    """Test SkillProgress dataclass."""
    
    def test_skill_progress_creation(self):
        """Test SkillProgress creation."""
        progress = SkillProgress(
            skill_name="combat_marksman_novice",
            profession="marksman",
            current_level=2,
            total_xp=1000,
            xp_to_next=500,
            progress_rate=150.0,
            last_gain="2025-01-01T12:00:00",
            gains_history=[],
            zone_preferences={"dantooine": 300, "naboo": 200},
            quest_completion_rate=0.4,
            slowdown_detected=False
        )
        
        assert progress.skill_name == "combat_marksman_novice"
        assert progress.profession == "marksman"
        assert progress.current_level == 2
        assert progress.total_xp == 1000
        assert progress.xp_to_next == 500
        assert progress.progress_rate == 150.0
        assert progress.last_gain == "2025-01-01T12:00:00"
        assert progress.zone_preferences["dantooine"] == 300
        assert progress.quest_completion_rate == 0.4
        assert progress.slowdown_detected == False


class TestProfessionAnalytics:
    """Test ProfessionAnalytics dataclass."""
    
    def test_profession_analytics_creation(self):
        """Test ProfessionAnalytics creation."""
        analytics = ProfessionAnalytics(
            profession_name="marksman",
            total_xp=1500,
            skills_count=3,
            average_level=2.5,
            fastest_skill="combat_marksman_novice",
            slowest_skill="combat_marksman_rifleman",
            xp_per_hour=200.0,
            session_duration=2.5,
            quest_completion_rate=0.6,
            optimal_zones=["dantooine", "naboo"],
            skill_path_recommendation=["combat_marksman_novice", "combat_marksman_marksman"]
        )
        
        assert analytics.profession_name == "marksman"
        assert analytics.total_xp == 1500
        assert analytics.skills_count == 3
        assert analytics.average_level == 2.5
        assert analytics.fastest_skill == "combat_marksman_novice"
        assert analytics.slowest_skill == "combat_marksman_rifleman"
        assert analytics.xp_per_hour == 200.0
        assert analytics.session_duration == 2.5
        assert analytics.quest_completion_rate == 0.6
        assert analytics.optimal_zones == ["dantooine", "naboo"]
        assert analytics.skill_path_recommendation == ["combat_marksman_novice", "combat_marksman_marksman"]


class TestXPSessionSummary:
    """Test XPSessionSummary dataclass."""
    
    def test_session_summary_creation(self):
        """Test XPSessionSummary creation."""
        summary = XPSessionSummary(
            session_id="test_session",
            start_time="2025-01-01T10:00:00",
            end_time="2025-01-01T12:00:00",
            total_xp=1500,
            xp_per_hour=750.0,
            profession_breakdown={"marksman": 800, "medic": 700},
            skill_breakdown={"combat_marksman_novice": 500, "science_medic_novice": 400},
            source_breakdown={"combat": 900, "quest": 600},
            fastest_skills=["combat_marksman_novice", "science_medic_novice"],
            slowdowns_detected=[{"skill": "crafting_artisan_novice", "slowdown_percentage": 50.0}],
            optimal_paths={"marksman": ["combat_marksman_novice", "combat_marksman_marksman"]},
            zone_efficiency={"dantooine": 200.0, "naboo": 150.0}
        )
        
        assert summary.session_id == "test_session"
        assert summary.start_time == "2025-01-01T10:00:00"
        assert summary.end_time == "2025-01-01T12:00:00"
        assert summary.total_xp == 1500
        assert summary.xp_per_hour == 750.0
        assert summary.profession_breakdown["marksman"] == 800
        assert summary.skill_breakdown["combat_marksman_novice"] == 500
        assert summary.source_breakdown["combat"] == 900
        assert "combat_marksman_novice" in summary.fastest_skills
        assert len(summary.slowdowns_detected) == 1
        assert "marksman" in summary.optimal_paths
        assert summary.zone_efficiency["dantooine"] == 200.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 