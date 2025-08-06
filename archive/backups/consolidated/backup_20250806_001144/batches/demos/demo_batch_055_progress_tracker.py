#!/usr/bin/env python3
"""
Demo for Enhanced Progress Tracker + "All the Things" To-Do List System (Batch 055)

This demo showcases the enhanced progress tracker with checklist support,
including markdown parsing, progress tracking, and smart suggestions.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.progress_tracker import (
    get_enhanced_progress_tracker,
    update_checklist_item,
    get_overall_progress,
    get_suggestions,
    export_progress_report,
    ChecklistStatus,
    ChecklistCategory
)


def setup_demo_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def demo_checklist_loading():
    """Demo checklist loading from markdown files."""
    print("\n" + "="*60)
    print("DEMO: CHECKLIST LOADING")
    print("="*60)
    
    tracker = get_enhanced_progress_tracker()
    checklists = tracker.get_all_checklists()
    
    print(f"Loaded {len(checklists)} checklists:")
    for name, checklist in checklists.items():
        print(f"  - {name}: {len(checklist.items)} items, "
              f"{checklist.completion_percentage:.1f}% complete")
    
    return tracker


def demo_overall_progress():
    """Demo overall progress tracking."""
    print("\n" + "="*60)
    print("DEMO: OVERALL PROGRESS")
    print("="*60)
    
    progress = get_overall_progress()
    
    print(f"Total Items: {progress['total_items']}")
    print(f"Completed: {progress['total_completed']}")
    print(f"Overall Completion: {progress['overall_percentage']:.1f}%")
    print(f"Total XP Gained: {progress['total_xp_gained']:,}")
    print(f"Total Credits Gained: {progress['total_credits_gained']:,}")
    
    print("\nCategory Progress:")
    for category, data in progress['category_progress'].items():
        if data['total'] > 0:
            print(f"  {category.replace('_', ' ').title()}: "
                  f"{data['completed']}/{data['total']} "
                  f"({data['percentage']:.1f}%)")


def demo_checklist_details():
    """Demo detailed checklist information."""
    print("\n" + "="*60)
    print("DEMO: CHECKLIST DETAILS")
    print("="*60)
    
    tracker = get_enhanced_progress_tracker()
    
    # Show details for the first checklist
    checklists = list(tracker.get_all_checklists().items())
    if checklists:
        name, checklist = checklists[0]
        print(f"Checklist: {checklist.name}")
        category_value = checklist.category.value if hasattr(checklist.category, 'value') else str(checklist.category)
        print(f"Category: {category_value.replace('_', ' ').title()}")
        print(f"Description: {checklist.description}")
        print(f"Progress: {checklist.completed_items}/{checklist.total_items} "
              f"({checklist.completion_percentage:.1f}%)")
        
        print(f"\nFirst 3 items:")
        for i, item in enumerate(checklist.items[:3], 1):
            print(f"  {i}. {item.name}")
            status_value = item.status.value if hasattr(item.status, 'value') else str(item.status)
            print(f"     Status: {status_value}")
            print(f"     Planet: {item.planet or 'N/A'}")
            print(f"     XP Reward: {item.xp_reward:,}")


def demo_item_updates():
    """Demo updating checklist items."""
    print("\n" + "="*60)
    print("DEMO: ITEM UPDATES")
    print("="*60)
    
    tracker = get_enhanced_progress_tracker()
    checklists = list(tracker.get_all_checklists().items())
    
    if not checklists:
        print("No checklists available for demo")
        return
    
    name, checklist = checklists[0]
    
    # Find an item to update
    if checklist.items:
        item = checklist.items[0]
        print(f"Updating item: {item.name}")
        status_value = item.status.value if hasattr(item.status, 'value') else str(item.status)
        print(f"Current status: {status_value}")
        
        # Update to in progress
        success = update_checklist_item(name, item.id, "in_progress", 0.5)
        print(f"Updated to in_progress (50%): {'Success' if success else 'Failed'}")
        
        # Update to completed
        success = update_checklist_item(name, item.id, "completed")
        print(f"Updated to completed: {'Success' if success else 'Failed'}")
        
        # Show updated progress
        updated_checklist = tracker.get_checklist(name)
        print(f"Updated progress: {updated_checklist.completed_items}/{updated_checklist.total_items} "
              f"({updated_checklist.completion_percentage:.1f}%)")


def demo_suggestions():
    """Demo smart suggestions."""
    print("\n" + "="*60)
    print("DEMO: SMART SUGGESTIONS")
    print("="*60)
    
    # Get general suggestions
    suggestions = get_suggestions()
    print(f"General suggestions ({len(suggestions)} items):")
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion['item_name']}")
        print(f"     Checklist: {suggestion['checklist_name']}")
        print(f"     Planet: {suggestion['planet'] or 'N/A'}")
        print(f"     XP Reward: {suggestion['xp_reward']:,}")
        priority = suggestion['priority']
        if isinstance(priority, (int, float)):
            print(f"     Priority: {priority:.2f}")
        else:
            print(f"     Priority: {priority}")
    
    # Get location-specific suggestions
    location_suggestions = get_suggestions("Tatooine")
    print(f"\nTatooine-specific suggestions ({len(location_suggestions)} items):")
    for i, suggestion in enumerate(location_suggestions[:3], 1):
        print(f"  {i}. {suggestion['item_name']}")
        print(f"     Checklist: {suggestion['checklist_name']}")
        print(f"     Location: {suggestion['location'] or 'N/A'}")
        print(f"     XP Reward: {suggestion['xp_reward']:,}")
        priority = suggestion['priority']
        if isinstance(priority, (int, float)):
            print(f"     Priority: {priority:.2f}")
        else:
            print(f"     Priority: {priority}")


def demo_progress_report():
    """Demo progress report export."""
    print("\n" + "="*60)
    print("DEMO: PROGRESS REPORT EXPORT")
    print("="*60)
    
    output_file = "demo_progress_report.json"
    
    try:
        export_progress_report(output_file)
        print(f"Progress report exported to: {output_file}")
        
        # Read and display a summary of the exported report
        with open(output_file, 'r') as f:
            report = json.load(f)
        
        overall = report['overall_progress']
        print(f"Report Summary:")
        print(f"  Total Items: {overall['total_items']}")
        print(f"  Completed: {overall['total_completed']}")
        print(f"  Overall Completion: {overall['overall_percentage']:.1f}%")
        print(f"  Total XP: {overall['total_xp_gained']:,}")
        print(f"  Total Credits: {overall['total_credits_gained']:,}")
        
        # Clean up demo file
        Path(output_file).unlink(missing_ok=True)
        print(f"Demo file cleaned up")
        
    except Exception as e:
        print(f"Error exporting report: {e}")


def demo_checklist_categories():
    """Demo checklist categories and organization."""
    print("\n" + "="*60)
    print("DEMO: CHECKLIST CATEGORIES")
    print("="*60)
    
    tracker = get_enhanced_progress_tracker()
    checklists = tracker.get_all_checklists()
    
    # Group by category
    categories = {}
    for checklist in checklists.values():
        category_value = checklist.category.value if hasattr(checklist.category, 'value') else str(checklist.category)
        category = category_value
        if category not in categories:
            categories[category] = []
        categories[category].append(checklist)
    
    print("Checklists by category:")
    for category, category_checklists in categories.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        total_items = sum(c.total_items for c in category_checklists)
        total_completed = sum(c.completed_items for c in category_checklists)
        completion_rate = (total_completed / total_items * 100) if total_items > 0 else 0
        
        print(f"  Total Items: {total_items}")
        print(f"  Completed: {total_completed}")
        print(f"  Completion Rate: {completion_rate:.1f}%")
        
        for checklist in category_checklists:
            print(f"    - {checklist.name}: {checklist.completed_items}/{checklist.total_items}")


def demo_integration_with_existing_systems():
    """Demo integration with existing progress tracking systems."""
    print("\n" + "="*60)
    print("DEMO: INTEGRATION WITH EXISTING SYSTEMS")
    print("="*60)
    
    # This would integrate with existing session management, todo tracker, etc.
    print("The enhanced progress tracker integrates with:")
    print("  - Session Memory System")
    print("  - Todo Tracker")
    print("  - Task Planner (Batch 051)")
    print("  - Inventory Manager (Batch 053)")
    print("  - NPC Detector (Batch 054)")
    
    print("\nIntegration features:")
    print("  - Automatic progress updates based on game events")
    print("  - Smart suggestions based on current location and goals")
    print("  - Cross-referencing with quest sources and NPC data")
    print("  - Integration with bot actions for automated completion")
    print("  - Export capabilities for external tools")


def main():
    """Main demo function."""
    print("Enhanced Progress Tracker + 'All the Things' To-Do List System")
    print("MS11 Batch 055 Demo")
    print("="*60)
    
    setup_demo_logging()
    
    try:
        # Run all demos
        demo_checklist_loading()
        demo_overall_progress()
        demo_checklist_details()
        demo_item_updates()
        demo_suggestions()
        demo_progress_report()
        demo_checklist_categories()
        demo_integration_with_existing_systems()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("The enhanced progress tracker provides:")
        print("  ✓ Markdown checklist parsing")
        print("  ✓ Progress tracking and statistics")
        print("  ✓ Smart suggestions based on location")
        print("  ✓ Item status management")
        print("  ✓ Category organization")
        print("  ✓ Export capabilities")
        print("  ✓ Integration with existing systems")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        logging.exception("Demo error")


if __name__ == "__main__":
    main() 