"""Demo for Batch 063 - Smart Crafting Integration.

This demo showcases:
- Crafting mode toggle and session management
- Schematic loop execution for known recipes
- Crafting validation (inventory, resources, power)
- Profession training for Artisan, Chef, and Structures
- Support for crafting profiles and configuration
"""

import json
import time
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import crafting modules
from modules.crafting.crafting_manager import CraftingManager, get_crafting_manager
from modules.crafting.schematic_looper import SchematicLooper
from modules.crafting.crafting_validator import CraftingValidator
from modules.crafting.profession_trainer import ProfessionTrainer


def demo_crafting_mode_toggle():
    """Demo crafting mode toggle functionality."""
    print("\n🔄 DEMO: Crafting Mode Toggle")
    print("=" * 50)
    
    manager = get_crafting_manager()
    
    # Show initial state
    status = manager.get_crafting_status()
    print(f"Initial crafting mode: {'Enabled' if status['mode_enabled'] else 'Disabled'}")
    
    # Toggle crafting mode on
    print("\n📋 Enabling crafting mode...")
    result = manager.toggle_crafting_mode(True)
    print(f"Crafting mode enabled: {result}")
    
    # Show updated status
    status = manager.get_crafting_status()
    print(f"Updated crafting mode: {'Enabled' if status['mode_enabled'] else 'Disabled'}")
    
    # Toggle crafting mode off
    print("\n📋 Disabling crafting mode...")
    result = manager.toggle_crafting_mode(False)
    print(f"Crafting mode disabled: {result}")
    
    print("✅ Crafting mode toggle demo completed!")


def demo_crafting_station_detection():
    """Demo crafting station detection."""
    print("\n🔍 DEMO: Crafting Station Detection")
    print("=" * 50)
    
    manager = get_crafting_manager()
    
    # Mock station detection
    print("🔍 Scanning for crafting stations...")
    
    # Simulate detected stations
    mock_stations = [
        {
            "name": "Artisan Workbench",
            "station_type": "artisan",
            "location": "Corellia - Coronet",
            "coords": (100, 200),
            "ui_elements": ["craft", "create", "build"]
        },
        {
            "name": "Kitchen Station",
            "station_type": "chef",
            "location": "Naboo - Theed",
            "coords": (150, 250),
            "ui_elements": ["cook", "prepare", "bake"]
        },
        {
            "name": "Structure Terminal",
            "station_type": "structures",
            "location": "Tatooine - Mos Eisley",
            "coords": (200, 300),
            "ui_elements": ["construct", "build", "erect"]
        }
    ]
    
    print(f"📊 Detected {len(mock_stations)} crafting stations:")
    for i, station in enumerate(mock_stations, 1):
        print(f"  {i}. {station['name']} ({station['station_type']}) - {station['location']}")
    
    print("✅ Crafting station detection demo completed!")


def demo_crafting_validation():
    """Demo crafting validation system."""
    print("\n✅ DEMO: Crafting Validation")
    print("=" * 50)
    
    validator = CraftingValidator()
    
    # Test validation scenarios
    test_profiles = [
        {
            "name": "Basic Artisan",
            "min_inventory_space": 5,
            "min_power": 100,
            "required_resources": ["metal", "chemical"]
        },
        {
            "name": "Advanced Chef",
            "min_inventory_space": 8,
            "min_power": 150,
            "required_resources": ["vegetable", "meat", "spice", "herb"]
        },
        {
            "name": "Complex Structures",
            "min_inventory_space": 10,
            "min_power": 200,
            "required_resources": ["wood", "metal", "stone", "crystal"]
        }
    ]
    
    for profile in test_profiles:
        print(f"\n🔍 Validating profile: {profile['name']}")
        
        # Mock validation results
        validation_summary = {
            "inventory_space": {
                "current": 15,
                "required": profile["min_inventory_space"],
                "valid": True
            },
            "power_level": {
                "current": 250,
                "required": profile["min_power"],
                "valid": True
            },
            "resources": {
                "available": {
                    "metal": 10,
                    "chemical": 8,
                    "vegetable": 5,
                    "meat": 3,
                    "spice": 2,
                    "herb": 1,
                    "wood": 15,
                    "stone": 12,
                    "crystal": 2
                },
                "required": profile["required_resources"],
                "missing": []
            },
            "character_status": {
                "health": 100,
                "action": 100,
                "valid": True
            },
            "overall_valid": True
        }
        
        print(f"  📦 Inventory Space: {validation_summary['inventory_space']['current']}/{validation_summary['inventory_space']['required']} ✅")
        print(f"  ⚡ Power Level: {validation_summary['power_level']['current']}/{validation_summary['power_level']['required']} ✅")
        print(f"  🧪 Resources: {len(validation_summary['resources']['available'])} available ✅")
        print(f"  💪 Character Status: Health {validation_summary['character_status']['health']}, Action {validation_summary['character_status']['action']} ✅")
        print(f"  🎯 Overall Validation: {'PASSED' if validation_summary['overall_valid'] else 'FAILED'}")
    
    print("\n✅ Crafting validation demo completed!")


