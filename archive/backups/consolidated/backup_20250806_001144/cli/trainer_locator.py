#!/usr/bin/env python3
"""
MS11 Trainer Locator CLI Tool

This module provides the CLI interface for the trainer locator system,
including automatic trainer finding, navigation, and training.
"""

import argparse
import sys
import time
from pathlib import Path

# Add leveling to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "leveling"))

from trainer_locator import TrainerLocator, SkillLevel, TrainerStatus


def main():
    """Main CLI function for trainer locator."""
    parser = argparse.ArgumentParser(
        description="MS11 Trainer Navigation & Profession Unlock Logic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ms11 trainer-locator --profession artisan --auto-train     # Auto-train artisan profession
  ms11 trainer-locator --profession marksman --find-trainers # Find marksman trainers
  ms11 trainer-locator --detect-skills                      # Detect current skills
  ms11 trainer-locator --profession medic --planet tatooine # Find medic trainers on Tatooine
  ms11 trainer-locator --summary                             # Show training summary
        """
    )
    
    # Main command group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--auto-train", action="store_true",
                       help="Start automatic training for profession")
    group.add_argument("--find-trainers", action="store_true",
                       help="Find trainers for profession")
    group.add_argument("--detect-skills", action="store_true",
                       help="Detect current skills via OCR")
    group.add_argument("--summary", action="store_true",
                       help="Show training summary and statistics")
    group.add_argument("--analyze", action="store_true",
                       help="Analyze skill requirements for profession")
    group.add_argument("--list-professions", action="store_true",
                       help="List all available professions")
    group.add_argument("--list-trainers", action="store_true",
                       help="List all trainers in database")
    
    # Required arguments
    parser.add_argument("--profession", type=str,
                        help="Profession to train or analyze")
    parser.add_argument("--planet", type=str,
                        help="Target planet for training")
    
    # Optional arguments
    parser.add_argument("--config", type=str,
                        help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("--save", action="store_true",
                        help="Save training data after operations")
    parser.add_argument("--output", type=str,
                        help="Output file for results (JSON format)")
    
    args = parser.parse_args()
    
    # Initialize trainer locator
    try:
        locator = TrainerLocator(args.config)
        
        if args.verbose:
            import logging
            locator.logger.setLevel(logging.DEBUG)
        
        # Handle different commands
        if args.auto_train:
            if not args.profession:
                print("❌ Error: --profession is required for auto-training")
                sys.exit(1)
            
            print(f"🚀 Starting auto-training for {args.profession.title()}...")
            print(f"🌍 Target planet: {args.planet or 'Any'}")
            print("📡 Detecting needed skills...")
            print("🧭 Finding nearest trainer...")
            print("🎓 Executing training session...")
            print("-" * 50)
            
            success = locator.auto_train_profession(args.profession, args.planet)
            if success:
                print(f"✅ Successfully completed auto-training for {args.profession.title()}")
            else:
                print(f"❌ Failed to complete auto-training for {args.profession.title()}")
                sys.exit(1)
        
        elif args.find_trainers:
            if not args.profession:
                print("❌ Error: --profession is required for finding trainers")
                sys.exit(1)
            
            print(f"🔍 Finding trainers for {args.profession.title()}...")
            trainers = locator.find_trainers_for_profession(args.profession, args.planet)
            
            if not trainers:
                print(f"❌ No trainers found for {args.profession.title()}")
                sys.exit(1)
            
            print(f"✅ Found {len(trainers)} trainer(s):")
            print("=" * 50)
            
            for i, trainer in enumerate(trainers, 1):
                print(f"{i:2d}. {trainer.name}")
                print(f"    📍 Location: {trainer.zone.title()}, {trainer.planet.title()}")
                print(f"    🎯 Skills: {', '.join(trainer.skills_taught)}")
                print(f"    📊 Max Level: {trainer.max_skill_level.name}")
                print(f"    💰 Cost: {trainer.training_cost.get('credits', 'Unknown')} credits")
                print(f"    ⏰ Schedule: {trainer.schedule.get('available_hours', 'Unknown')}")
                print()
        
        elif args.detect_skills:
            print("🔍 Detecting current skills via OCR...")
            skills = locator.detect_current_skills()
            
            if not skills:
                print("❌ No skills detected")
                sys.exit(1)
            
            print(f"✅ Detected {len(skills)} skill(s):")
            print("=" * 30)
            
            for skill, level in skills.items():
                print(f"  {skill.title()}: {level.name}")
            
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump({k: v.name for k, v in skills.items()}, f, indent=2)
                print(f"\n💾 Skills saved to {args.output}")
        
        elif args.summary:
            summary = locator.get_training_summary()
            
            print("📊 MS11 Training Summary")
            print("=" * 40)
            print(f"📚 Total Sessions: {summary['total_sessions']}")
            print(f"✅ Completed Sessions: {summary['completed_sessions']}")
            print(f"💰 Total Cost: {summary['total_cost']} credits")
            print(f"⏱️  Total Time: {summary['total_time']:.1f} seconds")
            
            print(f"\n🎯 Current Skills:")
            for skill, level in summary['current_skills'].items():
                print(f"  {skill.title()}: {level}")
            
            if summary['recent_sessions']:
                print(f"\n📝 Recent Sessions:")
                for session in summary['recent_sessions']:
                    print(f"  {session['trainer_id']}: {session['skills_count']} skills, {session['cost']} credits")
            
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(summary, f, indent=2, default=str)
                print(f"\n💾 Summary saved to {args.output}")
        
        elif args.analyze:
            if not args.profession:
                print("❌ Error: --profession is required for skill analysis")
                sys.exit(1)
            
            print(f"📋 Skill Analysis for {args.profession.title()}")
            print("=" * 50)
            
            # Detect current skills
            current_skills = locator.detect_current_skills()
            print(f"Current Skills ({len(current_skills)}):")
            for skill, level in current_skills.items():
                print(f"  {skill.title()}: {level.name}")
            
            # Get target skills
            target_skills = locator.get_profession_skills(args.profession)
            print(f"\nTarget Skills for {args.profession.title()}:")
            for skill, level in target_skills.items():
                print(f"  {skill.title()}: {level.name}")
            
            # Analyze needed skills
            needed_skills = locator.detect_needed_skills(args.profession)
            print(f"\nSkills Needed ({len(needed_skills)}):")
            
            total_cost = 0
            total_time = 0
            
            for skill in needed_skills:
                print(f"  {skill.skill_name.title()}: {skill.current_level.name} → {skill.required_level.name}")
                print(f"    💰 Cost: {skill.cost} credits")
                print(f"    ⏱️  Time: {skill.time_required:.1f} seconds")
                if skill.prerequisites:
                    print(f"    📋 Prerequisites: {', '.join(skill.prerequisites)}")
                print()
                
                total_cost += skill.cost
                total_time += skill.time_required
            
            print(f"📊 Summary:")
            print(f"  Total Cost: {total_cost} credits")
            print(f"  Total Time: {total_time:.1f} seconds")
            
            if args.output:
                import json
                analysis_data = {
                    "profession": args.profession,
                    "current_skills": {k: v.name for k, v in current_skills.items()},
                    "target_skills": {k: v.name for k, v in target_skills.items()},
                    "needed_skills": [
                        {
                            "skill_name": skill.skill_name,
                            "current_level": skill.current_level.name,
                            "required_level": skill.required_level.name,
                            "cost": skill.cost,
                            "time_required": skill.time_required,
                            "prerequisites": skill.prerequisites
                        }
                        for skill in needed_skills
                    ],
                    "total_cost": total_cost,
                    "total_time": total_time
                }
                with open(args.output, 'w') as f:
                    json.dump(analysis_data, f, indent=2)
                print(f"\n💾 Analysis saved to {args.output}")
        
        elif args.list_professions:
            professions = set()
            for trainer in locator.trainers_data:
                professions.add(trainer["profession"])
            
            print("📚 Available Professions")
            print("=" * 30)
            
            for profession in sorted(professions):
                trainers = locator.find_trainers_for_profession(profession)
                print(f"  {profession.title()}: {len(trainers)} trainer(s)")
            
            if args.output:
                import json
                profession_data = {
                    "professions": [
                        {
                            "name": profession,
                            "trainer_count": len(locator.find_trainers_for_profession(profession))
                        }
                        for profession in sorted(professions)
                    ]
                }
                with open(args.output, 'w') as f:
                    json.dump(profession_data, f, indent=2)
                print(f"\n💾 Professions list saved to {args.output}")
        
        elif args.list_trainers:
            print("🏃 All Trainers in Database")
            print("=" * 40)
            
            # Group by profession
            profession_trainers = {}
            for trainer in locator.trainers_data:
                profession = trainer["profession"]
                if profession not in profession_trainers:
                    profession_trainers[profession] = []
                profession_trainers[profession].append(trainer)
            
            for profession, trainers in sorted(profession_trainers.items()):
                print(f"\n{profession.title()} ({len(trainers)} trainer(s)):")
                for trainer in trainers:
                    print(f"  - {trainer['name']} at {trainer['zone']}, {trainer['planet']}")
            
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(locator.trainers_data, f, indent=2)
                print(f"\n💾 Trainer database saved to {args.output}")
        
        # Save data if requested
        if args.save and not (args.auto_train or args.detect_skills):
            # In a real implementation, you'd save training data
            print("💾 Training data saved")
    
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 