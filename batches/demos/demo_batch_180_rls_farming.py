#!/usr/bin/env python3
"""
Demo Script for Batch 180 - RLS Farming Mode

This script demonstrates the new Rare Loot Finder (RLS) farming mode with:
- Target selection and cooldown management
- Travel and group management
- Loot tracking and priority system
- Comprehensive reporting and analytics

Usage:
    python demo_batch_180_rls_farming.py [options]

Options:
    --target_priority TARGET    Specific target to prioritize (ig88, axkva_min, crystal_snake)
    --solo_mode                Run in solo mode (default: group mode)
    --max_sessions N           Maximum sessions to run (default: 3)
    --demo_mode                Run in demo mode with mock data
"""

import json
import logging
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import the RLS farming mode
try:
    from core.modes.rare_loot_farm import RLSFarmingMode, run_rls_farming_mode
except ImportError as e:
    print(f"Error importing RLS farming mode: {e}")
    print("Make sure the module is properly installed and accessible.")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_demo_environment():
    """Set up the demo environment with test data."""
    logger.info("Setting up demo environment...")
    
    # Create demo directories if they don't exist
    demo_dirs = [
        "data/rls_farming_sessions",
        "config",
        "logs"
    ]
    
    for dir_path in demo_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create demo session data
    demo_sessions = [
        {
            "target": {
                "id": "ig88",
                "name": "IG-88",
                "planet": "Lok",
                "zone": "Imperial Research Facility"
            },
            "start_time": "2025-01-04T10:00:00",
            "end_time": "2025-01-04T10:15:00",
            "duration_seconds": 900,
            "solo_mode": False,
            "success": True,
            "loot_log": [
                {
                    "name": "IG-88's Head",
                    "target": "IG-88",
                    "rarity": "legendary",
                    "value": 15000,
                    "is_rare": True,
                    "is_priority": True,
                    "timestamp": "2025-01-04T10:10:00",
                    "location": "Lok - Imperial Research Facility"
                },
                {
                    "name": "Assassin Droid Parts",
                    "target": "IG-88",
                    "rarity": "epic",
                    "value": 8000,
                    "is_rare": True,
                    "is_priority": True,
                    "timestamp": "2025-01-04T10:12:00",
                    "location": "Lok - Imperial Research Facility"
                }
            ],
            "combat_log": [
                {"type": "combat_start", "time": "2025-01-04T10:05:00"},
                {"type": "target_defeated", "time": "2025-01-04T10:10:00"}
            ]
        },
        {
            "target": {
                "id": "crystal_snake",
                "name": "Crystal Snake",
                "planet": "Dantooine",
                "zone": "Force Crystal Cave"
            },
            "start_time": "2025-01-04T11:00:00",
            "end_time": "2025-01-04T11:08:00",
            "duration_seconds": 480,
            "solo_mode": True,
            "success": True,
            "loot_log": [
                {
                    "name": "Crystal Snake Necklace",
                    "target": "Crystal Snake",
                    "rarity": "epic",
                    "value": 12000,
                    "is_rare": True,
                    "is_priority": True,
                    "timestamp": "2025-01-04T11:05:00",
                    "location": "Dantooine - Force Crystal Cave"
                },
                {
                    "name": "Force Crystals",
                    "target": "Crystal Snake",
                    "rarity": "rare",
                    "value": 3000,
                    "is_rare": True,
                    "is_priority": True,
                    "timestamp": "2025-01-04T11:06:00",
                    "location": "Dantooine - Force Crystal Cave"
                }
            ],
            "combat_log": [
                {"type": "combat_start", "time": "2025-01-04T11:02:00"},
                {"type": "target_defeated", "time": "2025-01-04T11:05:00"}
            ]
        }
    ]
    
    # Save demo sessions
    sessions_dir = Path("data/rls_farming_sessions")
    for i, session in enumerate(demo_sessions):
        session_file = sessions_dir / f"demo_session_{i+1}.json"
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
    
    logger.info("Demo environment setup complete")


