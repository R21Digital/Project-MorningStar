"""
Test Script for Batch 024 – Lightweight Combat Profile Dispatcher

This script tests the functionality of:
- combat/rotation_engine.py
- profiles/combat/rifleman_medic.json
"""

import sys
import time
import json
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from combat.rotation_engine import (
    RotationEngine, CombatProfile, SkillInfo, WeaponType, StanceType,
    get_rotation_engine, load_combat_profile, execute_rotation,
    is_skill_ready, get_rotation_status
)


def test_rotation_engine_initialization():
    """Test rotation engine initialization."""
    print("\n🧪 Testing Rotation Engine Initialization")
    
    try:
        # Initialize rotation engine
        engine = RotationEngine()
        print("✅ RotationEngine initialized successfully")
        
        # Check that profiles directory is set
        assert engine.profiles_dir.exists(), "Profiles directory not found"
        print("✅ Profiles directory found")
        
        # Check that available profiles are loaded
        assert len(engine.available_profiles) > 0, "No profiles found"
        print(f"✅ Found {len(engine.available_profiles)} available profiles")
        
        # Check that rifleman_medic profile is available
        assert "rifleman_medic" in engine.available_profiles, "rifleman_medic profile not found"
        print("✅ rifleman_medic profile found")
        
        return True
        
    except Exception as e:
        print(f"❌ Rotation Engine Initialization Test Failed: {e}")
        return False


def test_profile_loading():
    """Test profile loading functionality."""
    print("\n🧪 Testing Profile Loading")
    
    try:
        engine = RotationEngine()
        engine.enable_test_mode()
        
        # Test loading rifleman_medic profile
        success = engine.load_profile("rifleman_medic")
        assert success, "Failed to load rifleman_medic profile"
        print("✅ rifleman_medic profile loaded successfully")
        
        # Check profile properties
        assert engine.current_profile is not None, "Current profile not set"
        assert engine.current_profile.name == "rifleman_medic", "Profile name incorrect"
        assert engine.current_profile.weapon_type == WeaponType.RANGED, "Weapon type incorrect"
        assert engine.current_profile.stance == StanceType.KNEELING, "Stance incorrect"
        print("✅ Profile properties correct")
        
        # Check skills are loaded
        assert len(engine.current_profile.skills) > 0, "No skills loaded"
        print(f"✅ Loaded {len(engine.current_profile.skills)} skills")
        
        # Check rotation
        assert len(engine.current_profile.rotation) > 0, "No rotation skills"
        print(f"✅ Rotation has {len(engine.current_profile.rotation)} skills")
        
        return True
        
    except Exception as e:
        print(f"❌ Profile Loading Test Failed: {e}")
        return False


def test_skill_ready_check():
    """Test skill ready checking functionality."""
    print("\n🧪 Testing Skill Ready Check")
    
    try:
        engine = RotationEngine()
        engine.enable_test_mode()
        engine.load_profile("rifleman_medic")
        
        # Test skill ready check
        assert engine.is_skill_ready("aim"), "Aim skill should be ready (0 cooldown)"
        assert engine.is_skill_ready("rifle_shot"), "Rifle shot should be ready (0 cooldown)"
        print("✅ Skills with 0 cooldown are ready")
        
        # Test skills that don't exist
        assert not engine.is_skill_ready("nonexistent_skill"), "Non-existent skill should not be ready"
        print("✅ Non-existent skills correctly handled")
        
        # Test available skills list
        available_skills = engine.get_available_skills()
        assert len(available_skills) > 0, "No available skills found"
        assert "aim" in available_skills, "Aim should be available"
        assert "rifle_shot" in available_skills, "Rifle shot should be available"
        print(f"✅ Found {len(available_skills)} available skills")
        
        return True
        
    except Exception as e:
        print(f"❌ Skill Ready Check Test Failed: {e}")
        return False


def test_skill_execution():
    """Test skill execution functionality."""
    print("\n🧪 Testing Skill Execution")
    
    try:
        engine = RotationEngine()
        engine.enable_test_mode()
        engine.load_profile("rifleman_medic")
        
        # Test executing a skill
        success = engine.execute_skill("aim")
        assert success, "Skill execution failed"
        print("✅ Skill execution successful")
        
        # Test that skill is now on cooldown
        assert not engine.is_skill_ready("aim"), "Skill should be on cooldown after execution"
        print("✅ Skill cooldown working correctly")
        
        # Test executing skill that doesn't exist
        success = engine.execute_skill("nonexistent_skill")
        assert not success, "Non-existent skill should not execute"
        print("✅ Non-existent skill correctly rejected")
        
        # Test executing skill on cooldown
        success = engine.execute_skill("aim")
        assert not success, "Skill on cooldown should not execute"
        print("✅ Cooldown enforcement working")
        
        return True
        
    except Exception as e:
        print(f"❌ Skill Execution Test Failed: {e}")
        return False


