#!/usr/bin/env python3
"""
CLI Quest Detector for MS11 Batch 054

Provides command-line interface for detecting quest-giving NPCs
with confidence ratings and debug information.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vision.npc_detector import (
    get_npc_detector, detect_quest_npcs, get_available_quests_nearby, set_debug_mode,
    QuestNPC, QuestIcon
)

def setup_logging(verbose: bool = False):
    """Setup logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('quest_detector.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_quest_npcs(npcs: List[QuestNPC], show_details: bool = False):
    """Print detected quest NPCs in a formatted way."""
    if not npcs:
        print("No quest-giving NPCs detected.")
        return
    
    print(f"\n=== Detected Quest NPCs ({len(npcs)}) ===")
    
    for i, npc in enumerate(npcs, 1):
        print(f"\n{i}. {npc.name}")
        print(f"   Icon: {npc.icon_type} (Confidence: {npc.confidence:.2f})")
        print(f"   Position: {npc.coordinates}")
        
        if npc.quest_data:
            print(f"   Planet: {npc.quest_data.get('planet', 'Unknown')}")
            print(f"   City: {npc.quest_data.get('city', 'Unknown')}")
            
            quests = npc.quest_data.get('quests', [])
            if quests:
                print(f"   Available Quests: {len(quests)}")
                for j, quest in enumerate(quests, 1):
                    print(f"     {j}. {quest.get('name', 'Unknown Quest')}")
                    print(f"        Type: {quest.get('type', 'Unknown')}")
                    print(f"        XP Reward: {quest.get('xp_reward', 0)}")
                    print(f"        Credit Reward: {quest.get('credit_reward', 0)}")
        else:
            print("   Quest Data: Not found in quest_sources.json")
        
        if show_details and npc.screen_region:
            print(f"   Screen Region: {npc.screen_region}")

def print_available_quests(quests: List[Dict[str, Any]]):
    """Print available quests nearby with confidence ratings."""
    if not quests:
        print("No available quests detected nearby.")
        return
    
    print(f"\n=== Available Quests Nearby ({len(quests)}) ===")
    
    for i, quest_info in enumerate(quests, 1):
        npc_name = quest_info.get('npc_name', 'Unknown NPC')
        icon_type = quest_info.get('icon_type', '?')
        confidence = quest_info.get('confidence', 0.0)
        coordinates = quest_info.get('coordinates', (0, 0))
        planet = quest_info.get('planet', 'Unknown')
        city = quest_info.get('city', 'Unknown')
        
        print(f"\n{i}. {npc_name}")
        print(f"   Icon: {icon_type} (Confidence: {confidence:.2f})")
        print(f"   Location: {city}, {planet}")
        print(f"   Position: {coordinates}")
        
        quests_list = quest_info.get('quests', [])
        if quests_list:
            print(f"   Available Quests: {len(quests_list)}")
            for j, quest in enumerate(quests_list, 1):
                print(f"     {j}. {quest.get('name', 'Unknown Quest')}")
                print(f"        Type: {quest.get('type', 'Unknown')}")
                print(f"        Description: {quest.get('description', 'No description')}")
                print(f"        XP Reward: {quest.get('xp_reward', 0)}")
                print(f"        Credit Reward: {quest.get('credit_reward', 0)}")
                
                requirements = quest.get('requirements', [])
                if requirements:
                    print(f"        Requirements: {', '.join(requirements)}")
        else:
            print("   No quest data available")

def save_detection_results(npcs: List[QuestNPC], output_file: str):
    """Save detection results to a JSON file."""
    try:
        results = []
        for npc in npcs:
            npc_data = {
                "name": npc.name,
                "icon_type": npc.icon_type,
                "confidence": npc.confidence,
                "coordinates": npc.coordinates,
                "quest_data": npc.quest_data,
                "screen_region": npc.screen_region
            }
            results.append(npc_data)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Detection results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="MS11 Quest NPC Detector - Detect quest-giving NPCs using computer vision",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/quest_detector.py                    # Basic detection
  python cli/quest_detector.py --debug            # Enable debug mode
  python cli/quest_detector.py --verbose          # Verbose output
  python cli/quest_detector.py --save results.json # Save results to file
  python cli/quest_detector.py --details          # Show detailed information
        """
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for detailed logging"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--details",
        action="store_true",
        help="Show detailed information about detected NPCs"
    )
    
    parser.add_argument(
        "--save",
        metavar="FILE",
        help="Save detection results to JSON file"
    )
    
    parser.add_argument(
        "--quests-only",
        action="store_true",
        help="Show only available quests nearby (not individual NPCs)"
    )
    
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.6,
        help="Minimum confidence threshold for detection (default: 0.6)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Enable debug mode if requested
    if args.debug:
        set_debug_mode(True)
        print("Debug mode enabled")
    
    try:
        detector = get_npc_detector()
        
        # Set confidence threshold
        detector.min_confidence = args.confidence_threshold
        
        print("=== MS11 Quest NPC Detector ===")
        print(f"Confidence threshold: {args.confidence_threshold}")
        print("Scanning for quest-giving NPCs...")
        
        if args.quests_only:
            # Get available quests nearby
            available_quests = get_available_quests_nearby()
            print_available_quests(available_quests)
        else:
            # Detect quest NPCs
            detected_npcs = detect_quest_npcs()
            print_quest_npcs(detected_npcs, show_details=args.details)
            
            # Save results if requested
            if args.save:
                save_detection_results(detected_npcs, args.save)
        
        print("\n=== Detection Complete ===")
        
    except KeyboardInterrupt:
        print("\nDetection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during detection: {e}")
        logging.error(f"Detection error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 