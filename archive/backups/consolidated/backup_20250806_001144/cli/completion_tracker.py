#!/usr/bin/env python3
"""
CLI Interface for Batch 027 - Session To-Do Tracker & Completion Roadmap System

This module provides a command-line interface for the completion tracker system,
allowing users to view progress, generate roadmaps, and manage objectives.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import completion tracker modules
try:
    from core.completion_tracker import (
        get_completion_tracker, get_planet_progress, get_all_planet_progress,
        generate_roadmap, get_completion_summary, mark_objective_completed,
        get_next_objective, CompletionTracker
    )
    from ui.dashboard.completion_card import (
        get_planet_progress_card, get_roadmap_card, get_objective_detail_card,
        update_planet_progress_card, update_roadmap_card, update_objective_detail_card,
        PlanetProgressCard, RoadmapCard, ObjectiveDetailCard
    )
    COMPLETION_TRACKER_AVAILABLE = True
except ImportError as e:
    print(f"Error: Could not import completion tracker modules: {e}")
    COMPLETION_TRACKER_AVAILABLE = False


def display_planet_progress(planet: Optional[str] = None, detailed: bool = False):
    """Display planet progress in the format 'Naboo: 27/56 quests complete'."""
    if not COMPLETION_TRACKER_AVAILABLE:
        print("Error: Completion tracker not available")
        return
    
    tracker = get_completion_tracker()
    
    if planet:
        # Display specific planet progress
        progress = get_planet_progress(planet)
        if progress:
            _display_single_planet_progress(progress, detailed)
        else:
            print(f"Planet '{planet}' not found")
    else:
        # Display all planet progress
        all_progress = get_all_planet_progress()
        for planet_name, progress in all_progress.items():
            _display_single_planet_progress(progress, detailed)
            print()  # Add spacing between planets


def _display_single_planet_progress(progress, detailed: bool = False):
    """Display progress for a single planet."""
    # Main progress line
    progress_text = f"{progress.planet}: {progress.completed_objectives}/{progress.total_objectives}"
    
    if detailed:
        # Detailed format with percentage and breakdown
        progress_text += f" ({progress.completion_percentage:.1f}%)"
        print(f"📊 {progress_text}")
        
        # Breakdown by type
        for obj_type, count in progress.objectives_by_type.items():
            type_name = obj_type.value.replace('_', ' ').title()
            print(f"   {type_name}: {count}")
        
        # Time estimate if available
        if progress.estimated_time_remaining:
            hours = progress.estimated_time_remaining // 60
            minutes = progress.estimated_time_remaining % 60
            if hours > 0:
                time_text = f"{hours}h {minutes}m remaining"
            else:
                time_text = f"{minutes}m remaining"
            print(f"   ⏱️  {time_text}")
    else:
        # Simple format
        print(f"📊 {progress_text}")


def display_roadmap(planet: str, location: Tuple[int, int], level: int = 1, max_objectives: int = 5):
    """Display a prioritized roadmap for a planet."""
    if not COMPLETION_TRACKER_AVAILABLE:
        print("Error: Completion tracker not available")
        return
    
    try:
        roadmap = generate_roadmap(
            current_planet=planet,
            current_location=location,
            player_level=level
        )
        
        print(f"\n🗺️  Roadmap for {planet} (Level {level})")
        print(f"📍 Current Location: {location}")
        print("-" * 50)
        
        for i, objective in enumerate(roadmap.prioritized_objectives[:max_objectives]):
            status_icon = "🟢" if objective.status.value == "completed" else "🟡" if objective.status.value == "in_progress" else "⚪"
            priority_icon = "🔴" if objective.priority.value == "critical" else "🟠" if objective.priority.value == "high" else "🟡" if objective.priority.value == "medium" else "🟢"
            
            print(f"{i+1}. {status_icon} {priority_icon} {objective.name}")
            print(f"   Type: {objective.completion_type.value.title()}")
            print(f"   Priority: {objective.priority.value.title()}")
            print(f"   Status: {objective.status.value.replace('_', ' ').title()}")
            
            if objective.required_level:
                print(f"   Required Level: {objective.required_level}")
            
            if objective.estimated_time:
                print(f"   Estimated Time: {objective.estimated_time} minutes")
            
            if objective.description:
                print(f"   Description: {objective.description}")
            
            print()
        
        # Session statistics
        print(f"📈 Session Progress: {roadmap.session_completed} completed")
        print(f"⏱️  Session Time: {roadmap.session_time} minutes")
        
    except Exception as e:
        print(f"Error generating roadmap: {e}")


def display_completion_summary():
    """Display overall completion summary."""
    if not COMPLETION_TRACKER_AVAILABLE:
        print("Error: Completion tracker not available")
        return
    
    summary = get_completion_summary()
    
    print("\n📊 Overall Completion Summary")
    print("=" * 40)
    print(f"🎯 Total Objectives: {summary['total_objectives']}")
    print(f"✅ Completed: {summary['completed_objectives']}")
    print(f"📈 Overall Completion: {summary['overall_completion_percentage']:.1f}%")
    
    # Estimated time remaining
    hours = summary['estimated_time_remaining_minutes'] // 60
    minutes = summary['estimated_time_remaining_minutes'] % 60
    if hours > 0:
        time_text = f"{hours}h {minutes}m"
    else:
        time_text = f"{minutes}m"
    print(f"⏱️  Estimated Time Remaining: {time_text}")
    
    # Planet breakdown
    print("\n🌍 Planet Breakdown:")
    for planet, data in summary['planet_progress'].items():
        percentage = data['percentage']
        status_icon = "🟢" if percentage >= 100 else "🟡" if percentage >= 50 else "🟠" if percentage >= 25 else "🔴"
        print(f"   {status_icon} {planet}: {data['completed']}/{data['total']} ({percentage:.1f}%)")


def mark_objective_complete(objective_id: str):
    """Mark an objective as completed."""
    if not COMPLETION_TRACKER_AVAILABLE:
        print("Error: Completion tracker not available")
        return
    
    try:
        tracker = get_completion_tracker()
        if objective_id in tracker.objectives:
            objective = tracker.objectives[objective_id]
            print(f"✅ Marking '{objective.name}' as completed")
            mark_objective_completed(objective_id)
            print("✅ Objective marked as completed")
        else:
            print(f"❌ Objective '{objective_id}' not found")
    except Exception as e:
        print(f"Error marking objective complete: {e}")


def get_next_recommendation(location: Tuple[int, int]):
    """Get the next recommended objective."""
    if not COMPLETION_TRACKER_AVAILABLE:
        print("Error: Completion tracker not available")
        return
    
    try:
        next_objective = get_next_objective(location)
        if next_objective:
            print(f"\n🎯 Next Recommended Objective:")
            print(f"📝 Name: {next_objective.name}")
            print(f"🌍 Planet: {next_objective.planet}")
            print(f"📍 Zone: {next_objective.zone or 'Unknown'}")
            print(f"🎯 Type: {next_objective.completion_type.value.title()}")
            print(f"⭐ Priority: {next_objective.priority.value.title()}")
            print(f"📊 Status: {next_objective.status.value.replace('_', ' ').title()}")
            
            if next_objective.required_level:
                print(f"📈 Required Level: {next_objective.required_level}")
            
            if next_objective.estimated_time:
                print(f"⏱️  Estimated Time: {next_objective.estimated_time} minutes")
            
            if next_objective.description:
                print(f"📖 Description: {next_objective.description}")
            
            if next_objective.rewards:
                print(f"🎁 Rewards: {', '.join(next_objective.rewards)}")
        else:
            print("❌ No objectives available for recommendation")
    except Exception as e:
        print(f"Error getting next recommendation: {e}")


def list_objectives(planet: Optional[str] = None, objective_type: Optional[str] = None):
    """List objectives with optional filtering."""
    if not COMPLETION_TRACKER_AVAILABLE:
        print("Error: Completion tracker not available")
        return
    
    tracker = get_completion_tracker()
    objectives = list(tracker.objectives.values())
    
    # Apply filters
    if planet:
        objectives = [obj for obj in objectives if obj.planet.lower() == planet.lower()]
    
    if objective_type:
        objectives = [obj for obj in objectives if obj.completion_type.value == objective_type.lower()]
    
    if not objectives:
        print("No objectives found matching the criteria")
        return
    
    print(f"\n📋 Objectives ({len(objectives)} found):")
    print("-" * 60)
    
    for objective in objectives:
        status_icon = "🟢" if objective.status.value == "completed" else "🟡" if objective.status.value == "in_progress" else "⚪"
        priority_icon = "🔴" if objective.priority.value == "critical" else "🟠" if objective.priority.value == "high" else "🟡" if objective.priority.value == "medium" else "🟢"
        
        print(f"{status_icon} {priority_icon} {objective.name}")
        print(f"   ID: {objective.id}")
        print(f"   Planet: {objective.planet}")
        print(f"   Type: {objective.completion_type.value.title()}")
        print(f"   Status: {objective.status.value.replace('_', ' ').title()}")
        print(f"   Progress: {objective.progress_percentage:.1f}%")
        
        if objective.required_level:
            print(f"   Required Level: {objective.required_level}")
        
        if objective.estimated_time:
            print(f"   Estimated Time: {objective.estimated_time} minutes")
        
        print()


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Session To-Do Tracker & Completion Roadmap System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s progress                    # Show all planet progress
  %(prog)s progress --planet Naboo    # Show Naboo progress
  %(prog)s roadmap Tatooine 120 220   # Generate roadmap for Tatooine
  %(prog)s summary                    # Show overall completion summary
  %(prog)s next 120 220               # Get next recommendation
  %(prog)s complete tatooine_quest_1  # Mark objective as completed
  %(prog)s list --planet Tatooine     # List Tatooine objectives
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Progress command
    progress_parser = subparsers.add_parser('progress', help='Show planet progress')
    progress_parser.add_argument('--planet', help='Specific planet to show')
    progress_parser.add_argument('--detailed', action='store_true', help='Show detailed progress')
    
    # Roadmap command
    roadmap_parser = subparsers.add_parser('roadmap', help='Generate roadmap for planet')
    roadmap_parser.add_argument('planet', help='Planet name')
    roadmap_parser.add_argument('x', type=int, help='X coordinate')
    roadmap_parser.add_argument('y', type=int, help='Y coordinate')
    roadmap_parser.add_argument('--level', type=int, default=1, help='Player level')
    roadmap_parser.add_argument('--max', type=int, default=5, help='Maximum objectives to show')
    
    # Summary command
    subparsers.add_parser('summary', help='Show overall completion summary')
    
    # Next command
    next_parser = subparsers.add_parser('next', help='Get next recommended objective')
    next_parser.add_argument('x', type=int, help='X coordinate')
    next_parser.add_argument('y', type=int, help='Y coordinate')
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark objective as completed')
    complete_parser.add_argument('objective_id', help='Objective ID to complete')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List objectives')
    list_parser.add_argument('--planet', help='Filter by planet')
    list_parser.add_argument('--type', help='Filter by objective type')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'progress':
        display_planet_progress(args.planet, args.detailed)
    elif args.command == 'roadmap':
        display_roadmap(args.planet, (args.x, args.y), args.level, args.max)
    elif args.command == 'summary':
        display_completion_summary()
    elif args.command == 'next':
        get_next_recommendation((args.x, args.y))
    elif args.command == 'complete':
        mark_objective_complete(args.objective_id)
    elif args.command == 'list':
        list_objectives(args.planet, args.type)


if __name__ == "__main__":
    main() 