def demo_schematic_looping():
    """Demo schematic loop execution."""
    print("\n🔄 DEMO: Schematic Loop Execution")
    print("=" * 50)
    
    looper = SchematicLooper()
    
    # Test different schematic sets
    schematic_sets = [
        {
            "name": "Artisan Basics",
            "schematics": ["Basic Tool", "Survey Device"],
            "max_quantity": 5
        },
        {
            "name": "Chef Essentials",
            "schematics": ["Basic Meal", "Quality Meal"],
            "max_quantity": 8
        },
        {
            "name": "Structures Advanced",
            "schematics": ["Basic Structure", "Advanced Structure", "Complex Structure"],
            "max_quantity": 3
        }
    ]
    
    for schematic_set in schematic_sets:
        print(f"\n🔧 Running schematic loop: {schematic_set['name']}")
        
        # Simulate crafting results
        results = {
            "items_crafted": len(schematic_set["schematics"]) * 2,  # 2 items per schematic
            "schematics_completed": schematic_set["schematics"],
            "total_experience": len(schematic_set["schematics"]) * 75,  # 75 XP per schematic
            "errors": []
        }
        
        print(f"  📦 Items Crafted: {results['items_crafted']}")
        print(f"  📋 Schematics Completed: {', '.join(results['schematics_completed'])}")
        print(f"  ⭐ Total Experience: {results['total_experience']} XP")
        print(f"  ⚠️  Errors: {len(results['errors'])}")
        
        # Show crafting history
        print(f"  📊 Crafting History: {len(looper.get_crafting_history())} entries")
    
    print("\n✅ Schematic loop execution demo completed!")


def demo_profession_training():
    """Demo profession training system."""
    print("\n🎓 DEMO: Profession Training")
    print("=" * 50)
    
    trainer = ProfessionTrainer()
    
    # Test different professions
    professions = ["artisan", "chef", "structures"]
    
    for profession in professions:
        print(f"\n🎓 Training {profession.title()} profession:")
        
        # Get current skills
        current_skills = trainer.get_current_skills().get(profession, [])
        print(f"  📚 Current Skills: {len(current_skills)} learned")
        
        # Get missing skills
        missing_skills = trainer.get_missing_skills(profession)
        print(f"  📖 Missing Skills: {len(missing_skills)} to learn")
        
        # Get profession progress
        progress = trainer.get_profession_progress(profession)
        print(f"  📈 Progress: {progress['progress_percentage']:.1f}% complete")
        
        # Show training locations
        locations = trainer.training_locations.get(profession, [])
        print(f"  🏫 Training Locations: {len(locations)} available")
        
        # Simulate training session
        if missing_skills:
            print(f"  🎯 Starting training session for {profession}...")
            
            # Mock training results
            training_results = {
                "profession": profession,
                "location": f"{profession.title()} Trainer - Corellia",
                "skills_learned": min(2, len(missing_skills)),
                "skills_completed": missing_skills[:2],
                "errors": []
            }
            
            print(f"    📚 Skills Learned: {training_results['skills_learned']}")
            print(f"    ✅ Skills Completed: {', '.join(training_results['skills_completed'])}")
            print(f"    ⚠️  Errors: {len(training_results['errors'])}")
        else:
            print(f"  ✅ {profession.title()} training complete!")
    
    print("\n✅ Profession training demo completed!")


