#!/usr/bin/env python3
"""
Test script for Batch 020 - Mount Detection & Automatic Travel

This script tests the mount handler functionality including:
- Mount detection via OCR
- Zone permission checking
- Automatic mount summoning/dismounting
- Travel automation with mounts
- Configuration loading
- State persistence
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


def test_mount_handler_initialization():
    """Test mount handler initialization and configuration loading."""
    print("\n=== Testing Mount Handler Initialization ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        # Test basic initialization
        handler = MountHandler()
        
        # Check that default mounts are loaded
        assert len(handler.available_mounts) > 0, "No default mounts loaded"
        assert "Dewback" in handler.available_mounts, "Dewback mount not found"
        assert "Speeder" in handler.available_mounts, "Speeder mount not found"
        
        # Check mount priority
        assert len(handler.mount_priority) > 0, "Mount priority not loaded"
        assert "Dewback" in handler.mount_priority, "Dewback not in priority list"
        
        # Check zone data loading
        assert len(handler.zone_info) > 0, "No zones loaded"
        assert "Mos Eisley" in handler.zone_info, "Mos Eisley zone not found"
        
        print("✅ Mount handler initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Mount handler initialization failed: {e}")
        return False


def test_mount_detection():
    """Test mount detection via OCR."""
    print("\n=== Testing Mount Detection ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        handler = MountHandler()
        
        # Mock OCR to simulate mount detection
        with patch('core.mounts.mount_handler.OCREngine') as mock_ocr:
            mock_engine = Mock()
            mock_engine.extract_text_from_screen.return_value = Mock(
                text="Dewback Speeder Swoop Bantha Ronto"
            )
            handler.ocr_engine = mock_engine
            
            # Test mount detection
            detected_mounts = handler.detect_mounts()
            
            # Should detect the mounts from the mock OCR text
            expected_mounts = ["Dewback", "Speeder", "Swoop", "Bantha", "Ronto"]
            for mount in expected_mounts:
                assert mount in detected_mounts, f"Mount {mount} not detected"
                assert handler.available_mounts[mount].learned, f"Mount {mount} not marked as learned"
            
            print(f"✅ Mount detection successful: {detected_mounts}")
            return True
            
    except Exception as e:
        print(f"❌ Mount detection failed: {e}")
        return False


def test_zone_permissions():
    """Test zone permission checking."""
    print("\n=== Testing Zone Permissions ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        handler = MountHandler()
        
        # Test outdoor zone (should allow mounts)
        permissions = handler.check_zone_permissions("Tatooine Desert")
        assert permissions["mounts_allowed"] == True, "Outdoor zone should allow mounts"
        assert permissions["zone_type"] == "outdoor", "Zone type should be outdoor"
        
        # Test indoor zone (should not allow mounts)
        permissions = handler.check_zone_permissions("Mos Eisley Cantina")
        assert permissions["mounts_allowed"] == False, "Indoor zone should not allow mounts"
        assert permissions["zone_type"] == "indoor", "Zone type should be indoor"
        
        # Test city zone with restrictions
        permissions = handler.check_zone_permissions("Mos Eisley")
        assert permissions["mounts_allowed"] == True, "City should allow mounts"
        assert "Swoop" in permissions["restrictions"], "Swoop should be restricted in Mos Eisley"
        
        # Test combat zone
        permissions = handler.check_zone_permissions("PvP Arena")
        assert permissions["mounts_allowed"] == False, "Combat zone should not allow mounts"
        assert permissions["zone_type"] == "combat", "Zone type should be combat"
        
        print("✅ Zone permissions working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Zone permissions failed: {e}")
        return False


def test_mount_selection():
    """Test best mount selection logic."""
    print("\n=== Testing Mount Selection ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        handler = MountHandler()
        
        # Mark some mounts as learned
        handler.available_mounts["Dewback"].learned = True
        handler.available_mounts["Speeder"].learned = True
        handler.available_mounts["Swoop"].learned = True
        
        # Test outdoor zone (should prefer Dewback based on priority)
        best_mount = handler.get_best_mount("Tatooine Desert")
        assert best_mount == "Dewback", f"Expected Dewback, got {best_mount}"
        
        # Test city zone with Swoop restriction
        best_mount = handler.get_best_mount("Mos Eisley")
        assert best_mount == "Dewback", f"Expected Dewback (Swoop restricted), got {best_mount}"
        
        # Test indoor zone (should return None)
        best_mount = handler.get_best_mount("Mos Eisley Cantina")
        assert best_mount is None, f"Expected None for indoor zone, got {best_mount}"
        
        # Test with no learned mounts
        handler.available_mounts["Dewback"].learned = False
        handler.available_mounts["Speeder"].learned = False
        handler.available_mounts["Swoop"].learned = False
        
        best_mount = handler.get_best_mount("Tatooine Desert")
        assert best_mount is None, f"Expected None with no learned mounts, got {best_mount}"
        
        print("✅ Mount selection working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Mount selection failed: {e}")
        return False


def test_mount_summoning():
    """Test mount summoning and dismounting."""
    print("\n=== Testing Mount Summoning ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        handler = MountHandler()
        
        # Mark a mount as learned
        handler.available_mounts["Dewback"].learned = True
        
        # Test summoning
        success = handler.summon_mount("Dewback")
        assert success == True, "Mount summoning should succeed"
        assert handler.is_mounted == True, "Should be mounted after summoning"
        assert handler.current_mount == "Dewback", "Current mount should be Dewback"
        
        # Test summoning unknown mount
        success = handler.summon_mount("Unknown Mount")
        assert success == False, "Unknown mount should fail"
        
        # Test summoning unlearned mount
        handler.available_mounts["Speeder"].learned = False
        success = handler.summon_mount("Speeder")
        assert success == False, "Unlearned mount should fail"
        
        # Test dismounting
        success = handler.dismount()
        assert success == True, "Dismounting should succeed"
        assert handler.is_mounted == False, "Should not be mounted after dismounting"
        assert handler.current_mount is None, "Current mount should be None"
        
        # Test dismounting when not mounted
        success = handler.dismount()
        assert success == True, "Dismounting when not mounted should succeed"
        
        print("✅ Mount summoning/dismounting working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Mount summoning failed: {e}")
        return False


def test_auto_mount_travel():
    """Test automatic mount handling during travel."""
    print("\n=== Testing Auto-Mount Travel ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        handler = MountHandler()
        
        # Mark mounts as learned
        handler.available_mounts["Dewback"].learned = True
        handler.available_mounts["Speeder"].learned = True
        
        # Test outdoor travel (should mount)
        success = handler.auto_mount_travel("Tatooine Desert", "Tatooine Desert")
        assert success == True, "Auto-mount travel should succeed"
        assert handler.is_mounted == True, "Should be mounted for outdoor travel"
        assert handler.current_mount == "Dewback", "Should use Dewback (highest priority)"
        
        # Test indoor travel (should dismount)
        success = handler.auto_mount_travel("Mos Eisley Cantina", "Mos Eisley Cantina")
        assert success == True, "Auto-mount travel should succeed"
        assert handler.is_mounted == False, "Should not be mounted for indoor travel"
        
        # Test city travel with restrictions
        success = handler.auto_mount_travel("Mos Eisley", "Mos Eisley")
        assert success == True, "Auto-mount travel should succeed"
        assert handler.is_mounted == True, "Should be mounted for city travel"
        assert handler.current_mount == "Dewback", "Should use Dewback (Swoop restricted)"
        
        print("✅ Auto-mount travel working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Auto-mount travel failed: {e}")
        return False


def test_zone_updates():
    """Test zone change handling."""
    print("\n=== Testing Zone Updates ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        handler = MountHandler()
        
        # Mark a mount as learned
        handler.available_mounts["Dewback"].learned = True
        
        # Start in outdoor zone (should mount)
        handler.update_zone("Tatooine Desert")
        assert handler.is_mounted == True, "Should be mounted in outdoor zone"
        assert handler.current_mount == "Dewback", "Should use Dewback"
        
        # Move to indoor zone (should dismount)
        handler.update_zone("Mos Eisley Cantina")
        assert handler.is_mounted == False, "Should not be mounted in indoor zone"
        assert handler.current_mount is None, "Should not have current mount"
        
        # Move back to outdoor zone (should mount again)
        handler.update_zone("Naboo Plains")
        assert handler.is_mounted == True, "Should be mounted in outdoor zone"
        assert handler.current_mount == "Dewback", "Should use Dewback"
        
        print("✅ Zone updates working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Zone updates failed: {e}")
        return False


def test_state_persistence():
    """Test mount state saving and loading."""
    print("\n=== Testing State Persistence ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        handler = MountHandler()
        
        # Set up some state
        handler.available_mounts["Dewback"].learned = True
        handler.current_mount = "Dewback"
        handler.is_mounted = True
        handler.current_zone = "Tatooine Desert"
        
        # Save state
        handler.save_state()
        
        # Create new handler and load state
        new_handler = MountHandler()
        new_handler.load_state()
        
        # Check that state was restored
        assert new_handler.current_mount == "Dewback", "Current mount not restored"
        assert new_handler.is_mounted == True, "Mounted state not restored"
        assert new_handler.current_zone == "Tatooine Desert", "Current zone not restored"
        assert new_handler.available_mounts["Dewback"].learned == True, "Mount learning not restored"
        
        # Clean up
        state_file = Path("data/mount_state.json")
        if state_file.exists():
            state_file.unlink()
        
        print("✅ State persistence working correctly")
        return True
        
    except Exception as e:
        print(f"❌ State persistence failed: {e}")
        return False


def test_global_functions():
    """Test global mount handler functions."""
    print("\n=== Testing Global Functions ===")
    
    try:
        from core.mounts.mount_handler import (
            get_mount_handler, detect_mounts, auto_mount_travel,
            update_zone, get_mount_status
        )
        
        # Test getting mount handler
        handler = get_mount_handler()
        assert handler is not None, "Mount handler should not be None"
        
        # Test mount status
        status = get_mount_status()
        assert "is_mounted" in status, "Status should contain is_mounted"
        assert "current_mount" in status, "Status should contain current_mount"
        assert "available_mounts" in status, "Status should contain available_mounts"
        
        # Test other functions (they should not raise exceptions)
        detect_mounts()
        auto_mount_travel("Test Destination")
        update_zone("Test Zone")
        
        print("✅ Global functions working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Global functions failed: {e}")
        return False


def test_configuration_loading():
    """Test mount configuration loading."""
    print("\n=== Testing Configuration Loading ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        # Test with custom config
        handler = MountHandler("config/mount_config.json")
        
        # Check that custom mounts are loaded
        custom_mounts = ["Rare Speeder", "Combat Mount"]
        for mount_name in custom_mounts:
            assert mount_name in handler.available_mounts, f"Custom mount {mount_name} not loaded"
        
        # Check mount priority
        assert "Dewback" in handler.mount_priority, "Dewback should be in priority list"
        assert handler.mount_priority[0] == "Dewback", "Dewback should be first priority"
        
        print("✅ Configuration loading working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False


def test_error_handling():
    """Test error handling in mount handler."""
    print("\n=== Testing Error Handling ===")
    
    try:
        from core.mounts.mount_handler import MountHandler
        
        handler = MountHandler()
        
        # Test with invalid mount name
        success = handler.summon_mount("Invalid Mount")
        assert success == False, "Invalid mount should fail gracefully"
        
        # Test with unlearned mount
        handler.available_mounts["Speeder"].learned = False
        success = handler.summon_mount("Speeder")
        assert success == False, "Unlearned mount should fail gracefully"
        
        # Test zone permissions with unknown zone
        permissions = handler.check_zone_permissions("Unknown Zone")
        assert permissions["mounts_allowed"] == True, "Unknown zone should default to allowing mounts"
        
        # Test mount detection with OCR failure
        with patch('core.mounts.mount_handler.capture_screen') as mock_capture:
            mock_capture.side_effect = Exception("OCR failed")
            detected_mounts = handler.detect_mounts()
            assert isinstance(detected_mounts, list), "Should return empty list on OCR failure"
        
        print("✅ Error handling working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
        return False


def run_all_tests():
    """Run all mount handler tests."""
    print("🚀 Starting Batch 020 Mount Handler Tests")
    print("=" * 50)
    
    tests = [
        test_mount_handler_initialization,
        test_mount_detection,
        test_zone_permissions,
        test_mount_selection,
        test_mount_summoning,
        test_auto_mount_travel,
        test_zone_updates,
        test_state_persistence,
        test_global_functions,
        test_configuration_loading,
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
        print("🎉 All tests passed! Mount handler is working correctly.")
    else:
        print(f"⚠️  {failed} tests failed. Please check the implementation.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 