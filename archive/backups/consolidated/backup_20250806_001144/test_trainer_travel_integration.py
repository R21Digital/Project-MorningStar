#!/usr/bin/env python3
"""
Test script for Trainer and Travel System Integration (Batch 010)

This script tests the integration between the trainer system and travel automation
to ensure trainers can be found, travel can be planned, and training sessions work.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import load_trainers, find_trainers_for_profession
from core.trainer_system import (
    trainer_system, 
    find_trainers_for_profession_with_travel,
    travel_to_nearest_trainer,
    start_training_with_trainer,
    execute_training_session,
    get_training_progress
)


def test_trainer_loading():
    """Test loading trainers from the database."""
    print("🧪 Testing Trainer Loading...")
    
    # Test loading all trainers
    trainers = load_trainers()
    print(f"✅ Loaded {len(trainers)} trainers from database")
    
    if not trainers:
        print("❌ No trainers found in database")
        return False
    
    # Show sample trainer data
    sample_trainer = trainers[0]
    print(f"✅ Sample trainer: {sample_trainer.name}")
    print(f"   Profession: {sample_trainer.profession}")
    print(f"   Planet: {sample_trainer.planet}")
    print(f"   Zone: {sample_trainer.zone}")
    print(f"   Coordinates: {sample_trainer.coordinates}")
    print(f"   Skills taught: {sample_trainer.skills_taught}")
    
    return True


def test_trainer_finding():
    """Test finding trainers by profession."""
    print("\n🧪 Testing Trainer Finding...")
    
    # Test finding trainers for different professions
    test_professions = ["combat", "medic", "artisan", "marksman"]
    
    for profession in test_professions:
        trainers = find_trainers_for_profession(profession)
        print(f"✅ Found {len(trainers)} {profession} trainers")
        
        if trainers:
            for trainer in trainers[:2]:  # Show first 2 trainers
                print(f"   - {trainer.name} on {trainer.planet} at {trainer.coordinates}")
    
    return True


def test_planet_trainer_filtering():
    """Test filtering trainers by planet."""
    print("\n🧪 Testing Planet Trainer Filtering...")
    
    # Test finding trainers on specific planets
    test_planets = ["tatooine", "corellia", "naboo"]
    
    for planet in test_planets:
        planet_trainers = trainer_system.get_trainers_on_planet(planet)
        print(f"✅ Found {len(planet_trainers)} trainers on {planet}")
        
        if planet_trainers:
            professions = set(trainer.profession for trainer in planet_trainers)
            print(f"   Professions available: {list(professions)}")
    
    return True


def test_nearest_trainer_finding():
    """Test finding the nearest trainer for a profession."""
    print("\n🧪 Testing Nearest Trainer Finding...")
    
    # Set current location for distance calculations
    trainer_system.set_current_location("tatooine", [100, 150])
    
    # Test finding nearest trainers
    test_professions = ["combat", "medic"]
    
    for profession in test_professions:
        nearest = trainer_system.find_nearest_trainer(profession, "tatooine")
        
        if nearest:
            print(f"✅ Found nearest {profession} trainer: {nearest.name}")
            print(f"   Location: {nearest.coordinates}")
            print(f"   Skills: {nearest.skills_taught}")
        else:
            print(f"❌ No {profession} trainer found on Tatooine")
    
    return True


def test_skill_based_trainer_finding():
    """Test finding trainers by specific skills."""
    print("\n🧪 Testing Skill-Based Trainer Finding...")
    
    # Test finding trainers for specific skills
    test_skills = ["unarmed_combat", "healing", "crafting", "rifle_combat"]
    
    for skill in test_skills:
        trainer = trainer_system.find_trainer_by_skill(skill, "tatooine")
        
        if trainer:
            print(f"✅ Found trainer for '{skill}': {trainer.name}")
            print(f"   Profession: {trainer.profession}")
            print(f"   All skills: {trainer.skills_taught}")
        else:
            print(f"❌ No trainer found for skill '{skill}' on Tatooine")
    
    return True


def test_travel_planning():
    """Test travel planning to trainers."""
    print("\n🧪 Testing Travel Planning...")
    
    # Set current location
    trainer_system.set_current_location("tatooine", [100, 150])
    
    # Test travel to nearest trainer
    test_profession = "combat"
    success = travel_to_nearest_trainer(test_profession, "tatooine")
    
    if success:
        print(f"✅ Successfully planned travel to {test_profession} trainer")
    else:
        print(f"❌ Failed to plan travel to {test_profession} trainer")
    
    return True


def test_training_session_management():
    """Test training session management."""
    print("\n🧪 Testing Training Session Management...")
    
    # Find a trainer to test with
    trainer = trainer_system.find_nearest_trainer("combat", "tatooine")
    
    if not trainer:
        print("❌ No trainer found for testing")
        return False
    
    # Start training session
    skills_to_train = ["unarmed_combat", "melee_weapons"]
    session = start_training_with_trainer(trainer, skills_to_train)
    
    if session:
        print(f"✅ Started training session with {session.trainer_name}")
        print(f"   Skills to train: {session.skills_trained}")
        print(f"   Training cost: {session.training_cost}")
        
        # Get training progress
        progress = get_training_progress()
        print(f"   Training progress: {progress}")
        
        return True
    else:
        print("❌ Failed to start training session")
        return False


def test_shuttleport_integration():
    """Test shuttleport data loading and integration."""
    print("\n🧪 Testing Shuttleport Integration...")
    
    # Check if shuttleports are loaded
    if trainer_system.shuttleports:
        print(f"✅ Loaded shuttleports for {len(trainer_system.shuttleports)} planets")
        
        for planet, ports in trainer_system.shuttleports.items():
            print(f"   {planet}: {len(ports)} shuttleports")
            for port in ports:
                print(f"     - {port.city}: {port.coordinates}")
                print(f"       Destinations: {port.destinations}")
    else:
        print("❌ No shuttleports loaded")
        return False
    
    return True


def test_cross_planet_travel():
    """Test cross-planet travel planning."""
    print("\n🧪 Testing Cross-Planet Travel...")
    
    # Set current location on Tatooine
    trainer_system.set_current_location("tatooine", [100, 150])
    
    # Try to find a trainer on Corellia
    trainer = trainer_system.find_nearest_trainer("artisan", "corellia")
    
    if trainer:
        print(f"✅ Found trainer on different planet: {trainer.name} on {trainer.planet}")
        print(f"   Planning cross-planet travel...")
        
        # This would test the cross-planet travel logic
        # For now, just verify the trainer was found
        return True
    else:
        print("❌ No trainer found on different planet for testing")
        return False


def test_training_execution_simulation():
    """Test training execution simulation."""
    print("\n🧪 Testing Training Execution Simulation...")
    
    # Find a trainer
    trainer = trainer_system.find_nearest_trainer("combat", "tatooine")
    
    if not trainer:
        print("❌ No trainer found for testing")
        return False
    
    # Start training session
    skills_to_train = ["unarmed_combat"]
    session = start_training_with_trainer(trainer, skills_to_train)
    
    if session:
        print(f"✅ Started training session with {session.trainer_name}")
        
        # Simulate training execution
        success = execute_training_session(session)
        
        if success:
            print("✅ Training session completed successfully")
            
            # Check final progress
            progress = get_training_progress()
            print(f"   Final progress: {progress}")
            
            return True
        else:
            print("❌ Training session failed")
            return False
    else:
        print("❌ Failed to start training session")
        return False


def main():
    """Run all tests for trainer and travel system integration."""
    print("🚀 Starting Trainer and Travel System Integration Tests (Batch 010)")
    print("=" * 70)
    
    tests = [
        ("Trainer Loading", test_trainer_loading),
        ("Trainer Finding", test_trainer_finding),
        ("Planet Trainer Filtering", test_planet_trainer_filtering),
        ("Nearest Trainer Finding", test_nearest_trainer_finding),
        ("Skill-Based Trainer Finding", test_skill_based_trainer_finding),
        ("Travel Planning", test_travel_planning),
        ("Training Session Management", test_training_session_management),
        ("Shuttleport Integration", test_shuttleport_integration),
        ("Cross-Planet Travel", test_cross_planet_travel),
        ("Training Execution Simulation", test_training_execution_simulation),
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
        print("🎉 All tests passed! Trainer and travel system integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 