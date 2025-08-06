#!/usr/bin/env python3
"""
Demonstration script for Batch 027 - Session To-Do Tracker & Completion Roadmap System

This script demonstrates the completion tracker functionality including:
- Loading completion objectives from YAML
- Generating prioritized roadmaps
- Tracking progress by planet
- Updating UI cards with progress data
- Integration with existing quest and collection systems
"""

import time
from datetime import datetime
from pathlib import Path

# Import the completion tracker modules
try:
    from core.completion_tracker import (
        get_completion_tracker, get_planet_progress, get_all_planet_progress,
        generate_roadmap, get_completion_summary, mark_objective_completed,
        get_next_objective, CompletionTracker
    )
    from ui.dashboard.completion_card import (
        get_planet_progress_card, get_roadmap_card, get_objective_detail_card,
        update_planet_progress_card, update_roadmap_card, update_objective_detail_card,
        PlanetProgressCard, RoadmapCard, ObjectiveDetailCard, get_card_status
    )
    COMPLETION_TRACKER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import completion tracker modules: {e}")
    COMPLETION_TRACKER_AVAILABLE = False


def demonstrate_completion_tracker():
    """Demonstrate the completion tracker functionality."""
    if not COMPLETION_TRACKER_AVAILABLE:
        print("Completion tracker modules not available. Skipping demonstration.")
        return
    
    print("=== Completion Tracker Demonstration ===\n")
    
    # Get the completion tracker instance
    tracker = get_completion_tracker()
    
    print("1. Completion Tracker Initialization")
    print("-" * 40)
    
    # Show initial state
    summary = get_completion_summary()
    print(f"Total objectives: {summary['total_objectives']}")
    print(f"Completed objectives: {summary['completed_objectives']}")
    print(f"Overall completion: {summary['overall_completion_percentage']:.1f}%")
    print(f"Estimated time remaining: {summary['estimated_time_remaining_minutes']} minutes")
    print()
    
    # Show planet progress
    print("2. Planet Progress Overview")
    print("-" * 40)
    
    all_progress = get_all_planet_progress()
    for planet, progress in all_progress.items():
        print(f"{planet}:")
        print(f"  Total objectives: {progress.total_objectives}")
        print(f"  Completed: {progress.completed_objectives}")
        print(f"  Completion: {progress.completion_percentage:.1f}%")
        print(f"  Objectives by type: {progress.objectives_by_type}")
        print()
    
    # Demonstrate roadmap generation
    print("3. Roadmap Generation")
    print("-" * 40)
    
    # Generate roadmap for Tatooine
    current_location = (120, 220)
    player_level = 20
    
    roadmap = generate_roadmap(
        current_planet="Tatooine",
        current_location=current_location,
        player_level=player_level
    )
    
    print(f"Generated roadmap for {roadmap.current_planet}")
    print(f"Player level: {roadmap.player_level}")
    print(f"Prioritized objectives: {len(roadmap.prioritized_objectives)}")
    print()
    
    # Show prioritized objectives
    for i, objective in enumerate(roadmap.prioritized_objectives[:5]):
        print(f"{i+1}. {objective.name}")
        print(f"   Type: {objective.completion_type.value}")
        print(f"   Priority: {objective.priority.value}")
        print(f"   Status: {objective.status.value}")
        print(f"   Required level: {objective.required_level}")
        print(f"   Estimated time: {objective.estimated_time} minutes")
        print()
    
    # Demonstrate objective completion
    print("4. Objective Completion Tracking")
    print("-" * 40)
    
    # Mark some objectives as completed
    objectives_to_complete = ["tatooine_quest_1", "tatooine_collection_1"]
    
    for objective_id in objectives_to_complete:
        if objective_id in tracker.objectives:
            print(f"Completing objective: {tracker.objectives[objective_id].name}")
            mark_objective_completed(objective_id)
            tracker.update_session_progress(objective_id)
    
    # Show updated progress
    updated_summary = get_completion_summary()
    print(f"\nUpdated completion: {updated_summary['completed_objectives']}/{updated_summary['total_objectives']}")
    print(f"Overall completion: {updated_summary['overall_completion_percentage']:.1f}%")
    
    # Show updated planet progress
    print("\nUpdated planet progress:")
    updated_progress = get_all_planet_progress()
    for planet, progress in updated_progress.items():
        print(f"  {planet}: {progress.completed_objectives}/{progress.total_objectives} ({progress.completion_percentage:.1f}%)")
    
    print("\n5. Next Objective Selection")
    print("-" * 40)
    
    # Get next recommended objective
    next_objective = get_next_objective(current_location)
    if next_objective:
        print(f"Next recommended objective: {next_objective.name}")
        print(f"Type: {next_objective.completion_type.value}")
        print(f"Priority: {next_objective.priority.value}")
        print(f"Required level: {next_objective.required_level}")
        print(f"Estimated time: {next_objective.estimated_time} minutes")
    else:
        print("No objectives available for next recommendation")
    
    print("\n6. UI Card Integration")
    print("-" * 40)
    
    # Update planet progress card
    tatooine_progress = get_planet_progress("Tatooine")
    if tatooine_progress:
        planet_card_data = PlanetProgressCard(
            planet=tatooine_progress.planet,
            total_objectives=tatooine_progress.total_objectives,
            completed_objectives=tatooine_progress.completed_objectives,
            completion_percentage=tatooine_progress.completion_percentage,
            objectives_by_type={str(k.value): v for k, v in tatooine_progress.objectives_by_type.items()},
            estimated_time_remaining=tatooine_progress.estimated_time_remaining,
            last_updated=tatooine_progress.last_updated,
            is_current_planet=True
        )
        update_planet_progress_card(planet_card_data)
        print("Updated planet progress card")
    
    # Update roadmap card
    roadmap_card_data = RoadmapCard(
        current_planet=roadmap.current_planet,
        prioritized_objectives=[{
            "name": obj.name,
            "completion_type": obj.completion_type.value,
            "priority": obj.priority.value,
            "status": obj.status.value,
            "required_level": obj.required_level,
            "estimated_time": obj.estimated_time
        } for obj in roadmap.prioritized_objectives[:5]],
        session_completed=roadmap.session_completed,
        session_time=roadmap.session_time,
        next_objective={
            "name": next_objective.name,
            "completion_type": next_objective.completion_type.value,
            "priority": next_objective.priority.value
        } if next_objective else None
    )
    update_roadmap_card(roadmap_card_data)
    print("Updated roadmap card")
    
    # Update objective detail card
    if next_objective:
        objective_detail = ObjectiveDetailCard(
            objective_id=next_objective.id,
            name=next_objective.name,
            completion_type=next_objective.completion_type.value,
            planet=next_objective.planet,
            zone=next_objective.zone,
            status=next_objective.status.value,
            priority=next_objective.priority.value,
            progress_percentage=next_objective.progress_percentage,
            estimated_time=next_objective.estimated_time,
            rewards=next_objective.rewards,
            description=next_objective.description,
            tags=next_objective.tags
        )
        update_objective_detail_card(objective_detail)
        print("Updated objective detail card")
    
    # Show card status
    card_status = get_card_status()
    print(f"\nCard status:")
    for card_name, status in card_status.items():
        print(f"  {card_name}: {'Available' if status['frame_available'] else 'Unavailable'}")
    
    print("\n7. Advanced Features")
    print("-" * 40)
    
    # Demonstrate dependency checking
    print("Dependency checking:")
    for objective in tracker.objectives.values():
        if objective.dependencies:
            print(f"  {objective.name} depends on: {objective.dependencies}")
    
    # Demonstrate level requirements
    print("\nLevel requirements:")
    for objective in tracker.objectives.values():
        if objective.required_level:
            print(f"  {objective.name}: Level {objective.required_level}")
    
    # Demonstrate profession requirements
    print("\nProfession requirements:")
    for objective in tracker.objectives.values():
        if objective.required_profession:
            print(f"  {objective.name}: {objective.required_profession}")
    
    print("\n=== Demonstration Complete ===")


