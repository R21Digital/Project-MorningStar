#!/usr/bin/env python3
"""Demo script for Batch 150 - Quest Log Completion Verifier.

This script demonstrates the quest verification functionality including:
- OCR-based quest log scanning
- System log parsing
- Session tracking integration
- Manual quest marking
- CLI tool usage
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.quest_verifier import (
    get_quest_verifier,
    verify_quest_completed,
    mark_quest_completed,
    get_completion_status
)


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n📋 {title}")
    print("-" * 40)


def demo_quest_verification() -> None:
    """Demonstrate quest verification functionality."""
    print_header("Batch 150 - Quest Log Completion Verifier Demo")
    
    # Initialize quest verifier
    verifier = get_quest_verifier()
    print(f"✅ Quest verifier initialized")
    print(f"📁 History file: {verifier.history_file}")
    print(f"🔍 OCR engine: {verifier.ocr_engine}")
    
    # Test quests
    test_quests = [
        "Legacy Quest Part IV",
        "Tatooine Introduction",
        "Corellia Training",
        "Naboo Diplomacy",
        "Mustafar Expedition"
    ]
    
    print_section("Quest Verification Examples")
    
    for quest_name in test_quests:
        print(f"\n🔍 Checking: {quest_name}")
        
        # Get detailed status
        status = get_completion_status(quest_name)
        
        if status["is_completed"]:
            print(f"   ✅ COMPLETED")
            if status.get("completion_date"):
                print(f"   📅 Date: {status['completion_date']}")
            if status.get("verification_method"):
                print(f"   🔧 Method: {status['verification_method']}")
        else:
            print(f"   ❌ NOT COMPLETED")
        
        print(f"   ⏰ Last checked: {status['last_checked']}")


def demo_manual_marking() -> None:
    """Demonstrate manual quest marking."""
    print_section("Manual Quest Marking")
    
    # Mark some quests as completed
    test_markings = [
        ("Legacy Quest Part IV", "demo"),
        ("Tatooine Introduction", "demo"),
        ("Corellia Training", "demo")
    ]
    
    for quest_name, method in test_markings:
        print(f"\n📝 Marking '{quest_name}' as completed (method: {method})")
        mark_quest_completed(quest_name, method)
        
        # Verify the marking
        is_completed = verify_quest_completed(quest_name)
        print(f"   ✅ Verification result: {is_completed}")


def demo_history_management() -> None:
    """Demonstrate quest history management."""
    print_section("Quest History Management")
    
    verifier = get_quest_verifier()
    
    # Show current history
    print("\n📊 Current Quest History:")
    history = verifier.quest_history
    
    print(f"   Total completed quests: {len(history['completed_quests'])}")
    print(f"   Last updated: {history['last_updated']}")
    
    if history["completed_quests"]:
        print("\n   Completed Quests:")
        for quest_name in sorted(history["completed_quests"].keys()):
            completion_date = history["completion_dates"].get(quest_name, "Unknown")
            method = history["verification_methods"].get(quest_name, "Unknown")
            print(f"     - {quest_name} ({method}, {completion_date})")


def demo_verification_methods() -> None:
    """Demonstrate different verification methods."""
    print_section("Verification Methods")
    
    verifier = get_quest_verifier()
    
    print("\n🔍 Available verification methods:")
    print("   1. Internal quest history")
    print("   2. OCR from quest log UI")
    print("   3. In-game system logs")
    print("   4. Session tracking data")
    
    # Test each method for a specific quest
    test_quest = "Legacy Quest Part IV"
    print(f"\n🧪 Testing methods for: {test_quest}")
    
    # Method 1: Internal history
    print(f"\n   1. Internal history check:")
    result = verifier._check_internal_history(test_quest)
    print(f"      Result: {result}")
    
    # Method 2: Quest log UI (simulated)
    print(f"\n   2. Quest log UI check:")
    print(f"      (Simulated - would scan screen regions)")
    print(f"      Regions: {list(verifier.quest_log_regions.keys())}")
    
    # Method 3: System logs
    print(f"\n   3. System logs check:")
    print(f"      Patterns: {verifier.completion_patterns}")
    
    # Method 4: Session tracking
    print(f"\n   4. Session tracking check:")
    print(f"      (Would check session data and logs)")


def demo_cli_usage() -> None:
    """Demonstrate CLI tool usage."""
    print_section("CLI Tool Usage")
    
    print("\n💻 Available CLI commands:")
    print("   python cli/quest_verifier_cli.py verify \"Legacy Quest Part IV\"")
    print("   python cli/quest_verifier_cli.py mark-complete \"Legacy Quest Part IV\"")
    print("   python cli/quest_verifier_cli.py list-completed")
    print("   python cli/quest_verifier_cli.py show-history")
    print("   python cli/quest_verifier_cli.py clear-history \"Legacy Quest Part IV\"")
    
    print("\n📝 Example CLI session:")
    print("   $ python cli/quest_verifier_cli.py verify \"Legacy Quest Part IV\"")
    print("   🔍 Verifying quest completion: Legacy Quest Part IV")
    print("   --------------------------------------------------")
    print("   ❌ Quest 'Legacy Quest Part IV' is NOT COMPLETED")
    print("      Last checked: 2024-01-15T10:30:00")
    print("   ❌ RESULT: Quest is not completed")
    
    print("\n   $ python cli/quest_verifier_cli.py mark-complete \"Legacy Quest Part IV\"")
    print("   📝 Marking quest as completed: Legacy Quest Part IV")
    print("   --------------------------------------------------")
    print("   ✅ Quest 'Legacy Quest Part IV' is COMPLETED")
    print("      Completed: 2024-01-15T10:30:00")
    print("      Verified via: manual")
    print("      Last checked: 2024-01-15T10:30:00")
    print("   ✅ Quest has been marked as completed")


def demo_integration_example() -> None:
    """Demonstrate integration with MS11."""
    print_section("MS11 Integration Example")
    
    print("\n🔧 Integration with MS11 quest system:")
    print("   - Prevents starting already completed quests")
    print("   - Uses verify_quest_completed() function")
    print("   - Returns True/False for quest completion status")
    
    # Simulate MS11 quest checking
    print("\n🧪 Simulating MS11 quest checking:")
    
    quests_to_check = [
        "Legacy Quest Part IV",
        "Tatooine Introduction", 
        "Corellia Training"
    ]
    
    for quest_name in quests_to_check:
        is_completed = verify_quest_completed(quest_name)
        status = "✅ COMPLETED" if is_completed else "❌ NOT COMPLETED"
        print(f"   {quest_name}: {status}")
        
        if not is_completed:
            print(f"     → MS11 can start this quest")
        else:
            print(f"     → MS11 will skip this quest")


def create_sample_data() -> None:
    """Create sample quest history data."""
    print_section("Creating Sample Data")
    
    # Create sample quest history
    sample_history = {
        "completed_quests": {
            "Legacy Quest Part IV": True,
            "Tatooine Introduction": True,
            "Corellia Training": True
        },
        "completion_dates": {
            "Legacy Quest Part IV": "2024-01-10T15:30:00",
            "Tatooine Introduction": "2024-01-12T09:15:00", 
            "Corellia Training": "2024-01-14T14:45:00"
        },
        "verification_methods": {
            "Legacy Quest Part IV": "quest_log_ui",
            "Tatooine Introduction": "system_logs",
            "Corellia Training": "session_tracking"
        },
        "last_updated": datetime.now().isoformat()
    }
    
    # Save to history file
    history_file = Path("data/quest_history.json")
    history_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(sample_history, f, indent=2, default=str)
    
    print(f"✅ Created sample quest history with {len(sample_history['completed_quests'])} quests")
    print(f"📁 Saved to: {history_file}")


def main() -> None:
    """Main demo function."""
    try:
        # Create sample data first
        create_sample_data()
        
        # Run all demos
        demo_quest_verification()
        demo_manual_marking()
        demo_history_management()
        demo_verification_methods()
        demo_cli_usage()
        demo_integration_example()
        
        print_header("Demo Complete")
        print("✅ All Batch 150 functionality demonstrated successfully!")
        print("\n📚 Next steps:")
        print("   - Use the CLI tool for manual quest management")
        print("   - Integrate verify_quest_completed() into MS11")
        print("   - Configure OCR regions for your game UI")
        print("   - Set up system log monitoring")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 