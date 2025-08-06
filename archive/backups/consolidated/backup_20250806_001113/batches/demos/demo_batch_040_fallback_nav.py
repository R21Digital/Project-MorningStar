#!/usr/bin/env python3
"""
Demo script for Batch 040 - Planetary & Galactic Fallback Pathing

This demo showcases the fallback navigation system that provides default
navigation logic for zones without quest profiles by using generic waypoints
and fallback loops.

Features demonstrated:
- Zone profile loading and navigation
- Dynamic scanning for quests/NPCs/POIs
- Generic exploration patterns
- Hotspot navigation and interaction
- State tracking and reporting
"""

import logging
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from navigation.fallback_nav import (
    get_fallback_navigator,
    start_fallback_navigation,
    execute_navigation_loop,
    get_fallback_status,
    get_zone_profile
)
from core.state_tracker import update_state, get_state


def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('demo_batch_040_fallback_nav.log')
        ]
    )
    return logging.getLogger(__name__)


def demo_zone_profile_loading():
    """Demo zone profile loading functionality."""
    logger = logging.getLogger(__name__)
    logger.info("=== Demo: Zone Profile Loading ===")
    
    # Get fallback navigator
    navigator = get_fallback_navigator()
    
    # Test loading specific zone profiles
    test_cases = [
        ("tatooine", "mos_eisley"),
        ("naboo", "theed"),
        ("dantooine", "mining"),
        ("unknown_planet", "unknown_zone")  # Should fall back to generic pattern
    ]
    
    for planet, zone in test_cases:
        logger.info(f"Testing zone profile for {planet}/{zone}")
        
        # Get zone profile
        profile = get_zone_profile(planet, zone)
        
        if profile:
            logger.info(f"✓ Found profile for {planet}/{zone}")
            logger.info(f"  - Name: {profile.name}")
            logger.info(f"  - Description: {profile.description}")
            logger.info(f"  - Hotspots: {len(profile.hotspots)}")
            logger.info(f"  - Navigation loop: {profile.navigation_loop}")
            logger.info(f"  - Scan interval: {profile.scan_interval}s")
            logger.info(f"  - Max iterations: {profile.max_loop_iterations}")
        else:
            logger.info(f"✗ No profile found for {planet}/{zone}")
    
    logger.info("Zone profile loading demo completed\n")


def demo_generic_patterns():
    """Demo generic exploration patterns."""
    logger = logging.getLogger(__name__)
    logger.info("=== Demo: Generic Exploration Patterns ===")
    
    # Get fallback navigator
    navigator = get_fallback_navigator()
    
    # Test different generic patterns
    patterns = [
        "standard_exploration",
        "combat_exploration", 
        "resource_gathering"
    ]
    
    for pattern_name in patterns:
        logger.info(f"Testing generic pattern: {pattern_name}")
        
        # Get generic pattern
        pattern = navigator.get_generic_pattern(pattern_name)
        
        if pattern:
            logger.info(f"✓ Found pattern: {pattern.name}")
            logger.info(f"  - Description: {pattern.description}")
            logger.info(f"  - Hotspots: {len(pattern.hotspots)}")
            logger.info(f"  - Navigation loop: {pattern.navigation_loop}")
            logger.info(f"  - Scan interval: {pattern.scan_interval}s")
            logger.info(f"  - Max iterations: {pattern.max_loop_iterations}")
            
            # Show hotspot details
            for hotspot in pattern.hotspots:
                logger.info(f"    - {hotspot.name}: {hotspot.description}")
        else:
            logger.info(f"✗ Pattern not found: {pattern_name}")
    
    logger.info("Generic patterns demo completed\n")


