#!/usr/bin/env python3
"""Demo script for Batch 046 - Licensing System + Combat Intelligence v1."""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.license_manager import LicenseManager, LicenseType, LicenseStatus
from core.combat_logger import CombatLogger, SkillType, DamageType
from utils.ocr_damage_parser import OCRDamageParser


def demo_license_management():
    """Demonstrate license management functionality."""
    print("\n" + "="*60)
    print("LICENSE MANAGEMENT DEMO")
    print("="*60)
    
    # Initialize license manager
    manager = LicenseManager()
    
    # Test environment check
    print("\n1. Testing license environment check...")
    status = manager.check_license_environment()
    print(f"   License status: {status.value}")
    
    # Test adding a new license
    print("\n2. Adding test license...")
    success = manager.add_license(
        license_key="DEMO_LICENSE_001",
        discord_id="987654321098765432",
        license_type=LicenseType.BASIC,
        expiry_days=30,
        features=["combat_intelligence"],
        notes="Demo license for testing"
    )
    print(f"   License added: {success}")
    
    # Test license validation
    print("\n3. Testing license validation...")
    validation_status = manager.validate_license("DEMO_LICENSE_001", "987654321098765432")
    print(f"   Validation status: {validation_status.value}")
    
    # Test tester license validation
    print("\n4. Testing tester license validation...")
    tester_status = manager.validate_license("TESTER_001_MS11_2024", "123456789012345678")
    print(f"   Tester license status: {tester_status.value}")
    
    # Test whitelist functionality
    print("\n5. Testing whitelist functionality...")
    manager.add_to_whitelist("555555555555555555")
    whitelist = manager.get_whitelist()
    print(f"   Current whitelist: {whitelist}")
    
    # Get license summary
    print("\n6. License system summary...")
    summary = manager.get_license_summary()
    print(f"   Total licenses: {summary['total_licenses']}")
    print(f"   Valid licenses: {summary['valid_licenses']}")
    print(f"   Whitelist size: {summary['whitelist_size']}")
    
    # List all licenses
    print("\n7. All licenses:")
    licenses = manager.list_licenses()
    for license_info in licenses:
        print(f"   - {license_info['license_key']} ({license_info['license_type']}) - {license_info['status']}")


def demo_combat_logger():
    """Demonstrate combat logging functionality."""
    print("\n" + "="*60)
    print("COMBAT LOGGER DEMO")
    print("="*60)
    
    # Initialize combat logger
    logger = CombatLogger()
    
    # Start combat session
    print("\n1. Starting combat session...")
    session_id = logger.start_session()
    print(f"   Session ID: {session_id}")
    
    # Simulate combat events
    print("\n2. Simulating combat events...")
    
    # First combat sequence
    print("   - Using headshot skill...")
    logger.log_skill_usage("headshot", SkillType.WEAPON, "stormtrooper", 5.0)
    time.sleep(0.1)
    logger.log_damage_event(400, DamageType.PHYSICAL, "stormtrooper")
    logger.log_kill("stormtrooper")
    logger.log_xp_gain(255, "headshot")
    
    # Second combat sequence
    print("   - Using burst fire skill...")
    logger.log_skill_usage("burst_fire", SkillType.WEAPON, "imperial_officer", 8.0)
    time.sleep(0.1)
    logger.log_damage_event(400, DamageType.PHYSICAL, "imperial_officer")
    logger.log_kill("imperial_officer")
    logger.log_xp_gain(382, "burst_fire")
    
    # Third combat sequence
    print("   - Using rifle shot skill...")
    logger.log_skill_usage("rifle_shot", SkillType.WEAPON, "scout_trooper", 2.0)
    time.sleep(0.1)
    logger.log_damage_event(183, DamageType.PHYSICAL, "scout_trooper")
    logger.log_kill("scout_trooper")
    logger.log_xp_gain(172, "rifle_shot")
    
    # Fourth combat sequence (miss)
    print("   - Using sniper shot (miss)...")
    logger.log_skill_usage("sniper_shot", SkillType.WEAPON, "elite_trooper", 12.0)
    time.sleep(0.1)
    # No damage event (miss)
    logger.log_xp_gain(50, "sniper_shot")  # Reduced XP for miss
    
    # Get current session summary
    print("\n3. Current session summary...")
    current_summary = logger.get_current_session_summary()
    if current_summary:
        print(f"   Total damage: {current_summary['total_damage_dealt']}")
        print(f"   Total XP: {current_summary['total_xp_gained']}")
        print(f"   Kills: {current_summary['kills']}")
        print(f"   Skills used: {len(current_summary['skills'])}")
        
        # Show skill statistics
        print("\n   Skill statistics:")
        for skill_name, stats in current_summary['skills'].items():
            print(f"     - {skill_name}: {stats['usage_count']} uses, "
                  f"{stats['average_damage']:.1f} avg damage, "
                  f"{stats['success_rate']:.1%} success rate")
    
    # End session and get final summary
    print("\n4. Ending combat session...")
    final_summary = logger.end_session()
    
    if final_summary:
        print(f"   Session duration: {final_summary['duration_minutes']:.2f} minutes")
        print(f"   Final damage: {final_summary['total_damage_dealt']}")
        print(f"   Final XP: {final_summary['total_xp_gained']}")
        print(f"   Final kills: {final_summary['kills']}")
        print(f"   Targets engaged: {final_summary['targets_engaged']}")


