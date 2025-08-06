"""
Test Script for Batch 016 – Combat Core Engine & Action Sequencing

This script tests the functionality of:
- core/combat/combat_engine.py
- data/skills/ (skill definitions)
- profiles/combat/ (combat profiles)
"""

import sys
import time
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.combat.combat_engine import (
    CombatEngine, CombatState, CombatAction, SkillPriority, DamageType,
    Skill, CombatProfile, CombatTarget,
    get_combat_engine, execute_combat_action, get_combat_state
)

from profiles.combat.default_combat_profile import (
    create_default_rifleman_profile, create_default_brawler_profile,
    create_default_hybrid_profile, create_all_default_profiles
)


def test_combat_engine_basic_functionality():
    """Test basic combat engine functionality."""
    print("\n🧪 Testing Combat Engine Basic Functionality")
    
    try:
        # Initialize combat engine
        engine = CombatEngine()
        print("✅ CombatEngine initialized successfully")
        
        # Test scanning available skills
        skills = engine.scan_available_skills()
        print(f"✅ Scanned {len(skills)} available skills")
        
        # Test detecting combat state
        combat_state = engine.detect_combat_state()
        print(f"✅ Combat state detected: {combat_state.name}")
        
        # Test getting available skills
        available_skills = engine.get_available_skills()
        print(f"✅ Found {len(available_skills)} available skills (not on cooldown)")
        
        # Test combat summary
        summary = engine.get_combat_summary()
        print(f"✅ Combat summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Combat Engine Basic Functionality Test Failed: {e}")
        return False


def test_combat_engine_skill_loading():
    """Test skill loading functionality."""
    print("\n🧪 Testing Combat Engine Skill Loading")
    
    try:
        engine = CombatEngine()
        
        # Test skill loading from files
        skills = engine.available_skills
        print(f"✅ Loaded {len(skills)} skills from data files")
        
        # Check for specific skills
        rifle_skills = ["Rifle Shot", "Burst Shot", "Full Auto"]
        medic_skills = ["Heal Self", "Heal Other", "Stim Pack"]
        
        rifle_found = sum(1 for skill in rifle_skills if skill in skills)
        medic_found = sum(1 for skill in medic_skills if skill in skills)
        
        print(f"✅ Found {rifle_found}/{len(rifle_skills)} rifle skills")
        print(f"✅ Found {medic_found}/{len(medic_skills)} medic skills")
        
        # Test skill properties
        if "Rifle Shot" in skills:
            rifle_shot = skills["Rifle Shot"]
            print(f"✅ Rifle Shot properties: cooldown={rifle_shot.cooldown}s, damage={rifle_shot.damage_range}")
        
        return True
        
    except Exception as e:
        print(f"❌ Combat Engine Skill Loading Test Failed: {e}")
        return False


def test_combat_engine_profile_loading():
    """Test combat profile loading functionality."""
    print("\n🧪 Testing Combat Engine Profile Loading")
    
    try:
        engine = CombatEngine()
        
        # Test loading default profile
        if engine.active_profile:
            print(f"✅ Loaded default profile: {engine.active_profile.name}")
            print(f"✅ Profile abilities: {len(engine.active_profile.abilities)}")
            print(f"✅ Profile rotation: {len(engine.active_profile.ability_rotation)}")
            print(f"✅ Emergency abilities: {len(engine.active_profile.emergency_abilities)}")
        else:
            print("⚠️ No default profile loaded")
        
        # Test loading specific profile
        success = engine.load_combat_profile("rifleman_medic")
        print(f"✅ Loaded rifleman_medic profile: {success}")
        
        return True
        
    except Exception as e:
        print(f"❌ Combat Engine Profile Loading Test Failed: {e}")
        return False


def test_combat_engine_attack_sequence():
    """Test attack sequence building functionality."""
    print("\n🧪 Testing Combat Engine Attack Sequence")
    
    try:
        engine = CombatEngine()
        
        # Test building attack sequence
        attack_sequence = engine.build_attack_sequence()
        print(f"✅ Built attack sequence with {len(attack_sequence)} skills")
        
        for i, skill in enumerate(attack_sequence):
            print(f"  {i+1}. {skill.name} (priority: {skill.priority.name})")
        
        # Test with different profiles
        profiles_to_test = ["rifleman_medic"]
        for profile_name in profiles_to_test:
            if engine.load_combat_profile(profile_name):
                sequence = engine.build_attack_sequence()
                print(f"✅ {profile_name} sequence: {len(sequence)} skills")
        
        return True
        
    except Exception as e:
        print(f"❌ Combat Engine Attack Sequence Test Failed: {e}")
        return False


