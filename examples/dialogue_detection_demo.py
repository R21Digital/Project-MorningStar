#!/usr/bin/env python3
"""
Dialogue Detection System Demo

This script demonstrates how to use the OCR-based dialogue detection system
for automating NPC interactions in SWG (Star Wars Galaxies).

Usage Examples:
    python examples/dialogue_detection_demo.py --mode single
    python examples/dialogue_detection_demo.py --mode scan --duration 30
    python examples/dialogue_detection_demo.py --mode wait --expected quest_offer
"""

import argparse
import time
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.dialogue_detector import (
    DialogueDetector, 
    detect_dialogue, 
    scan_dialogues,
    register_custom_dialogue_pattern
)
from src.execution.dialogue import (
    execute_dialogue,
    scan_and_handle_dialogues,
    wait_for_dialogue,
    get_dialogue_history
)


def demo_single_detection():
    """Demonstrate single dialogue detection."""
    print("=== Single Dialogue Detection Demo ===")
    print("This will attempt to detect and handle any dialogue currently on screen...")
    
    detection = detect_dialogue(auto_respond=True)
    
    if detection:
        print(f"✅ Dialogue detected!")
        print(f"   Type: {detection.dialogue_type}")
        print(f"   Confidence: {detection.confidence:.2f}")
        print(f"   Action taken: {detection.response_action}")
        print(f"   Text preview: {detection.text_content[:100]}...")
    else:
        print("❌ No dialogue detected on screen")
        print("   Make sure you have a dialogue window open in SWG")


def demo_dialogue_scanning(duration: float = 10.0):
    """Demonstrate continuous dialogue scanning."""
    print(f"=== Dialogue Scanning Demo (Duration: {duration}s) ===")
    print("This will continuously scan for dialogues and handle them automatically...")
    print("Start a conversation with an NPC or open quest dialogues during this time.")
    
    detections = scan_dialogues(duration=duration, auto_respond=True)
    
    print(f"\n📊 Scan Results:")
    print(f"   Total dialogues detected: {len(detections)}")
    
    if detections:
        for i, detection in enumerate(detections, 1):
            print(f"   {i}. {detection.dialogue_type} (confidence: {detection.confidence:.2f})")
    else:
        print("   No dialogues were detected during the scan period")


def demo_wait_for_dialogue(expected_type: str = None, timeout: float = 30.0):
    """Demonstrate waiting for a specific dialogue type."""
    print(f"=== Wait for Dialogue Demo ===")
    if expected_type:
        print(f"Waiting for '{expected_type}' dialogue (timeout: {timeout}s)...")
    else:
        print(f"Waiting for any dialogue (timeout: {timeout}s)...")
    
    print("Start a conversation with an NPC now...")
    
    success = wait_for_dialogue(timeout=timeout, expected_type=expected_type)
    
    if success:
        print(f"✅ Expected dialogue detected and handled!")
    else:
        print(f"❌ Timeout waiting for dialogue")


def demo_quest_automation():
    """Demonstrate quest-specific dialogue automation."""
    print("=== Quest Automation Demo ===")
    print("This demonstrates automated quest acceptance and completion...")
    
    # Simulate quest steps with dialogue components
    quest_steps = [
        {
            "type": "dialogue",
            "target": "Quest Giver",
            "dialogue_type": "quest_offer",
            "region": "quest_window"
        },
        {
            "type": "dialogue", 
            "target": "Quest NPC",
            "dialogue_type": "quest_completion",
            "region": "dialogue_box"
        }
    ]
    
    print("Simulating quest dialogue steps...")
    for i, step in enumerate(quest_steps, 1):
        print(f"\nStep {i}: {step['dialogue_type']} with {step['target']}")
        
        # In a real scenario, you'd have actual dialogue windows open
        # Here we just demonstrate the API
        success = execute_dialogue(step)
        
        if success:
            print(f"✅ Step {i} completed successfully")
        else:
            print(f"❌ Step {i} failed")
            
        time.sleep(2)  # Brief pause between steps