def demo_target_selection():
    """Demonstrate target selection and cooldown management."""
    logger.info("=== Demo: Target Selection and Cooldown Management ===")
    
    # Initialize farming mode
    farming_mode = RLSFarmingMode()
    
    # Check cooldowns
    cooldown_status = farming_mode.check_cooldowns()
    logger.info(f"Cooldown status: {len(cooldown_status)} targets checked")
    
    # Show available targets
    available_targets = [tid for tid, status in cooldown_status.items() 
                        if status["available"]]
    logger.info(f"Available targets: {available_targets}")
    
    # Select targets
    for target_id in ["ig88", "axkva_min", "crystal_snake"]:
        target = farming_mode.select_farming_target(target_id)
        if target:
            logger.info(f"Selected target: {target['name']} (Level {target['level']})")
            logger.info(f"  Planet: {target['planet']}")
            logger.info(f"  Zone: {target['zone']}")
            logger.info(f"  Cooldown: {target['cooldown_hours']} hours")
            logger.info(f"  Priority loot: {target['loot_priority'][:3]}...")
        else:
            logger.warning(f"Target {target_id} not available")
    
    return farming_mode


def demo_farming_session(farming_mode: RLSFarmingMode, target_priority: Optional[str] = None):
    """Demonstrate a complete farming session."""
    logger.info("=== Demo: Farming Session ===")
    
    # Select target
    target = farming_mode.select_farming_target(target_priority)
    if not target:
        logger.error("No suitable target found")
        return None
    
    logger.info(f"Starting farming session for {target['name']}")
    
    # Simulate farming process
    logger.info("1. Traveling to target location...")
    time.sleep(1)  # Simulate travel time
    
    logger.info("2. Managing group...")
    time.sleep(1)  # Simulate group management
    
    logger.info("3. Engaging target...")
    time.sleep(2)  # Simulate combat
    
    logger.info("4. Collecting loot...")
    time.sleep(1)  # Simulate loot collection
    
    # Simulate loot results
    mock_loot = [
        {
            "name": target["loot_priority"][0],
            "target": target["name"],
            "rarity": "legendary" if target["rarity"] == "legendary" else "epic",
            "value": 15000 if target["rarity"] == "legendary" else 8000,
            "is_rare": True,
            "is_priority": True,
            "timestamp": datetime.now().isoformat(),
            "location": f"{target['planet']} - {target['zone']}"
        },
        {
            "name": "Common Trophy",
            "target": target["name"],
            "rarity": "common",
            "value": 500,
            "is_rare": False,
            "is_priority": False,
            "timestamp": datetime.now().isoformat(),
            "location": f"{target['planet']} - {target['zone']}"
        }
    ]
    
    logger.info(f"Session completed! Found {len(mock_loot)} items")
    for loot in mock_loot:
        rarity_emoji = "🌟" if loot["is_rare"] else "📦"
        logger.info(f"  {rarity_emoji} {loot['name']} ({loot['rarity']}) - {loot['value']} credits")
    
    return mock_loot


def demo_statistics(farming_mode: RLSFarmingMode):
    """Demonstrate statistics and reporting."""
    logger.info("=== Demo: Statistics and Reporting ===")
    
    # Get farming stats
    stats = farming_mode.get_farming_stats()
    
    logger.info("Farming Statistics:")
    logger.info(f"  Total sessions: {stats['total_sessions']}")
    logger.info(f"  Total loot found: {stats['total_loot']}")
    logger.info(f"  Total rare drops: {stats['total_rare_drops']}")
    logger.info(f"  Success rate: {stats['success_rate']}%")
    logger.info(f"  Average session duration: {stats['average_duration_minutes']} minutes")
    logger.info(f"  Kill count: {stats['kill_count']}")
    
    # Show target-specific stats
    logger.info("\nTarget-specific Statistics:")
    for target_id, target_stats in stats['target_stats'].items():
        logger.info(f"  {target_id}:")
        logger.info(f"    Sessions: {target_stats['sessions']}")
        logger.info(f"    Loot found: {target_stats['loot_found']}")
        logger.info(f"    Rare drops: {target_stats['rare_drops']}")
    
    # Show cooldown status
    logger.info("\nCooldown Status:")
    for target_id, status in stats['cooldown_status'].items():
        if status['available']:
            logger.info(f"  {target_id}: Available")
        else:
            logger.info(f"  {target_id}: {status['hours_remaining']} hours remaining")
    
    return stats


