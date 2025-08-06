"""
Test Script for Batch 025 – Passive Learning Hook System

This script tests the functionality of:
- logs/session_tracker.py
- logs/combat_usage_log.json
- profiles/learned_combat_insights.json
"""

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from logs.session_tracker import (
    PassiveLearningTracker, CombatSession, SkillUsage, SessionState,
    get_tracker, start_session, end_session, record_skill_usage,
    record_kill, record_death, update_xp, scan_xp_from_screen,
    get_session_status, get_learned_insights
)


def test_session_tracker_initialization():
    """Test session tracker initialization."""
    print("\n🧪 Testing Session Tracker Initialization")
    
    try:
        # Initialize tracker
        tracker = PassiveLearningTracker()
        print("✅ PassiveLearningTracker initialized successfully")
        
        # Check that logs directory is created
        assert tracker.logs_dir.exists(), "Logs directory not created"
        print("✅ Logs directory created")
        
        # Check that files are accessible
        assert tracker.combat_usage_log.parent.exists(), "Combat usage log directory not found"
        assert tracker.learned_insights.parent.exists(), "Learned insights directory not found"
        print("✅ File paths configured correctly")
        
        # Check that data is loaded
        assert isinstance(tracker.combat_usage_data, dict), "Combat usage data not loaded"
        assert isinstance(tracker.learned_insights_data, dict), "Learned insights data not loaded"
        print("✅ Data loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Session Tracker Initialization Test Failed: {e}")
        return False


def test_session_lifecycle():
    """Test session lifecycle (start, record, end)."""
    print("\n🧪 Testing Session Lifecycle")
    
    try:
        tracker = PassiveLearningTracker()
        
        # Start session
        session_id = tracker.start_session("test_session_001")
        assert session_id == "test_session_001", "Session ID not set correctly"
        assert tracker.current_session is not None, "Current session not created"
        assert tracker.current_session.state == SessionState.ACTIVE, "Session state not active"
        print("✅ Session started successfully")
        
        # Record skill usage
        tracker.record_skill_usage("headshot", damage=400, xp_gained=255, success=True)
        tracker.record_skill_usage("burst_fire", damage=400, xp_gained=382, success=True)
        tracker.record_skill_usage("rifle_shot", damage=183, xp_gained=172, success=True)
        
        assert len(tracker.current_session.skills_used) == 3, "Skill usage not recorded"
        assert "headshot" in tracker.current_session.skills_used, "Headshot not recorded"
        assert "burst_fire" in tracker.current_session.skills_used, "Burst fire not recorded"
        assert "rifle_shot" in tracker.current_session.skills_used, "Rifle shot not recorded"
        print("✅ Skill usage recorded successfully")
        
        # Record kills and deaths
        tracker.record_kill(xp_gained=100)
        tracker.record_kill(xp_gained=150)
        tracker.record_death()
        
        assert tracker.current_session.kills == 2, "Kills not recorded"
        assert tracker.current_session.deaths == 1, "Death not recorded"
        print("✅ Kills and deaths recorded successfully")
        
        # Update XP
        tracker.update_xp(1000)
        assert tracker.current_session.current_xp == 1000, "XP not updated"
        print("✅ XP updated successfully")
        
        # End session
        session_summary = tracker.end_session()
        assert session_summary is not None, "Session summary not generated"
        assert session_summary["session_id"] == "test_session_001", "Session ID incorrect"
        assert session_summary["state"] == "completed", "Session state incorrect"
        assert session_summary["total_xp_gained"] >= 0, "XP gained not calculated"
        print("✅ Session ended successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Session Lifecycle Test Failed: {e}")
        return False


