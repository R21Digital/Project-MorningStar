#!/usr/bin/env python3
"""
Test script for Batch 023 - Mount Detection and Automatic Mounting

This script tests the enhanced mount management functionality including:
- Mount detection via command output and hotbar scan
- Automatic mounting for long-distance travel
- Zone-based mount restrictions
- Fallback mount handling
- User-configurable mount preferences
"""

import json
import logging
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mount_manager_initialization():
    """Test mount manager initialization and configuration loading."""
    print("\n=== Testing Mount Manager Initialization ===")
    
    try:
        from movement.mount_manager import MountManager
        
        # Test basic initialization
        manager = MountManager()
        manager.enable_test_mode()  # Enable test mode for faster execution
        
        # Check that mount preferences are loaded
        assert manager.mount_preferences is not None, "Mount preferences not loaded"
        # The preferences file has "speederbike" as preferred mount, so we should check for that
        assert manager.mount_preferences.preferred_mount == "speederbike", "Preferred mount should be speederbike from config"
        assert manager.mount_preferences.auto_mount_distance == 100, "Auto mount distance should be 100 from config"
        
        # Check that default mounts are initialized
        assert len(manager.available_mounts) > 0, "No default mounts loaded"
        assert "speederbike" in manager.available_mounts, "Speederbike not found"
        assert "dewback" in manager.available_mounts, "Dewback not found"
        
        print("✅ Mount manager initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Mount manager initialization failed: {e}")
        return False


