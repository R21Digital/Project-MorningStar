#!/usr/bin/env python3
"""
Demo script for Batch 068 - Space Quest Support Module (Extended Phase)

This demo showcases:
1. Enhanced Hyperspace Pathing Simulation
2. Extended Mission Locations (Corellia Starport, Naboo Orbital, and more)
3. Advanced Tiered Ship Upgrades
4. AI Piloting Foundation with Future Integration

Features demonstrated:
- Advanced navigation between multiple space zones
- Comprehensive mission location management
- Advanced ship progression system with multiple tiers
- AI piloting with sophisticated decision-making
- Integrated space quest support system
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path
from typing import Dict, Any

# Import the space quest support modules
from modules.space_quest_support import (
    SpaceQuestSupport,
    HyperspacePathingSimulator,
    MissionLocationManager,
    ShipUpgradeManager,
    AIPilotingFoundation,
    PilotSkill
)


def create_mock_player_stats() -> Dict[str, Any]:
    """Create mock player statistics for testing."""
    return {
        "level": 25,
        "credits": 15000,
        "reputation": 500,
        "combat_rating": 5,
        "escort_rating": 4,
        "diplomatic_rating": 3,
        "exploration_rating": 4,
        "stealth_rating": 3,
        "faction_standing": "neutral"
    }


def demo_enhanced_hyperspace_pathing():
    """Demonstrate enhanced hyperspace pathing simulation."""
    print("\n" + "="*60)
    print("🚀 ENHANCED HYPESPACE PATHING SIMULATION")
    print("="*60)
    
    # Initialize hyperspace pathing
    hyperspace = HyperspacePathingSimulator()
    
    # Show available destinations from Corellia Starport
    print("\n📍 Available destinations from Corellia Starport:")
    destinations = hyperspace.get_available_destinations("Corellia Starport")
    for dest in destinations:
        print(f"  • {dest['name']} ({dest['zone']})")
        print(f"    Distance: {dest['distance']:.1f}, Time: {dest['travel_time']:.1f} min")
        print(f"    Fuel: {dest['fuel_cost']:.1f}, Risk: {dest['risk_level']:.2f}")
    
    # Calculate different route types
    print("\n🗺️  Route Calculation Examples:")
    from modules.space_quest_support.hyperspace_pathing import NavigationRequest, HyperspaceRouteType
    
    route_types = [
        ("SAFE", HyperspaceRouteType.SAFE, "Low risk, longer route"),
        ("FAST", HyperspaceRouteType.FAST, "High speed, moderate risk"),
        ("DIRECT", HyperspaceRouteType.DIRECT, "Shortest path, variable risk"),
        ("STEALTH", HyperspaceRouteType.STEALTH, "Covert route, high skill required")
    ]
    
    for route_name, route_type, description in route_types:
        print(f"\n  {route_name} Route to Naboo Orbital:")
        print(f"    {description}")
        
        request = NavigationRequest(
            start_location="Corellia Starport",
            destination="Naboo Orbital",
            route_type=route_type,
            ship_class="Advanced Fighter",
            fuel_capacity=150.0,
            max_risk_tolerance=0.5
        )
        
        result = hyperspace.calculate_route(request)
        if result:
            print(f"    ✅ Route found!")
            print(f"    Distance: {result.total_distance:.1f}, Time: {result.total_time:.1f} min")
            print(f"    Fuel Cost: {result.total_fuel_cost:.1f}, Risk: {result.route.risk_level:.2f}")
            print(f"    Waypoints: {' → '.join(result.waypoints)}")
        else:
            print(f"    ❌ No route found")
    
    # Demonstrate multi-hop navigation
    print("\n🌌 Multi-hop Navigation Example:")
    request = NavigationRequest(
        start_location="Corellia Starport",
        destination="Mustafar Mining Outpost",
        route_type=HyperspaceRouteType.SAFE,
        ship_class="Elite Fighter",
        fuel_capacity=200.0,
        max_risk_tolerance=0.4
    )
    
    result = hyperspace.calculate_route(request)
    if result:
        print(f"  ✅ Complex route calculated!")
        print(f"  Total Distance: {result.total_distance:.1f}")
        print(f"  Total Time: {result.total_time:.1f} minutes")
        print(f"  Total Fuel Cost: {result.total_fuel_cost:.1f}")
        print(f"  Waypoints: {' → '.join(result.waypoints)}")
        print(f"  Warnings: {', '.join(result.warnings) if result.warnings else 'None'}")
        
        # Start navigation
        hyperspace.start_navigation(result)
        print(f"  🚀 Navigation started! Estimated arrival: {result.estimated_arrival}")
    else:
        print("  ❌ No route found")


def demo_extended_mission_locations():
    """Demonstrate extended mission location management."""
    print("\n" + "="*60)
    print("🏛️  EXTENDED MISSION LOCATIONS")
    print("="*60)
    
    # Initialize mission locations
    locations = MissionLocationManager()
    
    # Show all available locations
    print("\n📍 Available Mission Locations:")
    all_locations = locations.get_available_locations()
    for location in all_locations:
        print(f"  • {location.name} ({location.location_type.value})")
        print(f"    Zone: {location.zone}, Security: {location.security_level:.2f}")
        print(f"    Missions: {', '.join(location.available_missions)}")
        print(f"    Givers: {', '.join(location.mission_givers)}")
    
    # Demonstrate location-specific interactions
    print("\n🎯 Location-Specific Interactions:")
    
    # Corellia Starport
    print("\n  Corellia Starport:")
    locations.visit_location("Corellia Starport")
    givers = locations.get_mission_givers_at_location("Corellia Starport")
    for giver in givers:
        print(f"    • {giver.name} ({giver.faction}) - Rep: {giver.reputation_required}")
        interaction = locations.interact_with_giver(giver.name)
        if interaction.get("available_missions"):
            print(f"      Available missions: {len(interaction['available_missions'])}")
    
    # Naboo Orbital
    print("\n  Naboo Orbital:")
    locations.visit_location("Naboo Orbital")
    givers = locations.get_mission_givers_at_location("Naboo Orbital")
    for giver in givers:
        print(f"    • {giver.name} ({giver.faction}) - Rep: {giver.reputation_required}")
        interaction = locations.interact_with_giver(giver.name)
        if interaction.get("available_missions"):
            print(f"      Available missions: {len(interaction['available_missions'])}")
    
    # Tatooine Spaceport (high-risk location)
    print("\n  Tatooine Spaceport (High-Risk):")
    locations.visit_location("Tatooine Spaceport")
    givers = locations.get_mission_givers_at_location("Tatooine Spaceport")
    for giver in givers:
        print(f"    • {giver.name} ({giver.faction}) - Rep: {giver.reputation_required}")
        interaction = locations.interact_with_giver(giver.name)
        if interaction.get("available_missions"):
            print(f"      Available missions: {len(interaction['available_missions'])}")
    
    # Imperial Fleet Command (faction-restricted)
    print("\n  Imperial Fleet Command (Faction-Restricted):")
    locations.visit_location("Imperial Fleet Command")
    givers = locations.get_mission_givers_at_location("Imperial Fleet Command")
    for giver in givers:
        print(f"    • {giver.name} ({giver.faction}) - Rep: {giver.reputation_required}")
        interaction = locations.interact_with_giver(giver.name)
        if interaction.get("available_missions"):
            print(f"      Available missions: {len(interaction['available_missions'])}")


def demo_advanced_ship_upgrades():
    """Demonstrate advanced tiered ship upgrades."""
    print("\n" + "="*60)
    print("🚀 ADVANCED TIERED SHIP UPGRADES")
    print("="*60)
    
    # Initialize ship upgrades
    upgrades = ShipUpgradeManager()
    
    # Show all available ships
    print("\n🛸 Available Ship Classes:")
    available_ships = upgrades.get_available_ships()
    for ship in available_ships:
        print(f"  • {ship.name} (Tier {ship.base_tier.value})")
        print(f"    Type: {ship.ship_type}, Max Tier: {ship.max_tier.value}")
        print(f"    Base Stats: Damage {ship.base_stats['damage']:.0f}, Speed {ship.base_stats['speed']:.0f}")
        print(f"    Upgrade Slots: {sum(ship.upgrade_slots.values())} total")
        print(f"    Unlocked: {ship.is_unlocked}")
    
    # Demonstrate ship unlocking
    print("\n🔓 Ship Unlocking Process:")
    player_stats = create_mock_player_stats()
    
    ships_to_unlock = ["Advanced Fighter", "Interceptor", "Elite Fighter"]
    for ship_name in ships_to_unlock:
        result = upgrades.unlock_ship(ship_name, player_stats)
        if result:
            print(f"  ✅ Unlocked {ship_name}")
        else:
            print(f"  ❌ Failed to unlock {ship_name}")
    
    # Show available upgrades for Basic Fighter
    print("\n🔧 Available Upgrades for Basic Fighter:")
    available_upgrades = upgrades.get_available_upgrades("Basic Fighter")
    for upgrade in available_upgrades:
        print(f"  • {upgrade.name} ({upgrade.rarity.value})")
        print(f"    Type: {upgrade.upgrade_type.value}, Tier: {upgrade.tier.value}")
        print(f"    Stats: {upgrade.stats}")
        print(f"    Cost: {upgrade.cost['credits']} credits")
    
    # Demonstrate upgrade installation
    print("\n⚙️  Upgrade Installation:")
    upgrade_results = [
        ("Basic Fighter", "basic_weapon_001", "weapons_1"),
        ("Basic Fighter", "basic_shield_001", "shields_1"),
        ("Basic Fighter", "basic_engine_001", "engines_1")
    ]
    
    for ship_name, upgrade_id, slot_id in upgrade_results:
        result = upgrades.install_upgrade(ship_name, upgrade_id, slot_id)
        if result.get("success"):
            print(f"  ✅ Installed {upgrade_id} on {ship_name}")
            print(f"    New stats: {result['new_stats']}")
        else:
            print(f"  ❌ Failed to install {upgrade_id} on {ship_name}")
    
    # Show ship statistics
    print("\n📊 Ship Statistics:")
    ship_stats = upgrades.get_ship_stats("Basic Fighter")
    print(f"  Basic Fighter Stats:")
    for stat, value in ship_stats.items():
        if isinstance(value, (int, float)):
            print(f"    {stat}: {value:.1f}")
        else:
            print(f"    {stat}: {value}")


def demo_ai_piloting_foundation():
    """Demonstrate AI piloting foundation."""
    print("\n" + "="*60)
    print("🤖 AI PILOTING FOUNDATION")
    print("="*60)
    
    # Initialize AI piloting
    ai_piloting = AIPilotingFoundation()
    
    # Show available pilots
    print("\n👨‍✈️  Available AI Pilots:")
    available_pilots = ai_piloting.get_available_pilots()
    for pilot in available_pilots:
        print(f"  • {pilot.name} ({pilot.pilot_id})")
        print(f"    Behavior: {pilot.behavior.value}")
        print(f"    Experience: {pilot.experience}")
        nav_skill = pilot.skill_levels.get(PilotSkill.NAVIGATION, 0)
        combat_skill = pilot.skill_levels.get(PilotSkill.COMBAT, 0)
        print(f"    Skills: Navigation {nav_skill}, Combat {combat_skill}")
        print(f"    Active: {pilot.is_active}")
    
    # Activate pilots
    print("\n🚀 Pilot Activation:")
    pilots_to_activate = ["nav_specialist_001", "combat_specialist_001", "stealth_specialist_001"]
    for pilot_id in pilots_to_activate:
        result = ai_piloting.activate_pilot(pilot_id)
        if result:
            print(f"  ✅ Activated {pilot_id}")
        else:
            print(f"  ❌ Failed to activate {pilot_id}")
    
    # Show active pilots
    print("\n🎯 Active Pilots:")
    active_pilots = ai_piloting.get_active_pilots()
    for pilot in active_pilots:
        print(f"  • {pilot.name} - {pilot.behavior.value} behavior")
    
    # Demonstrate mission assignment
    print("\n📋 Mission Assignment:")
    mission_data = {
        "mission_type": "patrol",
        "ship_name": "Advanced Fighter",
        "destination": "Naboo Orbital",
        "objectives": ["Patrol the route", "Eliminate threats", "Report findings"],
        "constraints": {"time_limit": 60.0, "fuel_limit": 50.0},
        "priority": 5,
        "estimated_duration": 45.0
    }
    
    # Assign mission to navigation specialist
    mission_id = ai_piloting.assign_mission("nav_specialist_001", mission_data)
    if mission_id:
        print(f"  ✅ Assigned patrol mission to Navigator Prime")
        print(f"    Mission ID: {mission_id}")
        
        # Start mission
        ai_piloting.start_mission(mission_id)
        print(f"  🚀 Mission started!")
        
        # Simulate mission progress
        print("\n📈 Mission Progress Simulation:")
        progress_data = {
            "current_waypoint": "Republic Naval Base",
            "fuel_remaining": 35.0,
            "damage_taken": 0.1,
            "threats_encountered": 2,
            "objectives_completed": 1
        }
        
        progress = ai_piloting.update_mission_progress(mission_id, progress_data)
        print(f"  Progress: {progress['completion_percentage']:.1f}% complete")
        print(f"  Status: {progress['status']}")
        print(f"  AI Decisions: {len(progress['ai_decisions'])} made")
        
        # Complete mission
        result = ai_piloting.complete_mission(mission_id)
        print(f"  ✅ Mission completed!")
        print(f"    Success: {result['success']}")
        print(f"    Experience gained: {result['experience_gained']}")
        print(f"    Credits earned: {result['credits_earned']}")
    
    # Show pilot performance
    print("\n📊 Pilot Performance:")
    performance = ai_piloting.get_pilot_performance("nav_specialist_001")
    if performance:
        print(f"  Navigator Prime Performance:")
        print(f"    Missions completed: {performance['missions_completed']}")
        print(f"    Success rate: {performance['success_rate']:.1f}%")
        print(f"    Average rating: {performance['average_mission_rating']:.1f}")
        print(f"    Total credits earned: {performance['total_credits_earned']}")


def demo_integrated_system():
    """Demonstrate integrated space quest support system."""
    print("\n" + "="*60)
    print("🎮 INTEGRATED SPACE QUEST SUPPORT")
    print("="*60)
    
    # Initialize integrated system
    space_quest = SpaceQuestSupport()
    
    # Start session
    print("\n🚀 Starting Space Quest Session:")
    session_id = space_quest.start_session("Corellia Starport")
    print(f"  Session ID: {session_id}")
    
    # Navigate to different locations
    print("\n🗺️  Navigation Examples:")
    destinations = ["Naboo Orbital", "Coruscant Central", "Tatooine Spaceport"]
    route_types = ["safe", "fast", "direct"]
    
    for dest, route_type in zip(destinations, route_types):
        print(f"\n  Navigating to {dest} via {route_type} route:")
        result = space_quest.navigate_to_location(dest, route_type)
        if result.get("success"):
            print(f"    ✅ Route calculated successfully")
            print(f"    Distance: {result['route']['total_distance']:.1f}")
            print(f"    Time: {result['route']['total_time']:.1f} minutes")
            print(f"    Fuel: {result['route']['total_fuel_cost']:.1f}")
        else:
            print(f"    ❌ Navigation failed")
    
    # Visit mission locations
    print("\n🏛️  Mission Location Visits:")
    locations_to_visit = ["Naboo Orbital", "Coruscant Central", "Imperial Fleet Command"]
    for location in locations_to_visit:
        result = space_quest.visit_mission_location(location)
        if result.get("success"):
            print(f"  ✅ Visited {location}")
            print(f"    Available givers: {len(result['mission_givers'])}")
            print(f"    Available missions: {len(result['available_missions'])}")
        else:
            print(f"  ❌ Failed to visit {location}")
    
    # Interact with mission givers
    print("\n👥 Mission Giver Interactions:")
    givers_to_interact = ["Ambassador Amidala", "Commander Tarkin", "Admiral Ackbar"]
    for giver in givers_to_interact:
        result = space_quest.interact_with_giver(giver)
        if result.get("success"):
            print(f"  ✅ Interacted with {giver}")
            if result.get("available_missions"):
                print(f"    Available missions: {len(result['available_missions'])}")
        else:
            print(f"  ❌ Failed to interact with {giver}")
    
    # Unlock ships
    print("\n🛸 Ship Unlocking:")
    player_stats = create_mock_player_stats()
    ships_to_unlock = ["Advanced Fighter", "Interceptor"]
    for ship in ships_to_unlock:
        result = space_quest.unlock_ship(ship, player_stats)
        if result.get("success"):
            print(f"  ✅ Unlocked {ship}")
        else:
            print(f"  ❌ Failed to unlock {ship}")
    
    # Install upgrades
    print("\n🔧 Upgrade Installation:")
    upgrade_data = [
        ("Basic Fighter", "basic_weapon_001", "weapons_1"),
        ("Basic Fighter", "basic_shield_001", "shields_1")
    ]
    for ship, upgrade, slot in upgrade_data:
        result = space_quest.install_upgrade(ship, upgrade, slot)
        if result.get("success"):
            print(f"  ✅ Installed {upgrade} on {ship}")
        else:
            print(f"  ❌ Failed to install {upgrade} on {ship}")
    
    # Activate AI pilots
    print("\n🤖 AI Pilot Activation:")
    pilots_to_activate = ["nav_specialist_001", "combat_specialist_001"]
    for pilot in pilots_to_activate:
        result = space_quest.activate_pilot(pilot)
        if result.get("success"):
            print(f"  ✅ Activated {pilot}")
        else:
            print(f"  ❌ Failed to activate {pilot}")
    
    # Assign AI missions
    print("\n📋 AI Mission Assignment:")
    mission_data = {
        "mission_type": "patrol",
        "ship_name": "Advanced Fighter",
        "destination": "Naboo Orbital",
        "objectives": ["Patrol route", "Eliminate threats"],
        "constraints": {"time_limit": 60.0},
        "priority": 5,
        "estimated_duration": 45.0
    }
    
    result = space_quest.assign_ai_mission("nav_specialist_001", mission_data)
    if result.get("success"):
        print(f"  ✅ Assigned mission to Navigator Prime")
        mission_id = result['mission_id']
        
        # Start and complete mission
        space_quest.start_ai_mission(mission_id)
        print(f"  🚀 AI mission started")
        
        # Simulate progress
        progress_data = {
            "current_waypoint": "Republic Naval Base",
            "fuel_remaining": 40.0,
            "damage_taken": 0.05,
            "objectives_completed": 1
        }
        
        progress = space_quest.update_ai_mission(mission_id, progress_data)
        print(f"  📈 Progress: {progress['completion_percentage']:.1f}%")
        
        # Complete mission
        completion = space_quest.complete_ai_mission(mission_id)
        print(f"  ✅ AI mission completed!")
        print(f"    Success: {completion['success']}")
        print(f"    Experience: {completion['experience_gained']}")
        print(f"    Credits: {completion['credits_earned']}")
    
    # Get session status
    print("\n📊 Session Status:")
    status = space_quest.get_session_status()
    print(f"  Session ID: {status['session_id']}")
    print(f"  Current Location: {status['current_location']}")
    print(f"  Session Duration: {status['session_duration']:.1f} minutes")
    print(f"  Missions Completed: {status['missions_completed']}")
    print(f"  Credits Earned: {status['credits_earned']}")
    print(f"  Ships Unlocked: {status['ships_unlocked']}")
    print(f"  Upgrades Installed: {status['upgrades_installed']}")
    print(f"  Pilots Activated: {status['pilots_activated']}")
    
    # End session
    print("\n🏁 Ending Session:")
    summary = space_quest.end_session()
    print(f"  ✅ Session ended successfully")
    print(f"  Total Duration: {summary['session_duration']:.1f} minutes")
    print(f"  Total Missions: {summary['total_missions']}")
    print(f"  Total Credits: {summary['total_credits']}")
    print(f"  Total Experience: {summary['total_experience']}")


def create_sample_data_files():
    """Create sample data files for demonstration."""
    print("\n" + "="*60)
    print("📁 CREATING SAMPLE DATA FILES")
    print("="*60)
    
    # Create temporary directory for sample data
    temp_dir = Path("temp_space_data")
    temp_dir.mkdir(exist_ok=True)
    
    # Sample hyperspace data
    hyperspace_data = {
        "nodes": [
            {
                "name": "Demo Starport",
                "zone": "demo_sector",
                "coordinates": [0.0, 0.0, 0.0],
                "security_level": 0.1,
                "traffic_density": 0.5,
                "fuel_cost": 5.0,
                "travel_time": 10.0,
                "connections": ["Demo Orbital"]
            }
        ],
        "routes": []
    }
    
    with open(temp_dir / "hyperspace_demo.json", "w") as f:
        json.dump(hyperspace_data, f, indent=2)
    
    # Sample mission data
    mission_data = {
        "locations": [
            {
                "name": "Demo Starport",
                "location_type": "starport",
                "zone": "demo_sector",
                "coordinates": [0.0, 0.0, 0.0],
                "security_level": 0.1,
                "available_missions": ["patrol", "escort"],
                "mission_givers": ["Demo Commander"],
                "facilities": ["mission_terminal", "fuel_station"],
                "restrictions": {"faction_standing": "neutral"}
            }
        ],
        "mission_givers": [
            {
                "name": "Demo Commander",
                "faction": "neutral",
                "mission_types": ["patrol", "escort"],
                "reputation_required": 0,
                "current_reputation": 0,
                "available_missions": ["demo_patrol_001", "demo_escort_001"]
            }
        ]
    }
    
    with open(temp_dir / "missions_demo.json", "w") as f:
        json.dump(mission_data, f, indent=2)
    
    print(f"  ✅ Created sample data files in {temp_dir}")
    print(f"  Files: hyperspace_demo.json, missions_demo.json")


def main():
    """Main demonstration function."""
    print("🚀 BATCH 068 - SPACE QUEST SUPPORT MODULE (EXTENDED PHASE)")
    print("="*80)
    print("Enhanced space quest support with advanced features:")
    print("• Enhanced hyperspace pathing simulation")
    print("• Extended mission locations (Corellia Starport, Naboo Orbital, and more)")
    print("• Advanced tiered ship upgrades")
    print("• AI piloting foundation for future integration")
    print("="*80)
    
    try:
        # Run demonstrations
        demo_enhanced_hyperspace_pathing()
        demo_extended_mission_locations()
        demo_advanced_ship_upgrades()
        demo_ai_piloting_foundation()
        demo_integrated_system()
        create_sample_data_files()
        
        print("\n" + "="*80)
        print("✅ BATCH 068 DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*80)
        print("Key Features Demonstrated:")
        print("• Advanced hyperspace navigation with multiple route types")
        print("• Comprehensive mission location management")
        print("• Tiered ship progression with upgrade system")
        print("• AI piloting with decision-making capabilities")
        print("• Integrated space quest support workflow")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 