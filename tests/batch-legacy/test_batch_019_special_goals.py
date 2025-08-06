#!/usr/bin/env python3
"""
Test Script for Batch 019 - Special Goals + Unlock Paths

This script demonstrates the special goals system functionality including:
- Goal loading and prioritization
- Milestone tracking and progress monitoring
- Dashboard integration
- Active goal management
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from profiles.special_goals import (
    get_special_goals_manager, start_goal_session, 
    get_current_goal_status, get_dashboard_data,
    update_milestone_progress, get_prioritized_goals
)
from core.special_goals import GoalType, GoalPriority, GoalStatus


def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_goal_loading():
    """Test that goals are loaded correctly from data/goals.json."""
    print("🔍 Testing Goal Loading...")
    
    manager = get_special_goals_manager()
    
    # Check that goals were loaded
    available_goals = manager.special_goals.get_available_goals()
    print(f"✅ Loaded {len(available_goals)} available goals")
    
    # Display some goal details
    for goal in available_goals[:3]:  # Show first 3 goals
        print(f"  - {goal.name} ({goal.goal_type.value}, {goal.priority.value})")
        print(f"    Location: {goal.planet} - {goal.zone}")
        print(f"    Requirements: {len(goal.requirements)}")
        print(f"    Estimated time: {goal.estimated_time_hours}h")
        print()
    
    return len(available_goals) > 0


def test_goal_prioritization():
    """Test goal prioritization logic."""
    print("🎯 Testing Goal Prioritization...")
    
    manager = get_special_goals_manager()
    prioritized_goals = manager.get_prioritized_goals(max_goals=5)
    
    print(f"✅ Prioritized {len(prioritized_goals)} goals:")
    
    for i, goal in enumerate(prioritized_goals, 1):
        score = manager._calculate_goal_score(goal)
        print(f"  {i}. {goal.name}")
        print(f"     Priority: {goal.priority.value}")
        print(f"     Type: {goal.goal_type.value}")
        print(f"     Score: {score:.1f}")
        print(f"     Planet: {goal.planet}")
        print()
    
    return len(prioritized_goals) > 0


def test_goal_session_management():
    """Test starting and managing goal sessions."""
    print("🚀 Testing Goal Session Management...")
    
    manager = get_special_goals_manager()
    
    # Get a goal to work on
    available_goals = manager.get_prioritized_goals(max_goals=1)
    if not available_goals:
        print("❌ No available goals to test with")
        return False
    
    test_goal = available_goals[0]
    print(f"🎯 Testing with goal: {test_goal.name}")
    
    # Start a goal session
    success = manager.start_goal_session(test_goal.name)
    if not success:
        print("❌ Failed to start goal session")
        return False
    
    print("✅ Goal session started successfully")
    
    # Check current goal status
    status = manager.get_current_goal_status()
    print(f"📊 Current goal status:")
    print(f"  Active: {status['active']}")
    print(f"  Goal: {status['goal_name']}")
    print(f"  Progress: {status['milestones_completed']}/{status['total_milestones']}")
    print(f"  Percentage: {status['progress_percentage']:.1f}%")
    
    # Test milestone progress update
    if status['milestones']:
        first_milestone = status['milestones'][0]
        milestone_name = first_milestone['name']
        
        print(f"🔄 Testing milestone progress update: {milestone_name}")
        
        # Simulate progress update
        if first_milestone['requirement_type'] == 'level':
            update_success = manager.update_milestone_progress(milestone_name, 25)
        elif first_milestone['requirement_type'] == 'reputation':
            update_success = manager.update_milestone_progress(milestone_name, 1500)
        else:
            update_success = manager.update_milestone_progress(milestone_name, "in_progress")
        
        if update_success:
            print("✅ Milestone progress updated successfully")
        else:
            print("❌ Failed to update milestone progress")
    
    return True


def test_dashboard_integration():
    """Test dashboard data generation."""
    print("📊 Testing Dashboard Integration...")
    
    dashboard_data = get_dashboard_data()
    
    print("✅ Dashboard data generated:")
    print(f"  Statistics:")
    print(f"    Total goals: {dashboard_data['statistics']['total_goals']}")
    print(f"    Completed goals: {dashboard_data['statistics']['completed_goals']}")
    print(f"    Completion rate: {dashboard_data['statistics']['completion_rate']:.1f}%")
    
    print(f"  Current goal active: {dashboard_data['current_goal']['active']}")
    print(f"  Prioritized goals: {len(dashboard_data['prioritized_goals'])}")
    
    # Show some prioritized goals
    for i, goal in enumerate(dashboard_data['prioritized_goals'][:3], 1):
        print(f"    {i}. {goal['name']} ({goal['priority']})")
    
    return True


def test_milestone_tracking():
    """Test milestone tracking functionality."""
    print("📋 Testing Milestone Tracking...")
    
    manager = get_special_goals_manager()
    
    # Get current goal status to see milestones
    status = manager.get_current_goal_status()
    
    if not status['active']:
        print("⚠️  No active goal to test milestones with")
        return True
    
    print(f"🎯 Testing milestones for: {status['goal_name']}")
    print(f"📊 Progress: {status['milestones_completed']}/{status['total_milestones']}")
    
    # Display milestone details
    for i, milestone in enumerate(status['milestones'], 1):
        status_icon = "✅" if milestone['completed'] else "⏳"
        print(f"  {i}. {status_icon} {milestone['name']}")
        print(f"     Type: {milestone['requirement_type']}")
        print(f"     Target: {milestone['target_value']}")
        print(f"     Current: {milestone['current_value']}")
        print()
    
    return True


def test_goal_completion_simulation():
    """Simulate completing a goal by updating all milestones."""
    print("🏆 Testing Goal Completion Simulation...")
    
    manager = get_special_goals_manager()
    status = manager.get_current_goal_status()
    
    if not status['active']:
        print("⚠️  No active goal to complete")
        return True
    
    print(f"🎯 Simulating completion of: {status['goal_name']}")
    
    # Update all milestones to completed state
    for milestone in status['milestones']:
        if not milestone['completed']:
            milestone_name = milestone['name']
            
            # Set appropriate completion values based on requirement type
            if milestone['requirement_type'] == 'level':
                completion_value = milestone['target_value']
            elif milestone['requirement_type'] == 'reputation':
                completion_value = milestone['target_value']
            elif milestone['requirement_type'] == 'quest':
                completion_value = "completed"
            elif milestone['requirement_type'] == 'skill':
                completion_value = milestone['target_value']
            elif milestone['requirement_type'] == 'collection':
                completion_value = "completed"
            else:
                completion_value = milestone['target_value']
            
            print(f"  🔄 Completing milestone: {milestone_name}")
            manager.update_milestone_progress(milestone_name, completion_value)
    
    # Check final status
    final_status = manager.get_current_goal_status()
    if final_status['active']:
        print("❌ Goal should be completed but is still active")
        return False
    else:
        print("✅ Goal completed successfully!")
        return True


def test_session_persistence():
    """Test that session data can be saved and loaded."""
    print("💾 Testing Session Persistence...")
    
    manager = get_special_goals_manager()
    
    # Save current session data
    manager.save_session_data()
    print("✅ Session data saved")
    
    # Create a new manager instance to test loading
    from profiles.special_goals import _special_goals_manager
    _special_goals_manager = None  # Reset global instance
    
    new_manager = get_special_goals_manager()
    print("✅ Session data loaded in new manager instance")
    
    # Check if data was preserved
    status = new_manager.get_current_goal_status()
    print(f"📊 Loaded session - Active goal: {status['active']}")
    
    return True


def run_all_tests():
    """Run all special goals tests."""
    print("🎯 Batch 019 - Special Goals + Unlock Paths Test Suite")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("Goal Loading", test_goal_loading),
        ("Goal Prioritization", test_goal_prioritization),
        ("Goal Session Management", test_goal_session_management),
        ("Dashboard Integration", test_dashboard_integration),
        ("Milestone Tracking", test_milestone_tracking),
        ("Goal Completion Simulation", test_goal_completion_simulation),
        ("Session Persistence", test_session_persistence),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Special Goals system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 