def demo_crafting_profiles():
    """Demo crafting profiles system."""
    print("\n📋 DEMO: Crafting Profiles")
    print("=" * 50)
    
    manager = get_crafting_manager()
    
    # Show available profiles
    status = manager.get_crafting_status()
    available_profiles = status["available_profiles"]
    
    print(f"📋 Available Crafting Profiles: {len(available_profiles)}")
    for profile_name in available_profiles:
        print(f"  📄 {profile_name}")
    
    # Test profile loading
    print("\n🔧 Testing profile configurations:")
    
    test_profiles = [
        {
            "name": "artisan_basic",
            "description": "Basic artisan crafting for beginners",
            "station_type": "artisan",
            "schematics": ["Basic Tool", "Survey Device"],
            "max_quantity": 5
        },
        {
            "name": "chef_basic",
            "description": "Basic chef crafting for food preparation",
            "station_type": "chef",
            "schematics": ["Basic Meal", "Quality Meal"],
            "max_quantity": 8
        },
        {
            "name": "structures_basic",
            "description": "Basic structures crafting for building",
            "station_type": "structures",
            "schematics": ["Basic Structure", "Advanced Structure"],
            "max_quantity": 3
        }
    ]
    
    for profile in test_profiles:
        print(f"\n  📄 Profile: {profile['name']}")
        print(f"    📝 Description: {profile['description']}")
        print(f"    🏭 Station Type: {profile['station_type']}")
        print(f"    📋 Schematics: {', '.join(profile['schematics'])}")
        print(f"    📦 Max Quantity: {profile['max_quantity']}")
    
    print("\n✅ Crafting profiles demo completed!")


def demo_complete_crafting_workflow():
    """Demo complete crafting workflow."""
    print("\n🛠️ DEMO: Complete Crafting Workflow")
    print("=" * 50)
    
    manager = get_crafting_manager()
    
    # Enable crafting mode
    print("🔄 Enabling crafting mode...")
    manager.toggle_crafting_mode(True)
    
    # Start crafting session
    print("🚀 Starting crafting session...")
    
    # Mock session setup
    session_data = {
        "profile_name": "artisan_basic",
        "station": {
            "name": "Artisan Workbench",
            "station_type": "artisan",
            "location": "Corellia - Coronet",
            "coords": (100, 200)
        },
        "start_time": time.time(),
        "session_id": f"craft_{int(time.time())}"
    }
    
    print(f"  📋 Profile: {session_data['profile_name']}")
    print(f"  🏭 Station: {session_data['station']['name']}")
    print(f"  📍 Location: {session_data['station']['location']}")
    print(f"  🆔 Session ID: {session_data['session_id']}")
    
    # Run crafting loop
    print("\n🔄 Running crafting loop...")
    
    # Simulate crafting results
    crafting_results = {
        "session_id": session_data["session_id"],
        "profile_name": session_data["profile_name"],
        "station": session_data["station"]["name"],
        "items_crafted": 8,
        "schematics_completed": ["Basic Tool", "Survey Device"],
        "total_experience": 200,
        "errors": []
    }
    
    print(f"  📦 Items Crafted: {crafting_results['items_crafted']}")
    print(f"  📋 Schematics Completed: {', '.join(crafting_results['schematics_completed'])}")
    print(f"  ⭐ Total Experience: {crafting_results['total_experience']} XP")
    print(f"  ⚠️  Errors: {len(crafting_results['errors'])}")
    
    # Stop session
    print("\n🛑 Stopping crafting session...")
    
    session_summary = {
        "session_id": session_data["session_id"],
        "profile_name": session_data["profile_name"],
        "station": session_data["station"]["name"],
        "duration_seconds": 1800,  # 30 minutes
        "items_crafted": 8,
        "success": True
    }
    
    print(f"  ⏱️  Duration: {session_summary['duration_seconds']} seconds")
    print(f"  📦 Total Items Crafted: {session_summary['items_crafted']}")
    print(f"  ✅ Session Status: {'SUCCESS' if session_summary['success'] else 'FAILED'}")
    
    # Disable crafting mode
    print("\n🔄 Disabling crafting mode...")
    manager.toggle_crafting_mode(False)
    
    print("\n✅ Complete crafting workflow demo completed!")