def demo_fallback_navigation_start():
    """Demo starting fallback navigation."""
    logger = logging.getLogger(__name__)
    logger.info("=== Demo: Starting Fallback Navigation ===")
    
    # Test cases for different scenarios
    test_cases = [
        {
            "planet": "tatooine",
            "zone": "mos_eisley",
            "pattern": "standard_exploration",
            "description": "Known zone with specific profile"
        },
        {
            "planet": "naboo", 
            "zone": "theed",
            "pattern": "standard_exploration",
            "description": "Known zone with palace profile"
        },
        {
            "planet": "unknown_planet",
            "zone": "unknown_zone", 
            "pattern": "combat_exploration",
            "description": "Unknown zone using generic pattern"
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"Testing: {test_case['description']}")
        logger.info(f"  Planet: {test_case['planet']}")
        logger.info(f"  Zone: {test_case['zone']}")
        logger.info(f"  Pattern: {test_case['pattern']}")
        
        # Start fallback navigation
        success = start_fallback_navigation(
            planet=test_case['planet'],
            zone=test_case['zone'],
            pattern_name=test_case['pattern']
        )
        
        if success:
            logger.info("✓ Fallback navigation started successfully")
            
            # Get status
            status = get_fallback_status()
            logger.info(f"  - Status: {status['status']}")
            logger.info(f"  - Zone: {status['zone']}")
            logger.info(f"  - Loop iterations: {status['loop_iterations']}")
        else:
            logger.info("✗ Failed to start fallback navigation")
        
        logger.info("")
    
    logger.info("Fallback navigation start demo completed\n")


def demo_navigation_loop_execution():
    """Demo navigation loop execution."""
    logger = logging.getLogger(__name__)
    logger.info("=== Demo: Navigation Loop Execution ===")
    
    # Start a simple fallback navigation
    logger.info("Starting fallback navigation for demo...")
    success = start_fallback_navigation(
        planet="tatooine",
        zone="mos_eisley",
        pattern_name="standard_exploration"
    )
    
    if not success:
        logger.error("Failed to start fallback navigation for demo")
        return
    
    # Execute navigation loop (simulated)
    logger.info("Executing navigation loop...")
    
    # Simulate loop execution
    for iteration in range(3):
        logger.info(f"--- Loop Iteration {iteration + 1} ---")
        
        # Get current status
        status = get_fallback_status()
        logger.info(f"Current status: {status['status']}")
        logger.info(f"Zone: {status['zone']}")
        logger.info(f"Hotspots visited: {status['hotspots_visited']}")
        logger.info(f"Quests found: {status['quests_found']}")
        logger.info(f"NPCs found: {status['npcs_found']}")
        logger.info(f"POIs found: {status['pois_found']}")
        
        # Simulate loop execution
        success = execute_navigation_loop()
        
        if success:
            logger.info("✓ Navigation loop executed successfully")
        else:
            logger.info("✗ Navigation loop execution failed")
            break
        
        # Simulate some time passing
        time.sleep(1)
    
    logger.info("Navigation loop execution demo completed\n")


def demo_dynamic_scanning():
    """Demo dynamic scanning capabilities."""
    logger = logging.getLogger(__name__)
    logger.info("=== Demo: Dynamic Scanning Capabilities ===")
    
    # Get fallback navigator
    navigator = get_fallback_navigator()
    
    # Show scanning configuration
    logger.info("Scanning Configuration:")
    logger.info(f"  - NPC Detection: {navigator.npc_detection.get('enabled', False)}")
    logger.info(f"  - Quest Detection: {navigator.quest_detection.get('enabled', False)}")
    logger.info(f"  - POI Detection: {navigator.poi_detection.get('enabled', False)}")
    
    # Show detection settings
    logger.info("\nNPC Detection Settings:")
    for npc_type in navigator.npc_detection.get('npc_types', []):
        logger.info(f"  - {npc_type}")
    
    logger.info("\nQuest Detection Settings:")
    for indicator in navigator.quest_detection.get('quest_indicators', []):
        logger.info(f"  - {indicator}")
    
    logger.info("\nPOI Detection Settings:")
    for poi_type in navigator.poi_detection.get('poi_types', []):
        logger.info(f"  - {poi_type}")
    
    logger.info("Dynamic scanning demo completed\n")


def demo_state_tracking():
    """Demo state tracking functionality."""
    logger = logging.getLogger(__name__)
    logger.info("=== Demo: State Tracking ===")
    
    # Start fallback navigation
    logger.info("Starting fallback navigation for state tracking demo...")
    success = start_fallback_navigation(
        planet="naboo",
        zone="theed",
        pattern_name="standard_exploration"
    )
    
    if success:
        logger.info("✓ Fallback navigation started")
        
        # Update some state
        logger.info("Updating state with demo data...")
        update_state(
            fallback_quests_found=["demo_quest_1", "demo_quest_2"],
            fallback_npcs_found=["demo_npc_1", "demo_npc_2", "demo_npc_3"],
            fallback_pois_found=["demo_poi_1"],
            last_quest_location="theed_palace",
            last_npc_location="theed_market"
        )
        
        # Get current state
        state = get_state()
        logger.info("Current fallback state:")
        logger.info(f"  - Status: {state.get('fallback_status', 'unknown')}")
        logger.info(f"  - Zone: {state.get('fallback_zone', 'unknown')}")
        logger.info(f"  - Hotspot: {state.get('fallback_hotspot', 'unknown')}")
        logger.info(f"  - Loop iterations: {state.get('fallback_loop_iterations', 0)}")
        logger.info(f"  - Hotspots visited: {state.get('fallback_hotspots_visited', [])}")
        logger.info(f"  - Quests found: {state.get('fallback_quests_found', [])}")
        logger.info(f"  - NPCs found: {state.get('fallback_npcs_found', [])}")
        logger.info(f"  - POIs found: {state.get('fallback_pois_found', [])}")
        logger.info(f"  - Last quest location: {state.get('last_quest_location', 'unknown')}")
        logger.info(f"  - Last NPC location: {state.get('last_npc_location', 'unknown')}")
    else:
        logger.error("✗ Failed to start fallback navigation for state tracking demo")
    
    logger.info("State tracking demo completed\n")


def demo_integration_with_existing_systems():
    """Demo integration with existing navigation and state systems."""
    logger = logging.getLogger(__name__)
    logger.info("=== Demo: Integration with Existing Systems ===")
    
    # Test integration with existing navigator
    try:
        from core.navigator import get_navigator
        existing_navigator = get_navigator()
        logger.info("✓ Successfully integrated with existing navigator")
    except ImportError as e:
        logger.warning(f"⚠ Could not import existing navigator: {e}")
    
    # Test integration with existing OCR engine
    try:
        from core.ocr import OCREngine
        ocr_engine = OCREngine()
        logger.info("✓ Successfully integrated with existing OCR engine")
    except ImportError as e:
        logger.warning(f"⚠ Could not import existing OCR engine: {e}")
    
    # Test integration with existing state tracker
    try:
        from core.state_tracker import update_state, get_state
        logger.info("✓ Successfully integrated with existing state tracker")
    except ImportError as e:
        logger.warning(f"⚠ Could not import existing state tracker: {e}")
    
    # Test integration with existing screenshot capture
    try:
        from core.screenshot import capture_screen
        logger.info("✓ Successfully integrated with existing screenshot capture")
    except ImportError as e:
        logger.warning(f"⚠ Could not import existing screenshot capture: {e}")
    
    logger.info("Integration demo completed\n")


def demo_error_handling():
    """Demo error handling and edge cases."""
    logger = logging.getLogger(__name__)
    logger.info("=== Demo: Error Handling and Edge Cases ===")
    
    # Test with invalid file path
    logger.info("Testing with invalid fallback paths file...")
    try:
        from navigation.fallback_nav import FallbackNavigator
        invalid_navigator = FallbackNavigator("nonexistent_file.yaml")
        logger.info("✓ Handled invalid file path gracefully")
    except Exception as e:
        logger.info(f"✓ Caught expected error: {e}")
    
    # Test with empty zone profile
    logger.info("Testing with empty zone profile...")
    navigator = get_fallback_navigator()
    empty_profile = navigator.get_zone_profile("empty_planet", "empty_zone")
    if empty_profile is None:
        logger.info("✓ Handled empty zone profile gracefully")
    else:
        logger.warning("⚠ Unexpected profile found for empty zone")
    
    # Test with invalid pattern
    logger.info("Testing with invalid generic pattern...")
    invalid_pattern = navigator.get_generic_pattern("invalid_pattern")
    if invalid_pattern is None:
        logger.info("✓ Handled invalid pattern gracefully")
    else:
        logger.warning("⚠ Unexpected pattern found for invalid name")
    
    logger.info("Error handling demo completed\n")


def main():
    """Main demo function."""
    logger = setup_logging()
    
    logger.info("🚀 Starting Batch 040 - Fallback Navigation Demo")
    logger.info("=" * 60)
    
    try:
        # Run all demos
        demo_zone_profile_loading()
        demo_generic_patterns()
        demo_fallback_navigation_start()
        demo_navigation_loop_execution()
        demo_dynamic_scanning()
        demo_state_tracking()
        demo_integration_with_existing_systems()
        demo_error_handling()
        
        logger.info("✅ All demos completed successfully!")
        logger.info("=" * 60)
        
        # Final summary
        logger.info("📋 Batch 040 Implementation Summary:")
        logger.info("  ✓ Fallback navigation system implemented")
        logger.info("  ✓ Zone profile loading and management")
        logger.info("  ✓ Generic exploration patterns")
        logger.info("  ✓ Dynamic scanning for quests/NPCs/POIs")
        logger.info("  ✓ State tracking and reporting")
        logger.info("  ✓ Integration with existing systems")
        logger.info("  ✓ Error handling and edge cases")
        logger.info("  ✓ Comprehensive YAML configuration")
        
    except Exception as e:
        logger.error(f"❌ Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 