def test_skill_usage_tracking():
    """Test detailed skill usage tracking."""
    print("\n🧪 Testing Skill Usage Tracking")
    
    try:
        tracker = PassiveLearningTracker()
        tracker.start_session("test_skill_tracking")
        
        # Record multiple skill usages
        for i in range(5):
            tracker.record_skill_usage("headshot", damage=400, xp_gained=255, success=True)
        
        for i in range(3):
            tracker.record_skill_usage("burst_fire", damage=400, xp_gained=382, success=True)
        
        # Record one failed skill usage
        tracker.record_skill_usage("headshot", damage=0, xp_gained=0, success=False)
        
        # Check skill usage data
        headshot_data = tracker.current_session.skills_used["headshot"]
        assert headshot_data.usage_count == 6, "Headshot usage count incorrect"
        assert headshot_data.total_damage == 2000, "Headshot total damage incorrect"
        assert abs(headshot_data.average_damage - 333.33) < 0.01, f"Headshot average damage incorrect: {headshot_data.average_damage}"
        assert abs(headshot_data.success_rate - 5/6) < 0.01, f"Headshot success rate incorrect: {headshot_data.success_rate}"
        print("✅ Skill usage statistics calculated correctly")
        
        # Check total session data
        assert tracker.current_session.total_damage_dealt == 3200, "Total damage incorrect"
        # XP calculation: 5 successful headshots (5*255) + 3 successful burst_fire (3*382) = 1275 + 1146 = 2421
        expected_xp = 5 * 255 + 3 * 382
        assert tracker.current_session.total_xp_gained == expected_xp, f"Total XP incorrect: {tracker.current_session.total_xp_gained}, expected: {expected_xp}"
        print("✅ Session totals calculated correctly")
        
        tracker.end_session()
        return True
        
    except Exception as e:
        print(f"❌ Skill Usage Tracking Test Failed: {e}")
        return False


def test_xp_tracking():
    """Test XP tracking functionality."""
    print("\n🧪 Testing XP Tracking")
    
    try:
        tracker = PassiveLearningTracker()
        tracker.start_session("test_xp_tracking")
        
        # Set initial XP
        tracker.update_xp(1000)
        assert tracker.current_session.start_xp == 1000, "Start XP not set"
        assert tracker.current_session.current_xp == 1000, "Current XP not set"
        assert tracker.current_session.total_xp_gained == 0, "Initial XP gained should be 0"
        print("✅ Initial XP set correctly")
        
        # Update XP (simulate XP gain)
        tracker.update_xp(1250)
        assert tracker.current_session.current_xp == 1250, "Current XP not updated"
        assert tracker.current_session.total_xp_gained == 250, "XP gained not calculated"
        print("✅ XP gain calculated correctly")
        
        # Update XP again
        tracker.update_xp(1500)
        assert tracker.current_session.total_xp_gained == 500, "Total XP gained incorrect"
        print("✅ Multiple XP updates handled correctly")
        
        tracker.end_session()
        return True
        
    except Exception as e:
        print(f"❌ XP Tracking Test Failed: {e}")
        return False


def test_session_status():
    """Test session status reporting."""
    print("\n🧪 Testing Session Status")
    
    try:
        tracker = PassiveLearningTracker()
        tracker.start_session("test_status")
        
        # Get initial status
        status = tracker.get_session_status()
        assert status["session_id"] == "test_status", "Session ID incorrect"
        assert status["state"] == "active", "Session state incorrect"
        assert status["total_xp_gained"] == 0, "Initial XP gained should be 0"
        assert status["skills_used"] == 0, "Initial skills used should be 0"
        print("✅ Initial status correct")
        
        # Record some activity
        tracker.record_skill_usage("headshot", damage=400, xp_gained=255)
        tracker.record_kill(xp_gained=100)
        
        # Get updated status
        status = tracker.get_session_status()
        assert status["skills_used"] == 1, "Skills used count incorrect"
        assert status["kills"] == 1, "Kills count incorrect"
        # XP gained should be 255 (from skill) + 100 (from kill) = 355
        expected_xp = 255 + 100
        assert status["total_xp_gained"] == expected_xp, f"Total XP gained incorrect: {status['total_xp_gained']}, expected: {expected_xp}"
        assert status["duration_minutes"] > 0, "Duration should be positive"
        print("✅ Updated status correct")
        
        tracker.end_session()
        return True
        
    except Exception as e:
        print(f"❌ Session Status Test Failed: {e}")
        return False