def demo_configuration():
    """Demonstrate configuration options."""
    logger.info("=== Demo: Configuration Options ===")
    
    # Load loot targets config
    config_path = Path("config/loot_targets.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.info("Configuration loaded:")
        logger.info(f"  Targets configured: {len(config['targets'])}")
        logger.info(f"  Settings enabled: {len(config['settings'])}")
        logger.info(f"  Loot categories: {len(config['loot_categories'])}")
        
        # Show some target details
        logger.info("\nTarget Details:")
        for target in config['targets'][:3]:  # Show first 3 targets
            logger.info(f"  {target['name']} (Level {target['level']})")
            logger.info(f"    Planet: {target['planet']}")
            logger.info(f"    Cooldown: {target['cooldown_hours']} hours")
            logger.info(f"    Difficulty: {target['difficulty']}")
            logger.info(f"    Group recommended: {target['group_recommended']}")
    else:
        logger.warning("Configuration file not found")


def demo_priority_system():
    """Demonstrate the loot priority system."""
    logger.info("=== Demo: Loot Priority System ===")
    
    # Example priority items for different targets
    priority_examples = {
        "ig88": ["IG-88's Head", "Assassin Droid Parts", "Rare Weapon Components"],
        "axkva_min": ["Axkva Min's Necklace", "Ancient Artifacts", "Force Crystals"],
        "crystal_snake": ["Crystal Snake Necklace", "Force Crystals", "Rare Gems"]
    }
    
    logger.info("Priority Loot Examples:")
    for target, items in priority_examples.items():
        logger.info(f"  {target}:")
        for item in items:
            logger.info(f"    - {item}")
    
    logger.info("\nPriority System Features:")
    logger.info("  ✅ Auto-detection of priority items")
    logger.info("  ✅ Manual override capability")
    logger.info("  ✅ Tracking and notifications")
    logger.info("  ✅ Value-based prioritization")


def run_full_demo(args):
    """Run the complete RLS farming demo."""
    logger.info("🚀 Starting RLS Farming Mode Demo")
    logger.info("=" * 50)
    
    # Setup demo environment
    setup_demo_environment()
    
    # Demo configuration
    demo_configuration()
    print()
    
    # Demo priority system
    demo_priority_system()
    print()
    
    # Demo target selection
    farming_mode = demo_target_selection()
    print()
    
    # Demo farming session
    loot_found = demo_farming_session(farming_mode, args.target_priority)
    print()
    
    # Demo statistics
    stats = demo_statistics(farming_mode)
    print()
    
    # Run actual farming mode (if not in demo mode)
    if not args.demo_mode:
        logger.info("=== Running Actual RLS Farming Mode ===")
        result = run_rls_farming_mode(
            target_priority=args.target_priority,
            solo_mode=args.solo_mode,
            max_sessions=args.max_sessions
        )
        
        if result["success"]:
            logger.info(f"✅ Farming mode completed successfully!")
            logger.info(f"   Sessions completed: {result['sessions_completed']}")
            logger.info(f"   Total loot found: {len(result['total_loot_found'])}")
            logger.info(f"   Report saved to: {result['report_path']}")
        else:
            logger.error(f"❌ Farming mode failed: {result.get('error', 'Unknown error')}")
    
    logger.info("=" * 50)
    logger.info("🎉 RLS Farming Mode Demo Complete!")
    
    return True


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Demo script for RLS Farming Mode")
    parser.add_argument(
        "--target_priority",
        choices=["ig88", "axkva_min", "crystal_snake"],
        help="Specific target to prioritize"
    )
    parser.add_argument(
        "--solo_mode",
        action="store_true",
        help="Run in solo mode (default: group mode)"
    )
    parser.add_argument(
        "--max_sessions",
        type=int,
        default=3,
        help="Maximum sessions to run (default: 3)"
    )
    parser.add_argument(
        "--demo_mode",
        action="store_true",
        help="Run in demo mode with mock data only"
    )
    
    args = parser.parse_args()
    
    try:
        success = run_full_demo(args)
        if success:
            print("\n✅ Demo completed successfully!")
            return 0
        else:
            print("\n❌ Demo failed!")
            return 1
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 