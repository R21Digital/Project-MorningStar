#!/usr/bin/env python3
"""CLI tool for Batch 150 - Quest Log Completion Verifier.

Provides command-line interface for:
- Verifying quest completion status
- Manually marking quests as complete
- Viewing quest completion history
- Clearing quest history
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.quest_verifier import (
    get_quest_verifier,
    verify_quest_completed,
    mark_quest_completed,
    get_completion_status
)


def print_status(status: dict) -> None:
    """Print quest completion status in a formatted way."""
    quest_name = status["quest_name"]
    is_completed = status["is_completed"]
    
    if is_completed:
        print(f"✅ Quest '{quest_name}' is COMPLETED")
        if status.get("completion_date"):
            print(f"   Completed: {status['completion_date']}")
        if status.get("verification_method"):
            print(f"   Verified via: {status['verification_method']}")
    else:
        print(f"❌ Quest '{quest_name}' is NOT COMPLETED")
    
    print(f"   Last checked: {status['last_checked']}")
    print()


def verify_quest_command(args) -> None:
    """Handle the verify command."""
    quest_name = args.quest_name
    
    print(f"🔍 Verifying quest completion: {quest_name}")
    print("-" * 50)
    
    # Get detailed status
    status = get_completion_status(quest_name)
    print_status(status)
    
    # Also show simple boolean result
    is_completed = verify_quest_completed(quest_name)
    if is_completed:
        print("✅ RESULT: Quest is completed")
    else:
        print("❌ RESULT: Quest is not completed")


def mark_complete_command(args) -> None:
    """Handle the mark-complete command."""
    quest_name = args.quest_name
    method = args.method or "manual"
    
    print(f"📝 Marking quest as completed: {quest_name}")
    print("-" * 50)
    
    # Mark as completed
    mark_quest_completed(quest_name, method)
    
    # Show updated status
    status = get_completion_status(quest_name)
    print_status(status)
    
    print("✅ Quest has been marked as completed")


def list_completed_command(args) -> None:
    """Handle the list-completed command."""
    verifier = get_quest_verifier()
    completed_quests = verifier.get_completed_quests()
    
    print(f"📋 Completed Quests ({len(completed_quests)} total)")
    print("-" * 50)
    
    if not completed_quests:
        print("No completed quests found.")
        return
    
    # Load history for additional details
    history = verifier.quest_history
    
    for i, quest_name in enumerate(sorted(completed_quests), 1):
        completion_date = history["completion_dates"].get(quest_name, "Unknown")
        method = history["verification_methods"].get(quest_name, "Unknown")
        
        print(f"{i:2d}. {quest_name}")
        print(f"     Completed: {completion_date}")
        print(f"     Method: {method}")
        print()


def clear_history_command(args) -> None:
    """Handle the clear-history command."""
    quest_name = args.quest_name
    
    verifier = get_quest_verifier()
    
    if quest_name:
        print(f"🗑️  Clearing history for quest: {quest_name}")
        verifier.clear_quest_history(quest_name)
        print(f"✅ Cleared history for '{quest_name}'")
    else:
        print("🗑️  Clearing all quest history...")
        verifier.clear_quest_history()
        print("✅ Cleared all quest history")


def show_history_command(args) -> None:
    """Handle the show-history command."""
    verifier = get_quest_verifier()
    history = verifier.quest_history
    
    print("📊 Quest Completion History")
    print("-" * 50)
    
    print(f"Total completed quests: {len(history['completed_quests'])}")
    print(f"Last updated: {history['last_updated']}")
    print(f"History file: {verifier.history_file}")
    print()
    
    if history["completed_quests"]:
        print("Completed Quests:")
        for quest_name in sorted(history["completed_quests"].keys()):
            completion_date = history["completion_dates"].get(quest_name, "Unknown")
            method = history["verification_methods"].get(quest_name, "Unknown")
            print(f"  - {quest_name} ({method}, {completion_date})")
    else:
        print("No completed quests in history.")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Batch 150 - Quest Log Completion Verifier CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s verify "Legacy Quest Part IV"
  %(prog)s mark-complete "Legacy Quest Part IV"
  %(prog)s list-completed
  %(prog)s clear-history "Legacy Quest Part IV"
  %(prog)s show-history
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Verify command
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify if a quest is completed"
    )
    verify_parser.add_argument(
        "quest_name",
        help="Name of the quest to verify"
    )
    verify_parser.set_defaults(func=verify_quest_command)
    
    # Mark complete command
    mark_parser = subparsers.add_parser(
        "mark-complete",
        help="Manually mark a quest as completed"
    )
    mark_parser.add_argument(
        "quest_name",
        help="Name of the quest to mark as completed"
    )
    mark_parser.add_argument(
        "--method",
        default="manual",
        help="Method used to mark completion (default: manual)"
    )
    mark_parser.set_defaults(func=mark_complete_command)
    
    # List completed command
    list_parser = subparsers.add_parser(
        "list-completed",
        help="List all completed quests"
    )
    list_parser.set_defaults(func=list_completed_command)
    
    # Clear history command
    clear_parser = subparsers.add_parser(
        "clear-history",
        help="Clear quest completion history"
    )
    clear_parser.add_argument(
        "quest_name",
        nargs="?",
        help="Specific quest to clear (optional, clears all if not specified)"
    )
    clear_parser.set_defaults(func=clear_history_command)
    
    # Show history command
    show_parser = subparsers.add_parser(
        "show-history",
        help="Show quest completion history details"
    )
    show_parser.set_defaults(func=show_history_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 