def test_learned_insights():
    """Test learned insights generation."""
    print("\n🧪 Testing Learned Insights")
    
    try:
        tracker = PassiveLearningTracker()
        tracker.start_session("test_insights")
        
        # Record skill usage to generate insights
        tracker.record_skill_usage("headshot", damage=400, xp_gained=255, success=True)
        tracker.record_skill_usage("burst_fire", damage=400, xp_gained=382, success=True)
        tracker.record_skill_usage("rifle_shot", damage=183, xp_gained=172, success=True)
        tracker.record_kill(xp_gained=100)
        
        # End session to generate insights
        session_summary = tracker.end_session()
        
        # Check learned insights
        insights = tracker.get_learned_insights()
        assert "skill_performance" in insights, "Skill performance not in insights"
        assert "xp_efficiency" in insights, "XP efficiency not in insights"
        assert "combat_patterns" in insights, "Combat patterns not in insights"
        print("✅ Learned insights structure correct")
        
        # Check skill performance data
        skill_performance = insights["skill_performance"]
        assert "headshot" in skill_performance, "Headshot not in skill performance"
        assert "burst_fire" in skill_performance, "Burst fire not in skill performance"
        assert "rifle_shot" in skill_performance, "Rifle shot not in skill performance"
        print("✅ Skill performance data generated")
        
        # Check specific skill data
        headshot_data = skill_performance["headshot"]
        assert headshot_data["total_uses"] >= 1, f"Headshot total uses should be at least 1, got: {headshot_data['total_uses']}"
        assert headshot_data["total_damage"] >= 400, f"Headshot total damage should be at least 400, got: {headshot_data['total_damage']}"
        # Average damage should be reasonable (between 200 and 600)
        assert 200 <= headshot_data["average_damage"] <= 600, f"Headshot average damage should be between 200-600, got: {headshot_data['average_damage']}"
        print("✅ Skill performance calculations correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Learned Insights Test Failed: {e}")
        return False


def test_skill_performance_analysis():
    """Test skill performance analysis."""
    print("\n🧪 Testing Skill Performance Analysis")
    
    try:
        tracker = PassiveLearningTracker()
        
        # Get skill performance for specific skill
        performance = tracker.get_skill_performance("headshot")
        # Should return None if no data exists yet
        if performance is None:
            print("✅ No performance data for new skill (expected)")
        else:
            assert isinstance(performance, dict), "Performance data should be dict"
            print("✅ Performance data retrieved")
        
        # Record some usage and check again
        tracker.start_session("test_performance")
        tracker.record_skill_usage("headshot", damage=400, xp_gained=255, success=True)
        tracker.end_session()
        
        # Check updated performance
        performance = tracker.get_skill_performance("headshot")
        if performance is not None:
            assert performance["total_uses"] >= 1, "Total uses should be at least 1"
            print("✅ Performance data updated correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Skill Performance Analysis Test Failed: {e}")
        return False


def test_global_functions():
    """Test global functions."""
    print("\n🧪 Testing Global Functions")
    
    try:
        # Test get_tracker
        tracker = get_tracker()
        assert isinstance(tracker, PassiveLearningTracker), "get_tracker should return PassiveLearningTracker"
        print("✅ get_tracker working")
        
        # Test start_session
        session_id = start_session("test_global")
        assert isinstance(session_id, str), "start_session should return string"
        print("✅ start_session working")
        
        # Test record_skill_usage
        record_skill_usage("headshot", damage=400, xp_gained=255)
        print("✅ record_skill_usage working")
        
        # Test record_kill
        record_kill(xp_gained=100)
        print("✅ record_kill working")
        
        # Test record_death
        record_death()
        print("✅ record_death working")
        
        # Test update_xp
        update_xp(1500)
        print("✅ update_xp working")
        
        # Test get_session_status
        status = get_session_status()
        assert isinstance(status, dict), "get_session_status should return dict"
        print("✅ get_session_status working")
        
        # Test get_learned_insights
        insights = get_learned_insights()
        assert isinstance(insights, dict), "get_learned_insights should return dict"
        print("✅ get_learned_insights working")
        
        # Test end_session
        summary = end_session()
        assert isinstance(summary, dict), "end_session should return dict"
        print("✅ end_session working")
        
        return True
        
    except Exception as e:
        print(f"❌ Global Functions Test Failed: {e}")
        return False