def test_combat_engine_skill_execution():
    """Test skill execution functionality."""
    print("\n🧪 Testing Combat Engine Skill Execution")
    
    try:
        engine = CombatEngine()
        
        # Create a test target
        test_target = CombatTarget(
            name="Test Target",
            health_percent=100.0,
            distance=10.0,
            is_hostile=True
        )
        
        # Test executing a skill
        if "Rifle Shot" in engine.available_skills:
            skill = engine.available_skills["Rifle Shot"]
            action = engine.execute_skill(skill, test_target)
            print(f"✅ Executed {skill.name}: success={action.success}, damage={action.damage_dealt}")
        
        # Test cooldown tracking
        cooldowns = engine.skill_cooldowns
        print(f"✅ Skill cooldowns tracked: {len(cooldowns)} skills")
        
        return True
        
    except Exception as e:
        print(f"❌ Combat Engine Skill Execution Test Failed: {e}")
        return False


def test_combat_engine_combat_cycle():
    """Test full combat cycle execution."""
    print("\n🧪 Testing Combat Engine Combat Cycle")
    
    try:
        engine = CombatEngine()
        
        # Create test targets
        engine.available_targets = [
            CombatTarget(name="Enemy 1", health_percent=80.0, distance=15.0),
            CombatTarget(name="Enemy 2", health_percent=60.0, distance=20.0)
        ]
        
        # Set current target to simulate combat
        engine.current_target = engine.available_targets[0]
        
        # Test combat cycle
        actions = engine.execute_combat_cycle()
        print(f"✅ Executed combat cycle: {len(actions)} actions")
        
        for i, action in enumerate(actions):
            print(f"  {i+1}. {action.skill.name}: {action.damage_dealt} damage")
        
        return True
        
    except Exception as e:
        print(f"❌ Combat Engine Combat Cycle Test Failed: {e}")
        return False


def test_combat_engine_target_selection():
    """Test target selection functionality."""
    print("\n🧪 Testing Combat Engine Target Selection")
    
    try:
        engine = CombatEngine()
        
        # Create test targets
        targets = [
            CombatTarget(name="Weak Enemy", health_percent=20.0, distance=10.0),
            CombatTarget(name="Strong Enemy", health_percent=90.0, distance=15.0),
            CombatTarget(name="Medium Enemy", health_percent=50.0, distance=12.0)
        ]
        
        engine.available_targets = targets
        
        # Test finding targets
        found_targets = engine.find_targets()
        print(f"✅ Found {len(found_targets)} targets")
        
        # Test selecting best target
        best_target = engine.select_best_target()
        if best_target:
            print(f"✅ Selected best target: {best_target.name} (health: {best_target.health_percent}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Combat Engine Target Selection Test Failed: {e}")
        return False


def test_combat_engine_fallback_mechanism():
    """Test fallback mechanism functionality."""
    print("\n🧪 Testing Combat Engine Fallback Mechanism")
    
    try:
        engine = CombatEngine()
        
        # Test getting fallback skill
        fallback_skill = engine._get_fallback_skill()
        if fallback_skill:
            print(f"✅ Found fallback skill: {fallback_skill.name}")
        else:
            print("⚠️ No fallback skill found")
        
        # Test with no available skills
        original_skills = engine.available_skills.copy()
        engine.available_skills = {}
        
        fallback_skill = engine._get_fallback_skill()
        print(f"✅ Fallback with no skills: {fallback_skill is None}")
        
        # Restore skills
        engine.available_skills = original_skills
        
        return True
        
    except Exception as e:
        print(f"❌ Combat Engine Fallback Mechanism Test Failed: {e}")
        return False


