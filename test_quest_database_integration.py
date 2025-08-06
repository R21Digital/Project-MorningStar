#!/usr/bin/env python3
"""
Test script for Quest Database Integration (Batch 009)

This script tests the integration between the quest system and the database
to ensure quests can be loaded and executed dynamically.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import load_quest, list_available_quests
from src.quest_engine import execute_quest_from_database, get_quest_progress


def test_database_quest_loading():
    """Test loading quests from the database."""
    print("🧪 Testing Database Quest Loading...")
    
    # Test listing available quests
    available_quests = list_available_quests()
    print(f"✅ Available quests: {available_quests}")
    
    if not available_quests:
        print("❌ No quests found in database")
        return False
    
    # Test loading a specific quest
    test_quest_id = available_quests[0]
    quest = load_quest(test_quest_id)
    
    if quest:
        print(f"✅ Successfully loaded quest: {quest.name}")
        print(f"   Quest ID: {quest.quest_id}")
        print(f"   Type: {quest.quest_type}")
        print(f"   Difficulty: {quest.difficulty}")
        print(f"   Level Requirement: {quest.level_requirement}")
        print(f"   Planet: {quest.planet}")
        print(f"   Zone: {quest.zone}")
        print(f"   Steps: {len(quest.steps) if quest.steps else 0}")
        
        if quest.steps:
            print("   Step types:")
            for i, step in enumerate(quest.steps[:3]):  # Show first 3 steps
                step_type = step.get("type", "unknown")
                step_id = step.get("step_id", f"step_{i+1}")
                print(f"     {i+1}. {step_id} ({step_type})")
        
        return True
    else:
        print(f"❌ Failed to load quest: {test_quest_id}")
        return False


def test_quest_execution_simulation():
    """Test quest execution simulation (without actual game interaction)."""
    print("\n🧪 Testing Quest Execution Simulation...")
    
    # Test with a known quest ID
    test_quest_id = "legacy_begins"
    
    print(f"Starting quest execution simulation for: {test_quest_id}")
    
    # Simulate quest execution
    result = execute_quest_from_database(test_quest_id)
    
    print(f"Quest execution result: {result}")
    
    if result.get("success"):
        print("✅ Quest execution simulation completed successfully")
        if "progress" in result:
            progress = result["progress"]
            print(f"   Progress: {progress.get('progress_percentage', 0):.1f}%")
            print(f"   Completed steps: {progress.get('completed_steps', 0)}")
            print(f"   Failed steps: {progress.get('failed_steps', 0)}")
        return True
    else:
        print(f"❌ Quest execution failed: {result.get('error', 'Unknown error')}")
        return False


def test_quest_progress_tracking():
    """Test quest progress tracking functionality."""
    print("\n🧪 Testing Quest Progress Tracking...")
    
    # Get current quest progress
    progress = get_quest_progress()
    print(f"Current quest progress: {progress}")
    
    if progress.get("status") == "no_quest":
        print("ℹ️  No active quest (expected when not executing)")
        return True
    else:
        print(f"✅ Quest progress tracking working: {progress.get('quest_name', 'Unknown')}")
        return True


def test_legacy_questline_integration():
    """Test integration with the Legacy Questline."""
    print("\n🧪 Testing Legacy Questline Integration...")
    
    legacy_quests = ["legacy_begins", "desert_secrets", "legacy_call"]
    
    for quest_id in legacy_quests:
        print(f"Testing quest: {quest_id}")
        quest = load_quest(quest_id)
        
        if quest:
            print(f"✅ {quest.name} loaded successfully")
            print(f"   Prerequisites: {quest.prerequisites}")
            print(f"   Quest chain: {quest.quest_chain}")
            print(f"   Rewards: {quest.rewards}")
        else:
            print(f"❌ Failed to load {quest_id}")
            return False
    
    print("✅ All Legacy Questline quests loaded successfully")
    return True


def test_step_type_handling():
    """Test handling of different step types."""
    print("\n🧪 Testing Step Type Handling...")
    
    # Load a quest with various step types
    quest = load_quest("legacy_begins")
    if not quest or not quest.steps:
        print("❌ No quest steps available for testing")
        return False
    
    step_types = set()
    for step in quest.steps:
        step_type = step.get("type", "unknown")
        step_types.add(step_type)
        print(f"   Step type: {step_type}")
    
    expected_types = {"dialogue", "collection", "combat"}
    supported_types = {"dialogue", "movement", "combat", "collection", "exploration", "interaction", "ritual"}
    
    print(f"Found step types: {step_types}")
    print(f"Supported step types: {supported_types}")
    
    # Check if all found types are supported
    unsupported = step_types - supported_types
    if unsupported:
        print(f"⚠️  Unsupported step types found: {unsupported}")
        return False
    else:
        print("✅ All step types are supported")
        return True


def test_fallback_handling():
    """Test fallback handling for missing quest data."""
    print("\n🧪 Testing Fallback Handling...")
    
    # Test with a non-existent quest ID
    non_existent_quest_id = "non_existent_quest_12345"
    
    quest = load_quest(non_existent_quest_id)
    if quest is None:
        print("✅ Correctly handled missing quest (returned None)")
        return True
    else:
        print("❌ Should have returned None for missing quest")
        return False


def main():
    """Run all tests for quest database integration."""
    print("🚀 Starting Quest Database Integration Tests (Batch 009)")
    print("=" * 60)
    
    tests = [
        ("Database Quest Loading", test_database_quest_loading),
        ("Quest Execution Simulation", test_quest_execution_simulation),
        ("Quest Progress Tracking", test_quest_progress_tracking),
        ("Legacy Questline Integration", test_legacy_questline_integration),
        ("Step Type Handling", test_step_type_handling),
        ("Fallback Handling", test_fallback_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Quest database integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 