def demonstrate_completion_map_structure():
    """Demonstrate the completion map file structure."""
    print("\n=== Completion Map Structure ===\n")
    
    completion_map_path = Path("data/completion_map.yaml")
    
    if completion_map_path.exists():
        import yaml
        with open(completion_map_path, 'r') as f:
            data = yaml.safe_load(f)
        
        print("Completion Map Overview:")
        print("-" * 25)
        
        # Show objectives by planet
        objectives_by_planet = {}
        for objective in data.get("objectives", []):
            planet = objective.get("planet", "Unknown")
            if planet not in objectives_by_planet:
                objectives_by_planet[planet] = []
            objectives_by_planet[planet].append(objective)
        
        for planet, objectives in objectives_by_planet.items():
            print(f"\n{planet}:")
            for obj in objectives:
                print(f"  - {obj['name']} ({obj['type']})")
                print(f"    Priority: {obj['priority']} | Level: {obj.get('required_level', 'Any')}")
                print(f"    Status: {obj['status']} | Time: {obj.get('estimated_time', 'Unknown')} min")
        
        # Show configuration
        if "config" in data:
            print(f"\nConfiguration:")
            config = data["config"]
            for section, settings in config.items():
                print(f"  {section}:")
                for key, value in settings.items():
                    print(f"    {key}: {value}")
        
        # Show metadata
        if "metadata" in data:
            print(f"\nMetadata:")
            metadata = data["metadata"]
            for key, value in metadata.items():
                print(f"  {key}: {value}")
    
    else:
        print("Completion map file not found.")


def demonstrate_integration():
    """Demonstrate integration with existing systems."""
    print("\n=== Integration with Existing Systems ===\n")
    
    # Check if quest system is available
    try:
        from core.questing.quest_scanner import get_quest_scanner
        quest_scanner = get_quest_scanner()
        print("✓ Quest scanner integration available")
        print(f"  Available quests: {len(quest_scanner.available_quests)}")
    except ImportError:
        print("✗ Quest scanner integration not available")
    
    # Check if collection system is available
    try:
        from core.collection_tracker import get_collection_tracker
        collection_tracker = get_collection_tracker()
        print("✓ Collection tracker integration available")
        print(f"  Collections loaded: {len(collection_tracker.collections)}")
    except ImportError:
        print("✗ Collection tracker integration not available")
    
    # Show completion tracker integration
    tracker = get_completion_tracker()
    print(f"✓ Completion tracker available")
    print(f"  Objectives loaded: {len(tracker.objectives)}")
    print(f"  Planets tracked: {len(tracker.planet_progress)}")
    
    # Show UI card integration
    card_status = get_card_status()
    print(f"✓ UI cards available:")
    for card_name, status in card_status.items():
        print(f"  {card_name}: {'✓' if status['frame_available'] else '✗'}")


if __name__ == "__main__":
    print("Batch 027 - Session To-Do Tracker & Completion Roadmap System")
    print("=" * 65)
    
    # Run demonstrations
    demonstrate_completion_tracker()
    demonstrate_completion_map_structure()
    demonstrate_integration()
    
    print("\nDemonstration completed successfully!") 