def demo_crafting_statistics():
    """Demo crafting statistics and reporting."""
    print("\n📊 DEMO: Crafting Statistics")
    print("=" * 50)
    
    looper = SchematicLooper()
    
    # Simulate crafting history
    print("📈 Generating crafting statistics...")
    
    # Mock crafting history data
    crafting_stats = {
        "total_sessions": 15,
        "total_items_crafted": 127,
        "total_experience_gained": 8500,
        "success_rate": 0.92,
        "average_session_duration": 1800,
        "profession_breakdown": {
            "artisan": {
                "sessions": 8,
                "items_crafted": 65,
                "experience": 4200,
                "success_rate": 0.94
            },
            "chef": {
                "sessions": 4,
                "items_crafted": 42,
                "experience": 2800,
                "success_rate": 0.89
            },
            "structures": {
                "sessions": 3,
                "items_crafted": 20,
                "experience": 1500,
                "success_rate": 0.87
            }
        },
        "top_schematics": [
            {"name": "Basic Tool", "crafted": 25, "success_rate": 0.96},
            {"name": "Basic Meal", "crafted": 18, "success_rate": 0.89},
            {"name": "Survey Device", "crafted": 15, "success_rate": 0.93},
            {"name": "Quality Meal", "crafted": 12, "success_rate": 0.85},
            {"name": "Basic Structure", "crafted": 8, "success_rate": 0.88}
        ]
    }
    
    print(f"📊 Overall Statistics:")
    print(f"  🎯 Total Sessions: {crafting_stats['total_sessions']}")
    print(f"  📦 Total Items Crafted: {crafting_stats['total_items_crafted']}")
    print(f"  ⭐ Total Experience: {crafting_stats['total_experience_gained']} XP")
    print(f"  📈 Success Rate: {crafting_stats['success_rate']:.1%}")
    print(f"  ⏱️  Average Session Duration: {crafting_stats['average_session_duration']} seconds")
    
    print(f"\n🏭 Profession Breakdown:")
    for profession, stats in crafting_stats["profession_breakdown"].items():
        print(f"  {profession.title()}:")
        print(f"    📊 Sessions: {stats['sessions']}")
        print(f"    📦 Items: {stats['items_crafted']}")
        print(f"    ⭐ Experience: {stats['experience']} XP")
        print(f"    📈 Success Rate: {stats['success_rate']:.1%}")
    
    print(f"\n🏆 Top Schematics:")
    for i, schematic in enumerate(crafting_stats["top_schematics"], 1):
        print(f"  {i}. {schematic['name']}: {schematic['crafted']} crafted ({schematic['success_rate']:.1%} success)")
    
    print("\n✅ Crafting statistics demo completed!")


def main():
    """Run the complete crafting demo."""
    print("🛠️ BATCH 063 - SMART CRAFTING INTEGRATION DEMO")
    print("=" * 60)
    print("This demo showcases the complete smart crafting system")
    print("including mode toggle, validation, schematic looping,")
    print("profession training, and comprehensive statistics.")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_crafting_mode_toggle()
        demo_crafting_station_detection()
        demo_crafting_validation()
        demo_schematic_looping()
        demo_profession_training()
        demo_crafting_profiles()
        demo_complete_crafting_workflow()
        demo_crafting_statistics()
        
        print("\n" + "=" * 60)
        print("🎉 ALL CRAFTING DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n✅ Features Demonstrated:")
        print("  🔄 Crafting mode toggle functionality")
        print("  🔍 Crafting station detection")
        print("  ✅ Inventory, resource, and power validation")
        print("  🔄 Schematic loop execution")
        print("  🎓 Profession training (Artisan, Chef, Structures)")
        print("  📋 Crafting profiles and configuration")
        print("  🛠️ Complete crafting workflow")
        print("  📊 Statistics and reporting")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)


if __name__ == "__main__":
    main() 