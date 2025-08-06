#!/usr/bin/env python3
"""
Demonstration script for Batch 026 - Quest Availability Detection & Scanning Radius Logic

This script demonstrates the quest scanner functionality including:
- Quest detection using OCR
- Scanning radius logic
- UI overlay for displaying detected quests
- Integration with existing quest data
"""

import time
from datetime import datetime
from pathlib import Path

# Import the quest scanner modules
try:
    from core.questing.quest_scanner import (
        get_quest_scanner, scan_for_quests, get_available_quests,
        mark_quest_completed, get_scanning_status
    )
    from ui.overlay.quest_overlay import (
        get_quest_overlay, update_quest_overlay, show_quest_overlay,
        hide_quest_overlay, get_overlay_status
    )
    QUEST_SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import quest scanner modules: {e}")
    QUEST_SCANNER_AVAILABLE = False


def demonstrate_quest_scanner():
    """Demonstrate the quest scanner functionality."""
    if not QUEST_SCANNER_AVAILABLE:
        print("Quest scanner modules not available. Skipping demonstration.")
        return
    
    print("=== Quest Scanner Demonstration ===\n")
    
    # Get the quest scanner instance
    scanner = get_quest_scanner()
    overlay = get_quest_overlay()
    
    print("1. Quest Scanner Initialization")
    print("-" * 40)
    status = get_scanning_status()
    print(f"Available quests: {status['available_quests']}")
    print(f"Completed quests: {status['completed_quests']}")
    print(f"Scanning radius (outdoor): {status['scanning_radius']['outdoor']}m")
    print(f"OCR available: {status['ocr_available']}")
    print()
    
    # Demonstrate quest detection
    print("2. Quest Detection Simulation")
    print("-" * 40)
    
    # Simulate different locations
    test_locations = [
        ((120, 220), "outdoor", "Near Tatooine quest location"),
        ((1000, 1000), "outdoor", "Far from quest locations"),
        ((300, 400), "indoor", "Near another quest location")
    ]
    
    for coords, location_type, description in test_locations:
        print(f"\nLocation: {coords} ({description})")
        print(f"Location type: {location_type}")
        
        # Scan for quests
        detections = scan_for_quests(coords, location_type)
        
        if detections:
            print(f"Found {len(detections)} quest(s):")
            for detection in detections:
                print(f"  - {detection.location.name} (Confidence: {detection.confidence:.2f})")
                print(f"    NPC: {detection.location.npc_name}")
                print(f"    Type: {detection.location.quest_type.value}")
                print(f"    Method: {detection.detection_method}")
        else:
            print("No quests detected")
    
    print("\n3. Available Quests by Location")
    print("-" * 40)
    
    # Show available quests for different locations
    for coords, _, description in test_locations:
        available_quests = get_available_quests(coords)
        print(f"\n{description}:")
        if available_quests:
            for quest in available_quests:
                distance = quest.distance_to(coords)
                print(f"  - {quest.name} (Distance: {distance:.0f}m)")
        else:
            print("  No quests available in range")
    
    print("\n4. Quest Completion Tracking")
    print("-" * 40)
    
    # Mark a quest as completed
    test_quest_id = "test_quest_1"
    print(f"Marking quest '{test_quest_id}' as completed...")
    mark_quest_completed(test_quest_id)
    
    # Check status again
    status = get_scanning_status()
    print(f"Completed quests: {status['completed_quests']}")
    
    print("\n5. Overlay System")
    print("-" * 40)
    
    # Get overlay status
    overlay_status = get_overlay_status()
    print(f"Overlay visible: {overlay_status['visible']}")
    print(f"Tkinter available: {overlay_status['tkinter_available']}")
    print(f"Items in overlay: {overlay_status['items_count']}")
    
    # Simulate quest detections for overlay
    print("\nSimulating quest detections for overlay...")
    
    # Create mock detections
    from unittest.mock import Mock
    mock_detections = []
    
    # Mock detection 1
    mock_detection1 = Mock(
        quest_id="imp_agent_kill",
        location=Mock(
            name="Imperial Agent Kill Mission",
            npc_name="Imperial Terminal Officer",
            quest_type=Mock(value="faction"),
            difficulty=Mock(value="medium"),
            coordinates=(123, -456),
            distance_to=Mock(return_value=50.0)
        ),
        detected_at=datetime.now(),
        confidence=0.85
    )
    mock_detections.append(mock_detection1)
    
    # Mock detection 2
    mock_detection2 = Mock(
        quest_id="moisture_farm_delivery",
        location=Mock(
            name="Moisture Farm Delivery",
            npc_name="Mos Eisley Merchant",
            quest_type=Mock(value="delivery"),
            difficulty=Mock(value="easy"),
            coordinates=(200, 300),
            distance_to=Mock(return_value=75.0)
        ),
        detected_at=datetime.now(),
        confidence=0.72
    )
    mock_detections.append(mock_detection2)
    
    # Update overlay with detections
    current_location = (150, 250)
    update_quest_overlay(mock_detections, current_location)
    
    # Check overlay status
    overlay_status = get_overlay_status()
    print(f"Items in overlay: {overlay_status['items_count']}")
    
    print("\n6. Recent Detections")
    print("-" * 40)
    
    # Get recent detections
    recent_detections = scanner.get_recent_detections(minutes=30)
    print(f"Recent detections: {len(recent_detections)}")
    
    for detection in recent_detections:
        print(f"  - {detection.quest_id} (Detected: {detection.detected_at.strftime('%H:%M:%S')})")
    
    print("\n7. Scanning Configuration")
    print("-" * 40)
    
    radius_config = status['scanning_radius']
    print("Scanning radius configuration:")
    for location_type, radius in radius_config.items():
        print(f"  {location_type}: {radius}m")
    
    print(f"\nScan interval: {status['scan_interval']} seconds")
    
    print("\n=== Demonstration Complete ===")