def test_rotation_execution():
    """Test rotation execution functionality."""
    print("\n🧪 Testing Rotation Execution")
    
    try:
        engine = RotationEngine()
        engine.enable_test_mode()
        engine.load_profile("rifleman_medic")
        
        # Test rotation execution
        executed_skills = engine.execute_rotation()
        assert len(executed_skills) > 0, "No skills executed in rotation"
        print(f"✅ Executed {len(executed_skills)} skills in rotation")
        
        # Test that executed skills are on cooldown
        for skill_name in executed_skills:
            assert not engine.is_skill_ready(skill_name), f"Executed skill {skill_name} should be on cooldown"
        print("✅ Executed skills are on cooldown")
        
        # Test fallback when rotation skills are on cooldown
        # First, ensure all rotation skills are on cooldown
        for skill_name in engine.current_profile.rotation:
            if engine.is_skill_ready(skill_name):
                engine.execute_skill(skill_name)
        
        # Now test fallback
        executed_skills = engine.execute_rotation()
        if executed_skills:
            assert executed_skills[0] == "rifle_shot", "Fallback skill should be used"
            print("✅ Fallback skill used when rotation skills on cooldown")
        
        return True
        
    except Exception as e:
        print(f"❌ Rotation Execution Test Failed: {e}")
        return False


def test_emergency_skills():
    """Test emergency skill functionality."""
    print("\n🧪 Testing Emergency Skills")
    
    try:
        engine = RotationEngine()
        engine.enable_test_mode()
        engine.load_profile("rifleman_medic")
        
        # Check that emergency skills are loaded
        assert "critical_heal" in engine.current_profile.emergency_skills, "Critical heal not found"
        assert "defensive" in engine.current_profile.emergency_skills, "Defensive skill not found"
        print("✅ Emergency skills loaded correctly")
        
        # Test emergency skill execution (simplified - in practice you'd check health)
        # For now, we'll just verify the emergency skill checking doesn't crash
        emergency_skill = engine._check_emergency_skills()
        # Should return None since we're not in a low health situation
        print("✅ Emergency skill checking working")
        
        return True
        
    except Exception as e:
        print(f"❌ Emergency Skills Test Failed: {e}")
        return False


def test_rotation_status():
    """Test rotation status functionality."""
    print("\n🧪 Testing Rotation Status")
    
    try:
        engine = RotationEngine()
        engine.enable_test_mode()
        engine.load_profile("rifleman_medic")
        
        # Get rotation status
        status = engine.get_rotation_status()
        assert "profile" in status, "Profile not in status"
        assert "weapon_type" in status, "Weapon type not in status"
        assert "stance" in status, "Stance not in status"
        assert "available_skills" in status, "Available skills not in status"
        assert "rotation" in status, "Rotation not in status"
        assert "fallback" in status, "Fallback not in status"
        assert "skill_cooldowns" in status, "Skill cooldowns not in status"
        print("✅ Rotation status contains all required fields")
        
        # Check status values
        assert status["profile"] == "rifleman_medic", "Profile name incorrect"
        assert status["weapon_type"] == "ranged", "Weapon type incorrect"
        assert status["stance"] == "kneeling", "Stance incorrect"
        assert status["fallback"] == "rifle_shot", "Fallback incorrect"
        print("✅ Rotation status values correct")
        
        # Check cooldown information
        cooldowns = status["skill_cooldowns"]
        assert "aim" in cooldowns, "Aim cooldown not in status"
        assert "headshot" in cooldowns, "Headshot cooldown not in status"
        print("✅ Cooldown information present")
        
        return True
        
    except Exception as e:
        print(f"❌ Rotation Status Test Failed: {e}")
        return False


def test_toolbar_scanning():
    """Test toolbar scanning functionality."""
    print("\n🧪 Testing Toolbar Scanning")
    
    try:
        engine = RotationEngine()
        engine.enable_test_mode()
        engine.load_profile("rifleman_medic")
        
        # Test toolbar scanning (will return empty list in test mode)
        found_skills = engine.scan_toolbar_skills()
        assert isinstance(found_skills, list), "Toolbar scanning should return list"
        print("✅ Toolbar scanning working (returns list)")
        
        # Test action log checking
        success = engine.check_action_log("aim")
        assert isinstance(success, bool), "Action log check should return boolean"
        print("✅ Action log checking working")
        
        return True
        
    except Exception as e:
        print(f"❌ Toolbar Scanning Test Failed: {e}")
        return False


