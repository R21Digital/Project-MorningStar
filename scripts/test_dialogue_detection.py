#!/usr/bin/env python3
"""Test script for dialogue detection functionality."""

import time
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dialogue_detector import (
    get_dialogue_detector, detect_dialogue_window, 
    handle_quest_dialogue, handle_trainer_dialogue,
    auto_accept_quests, auto_complete_quests
)


def test_dialogue_detection():
    """Test the dialogue detection system."""
    print("=== Dialogue Detection Test ===")
    
    detector = get_dialogue_detector()
    
    # Test 1: Detect dialogue window
    print("\n1. Testing dialogue window detection...")
    dialogue = detect_dialogue_window()
    
    if dialogue:
        print(f"✓ Dialogue detected!")
        print(f"  - Type: {dialogue.window_type}")
        print(f"  - Text: {dialogue.text[:100]}...")
        print(f"  - Options: {dialogue.options}")
        print(f"  - Confidence: {dialogue.confidence:.1f}%")
    else:
        print("✗ No dialogue window detected")
    
    # Test 2: Auto-accept quests
    print("\n2. Testing auto-accept quests...")
    if auto_accept_quests():
        print("✓ Quest auto-accepted!")
    else:
        print("✗ No quest to accept or auto-accept failed")
    
    # Test 3: Auto-complete quests
    print("\n3. Testing auto-complete quests...")
    if auto_complete_quests():
        print("✓ Quest auto-completed!")
    else:
        print("✗ No quest to complete or auto-complete failed")
    
    # Test 4: Handle trainer dialogue
    print("\n4. Testing trainer dialogue handling...")
    if handle_trainer_dialogue():
        print("✓ Trainer dialogue handled!")
    else:
        print("✗ No trainer dialogue or handling failed")
    
    # Test 5: Wait for dialogue
    print("\n5. Testing wait for dialogue (5 seconds)...")
    dialogue = detector.wait_for_dialogue(timeout=5.0)
    if dialogue:
        print(f"✓ Dialogue appeared after waiting!")
        print(f"  - Type: {dialogue.window_type}")
        print(f"  - Options: {dialogue.options}")
    else:
        print("✗ No dialogue appeared within timeout")


def test_quest_integration():
    """Test integration with quest system."""
    print("\n=== Quest Integration Test ===")
    
    detector = get_dialogue_detector()
    
    # Test quest acceptance
    print("\n1. Testing quest acceptance...")
    if handle_quest_dialogue("accept"):
        print("✓ Quest accepted successfully!")
    else:
        print("✗ Quest acceptance failed or no quest dialogue")
    
    # Test quest completion
    print("\n2. Testing quest completion...")
    if handle_quest_dialogue("complete"):
        print("✓ Quest completed successfully!")
    else:
        print("✗ Quest completion failed or no quest dialogue")
    
    # Test quest decline
    print("\n3. Testing quest decline...")
    if handle_quest_dialogue("decline"):
        print("✓ Quest declined successfully!")
    else:
        print("✗ Quest decline failed or no quest dialogue")


def test_logging():
    """Test the logging functionality."""
    print("\n=== Logging Test ===")
    
    detector = get_dialogue_detector()
    
    # Create a test dialogue window
    from core.dialogue_detector import DialogueWindow
    
    test_dialogue = DialogueWindow(
        x=100, y=200, width=300, height=400,
        text="Test dialogue for logging",
        options=["Accept", "Decline"],
        confidence=85.0,
        window_type="quest"
    )
    
    # Test logging
    print("1. Testing dialogue event logging...")
    detector.log_dialogue_event(
        "test_event", 
        test_dialogue, 
        "test_action", 
        True, 
        {"test_key": "test_value"}
    )
    print("✓ Log entry created!")
    
    # Check if log file exists
    import datetime
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    log_file = os.path.join("logs", "dialogue", f"dialogue_{date_str}.json")
    
    if os.path.exists(log_file):
        print(f"✓ Log file created: {log_file}")
        
        # Read and display log content
        import json
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        print(f"  - Log entries: {len(logs)}")
        if logs:
            latest_entry = logs[-1]
            print(f"  - Latest event: {latest_entry.get('event_type')}")
            print(f"  - Action: {latest_entry.get('action')}")
            print(f"  - Success: {latest_entry.get('success')}")
    else:
        print("✗ Log file not found")


def main():
    """Main test function."""
    print("Dialogue Detection System Test")
    print("=" * 40)
    
    try:
        # Test basic functionality
        test_dialogue_detection()
        
        # Test quest integration
        test_quest_integration()
        
        # Test logging
        test_logging()
        
        print("\n" + "=" * 40)
        print("✓ All tests completed!")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 