def demonstrate_quest_index_structure():
    """Demonstrate the quest index file structure."""
    print("\n=== Quest Index File Structure ===\n")
    
    quest_index_path = Path("data/quest_index.yaml")
    
    if quest_index_path.exists():
        import yaml
        with open(quest_index_path, 'r') as f:
            data = yaml.safe_load(f)
        
        print("Quest Index Structure:")
        print("-" * 30)
        
        # Show quest availability
        if "quest_availability" in data:
            print("\nQuest Availability:")
            for planet, planet_data in data["quest_availability"].items():
                print(f"  {planet}:")
                for quest_id, quest_info in planet_data.items():
                    print(f"    - {quest_id}: {quest_info.get('npc_name', 'Unknown NPC')}")
        
        # Show scanning configuration
        if "scanning_config" in data:
            print("\nScanning Configuration:")
            config = data["scanning_config"]
            for key, value in config.items():
                print(f"  {key}: {value}")
        
        # Show detection patterns
        if "detection_patterns" in data:
            print("\nDetection Patterns:")
            patterns = data["detection_patterns"]
            for pattern_type, pattern_list in patterns.items():
                print(f"  {pattern_type}: {len(pattern_list)} patterns")
    
    else:
        print("Quest index file not found.")


def demonstrate_integration():
    """Demonstrate integration with existing quest data."""
    print("\n=== Integration with Existing Quest Data ===\n")
    
    # Check internal quest index
    internal_index_path = Path("data/internal_index.yaml")
    
    if internal_index_path.exists():
        import yaml
        with open(internal_index_path, 'r') as f:
            data = yaml.safe_load(f)
        
        print("Internal Quest Index:")
        print("-" * 25)
        
        total_quests = 0
        for planet, planet_data in data.get("planets", {}).items():
            quests = planet_data.get("quests", {})
            total_quests += len(quests)
            print(f"  {planet}: {len(quests)} quests")
        
        print(f"\nTotal quests: {total_quests}")
        
        # Show quest types
        if "quest_types" in data:
            print("\nQuest Types:")
            for quest_type, quest_ids in data["quest_types"].items():
                print(f"  {quest_type}: {len(quest_ids)} quests")
    
    else:
        print("Internal quest index not found.")


if __name__ == "__main__":
    print("Batch 026 - Quest Availability Detection & Scanning Radius Logic")
    print("=" * 65)
    
    # Run demonstrations
    demonstrate_quest_scanner()
    demonstrate_quest_index_structure()
    demonstrate_integration()
    
    print("\nDemonstration completed successfully!") 