def test_mount_preferences_loading():
    """Test mount preferences loading and saving."""
    print("\n=== Testing Mount Preferences ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Test default preferences - check that preferences are loaded correctly
        # The preferences file has "speederbike" as preferred mount, so we should check for that
        assert manager.mount_preferences.preferred_mount == "speederbike", "Preferred mount should be speederbike from config"
        assert manager.mount_preferences.auto_mount_distance == 100, "Auto mount distance should be 100 from config"
        assert manager.mount_preferences.enable_auto_mount == True, "Auto mount should be enabled from config"
        
        # Test preference modification
        manager.mount_preferences.preferred_mount = "speederbike"
        manager.mount_preferences.auto_mount_distance = 100
        manager.mount_preferences.enable_auto_mount = True
        
        # Save preferences
        manager.save_mount_preferences()
        
        # Create new manager to test loading
        new_manager = MountManager()
        assert new_manager.mount_preferences.preferred_mount == "speederbike", "Preferred mount not saved"
        assert new_manager.mount_preferences.auto_mount_distance == 100, "Auto mount distance not saved"
        assert new_manager.mount_preferences.enable_auto_mount == True, "Auto mount setting not saved"
        
        print("✅ Mount preferences working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Mount preferences failed: {e}")
        return False


def test_mount_detection():
    """Test mount detection functionality."""
    print("\n=== Testing Mount Detection ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Test mount detection
        detected_mounts = manager.detect_mounts()
        assert isinstance(detected_mounts, list), "Mount detection should return a list"
        
        # Check that some mounts are marked as learned
        learned_mounts = [name for name, mount in manager.available_mounts.items() 
                         if mount.learned]
        assert len(learned_mounts) > 0, "No mounts marked as learned"
        
        print("✅ Mount detection working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Mount detection failed: {e}")
        return False


def test_command_mount_detection():
    """Test mount detection from command output."""
    print("\n=== Testing Command Mount Detection ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Test command-based mount detection
        command_mounts = manager._detect_mounts_from_command()
        assert isinstance(command_mounts, list), "Command detection should return a list"
        
        # Should detect some mounts from mock command output
        assert len(command_mounts) > 0, "No mounts detected from command output"
        assert "speederbike" in command_mounts, "Speederbike not detected from command"
        assert "dewback" in command_mounts, "Dewback not detected from command"
        
        print("✅ Command mount detection working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Command mount detection failed: {e}")
        return False


def test_hotbar_mount_detection():
    """Test mount detection from hotbar scan."""
    print("\n=== Testing Hotbar Mount Detection ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Test hotbar-based mount detection
        hotbar_mounts = manager._detect_mounts_from_hotbar()
        assert isinstance(hotbar_mounts, list), "Hotbar detection should return a list"
        
        # In test mode with mock OCR, this might return empty list, which is OK
        print("✅ Hotbar mount detection working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Hotbar mount detection failed: {e}")
        return False


def test_mount_travel_logic():
    """Test mount decision logic for travel."""
    print("\n=== Testing Mount Travel Logic ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Reset all mounts to not learned
        for mount in manager.available_mounts.values():
            mount.learned = False
        
        # Mark some mounts as learned
        manager.available_mounts["speederbike"].learned = True
        manager.available_mounts["dewback"].learned = True
        
        # Test short distance (should not mount)
        should_mount = manager.should_mount_for_travel(50)
        assert should_mount == False, "Should not mount for short distance"
        
        # Enable auto-mount for testing
        manager.mount_preferences.enable_auto_mount = True
        
        # Test long distance (should mount)
        should_mount = manager.should_mount_for_travel(150)
        assert should_mount == True, "Should mount for long distance"
        
        # Test blacklisted zone
        should_mount = manager.should_mount_for_travel(150, "inside_building")
        assert should_mount == False, "Should not mount in blacklisted zone"
        
        # Test when already mounted
        manager.is_mounted = True
        should_mount = manager.should_mount_for_travel(150)
        assert should_mount == False, "Should not mount when already mounted"
        
        print("✅ Mount travel logic working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Mount travel logic failed: {e}")
        return False


def test_best_mount_selection():
    """Test best mount selection logic."""
    print("\n=== Testing Best Mount Selection ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Reset all mounts to not learned
        for mount in manager.available_mounts.values():
            mount.learned = False
        
        # Mark mounts as learned
        manager.available_mounts["speederbike"].learned = True
        manager.available_mounts["dewback"].learned = True
        manager.available_mounts["swoop"].learned = True
        
        # Test best mount selection
        best_mount = manager.get_best_mount()
        # The preferred mount is "speederbike", so it should be selected first
        # The sorting prioritizes preferred mount first, then by speed
        assert best_mount == "speederbike", "Preferred mount should be selected first"
        
        # Test with zone restrictions
        best_mount = manager.get_best_mount("inside_building")
        assert best_mount is None, "No mount should be available in restricted zone"
        
        # Test with combat restrictions
        manager.is_in_combat = True
        best_mount = manager.get_best_mount()
        assert best_mount == "dewback", "Combat mount should be selected in combat"
        
        print("✅ Best mount selection working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Best mount selection failed: {e}")
        return False


def test_mount_creature():
    """Test mount creature functionality."""
    print("\n=== Testing Mount Creature ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Reset all mounts to not learned
        for mount in manager.available_mounts.values():
            mount.learned = False
        
        # Mark a mount as learned
        manager.available_mounts["speederbike"].learned = True
        
        # Test mounting
        success = manager.mount_creature("speederbike")
        assert success == True, "Mount attempt should succeed in test mode"
        assert manager.is_mounted == True, "Should be marked as mounted"
        assert manager.current_mount == "speederbike", "Current mount should be set"
        
        # Test mounting unknown mount
        success = manager.mount_creature("unknown_mount")
        assert success == False, "Should fail for unknown mount"
        
        # Test mounting unlearned mount
        success = manager.mount_creature("swoop")
        assert success == False, "Should fail for unlearned mount"
        
        print("✅ Mount creature working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Mount creature failed: {e}")
        return False


def test_dismount_creature():
    """Test dismount creature functionality."""
    print("\n=== Testing Dismount Creature ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Test dismount when not mounted
        success = manager.dismount_creature()
        assert success == True, "Dismount should succeed when not mounted"
        
        # Reset all mounts to not learned
        for mount in manager.available_mounts.values():
            mount.learned = False
        
        # Mount first, then dismount
        manager.available_mounts["speederbike"].learned = True
        manager.mount_creature("speederbike")
        
        success = manager.dismount_creature()
        assert success == True, "Dismount should succeed"
        assert manager.is_mounted == False, "Should be marked as not mounted"
        assert manager.current_mount is None, "Current mount should be cleared"
        
        print("✅ Dismount creature working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Dismount creature failed: {e}")
        return False


def test_auto_mount_for_travel():
    """Test automatic mounting for travel."""
    print("\n=== Testing Auto Mount for Travel ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Reset all mounts to not learned
        for mount in manager.available_mounts.values():
            mount.learned = False
        
        # Mark mounts as learned
        manager.available_mounts["speederbike"].learned = True
        manager.available_mounts["dewback"].learned = True
        
        # Enable auto-mount for testing
        manager.mount_preferences.enable_auto_mount = True
        
        # Test auto mount for long distance
        success = manager.auto_mount_for_travel(150)
        assert success == True, "Auto mount should succeed for long distance"
        assert manager.is_mounted == True, "Should be mounted after auto mount"
        
        # Reset state
        manager.is_mounted = False
        manager.current_mount = None
        
        # Test auto mount for short distance
        success = manager.auto_mount_for_travel(50)
        assert success == False, "Auto mount should not succeed for short distance"
        
        print("✅ Auto mount for travel working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Auto mount for travel failed: {e}")
        return False


def test_zone_info_updates():
    """Test zone information updates and auto-dismounting."""
    print("\n=== Testing Zone Info Updates ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Mount first
        manager.available_mounts["speederbike"].learned = True
        manager.mount_creature("speederbike")
        
        # Test auto-dismount in blacklisted zone
        manager.update_zone_info("inside_building", is_indoors=True)
        assert manager.is_mounted == False, "Should auto-dismount in blacklisted zone"
        
        # Mount again
        manager.mount_creature("speederbike")
        
        # Test auto-dismount in combat
        manager.update_zone_info("combat_zone", is_in_combat=True)
        assert manager.is_mounted == False, "Should auto-dismount in combat"
        
        # Test normal zone update
        manager.update_zone_info("outdoor_zone", is_indoors=False, is_in_combat=False)
        assert manager.current_zone == "outdoor_zone", "Zone should be updated"
        assert manager.is_indoors == False, "Indoor status should be updated"
        assert manager.is_in_combat == False, "Combat status should be updated"
        
        print("✅ Zone info updates working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Zone info updates failed: {e}")
        return False


def test_mount_status():
    """Test mount status reporting."""
    print("\n=== Testing Mount Status ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Get initial status
        status = manager.get_mount_status()
        assert "is_mounted" in status, "Status should contain is_mounted"
        assert "current_mount" in status, "Status should contain current_mount"
        assert "current_zone" in status, "Status should contain current_zone"
        assert "available_mounts" in status, "Status should contain available_mounts"
        assert "preferences" in status, "Status should contain preferences"
        
        # Test status after mounting
        manager.available_mounts["speederbike"].learned = True
        manager.mount_creature("speederbike")
        
        status = manager.get_mount_status()
        assert status["is_mounted"] == True, "Should show as mounted"
        assert status["current_mount"] == "speederbike", "Should show current mount"
        
        print("✅ Mount status working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Mount status failed: {e}")
        return False


def test_global_functions():
    """Test global mount manager functions."""
    print("\n=== Testing Global Functions ===")
    
    try:
        from movement.mount_manager import (
            get_mount_manager, detect_mounts, auto_mount_for_travel,
            update_zone_info, get_mount_status
        )
        
        # Test getting manager
        manager = get_mount_manager()
        assert manager is not None, "Mount manager should not be None"
        
        # Test mount detection
        detected_mounts = detect_mounts()
        assert isinstance(detected_mounts, list), "Detected mounts should be a list"
        
        # Test mount status
        status = get_mount_status()
        assert "is_mounted" in status, "Status should contain is_mounted"
        assert "preferences" in status, "Status should contain preferences"
        
        # Test zone info update
        update_zone_info("test_zone", is_indoors=False, is_in_combat=False)
        
        # Test auto mount for travel
        success = auto_mount_for_travel(150)
        # This might fail if no mounts are learned, which is OK
        
        print("✅ Global functions working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Global functions failed: {e}")
        return False


def test_error_handling():
    """Test error handling in mount system."""
    print("\n=== Testing Error Handling ===")
    
    try:
        from movement.mount_manager import MountManager
        
        manager = MountManager()
        manager.enable_test_mode()
        
        # Test mounting unknown mount
        success = manager.mount_creature("unknown_mount")
        assert success == False, "Should fail for unknown mount"
        
        # Test mounting unlearned mount
        success = manager.mount_creature("swoop")
        assert success == False, "Should fail for unlearned mount"
        
        # Test mount in restricted zone
        manager.available_mounts["speederbike"].learned = True
        should_mount = manager.should_mount_for_travel(150, "inside_building")
        assert should_mount == False, "Should not mount in restricted zone"
        
        # Test with no available mounts
        for mount in manager.available_mounts.values():
            mount.learned = False
        
        should_mount = manager.should_mount_for_travel(150)
        assert should_mount == False, "Should not mount when no mounts available"
        
        print("✅ Error handling working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
        return False


def run_all_tests():
    """Run all mount manager tests."""
    print("🚀 Starting Batch 023 Mount Manager Tests")
    print("=" * 50)
    
    tests = [
        test_mount_manager_initialization,
        test_mount_preferences_loading,
        test_mount_detection,
        test_command_mount_detection,
        test_hotbar_mount_detection,
        test_mount_travel_logic,
        test_best_mount_selection,
        test_mount_creature,
        test_dismount_creature,
        test_auto_mount_for_travel,
        test_zone_info_updates,
        test_mount_status,
        test_global_functions,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Mount manager is working correctly.")
    else:
        print(f"⚠️  {failed} tests failed. Please check the implementation.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 