def test_cooldown_management():
    """Test cooldown management functionality."""
    print("\n🧪 Testing Cooldown Management")
    
    try:
        engine = RotationEngine()
        engine.enable_test_mode()
        engine.load_profile("rifleman_medic")
        
        # Test initial state
        assert engine.is_skill_ready("headshot"), "Headshot should be ready initially"
        print("✅ Skills ready initially")
        
        # Execute skill and check cooldown
        engine.execute_skill("headshot")
        assert not engine.is_skill_ready("headshot"), "Headshot should be on cooldown"
        print("✅ Skill goes on cooldown after execution")
        
        # Check cooldown time
        skill_info = engine.current_profile.skills["headshot"]
        assert skill_info.cooldown == 5, "Headshot cooldown should be 5 seconds"
        print("✅ Cooldown time correct")
        
        # Test cooldown expiration (simulate time passing)
        skill_info.last_used = time.time() - 6  # 6 seconds ago
        assert engine.is_skill_ready("headshot"), "Headshot should be ready after cooldown"
        print("✅ Cooldown expiration working")
        
        return True
        
    except Exception as e:
        print(f"❌ Cooldown Management Test Failed: {e}")
        return False


def test_global_functions():
    """Test global functions."""
    print("\n🧪 Testing Global Functions")
    
    try:
        # Test get_rotation_engine
        engine = get_rotation_engine()
        assert isinstance(engine, RotationEngine), "get_rotation_engine should return RotationEngine"
        print("✅ get_rotation_engine working")
        
        # Test load_combat_profile
        success = load_combat_profile("rifleman_medic")
        assert success, "load_combat_profile should succeed"
        print("✅ load_combat_profile working")
        
        # Test is_skill_ready
        ready = is_skill_ready("aim")
        assert isinstance(ready, bool), "is_skill_ready should return boolean"
        print("✅ is_skill_ready working")
        
        # Test execute_rotation
        executed = execute_rotation()
        assert isinstance(executed, list), "execute_rotation should return list"
        print("✅ execute_rotation working")
        
        # Test get_rotation_status
        status = get_rotation_status()
        assert isinstance(status, dict), "get_rotation_status should return dict"
        print("✅ get_rotation_status working")
        
        return True
        
    except Exception as e:
        print(f"❌ Global Functions Test Failed: {e}")
        return False


def test_error_handling():
    """Test error handling functionality."""
    print("\n🧪 Testing Error Handling")
    
    try:
        engine = RotationEngine()
        engine.enable_test_mode()
        
        # Test loading non-existent profile
        success = engine.load_profile("nonexistent_profile")
        assert not success, "Loading non-existent profile should fail"
        print("✅ Non-existent profile loading handled correctly")
        
        # Test executing skill without profile loaded
        success = engine.execute_skill("aim")
        assert not success, "Executing skill without profile should fail"
        print("✅ Skill execution without profile handled correctly")
        
        # Test rotation without profile
        executed = engine.execute_rotation()
        assert len(executed) == 0, "Rotation without profile should return empty list"
        print("✅ Rotation without profile handled correctly")
        
        # Test status without profile
        status = engine.get_rotation_status()
        assert "error" in status, "Status without profile should contain error"
        print("✅ Status without profile handled correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error Handling Test Failed: {e}")
        return False


def test_profile_format():
    """Test profile JSON format."""
    print("\n🧪 Testing Profile Format")
    
    try:
        # Load and parse the rifleman_medic profile
        profile_path = Path("profiles/combat/rifleman_medic.json")
        assert profile_path.exists(), "rifleman_medic.json not found"
        
        with open(profile_path, 'r') as f:
            profile_data = json.load(f)
        
        # Check required fields
        required_fields = ["name", "weapon_type", "stance", "rotation", "heal_threshold", "fallback", "cooldowns"]
        for field in required_fields:
            assert field in profile_data, f"Required field '{field}' missing from profile"
        print("✅ All required fields present in profile")
        
        # Check field types
        assert isinstance(profile_data["name"], str), "Name should be string"
        assert isinstance(profile_data["weapon_type"], str), "Weapon type should be string"
        assert isinstance(profile_data["stance"], str), "Stance should be string"
        assert isinstance(profile_data["rotation"], list), "Rotation should be list"
        assert isinstance(profile_data["heal_threshold"], int), "Heal threshold should be int"
        assert isinstance(profile_data["fallback"], str), "Fallback should be string"
        assert isinstance(profile_data["cooldowns"], dict), "Cooldowns should be dict"
        print("✅ All field types correct")
        
        # Check weapon type value
        assert profile_data["weapon_type"] in ["ranged", "melee", "hybrid"], "Invalid weapon type"
        print("✅ Weapon type value valid")
        
        # Check stance value
        assert profile_data["stance"] in ["standing", "kneeling", "prone", "cover"], "Invalid stance"
        print("✅ Stance value valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Profile Format Test Failed: {e}")
        return False


def run_all_tests():
    """Run all tests and return results."""
    print("🚀 Starting Batch 024 - Lightweight Combat Profile Dispatcher Tests")
    print("=" * 60)
    
    tests = [
        test_rotation_engine_initialization,
        test_profile_loading,
        test_skill_ready_check,
        test_skill_execution,
        test_rotation_execution,
        test_emergency_skills,
        test_rotation_status,
        test_toolbar_scanning,
        test_cooldown_management,
        test_global_functions,
        test_error_handling,
        test_profile_format
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
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Batch 024 implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 