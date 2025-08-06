#!/usr/bin/env python3
"""
CLI Progress Tracker for MS11 Batch 055

Provides command-line interface for the enhanced progress tracker
with checklist support and "All the Things" style tracking.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.progress_tracker import (
    get_enhanced_progress_tracker,
    update_checklist_item,
    get_overall_progress,
    get_suggestions,
    export_progress_report,
    ChecklistStatus,
    ChecklistCategory
)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def display_overall_progress():
    """Display overall progress across all checklists."""
    progress = get_overall_progress()
    
    print("\n" + "="*60)
    print("OVERALL PROGRESS SUMMARY")
    print("="*60)
    
    print(f"Total Items: {progress['total_items']}")
    print(f"Completed: {progress['total_completed']}")
    print(f"Overall Completion: {progress['overall_percentage']:.1f}%")
    print(f"Total XP Gained: {progress['total_xp_gained']:,}")
    print(f"Total Credits Gained: {progress['total_credits_gained']:,}")
    
    print("\nCategory Progress:")
    print("-" * 40)
    for category, data in progress['category_progress'].items():
        if data['total'] > 0:
            print(f"{category.replace('_', ' ').title()}: "
                  f"{data['completed']}/{data['total']} "
                  f"({data['percentage']:.1f}%)")
    
    print("\nChecklist Progress:")
    print("-" * 40)
    for name, data in progress['checklists'].items():
        print(f"{name}: {data['completed_items']}/{data['total_items']} "
              f"({data['completion_percentage']:.1f}%)")


def display_checklist_details(checklist_name: str):
    """Display detailed information for a specific checklist."""
    tracker = get_enhanced_progress_tracker()
    checklist = tracker.get_checklist(checklist_name)
    
    if not checklist:
        print(f"Checklist not found: {checklist_name}")
        return
    
    print(f"\n{checklist.name.upper()}")
    print("=" * len(checklist.name))
    print(f"Description: {checklist.description}")
    print(f"Category: {checklist.category.value.replace('_', ' ').title()}")
    print(f"Progress: {checklist.completed_items}/{checklist.total_items} "
          f"({checklist.completion_percentage:.1f}%)")
    print(f"Last Updated: {checklist.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nItems:")
    print("-" * 60)
    
    for item in checklist.items:
        status_icon = "✓" if item.status == ChecklistStatus.COMPLETED else "□"
        print(f"{status_icon} {item.name}")
        print(f"    Description: {item.description}")
        status_value = item.status.value if hasattr(item.status, 'value') else str(item.status)
        print(f"    Status: {status_value.replace('_', ' ').title()}")
        print(f"    Progress: {item.progress * 100:.1f}%")
        
        if item.planet:
            print(f"    Planet: {item.planet}")
        if item.location:
            print(f"    Location: {item.location}")
        if item.xp_reward > 0:
            print(f"    XP Reward: {item.xp_reward:,}")
        if item.credit_reward > 0:
            print(f"    Credit Reward: {item.credit_reward:,}")
        
        if item.requirements:
            print(f"    Requirements: {', '.join(item.requirements)}")
        if item.rewards:
            print(f"    Rewards: {', '.join(item.rewards)}")
        
        if item.completed_at:
            print(f"    Completed: {item.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print()


def display_suggestions(current_location: str = None):
    """Display suggestions for next items to work on."""
    suggestions = get_suggestions(current_location)
    
    print("\n" + "="*60)
    print("SUGGESTIONS FOR NEXT ITEMS")
    print("="*60)
    
    if current_location:
        print(f"Based on current location: {current_location}")
    
    if not suggestions:
        print("No suggestions available. All items may be completed or no suitable items found.")
        return
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion['item_name']}")
        print(f"   Checklist: {suggestion['checklist_name']}")
        print(f"   Description: {suggestion['description']}")
        
        if suggestion['planet']:
            print(f"   Planet: {suggestion['planet']}")
        if suggestion['location']:
            print(f"   Location: {suggestion['location']}")
        
        print(f"   XP Reward: {suggestion['xp_reward']:,}")
        print(f"   Credit Reward: {suggestion['credit_reward']:,}")
        print(f"   Priority: {suggestion['priority']:.2f}")


def update_item_status(checklist_name: str, item_id: str, status: str, progress: float = None):
    """Update the status of a checklist item."""
    try:
        status_enum = ChecklistStatus(status.lower())
    except ValueError:
        print(f"Invalid status: {status}")
        print(f"Valid statuses: {[s.value for s in ChecklistStatus]}")
        return False
    
    success = update_checklist_item(checklist_name, item_id, status_enum, progress)
    
    if success:
        print(f"Successfully updated {checklist_name}:{item_id} to {status}")
    else:
        print(f"Failed to update {checklist_name}:{item_id}")
    
    return success


def list_checklists():
    """List all available checklists."""
    tracker = get_enhanced_progress_tracker()
    checklists = tracker.get_all_checklists()
    
    print("\n" + "="*60)
    print("AVAILABLE CHECKLISTS")
    print("="*60)
    
    for name, checklist in checklists.items():
        print(f"\n{name}")
        print(f"  Category: {checklist.category.value.replace('_', ' ').title()}")
        print(f"  Description: {checklist.description}")
        print(f"  Progress: {checklist.completed_items}/{checklist.total_items} "
              f"({checklist.completion_percentage:.1f}%)")
        print(f"  Items: {len(checklist.items)}")


def export_report(output_file: str):
    """Export a detailed progress report."""
    try:
        export_progress_report(output_file)
        print(f"Progress report exported to: {output_file}")
    except Exception as e:
        print(f"Error exporting report: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Enhanced Progress Tracker CLI for MS11 Batch 055",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --overall                    # Show overall progress
  %(prog)s --checklist "Legacy Quest"   # Show checklist details
  %(prog)s --suggestions                # Show suggestions
  %(prog)s --suggestions "Tatooine"     # Show suggestions for Tatooine
  %(prog)s --update "Legacy Quest" "item_001" "completed"  # Update item status
  %(prog)s --list                       # List all checklists
  %(prog)s --export report.json         # Export progress report
        """
    )
    
    parser.add_argument(
        '--overall', 
        action='store_true',
        help='Display overall progress summary'
    )
    
    parser.add_argument(
        '--checklist',
        type=str,
        help='Display details for a specific checklist'
    )
    
    parser.add_argument(
        '--suggestions',
        nargs='?',
        const='',
        metavar='LOCATION',
        help='Display suggestions (optionally for a specific location)'
    )
    
    parser.add_argument(
        '--update',
        nargs=3,
        metavar=('CHECKLIST', 'ITEM_ID', 'STATUS'),
        help='Update item status (checklist, item_id, status)'
    )
    
    parser.add_argument(
        '--progress',
        type=float,
        help='Progress value (0.0 to 1.0) for update command'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available checklists'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        metavar='FILE',
        help='Export progress report to file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle commands
    if args.overall:
        display_overall_progress()
    
    elif args.checklist:
        display_checklist_details(args.checklist)
    
    elif args.suggestions is not None:
        location = args.suggestions if args.suggestions else None
        display_suggestions(location)
    
    elif args.update:
        checklist_name, item_id, status = args.update
        update_item_status(checklist_name, item_id, status, args.progress)
    
    elif args.list:
        list_checklists()
    
    elif args.export:
        export_report(args.export)
    
    else:
        # Default: show overall progress
        display_overall_progress()


if __name__ == "__main__":
    main() 