def demo_ocr_damage_parser():
    """Demonstrate OCR damage parsing functionality."""
    print("\n" + "="*60)
    print("OCR DAMAGE PARSER DEMO")
    print("="*60)
    
    # Initialize OCR parser
    parser = OCRDamageParser()
    
    print("\n1. Testing OCR damage detection...")
    
    # Create test image with damage numbers
    import cv2
    import numpy as np
    
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Add test damage numbers
    cv2.putText(test_image, "183", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
    cv2.putText(test_image, "400 damage", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(test_image, "255 pts", (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(test_image, "800 DMG", (400, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Scan for damage
    damage_events = parser.scan_for_damage(test_image)
    
    print(f"   Found {len(damage_events)} damage events:")
    for event in damage_events:
        print(f"     - {event.damage_amount} {event.damage_type} damage "
              f"(confidence: {event.confidence:.2f})")
    
    # Get damage statistics
    print("\n2. Damage statistics...")
    stats = parser.get_damage_statistics()
    print(f"   Total damage: {stats['total_damage']}")
    print(f"   Event count: {stats['event_count']}")
    print(f"   Average damage: {stats['average_damage']:.1f}")
    print(f"   Highest damage: {stats['highest_damage']}")
    print(f"   Lowest damage: {stats['lowest_damage']}")
    
    # Show damage by type
    if stats['damage_by_type']:
        print("\n   Damage by type:")
        for damage_type, type_stats in stats['damage_by_type'].items():
            print(f"     - {damage_type}: {type_stats['total']} total, "
                  f"{type_stats['average']:.1f} average, "
                  f"{type_stats['count']} events")
    
    # Test export/import functionality
    print("\n3. Testing export/import functionality...")
    export_success = parser.export_damage_history("logs/combat/damage_history_export.json")
    print(f"   Export successful: {export_success}")
    
    # Clear history and import
    parser.clear_history()
    import_success = parser.import_damage_history("logs/combat/damage_history_export.json")
    print(f"   Import successful: {import_success}")
    
    # Get recent events
    print("\n4. Recent damage events...")
    recent_events = parser.get_recent_damage_events(seconds=60.0)
    print(f"   Recent events: {len(recent_events)}")


def demo_integration():
    """Demonstrate integration between components."""
    print("\n" + "="*60)
    print("INTEGRATION DEMO")
    print("="*60)
    
    # Initialize all components
    license_manager = LicenseManager()
    combat_logger = CombatLogger()
    ocr_parser = OCRDamageParser()
    
    print("\n1. License validation before combat...")
    license_status = license_manager.check_license_environment()
    print(f"   License status: {license_status.value}")
    
    if license_status == LicenseStatus.VALID:
        print("   ✓ License valid, proceeding with combat...")
        
        # Start combat session
        session_id = combat_logger.start_session()
        print(f"   Combat session started: {session_id}")
        
        # Simulate combat with OCR integration
        print("\n2. Simulating combat with OCR damage detection...")
        
        # Create test image for OCR
        import cv2
        import numpy as np
        
        test_image = np.zeros((400, 600, 3), dtype=np.uint8)
        cv2.putText(test_image, "450", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
        
        # Log skill usage
        combat_logger.log_skill_usage("headshot", SkillType.WEAPON, "target_1")
        
        # Simulate OCR damage detection
        damage_events = ocr_parser.scan_for_damage(test_image)
        if damage_events:
            for event in damage_events:
                # Convert OCR damage event to combat logger format
                combat_logger.log_damage_event(
                    event.damage_amount,
                    DamageType.PHYSICAL,  # Assume physical for demo
                    "target_1"
                )
                print(f"   OCR detected: {event.damage_amount} damage")
        
        # Log kill
        combat_logger.log_kill("target_1")
        combat_logger.log_xp_gain(255, "headshot")
        
        # Get session summary
        summary = combat_logger.get_current_session_summary()
        if summary:
            print(f"\n   Session summary:")
            print(f"     - Total damage: {summary['total_damage_dealt']}")
            print(f"     - Total XP: {summary['total_xp_gained']}")
            print(f"     - Kills: {summary['kills']}")
        
        # End session
        final_summary = combat_logger.end_session()
        print(f"\n   Combat session completed")
        
    else:
        print("   ✗ License invalid, running in offline mode")
        print("   Combat intelligence features disabled")


def main():
    """Run all demos."""
    print("🎯 BATCH 046 - LICENSING SYSTEM + COMBAT INTELLIGENCE v1")
    print("="*60)
    print("This demo showcases the new licensing system and combat intelligence features.")
    print("="*60)
    
    try:
        # Run all demos
        demo_license_management()
        demo_combat_logger()
        demo_ocr_damage_parser()
        demo_integration()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("Batch 046 features implemented:")
        print("  ✓ License Management with manual whitelist")
        print("  ✓ Hardcoded tester licenses (4 lifetime-valid)")
        print("  ✓ License check at session start")
        print("  ✓ Stripe-ready webhook stub")
        print("  ✓ Combat Intelligence with skill tracking")
        print("  ✓ OCR-based damage detection")
        print("  ✓ Session summary with damage statistics")
        print("  ✓ Combat stats saved to logs/combat/")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 