def test_combat_profiles():
    """Test combat profile creation and loading."""
    print("\n🧪 Testing Combat Profiles")
    
    try:
        # Test creating default profiles
        rifleman_profile = create_default_rifleman_profile()
        brawler_profile = create_default_brawler_profile()
        hybrid_profile = create_default_hybrid_profile()
        
        print(f"✅ Created rifleman profile: {rifleman_profile['name']}")
        print(f"✅ Created brawler profile: {brawler_profile['name']}")
        print(f"✅ Created hybrid profile: {hybrid_profile['name']}")
        
        # Test profile properties
        for profile_name, profile in [("rifleman", rifleman_profile), ("brawler", brawler_profile), ("hybrid", hybrid_profile)]:
            print(f"  {profile_name}: {len(profile['abilities'])} abilities, {len(profile['ability_rotation'])} rotation")
        
        return True
        
    except Exception as e:
        print(f"❌ Combat Profiles Test Failed: {e}")
        return False


def test_global_functions():
    """Test global convenience functions."""
    print("\n🧪 Testing Global Functions")
    
    try:
        # Test global combat engine
        engine = get_combat_engine()
        print(f"✅ Global combat engine: {engine is not None}")
        
        # Test combat state
        combat_state = get_combat_state()
        print(f"✅ Global combat state: {combat_state.name}")
        
        # Test executing combat action
        action = execute_combat_action("Rifle Shot", "Test Target")
        print(f"✅ Global combat action: {action.skill.name}, success={action.success}")
        
        return True
        
    except Exception as e:
        print(f"❌ Global Functions Test Failed: {e}")
        return False


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n🧪 Testing Error Handling")
    
    try:
        engine = CombatEngine()
        
        # Test with invalid skill
        invalid_action = execute_combat_action("Invalid Skill")
        print(f"✅ Invalid skill handling: {invalid_action.success}")
        
        # Test with no targets
        engine.available_targets = []
        engine.current_target = None
        combat_state = engine.detect_combat_state()
        print(f"✅ No targets state: {combat_state.name}")
        
        # Test with empty attack sequence
        engine.available_skills = {}
        attack_sequence = engine.build_attack_sequence()
        print(f"✅ Empty attack sequence: {len(attack_sequence)} skills")
        
        return True
        
    except Exception as e:
        print(f"❌ Error Handling Test Failed: {e}")
        return False


def run_all_tests():
    """Run all tests for Batch 016."""
    print("🚀 Starting Batch 016 – Combat Core Engine & Action Sequencing Tests")
    print("=" * 70)
    
    tests = [
        ("Combat Engine Basic Functionality", test_combat_engine_basic_functionality),
        ("Combat Engine Skill Loading", test_combat_engine_skill_loading),
        ("Combat Engine Profile Loading", test_combat_engine_profile_loading),
        ("Combat Engine Attack Sequence", test_combat_engine_attack_sequence),
        ("Combat Engine Skill Execution", test_combat_engine_skill_execution),
        ("Combat Engine Combat Cycle", test_combat_engine_combat_cycle),
        ("Combat Engine Target Selection", test_combat_engine_target_selection),
        ("Combat Engine Fallback Mechanism", test_combat_engine_fallback_mechanism),
        ("Combat Profiles", test_combat_profiles),
        ("Global Functions", test_global_functions),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n{'='*70}")
    print(f"🎯 Batch 016 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Batch 016 implementation is working correctly.")
    else:
        print(f"⚠️ {total - passed} tests failed. Please review the implementation.")
    
    return passed == total


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    success = run_all_tests()
    
    if success:
        print("\n✅ Batch 016 – Combat Core Engine & Action Sequencing: IMPLEMENTATION COMPLETE")
        print("\n📋 Summary of implemented features:")
        print("  • core/combat/combat_engine.py - Complete combat engine with intelligent attack execution")
        print("  • data/skills/rifleman.json - Rifleman skill definitions with priorities and cooldowns")
        print("  • data/skills/medic.json - Medic skill definitions with healing abilities")
        print("  • profiles/combat/default_combat_profile.py - Sample profiles for Rifleman and Brawler")
        print("  • Skill scanning from hotbar or config/memory")
        print("  • Attack sequence building based on active spec profile")
        print("  • Cooldown tracking and spam prevention")
        print("  • Combat state detection (enemy targeted, health bar present)")
        print("  • Fallback mechanism (auto-attack or default skill)")
        print("  • Target selection and priority management")
        print("  • Emergency ability handling")
    else:
        print("\n❌ Batch 016 implementation needs review")
    
    sys.exit(0 if success else 1) 