def demo_trainer_automation():
    """Demonstrate trainer dialogue automation."""
    print("=== Trainer Automation Demo ===")
    print("This demonstrates automated trainer interactions...")
    
    trainer_step = {
        "type": "dialogue",
        "target": "Trainer",
        "dialogue_type": "trainer",
        "region": "dialogue_box"
    }
    
    print("Attempting to interact with trainer...")
    success = execute_dialogue(trainer_step)
    
    if success:
        print("✅ Trainer interaction completed")
    else:
        print("❌ Trainer interaction failed")


def demo_custom_patterns():
    """Demonstrate registering custom dialogue patterns."""
    print("=== Custom Pattern Demo ===")
    print("This shows how to register custom dialogue patterns...")
    
    # Register a custom pattern for auction house interactions
    register_custom_dialogue_pattern(
        "auction_house",
        [r"auction.*house", r"buy.*sell.*items", r"marketplace"],
        {"key": "1", "description": "Browse auctions"}
    )
    
    # Register a custom pattern for guild interactions
    register_custom_dialogue_pattern(
        "guild_recruiter", 
        [r"join.*guild", r"recruitment.*officer", r"guild.*invitation"],
        {"key": "2", "description": "Decline invitation"}
    )
    
    print("✅ Custom patterns registered:")
    print("   - auction_house: for auction house interactions")
    print("   - guild_recruiter: for guild recruitment dialogues")
    print("\nThese patterns will now be recognized by the dialogue detector!")


def demo_dialogue_history():
    """Demonstrate dialogue history retrieval."""
    print("=== Dialogue History Demo ===")
    print("Retrieving recent dialogue history...")
    
    history = get_dialogue_history(limit=10)
    
    if history:
        print(f"📖 Found {len(history)} recent dialogues:")
        for i, entry in enumerate(history, 1):
            timestamp = entry.get("timestamp", "Unknown")
            dialogue_type = entry.get("dialogue_type", "Unknown")
            print(f"   {i}. {timestamp}: {dialogue_type}")
    else:
        print("📖 No dialogue history found")
        print("   Run some dialogue detection first to build up history")


def main():
    """Main demo function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Dialogue Detection System Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python dialogue_detection_demo.py --mode single
    python dialogue_detection_demo.py --mode scan --duration 30
    python dialogue_detection_demo.py --mode wait --expected quest_offer --timeout 60
    python dialogue_detection_demo.py --mode quest
    python dialogue_detection_demo.py --mode trainer
    python dialogue_detection_demo.py --mode history
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["single", "scan", "wait", "quest", "trainer", "custom", "history"],
        default="single",
        help="Demo mode to run"
    )
    
    parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="Duration for scanning mode (seconds)"
    )
    
    parser.add_argument(
        "--expected",
        type=str,
        help="Expected dialogue type for wait mode"
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Timeout for wait mode (seconds)"
    )
    
    args = parser.parse_args()
    
    print("🎮 SWG Dialogue Detection System Demo")
    print("=" * 50)
    print()
    
    # Check dependencies
    try:
        import cv2
        import pytesseract
        import pyautogui
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install: pip install opencv-python pytesseract pyautogui")
        return
    
    print()
    
    # Run selected demo
    if args.mode == "single":
        demo_single_detection()
        
    elif args.mode == "scan":
        demo_dialogue_scanning(duration=args.duration)
        
    elif args.mode == "wait":
        demo_wait_for_dialogue(expected_type=args.expected, timeout=args.timeout)
        
    elif args.mode == "quest":
        demo_quest_automation()
        
    elif args.mode == "trainer":
        demo_trainer_automation()
        
    elif args.mode == "custom":
        demo_custom_patterns()
        
    elif args.mode == "history":
        demo_dialogue_history()
    
    print()
    print("🎯 Demo completed!")
    print("\nTips for real usage:")
    print("- Ensure SWG is running and visible on screen")
    print("- Position dialogue windows in predictable locations")
    print("- Test different OCR regions for better detection")
    print("- Review logs in logs/dialogue/ for debugging")
    print("- Customize patterns for your specific server/gameplay")


if __name__ == "__main__":
    main()