def test_file_operations():
    """Test file operations (save/load)."""
    print("\n🧪 Testing File Operations")
    
    try:
        tracker = PassiveLearningTracker()
        
        # Start and end a session to trigger file saves
        tracker.start_session("test_file_ops")
        tracker.record_skill_usage("headshot", damage=400, xp_gained=255)
        tracker.record_kill(xp_gained=100)
        session_summary = tracker.end_session()
        
        # Check that files were created/updated
        assert tracker.combat_usage_log.exists(), "Combat usage log should exist"
        assert tracker.learned_insights.exists(), "Learned insights should exist"
        print("✅ Files created successfully")
        
        # Check file contents
        with open(tracker.combat_usage_log, 'r') as f:
            combat_data = json.load(f)
        assert "sessions" in combat_data, "Sessions array should exist"
        assert len(combat_data["sessions"]) > 0, "Should have at least one session"
        print("✅ Combat usage log contains data")
        
        with open(tracker.learned_insights, 'r') as f:
            insights_data = json.load(f)
        assert "skill_performance" in insights_data, "Skill performance should exist"
        assert "last_updated" in insights_data, "Last updated should exist"
        print("✅ Learned insights contains data")
        
        return True
        
    except Exception as e:
        print(f"❌ File Operations Test Failed: {e}")
        return False


def test_error_handling():
    """Test error handling functionality."""
    print("\n🧪 Testing Error Handling")
    
    try:
        tracker = PassiveLearningTracker()
        
        # Test recording without active session
        tracker.record_skill_usage("headshot", damage=400, xp_gained=255)
        # Should log warning but not crash
        print("✅ Recording without session handled gracefully")
        
        # Test ending session without active session
        summary = tracker.end_session()
        assert summary is None, "Ending non-existent session should return None"
        print("✅ Ending non-existent session handled gracefully")
        
        # Test XP scanning without OCR
        xp_value = tracker.scan_xp_from_screen()
        # Should return None when OCR not available
        print("✅ XP scanning without OCR handled gracefully")
        
        # Test session status without active session
        status = tracker.get_session_status()
        assert status["status"] == "no_active_session", "Status should indicate no session"
        print("✅ Status without session handled gracefully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error Handling Test Failed: {e}")
        return False


def test_data_structures():
    """Test data structure functionality."""
    print("\n🧪 Testing Data Structures")
    
    try:
        # Test SkillUsage dataclass
        skill_usage = SkillUsage(skill_name="test_skill")
        assert skill_usage.skill_name == "test_skill", "Skill name not set"
        assert skill_usage.usage_count == 0, "Initial usage count should be 0"
        print("✅ SkillUsage dataclass working")
        
        # Test update_usage method
        skill_usage.update_usage(damage=100, xp_gained=50, success=True)
        assert skill_usage.usage_count == 1, "Usage count not incremented"
        assert skill_usage.total_damage == 100, "Total damage not updated"
        assert skill_usage.average_damage == 100.0, "Average damage not calculated"
        assert skill_usage.success_rate == 1.0, "Success rate not calculated"
        print("✅ SkillUsage update_usage working")
        
        # Test CombatSession dataclass
        session = CombatSession(
            session_id="test_session",
            start_time=datetime.now()
        )
        assert session.session_id == "test_session", "Session ID not set"
        assert session.state == SessionState.ACTIVE, "Default state should be active"
        print("✅ CombatSession dataclass working")
        
        # Test add_skill_usage method
        session.add_skill_usage("test_skill", damage=100, xp_gained=50)
        assert "test_skill" in session.skills_used, "Skill not added to session"
        assert session.total_damage_dealt == 100, "Total damage not updated"
        print("✅ CombatSession add_skill_usage working")
        
        # Test get_session_summary method
        summary = session.get_session_summary()
        assert "session_id" in summary, "Session ID not in summary"
        assert "skills" in summary, "Skills not in summary"
        print("✅ CombatSession get_session_summary working")
        
        return True
        
    except Exception as e:
        print(f"❌ Data Structures Test Failed: {e}")
        return False


def run_all_tests():
    """Run all tests and return results."""
    print("🚀 Starting Batch 025 - Passive Learning Hook System Tests")
    print("=" * 60)
    
    tests = [
        test_session_tracker_initialization,
        test_session_lifecycle,
        test_skill_usage_tracking,
        test_xp_tracking,
        test_session_status,
        test_learned_insights,
        test_skill_performance_analysis,
        test_global_functions,
        test_file_operations,
        test_error_handling,
        test_data_structures
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Batch 025 implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 