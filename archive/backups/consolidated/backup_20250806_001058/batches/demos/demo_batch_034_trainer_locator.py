#!/usr/bin/env python3
"""
Demo script for Batch 034 - Trainer Navigation & Profession Unlock Logic

This script demonstrates the trainer locator functionality including:
- Skill detection and analysis
- Trainer lookup and navigation
- OCR-based trainer detection
- Training session execution
- Multi-profession support
"""

import sys
import time
from pathlib import Path

# Add leveling to path for imports
sys.path.insert(0, str(Path(__file__).parent / "leveling"))

from trainer_locator import TrainerLocator, SkillLevel, TrainerStatus
from datetime import datetime


def demo_trainer_locator():
    """Demonstrate the trainer locator functionality."""
    print("🚀 Batch 034 - Trainer Navigation & Profession Unlock Logic")
    print("=" * 60)
    
    # Initialize trainer locator
    print("📚 Initializing Trainer Locator...")
    locator = TrainerLocator()
    
    # Show loaded trainer data
    print(f"\n📊 Loaded {len(locator.trainers_data)} trainers from database")
    
    # Demonstrate skill detection
    print("\n🔍 Skill Detection Demo:")
    skills = locator.detect_current_skills()
    print(f"   Detected {len(skills)} current skills:")
    for skill, level in skills.items():
        print(f"     {skill}: {level.name}")
    
    # Demonstrate profession skill requirements
    print("\n🎯 Profession Skill Requirements:")
    professions = ["artisan", "marksman", "combat", "medic"]
    
    for profession in professions:
        target_skills = locator.get_profession_skills(profession)
        print(f"\n   {profession.title()} Skills:")
        for skill, level in target_skills.items():
            print(f"     {skill}: {level.name}")
    
    # Demonstrate needed skills detection
    print("\n📋 Needed Skills Detection:")
    for profession in professions:
        needed_skills = locator.detect_needed_skills(profession)
        print(f"\n   {profession.title()} - Skills Needed: {len(needed_skills)}")
        for skill in needed_skills:
            print(f"     {skill.skill_name}: {skill.current_level.name} → {skill.required_level.name}")
            print(f"       Cost: {skill.cost} credits, Time: {skill.time_required:.1f}s")
    
    # Demonstrate trainer finding
    print("\n🏃 Trainer Finding Demo:")
    for profession in professions:
        trainers = locator.find_trainers_for_profession(profession)
        print(f"\n   {profession.title()} Trainers ({len(trainers)} found):")
        for trainer in trainers:
            print(f"     {trainer.name} at {trainer.zone}, {trainer.planet}")
            print(f"       Skills: {', '.join(trainer.skills_taught)}")
            print(f"       Max Level: {trainer.max_skill_level.name}")
            print(f"       Cost: {trainer.training_cost.get('credits', 'Unknown')} credits")
    
    # Demonstrate nearest trainer finding
    print("\n📍 Nearest Trainer Finding:")
    for profession in professions:
        trainer = locator.find_nearest_trainer(profession)
        if trainer:
            print(f"   {profession.title()}: {trainer.name} at {trainer.zone}, {trainer.planet}")
        else:
            print(f"   {profession.title()}: No trainer found")
    
    # Demonstrate navigation simulation
    print("\n🧭 Navigation Simulation:")
    test_trainer = locator.find_nearest_trainer("artisan")
    if test_trainer:
        print(f"   Navigating to {test_trainer.name} at {test_trainer.zone}, {test_trainer.planet}")
        success = locator.navigate_to_trainer(test_trainer)
        print(f"   Navigation result: {'✅ Success' if success else '❌ Failed'}")
    
    # Demonstrate trainer detection
    print("\n👁️  Trainer Detection Demo:")
    if test_trainer:
        print(f"   Detecting trainer: {test_trainer.name}")
        detected = locator.detect_trainer_npc(test_trainer)
        print(f"   Detection result: {'✅ Detected' if detected else '❌ Not found'}")
    
    # Demonstrate training session
    print("\n🎓 Training Session Demo:")
    if test_trainer:
        needed_skills = locator.detect_needed_skills("artisan")
        if needed_skills:
            print(f"   Starting training session with {test_trainer.name}")
            print(f"   Skills to learn: {len(needed_skills)}")
            
            # Create a mock training session
            total_cost = sum(skill.cost for skill in needed_skills)
            total_time = sum(skill.time_required for skill in needed_skills)
            
            print(f"   Total cost: {total_cost} credits")
            print(f"   Estimated time: {total_time:.1f} seconds")
            
            # Simulate training execution
            success = locator.execute_training(test_trainer, needed_skills[:1])  # Train first skill only
            print(f"   Training result: {'✅ Completed' if success else '❌ Failed'}")
    
    # Demonstrate auto-training
    print("\n🤖 Auto-Training Demo:")
    for profession in ["artisan", "marksman"]:
        print(f"\n   Auto-training {profession.title()}:")
        success = locator.auto_train_profession(profession)
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Show training summary
    print("\n📊 Training Summary:")
    summary = locator.get_training_summary()
    print(f"   Total Sessions: {summary['total_sessions']}")
    print(f"   Completed Sessions: {summary['completed_sessions']}")
    print(f"   Total Cost: {summary['total_cost']} credits")
    print(f"   Total Time: {summary['total_time']:.1f} seconds")
    
    print(f"   Current Skills:")
    for skill, level in summary['current_skills'].items():
        print(f"     {skill}: {level}")
    
    if summary['recent_sessions']:
        print(f"   Recent Sessions:")
        for session in summary['recent_sessions']:
            print(f"     {session['trainer_id']}: {session['skills_count']} skills, {session['cost']} credits")


