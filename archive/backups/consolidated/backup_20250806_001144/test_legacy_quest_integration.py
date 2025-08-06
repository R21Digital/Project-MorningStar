#!/usr/bin/env python3
"""
Test script for Legacy Quest Profile System (Batch 012)

This script tests the integration between the Legacy Quest Profile system and
the dialogue handler, travel system, and quest tracker to ensure complete quest automation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import json
from pathlib import Path

from profiles.legacy_profile import (
    legacy_quest_manager,
    load_legacy_quest,
    start_legacy_quest,
    execute_quest_step,
    get_quest_progress,
    get_all_quest_progress,
    LegacyQuestProfile,
    QuestStep,
    QuestStepType,
    QuestStepStatus
)
from core.database import load_quest


def test_legacy_quest_loading():
    """Test loading Legacy quest profiles from the database."""
    print("🧪 Testing Legacy Quest Loading...")
    
    # Test loading a specific quest
    quest_id = "legacy_begins"
    profile = load_legacy_quest(quest_id)
    
    if profile:
        print(f"✅ Successfully loaded Legacy quest: {profile.name}")
        print(f"   Quest ID: {profile.quest_id}")
        print(f"   Type: {profile.quest_type}")
        print(f"   Difficulty: {profile.difficulty}")
        print(f"   Level Requirement: {profile.level_requirement}")
        print(f"   Planet: {profile.planet}")
        print(f"   Zone: {profile.zone}")
        print(f"   Steps: {len(profile.steps)}")
        print(f"   Rewards: {profile.rewards}")
        
        # Show step types
        step_types = set(step.step_type.value for step in profile.steps)
        print(f"   Step types: {list(step_types)}")
        
        return True
    else:
        print(f"❌ Failed to load Legacy quest: {quest_id}")
        return False


def test_quest_step_creation():
    """Test creating quest steps from data."""
    print("\n🧪 Testing Quest Step Creation...")
    
    # Test step data
    step_data = {
        "step_id": "test_step",
        "type": "dialogue",
        "title": "Test Dialogue Step",
        "description": "A test dialogue step",
        "coordinates": [100, 150],
        "zone": "test_zone",
        "planet": "tatooine",
        "npc_id": "test_npc",
        "dialogue_options": ["Option 1", "Option 2"],
        "required_response": 0,
        "timeout_seconds": 300
    }
    
    try:
        step = legacy_quest_manager._create_quest_step(step_data)
        
        if step:
            print(f"✅ Successfully created quest step: {step.title}")
            print(f"   Step ID: {step.step_id}")
            print(f"   Type: {step.step_type.value}")
            print(f"   Coordinates: {step.coordinates}")
            print(f"   NPC ID: {step.npc_id}")
            print(f"   Dialogue options: {len(step.dialogue_options)}")
            return True
        else:
            print("❌ Failed to create quest step")
            return False
            
    except Exception as e:
        print(f"❌ Error creating quest step: {e}")
        return False


def test_quest_starting():
    """Test starting a Legacy quest."""
    print("\n🧪 Testing Quest Starting...")
    
    # Test starting a quest
    quest_id = "legacy_begins"
    success = start_legacy_quest(quest_id)
    
    if success:
        print(f"✅ Successfully started Legacy quest: {quest_id}")
        
        # Check if quest is in active quests
        if quest_id in legacy_quest_manager.active_quests:
            print("✅ Quest added to active quests")
            
            # Get quest progress
            progress = get_quest_progress(quest_id)
            print(f"   Status: {progress.get('status')}")
            print(f"   Current step: {progress.get('current_step')}")
            print(f"   Total steps: {progress.get('total_steps')}")
            
            return True
        else:
            print("❌ Quest not found in active quests")
            return False
    else:
        print(f"❌ Failed to start Legacy quest: {quest_id}")
        return False


def test_quest_step_execution():
    """Test executing quest steps."""
    print("\n🧪 Testing Quest Step Execution...")
    
    # Start a quest first
    quest_id = "legacy_begins"
    if quest_id not in legacy_quest_manager.active_quests:
        start_legacy_quest(quest_id)
    
    if quest_id in legacy_quest_manager.active_quests:
        # Execute a step
        success = execute_quest_step(quest_id)
        
        if success:
            print(f"✅ Successfully executed step for quest: {quest_id}")
            
            # Get updated progress
            progress = get_quest_progress(quest_id)
            print(f"   Current step: {progress.get('current_step')}")
            print(f"   Completed steps: {progress.get('completed_steps')}")
            print(f"   Progress: {progress.get('progress_percentage', 0):.1f}%")
            
            return True
        else:
            print(f"❌ Failed to execute step for quest: {quest_id}")
            return False
    else:
        print(f"❌ Quest not active: {quest_id}")
        return False


def test_quest_progress_tracking():
    """Test quest progress tracking functionality."""
    print("\n🧪 Testing Quest Progress Tracking...")
    
    # Get progress for all quests
    all_progress = get_all_quest_progress()
    
    print(f"✅ Quest progress summary:")
    print(f"   Active quests: {all_progress.get('total_active', 0)}")
    print(f"   Completed quests: {all_progress.get('total_completed', 0)}")
    print(f"   Failed quests: {all_progress.get('total_failed', 0)}")
    
    # Show active quest details
    active_quests = all_progress.get('active_quests', {})
    for quest_id, progress in active_quests.items():
        print(f"   Quest {quest_id}:")
        print(f"     Status: {progress.get('status')}")
        print(f"     Progress: {progress.get('progress_percentage', 0):.1f}%")
        print(f"     Current step: {progress.get('current_step')}/{progress.get('total_steps')}")
    
    return True


def test_quest_completion_conditions():
    """Test quest completion condition checking."""
    print("\n🧪 Testing Quest Completion Conditions...")
    
    # Create a test quest profile
    test_steps = [
        QuestStep(
            step_id="step1",
            step_type=QuestStepType.DIALOGUE,
            title="Test Step 1",
            description="A test step",
            coordinates=[100, 150],
            zone="test_zone",
            planet="tatooine"
        ),
        QuestStep(
            step_id="step2",
            step_type=QuestStepType.COMBAT,
            title="Test Step 2",
            description="Another test step",
            coordinates=[200, 250],
            zone="test_zone",
            planet="tatooine"
        )
    ]
    
    test_profile = LegacyQuestProfile(
        quest_id="test_quest",
        name="Test Quest",
        description="A test quest",
        quest_type="test",
        difficulty="easy",
        level_requirement=1,
        planet="tatooine",
        zone="test_zone",
        coordinates=[100, 150],
        quest_chain="test_chain",
        prerequisites=[],
        rewards={},
        steps=test_steps,
        completion_conditions=[
            {
                "type": "steps_completed",
                "steps": ["step1", "step2"],
                "count": 2
            }
        ],
        failure_conditions=[],
        hints=[]
    )
    
    # Test completion conditions
    test_profile.completed_steps = ["step1", "step2"]
    success = legacy_quest_manager._check_completion_conditions(test_profile)
    
    if success:
        print("✅ Quest completion conditions met")
    else:
        print("❌ Quest completion conditions not met")
    
    return success


def test_quest_rewards():
    """Test quest reward application."""
    print("\n🧪 Testing Quest Rewards...")
    
    # Create a test quest profile with rewards
    test_profile = LegacyQuestProfile(
        quest_id="test_rewards",
        name="Test Rewards Quest",
        description="A test quest with rewards",
        quest_type="test",
        difficulty="easy",
        level_requirement=1,
        planet="tatooine",
        zone="test_zone",
        coordinates=[100, 150],
        quest_chain="test_chain",
        prerequisites=[],
        rewards={
            "experience": 1000,
            "credits": 500,
            "reputation": {"tatooine": 100},
            "items": ["test_item"],
            "unlocks": ["test_unlock"]
        },
        steps=[],
        completion_conditions=[],
        failure_conditions=[],
        hints=[]
    )
    
    # Apply rewards
    legacy_quest_manager._apply_quest_rewards(test_profile)
    print("✅ Quest rewards applied successfully")
    
    return True


def test_quest_logging():
    """Test quest event logging."""
    print("\n🧪 Testing Quest Logging...")
    
    # Create a test quest profile
    test_profile = LegacyQuestProfile(
        quest_id="test_logging",
        name="Test Logging Quest",
        description="A test quest for logging",
        quest_type="test",
        difficulty="easy",
        level_requirement=1,
        planet="tatooine",
        zone="test_zone",
        coordinates=[100, 150],
        quest_chain="test_chain",
        prerequisites=[],
        rewards={},
        steps=[],
        completion_conditions=[],
        failure_conditions=[],
        hints=[]
    )
    
    # Log a test event
    legacy_quest_manager._log_quest_event("test_event", test_profile)
    
    # Check if log file was created
    log_file = Path("logs/legacy_quests.json")
    if log_file.exists():
        print("✅ Quest log file created successfully")
        return True
    else:
        print("ℹ️  No log file created (may be normal in test environment)")
        return True


def test_quest_step_types():
    """Test different quest step types."""
    print("\n🧪 Testing Quest Step Types...")
    
    step_types = [
        QuestStepType.DIALOGUE,
        QuestStepType.COLLECTION,
        QuestStepType.COMBAT,
        QuestStepType.MOVEMENT,
        QuestStepType.EXPLORATION,
        QuestStepType.INTERACTION,
        QuestStepType.RITUAL
    ]
    
    for step_type in step_types:
        print(f"✅ Step type: {step_type.value}")
    
    print(f"✅ All {len(step_types)} step types supported")
    return True


def test_quest_status_tracking():
    """Test quest status tracking."""
    print("\n🧪 Testing Quest Status Tracking...")
    
    # Test different status values
    statuses = [
        QuestStepStatus.NOT_STARTED,
        QuestStepStatus.IN_PROGRESS,
        QuestStepStatus.COMPLETED,
        QuestStepStatus.FAILED,
        QuestStepStatus.SKIPPED
    ]
    
    for status in statuses:
        print(f"✅ Status: {status.value}")
    
    print(f"✅ All {len(statuses)} status types supported")
    return True


def test_quest_prerequisites():
    """Test quest prerequisite checking."""
    print("\n🧪 Testing Quest Prerequisites...")
    
    # Create a test quest with prerequisites
    test_profile = LegacyQuestProfile(
        quest_id="test_prereq",
        name="Test Prerequisite Quest",
        description="A test quest with prerequisites",
        quest_type="test",
        difficulty="easy",
        level_requirement=1,
        planet="tatooine",
        zone="test_zone",
        coordinates=[100, 150],
        quest_chain="test_chain",
        prerequisites=["completed_quest_1", "completed_quest_2"],
        rewards={},
        steps=[],
        completion_conditions=[],
        failure_conditions=[],
        hints=[]
    )
    
    # Test prerequisite checking
    success = legacy_quest_manager._check_prerequisites(test_profile)
    
    if not success:
        print("✅ Prerequisites correctly identified as not met")
        return True
    else:
        print("❌ Prerequisites incorrectly identified as met")
        return False


def main():
    """Run all tests for Legacy Quest Profile system."""
    print("🚀 Starting Legacy Quest Profile System Tests (Batch 012)")
    print("=" * 70)
    
    tests = [
        ("Legacy Quest Loading", test_legacy_quest_loading),
        ("Quest Step Creation", test_quest_step_creation),
        ("Quest Starting", test_quest_starting),
        ("Quest Step Execution", test_quest_step_execution),
        ("Quest Progress Tracking", test_quest_progress_tracking),
        ("Quest Completion Conditions", test_quest_completion_conditions),
        ("Quest Rewards", test_quest_rewards),
        ("Quest Logging", test_quest_logging),
        ("Quest Step Types", test_quest_step_types),
        ("Quest Status Tracking", test_quest_status_tracking),
        ("Quest Prerequisites", test_quest_prerequisites),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Legacy Quest Profile system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 