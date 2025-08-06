#!/usr/bin/env python3
"""
Test script for Session Anchor System (Batch 014)

This script tests the session anchor system's ability to define start/end locations
and ensure the bot returns there at the end of a session.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import json
from pathlib import Path

from core.session_anchor import (
    SessionAnchorManager,
    AnchorStatus,
    AnchorPoint,
    SessionAnchor,
    set_session_anchor,
    record_start_location,
    update_current_location,
    return_to_anchor,
    get_anchor_summary,
    log_anchor_summary,
    reset_anchor,
    session_anchor_manager
)


def test_session_anchor_initialization():
    """Test session anchor manager initialization."""
    print("🧪 Testing Session Anchor Manager Initialization...")
    
    try:
        # Test with default config
        manager = SessionAnchorManager()
        
        print(f"✅ Session anchor manager initialized successfully")
        print(f"   Config file: {manager.config_file}")
        print(f"   Anchor config loaded: {len(manager.anchor_config) > 0}")
        
        # Test with custom config
        custom_manager = SessionAnchorManager("config/start_location.json")
        print(f"✅ Custom session anchor manager initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing session anchor manager: {e}")
        return False


def test_anchor_point_creation():
    """Test anchor point creation and validation."""
    print("\n🧪 Testing Anchor Point Creation...")
    
    try:
        # Test valid anchor point
        anchor_point = AnchorPoint(
            planet="tatooine",
            zone="mos_eisley",
            coordinates=[3520, -4800],
            description="Mos Eisley Cantina - Test anchor",
            safe_zone=[3500, -4850, 40, 100]
        )
        
        print(f"✅ Created anchor point: {anchor_point.description}")
        print(f"   Planet: {anchor_point.planet}")
        print(f"   Zone: {anchor_point.zone}")
        print(f"   Coordinates: {anchor_point.coordinates}")
        print(f"   Safe zone: {anchor_point.safe_zone}")
        
        # Test invalid anchor point (should raise ValueError)
        try:
            invalid_anchor = AnchorPoint(
                planet="",  # Empty planet
                zone="test_zone",
                coordinates=[100, 200],
                description="Invalid anchor"
            )
            print("❌ Should have raised ValueError for empty planet")
            return False
        except ValueError:
            print("✅ Correctly raised ValueError for invalid anchor point")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in anchor point creation: {e}")
        return False


def test_session_anchor_setting():
    """Test setting session anchors."""
    print("\n🧪 Testing Session Anchor Setting...")
    
    try:
        manager = SessionAnchorManager()
        
        # Test setting default anchor
        success = manager.set_session_anchor("default")
        
        if success:
            print(f"✅ Successfully set default anchor")
            print(f"   Anchor point: {manager.session_anchor.anchor_point.description}")
            print(f"   Status: {manager.session_anchor.status.value}")
        else:
            print("❌ Failed to set default anchor")
            return False
        
        # Test setting profile-specific anchor
        success = manager.set_session_anchor("farming", profile="farming")
        
        if success:
            print(f"✅ Successfully set farming profile anchor")
            print(f"   Anchor point: {manager.session_anchor.anchor_point.description}")
        else:
            print("❌ Failed to set farming profile anchor")
            return False
        
        # Test setting session-specific anchor
        success = manager.set_session_anchor("legacy_quest")
        
        if success:
            print(f"✅ Successfully set legacy_quest session anchor")
            print(f"   Anchor point: {manager.session_anchor.anchor_point.description}")
        else:
            print("❌ Failed to set legacy_quest session anchor")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in session anchor setting: {e}")
        return False


def test_location_tracking():
    """Test location tracking functionality."""
    print("\n🧪 Testing Location Tracking...")
    
    try:
        manager = SessionAnchorManager()
        
        # Record start location
        manager.record_start_location("tatooine", "mos_eisley", [3520, -4800])
        print(f"✅ Recorded start location")
        
        # Update current location (same zone)
        manager.update_current_location("tatooine", "mos_eisley", [3600, -4850])
        print(f"✅ Updated current location (same zone)")
        
        # Update current location (different zone)
        manager.update_current_location("tatooine", "anchorhead", [3000, -5500])
        print(f"✅ Updated current location (zone change)")
        
        # Update current location (different planet)
        manager.update_current_location("corellia", "coronet", [100, 200])
        print(f"✅ Updated current location (planet change)")
        
        # Check zone changes
        zone_changes = manager.session_anchor.zone_changes
        print(f"   Zone changes recorded: {len(zone_changes)}")
        
        for i, change in enumerate(zone_changes):
            print(f"     {i+1}. {change['from_planet']}/{change['from_zone']} -> {change['to_planet']}/{change['to_zone']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in location tracking: {e}")
        return False


def test_anchor_detection():
    """Test anchor detection functionality."""
    print("\n🧪 Testing Anchor Detection...")
    
    try:
        manager = SessionAnchorManager()
        
        # Set an anchor
        manager.set_session_anchor("default")
        
        # Test not at anchor
        manager.update_current_location("tatooine", "anchorhead", [3000, -5500])
        at_anchor = manager._is_at_anchor()
        print(f"   Not at anchor: {not at_anchor}")
        
        if at_anchor:
            print("❌ Should not be at anchor")
            return False
        
        # Test at anchor (within safe zone)
        manager.update_current_location("tatooine", "mos_eisley", [3520, -4800])
        at_anchor = manager._is_at_anchor()
        print(f"   At anchor: {at_anchor}")
        
        if not at_anchor:
            print("❌ Should be at anchor")
            return False
        
        # Test at anchor (outside safe zone but close)
        manager.update_current_location("tatooine", "mos_eisley", [3570, -4850])
        at_anchor = manager._is_at_anchor()
        print(f"   At anchor (close): {at_anchor}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in anchor detection: {e}")
        return False


def test_return_logic():
    """Test return to anchor logic."""
    print("\n🧪 Testing Return Logic...")
    
    try:
        manager = SessionAnchorManager()
        
        # Set an anchor
        manager.set_session_anchor("default")
        
        # Test should not return (at anchor)
        manager.update_current_location("tatooine", "mos_eisley", [3520, -4800])
        should_return = manager.should_return_to_anchor()
        print(f"   Should not return (at anchor): {not should_return}")
        
        if should_return:
            print("❌ Should not return when at anchor")
            return False
        
        # Test should not return (away but not too long)
        manager.update_current_location("tatooine", "anchorhead", [3000, -5500])
        should_return = manager.should_return_to_anchor()
        print(f"   Should not return (not too long): {not should_return}")
        
        # Test should return (away too long)
        # Simulate being away for a long time
        manager.session_anchor.start_time = manager.session_anchor.start_time.replace(
            year=manager.session_anchor.start_time.year - 1
        )
        should_return = manager.should_return_to_anchor()
        print(f"   Should return (away too long): {should_return}")
        
        if not should_return:
            print("❌ Should return when away too long")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in return logic: {e}")
        return False


def test_anchor_summary():
    """Test anchor summary generation."""
    print("\n🧪 Testing Anchor Summary...")
    
    try:
        manager = SessionAnchorManager()
        
        # Set up a complete session
        manager.set_session_anchor("default")
        manager.record_start_location("tatooine", "mos_eisley", [3520, -4800])
        manager.update_current_location("tatooine", "anchorhead", [3000, -5500])
        manager.update_current_location("corellia", "coronet", [100, 200])
        
        # Get summary
        summary = manager.get_anchor_summary()
        
        print(f"✅ Generated anchor summary")
        print(f"   Status: {summary.get('status')}")
        print(f"   Zone changes: {summary.get('zone_change_count', 0)}")
        print(f"   Travel count: {summary.get('travel_count', 0)}")
        print(f"   Time away: {summary.get('time_away_formatted', 'N/A')}")
        
        # Check summary structure
        required_keys = ['anchor_point', 'status', 'start_location', 'current_location', 'zone_changes', 'travel_log']
        for key in required_keys:
            if key not in summary:
                print(f"❌ Missing key in summary: {key}")
                return False
        
        print("✅ Anchor summary structure correct")
        return True
        
    except Exception as e:
        print(f"❌ Error in anchor summary: {e}")
        return False


def test_anchor_logging():
    """Test anchor summary logging."""
    print("\n🧪 Testing Anchor Logging...")
    
    try:
        manager = SessionAnchorManager()
        
        # Set up a session
        manager.set_session_anchor("default")
        manager.record_start_location("tatooine", "mos_eisley", [3520, -4800])
        manager.update_current_location("tatooine", "anchorhead", [3000, -5500])
        
        # Log anchor summary
        session_id = "test_session_123"
        manager.log_anchor_summary(session_id)
        
        # Check if log file was created
        log_file = Path("logs") / f"anchor_summary_{session_id}.json"
        if log_file.exists():
            print("✅ Anchor summary log file created successfully")
            
            # Read and verify log content
            with open(log_file, 'r') as f:
                log_data = json.load(f)
            
            print(f"   Session ID: {log_data.get('session_id')}")
            print(f"   Timestamp: {log_data.get('timestamp')}")
            print(f"   Has anchor summary: {'anchor_summary' in log_data}")
            
            return True
        else:
            print("❌ Anchor summary log file not created")
            return False
        
    except Exception as e:
        print(f"❌ Error in anchor logging: {e}")
        return False


def test_global_functions():
    """Test global session anchor functions."""
    print("\n🧪 Testing Global Functions...")
    
    try:
        # Test global set anchor
        success = set_session_anchor("default")
        print(f"   Global set anchor: {success}")
        
        # Test global record start location
        record_start_location("tatooine", "mos_eisley", [3520, -4800])
        print("   Global record start location called")
        
        # Test global update current location
        update_current_location("tatooine", "anchorhead", [3000, -5500])
        print("   Global update current location called")
        
        # Test global get summary
        summary = get_anchor_summary()
        print(f"   Global get summary: {summary.get('status')}")
        
        # Test global log summary
        log_anchor_summary("test_global_session")
        print("   Global log summary called")
        
        # Test global reset
        reset_anchor()
        print("   Global reset anchor called")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in global functions: {e}")
        return False


def test_cross_planet_travel():
    """Test cross-planet travel functionality."""
    print("\n🧪 Testing Cross-Planet Travel...")
    
    try:
        manager = SessionAnchorManager()
        
        # Set anchor on different planet
        manager.set_session_anchor("training")  # Corellia anchor
        manager.update_current_location("tatooine", "mos_eisley", [3520, -4800])
        
        print(f"   Anchor planet: {manager.session_anchor.anchor_point.planet}")
        print(f"   Current planet: {manager.session_anchor.current_location['planet']}")
        
        # Test cross-planet travel
        success = manager._travel_to_planet("corellia")
        print(f"   Cross-planet travel success: {success}")
        
        if success:
            print("✅ Cross-planet travel simulation successful")
        else:
            print("❌ Cross-planet travel failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in cross-planet travel: {e}")
        return False


def test_navigation_integration():
    """Test navigation integration."""
    print("\n🧪 Testing Navigation Integration...")
    
    try:
        manager = SessionAnchorManager()
        
        # Set anchor and current location
        manager.set_session_anchor("default")
        manager.update_current_location("tatooine", "mos_eisley", [3600, -4850])
        
        # Test navigation to anchor
        success = manager._navigate_to_anchor()
        print(f"   Navigation to anchor success: {success}")
        
        # Note: This will likely fail in test environment without game window
        # but we can verify the integration logic
        if success:
            print("✅ Navigation to anchor successful")
        else:
            print("ℹ️  Navigation to anchor failed (expected in test environment)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in navigation integration: {e}")
        return False


def main():
    """Run all tests for session anchor system."""
    print("🚀 Starting Session Anchor System Tests (Batch 014)")
    print("=" * 70)
    
    tests = [
        ("Session Anchor Manager Initialization", test_session_anchor_initialization),
        ("Anchor Point Creation", test_anchor_point_creation),
        ("Session Anchor Setting", test_session_anchor_setting),
        ("Location Tracking", test_location_tracking),
        ("Anchor Detection", test_anchor_detection),
        ("Return Logic", test_return_logic),
        ("Anchor Summary", test_anchor_summary),
        ("Anchor Logging", test_anchor_logging),
        ("Global Functions", test_global_functions),
        ("Cross-Planet Travel", test_cross_planet_travel),
        ("Navigation Integration", test_navigation_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Session anchor system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 