def demo_skill_analysis():
    """Demonstrate skill analysis and requirements."""
    print("\n🔍 Skill Analysis Demo:")
    print("-" * 40)
    
    locator = TrainerLocator()
    
    # Test different skill scenarios
    test_scenarios = [
        ("artisan", {"crafting": SkillLevel.NOVICE, "engineering": SkillLevel.NONE}),
        ("marksman", {"ranged_weapons": SkillLevel.APPRENTICE, "tactics": SkillLevel.NOVICE}),
        ("medic", {"healing": SkillLevel.JOURNEYMAN, "diagnosis": SkillLevel.APPRENTICE}),
        ("combat", {"unarmed_combat": SkillLevel.EXPERT, "melee_weapons": SkillLevel.JOURNEYMAN})
    ]
    
    for profession, current_skills in test_scenarios:
        print(f"\n📋 {profession.title()} Analysis:")
        print(f"   Current Skills: {current_skills}")
        
        # Set current skills for testing
        locator.current_skills = current_skills
        
        # Get needed skills
        needed_skills = locator.detect_needed_skills(profession)
        print(f"   Skills Needed: {len(needed_skills)}")
        
        for skill in needed_skills:
            print(f"     {skill.skill_name}: {skill.current_level.name} → {skill.required_level.name}")
            print(f"       Cost: {skill.cost} credits, Time: {skill.time_required:.1f}s")
            if skill.prerequisites:
                print(f"       Prerequisites: {', '.join(skill.prerequisites)}")


def demo_trainer_database():
    """Demonstrate trainer database functionality."""
    print("\n🗄️  Trainer Database Demo:")
    print("-" * 40)
    
    locator = TrainerLocator()
    
    # Show all available professions
    professions = set()
    for trainer in locator.trainers_data:
        professions.add(trainer["profession"])
    
    print(f"Available Professions: {', '.join(sorted(professions))}")
    
    # Show trainers by planet
    planets = {}
    for trainer in locator.trainers_data:
        planet = trainer["planet"]
        if planet not in planets:
            planets[planet] = []
        planets[planet].append(trainer)
    
    print(f"\nTrainers by Planet:")
    for planet, trainers in planets.items():
        print(f"   {planet.title()}: {len(trainers)} trainers")
        for trainer in trainers[:3]:  # Show first 3
            print(f"     - {trainer['name']} ({trainer['profession']})")
        if len(trainers) > 3:
            print(f"     ... and {len(trainers) - 3} more")
    
    # Show trainer statistics
    print(f"\nTrainer Statistics:")
    total_trainers = len(locator.trainers_data)
    profession_counts = {}
    planet_counts = {}
    
    for trainer in locator.trainers_data:
        profession = trainer["profession"]
        planet = trainer["planet"]
        
        profession_counts[profession] = profession_counts.get(profession, 0) + 1
        planet_counts[planet] = planet_counts.get(planet, 0) + 1
    
    print(f"   Total Trainers: {total_trainers}")
    print(f"   Professions: {len(profession_counts)}")
    print(f"   Planets: {len(planet_counts)}")
    
    print(f"\nTop Professions:")
    sorted_professions = sorted(profession_counts.items(), key=lambda x: x[1], reverse=True)
    for profession, count in sorted_professions[:5]:
        print(f"   {profession.title()}: {count} trainers")
    
    print(f"\nTop Planets:")
    sorted_planets = sorted(planet_counts.items(), key=lambda x: x[1], reverse=True)
    for planet, count in sorted_planets[:5]:
        print(f"   {planet.title()}: {count} trainers")


if __name__ == "__main__":
    print("🎯 Batch 034 - Trainer Navigation & Profession Unlock Logic")
    print("=" * 70)
    
    # Run main demo
    demo_trainer_locator()
    
    # Run skill analysis demo
    demo_skill_analysis()
    
    # Run trainer database demo
    demo_trainer_database()
    
    print("\n🎉 All demonstrations completed successfully!")
    print("   The trainer locator system is ready for use.") 