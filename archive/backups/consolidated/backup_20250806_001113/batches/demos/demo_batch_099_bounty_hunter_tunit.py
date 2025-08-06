"""Demo Batch 099 - T-Unit Bounty Hunter Mode (Phase 1)

This demo showcases the bounty hunter mode functionality including:
- Mission acceptance and filtering
- Travel to target locations
- Combat engagement with different difficulty levels
- Mission completion and reward collection
- Discord alerts integration
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Import the bounty hunter mode
from android_ms11.modes.bounty_hunter_tunit import BountyHunterTUnit
from modules.discord_alerts import send_bounty_alert, send_mission_complete_alert


def create_sample_terminal_text() -> str:
    """Create sample BH terminal text for demonstration."""
    return """
    BOUNTY HUNTER TERMINAL - MOS EISLEY
    
    Available Missions:
    Rebel Scout 3520,-4800 300m 500c
    Smuggler Boss 50,75 1500m 1200c
    Elite Rebel Commander 100,-200 2500m 2500c
    Low Reward Target 100,100 500m 200c
    Far Away Target 10000,10000 8000m 1000c
    """


def create_sample_missions() -> List[Dict[str, Any]]:
    """Create sample missions for demonstration."""
    return [
        {
            "mission_id": "demo_001",
            "name": "Rebel Scout",
            "target_type": "npc",
            "location": {
                "planet": "tatooine",
                "city": "mos_eisley",
                "coordinates": [3520, -4800],
                "zone": "cantina"
            },
            "difficulty": "easy",
            "reward_credits": 500,
            "combat_profile": "aggressive",
            "distance": 300
        },
        {
            "mission_id": "demo_002",
            "name": "Smuggler Boss",
            "target_type": "npc",
            "location": {
                "planet": "dantooine",
                "city": "imperial_outpost",
                "coordinates": [50, 75],
                "zone": "cave"
            },
            "difficulty": "medium",
            "reward_credits": 1200,
            "combat_profile": "tactical",
            "distance": 1500
        },
        {
            "mission_id": "demo_003",
            "name": "Elite Rebel Commander",
            "target_type": "npc",
            "location": {
                "planet": "naboo",
                "city": "theed",
                "coordinates": [100, -200],
                "zone": "palace_grounds"
            },
            "difficulty": "hard",
            "reward_credits": 2500,
            "combat_profile": "defensive",
            "distance": 2500
        }
    ]


def demo_mission_acceptance(bounty_hunter: BountyHunterTUnit) -> None:
    """Demonstrate mission acceptance and filtering."""
    print("\n" + "="*60)
    print("🎯 DEMO: Mission Acceptance and Filtering")
    print("="*60)
    
    # Create sample terminal text
    terminal_text = create_sample_terminal_text()
    print(f"Terminal Text:\n{terminal_text}")
    
    # Accept missions
    accepted_missions = bounty_hunter.accept_missions(terminal_text)
    
    print(f"\nAccepted Missions: {len(accepted_missions)}")
    for i, mission in enumerate(accepted_missions, 1):
        print(f"  {i}. {mission['name']} - {mission.get('credits', 0)} credits")
    
    # Show filtering logic
    print(f"\nFiltering Criteria:")
    print(f"  - Max Travel Distance: {bounty_hunter.profile.get('max_travel_distance', 5000)}m")
    print(f"  - Min Reward Credits: {bounty_hunter.profile.get('min_reward_credits', 500)}c")
    print(f"  - Max Active Missions: {bounty_hunter.profile.get('max_active_missions', 3)}")


def demo_travel_to_targets(bounty_hunter: BountyHunterTUnit) -> None:
    """Demonstrate travel to target locations."""
    print("\n" + "="*60)
    print("🚀 DEMO: Travel to Target Locations")
    print("="*60)
    
    sample_missions = create_sample_missions()
    
    for mission in sample_missions:
        print(f"\nTraveling to: {mission['name']}")
        print(f"  Location: {mission['location']['city']}, {mission['location']['planet']}")
        print(f"  Coordinates: {mission['location']['coordinates']}")
        print(f"  Difficulty: {mission['difficulty']}")
        
        # Simulate travel
        success = bounty_hunter.travel_to_target(mission)
        if success:
            print(f"  ✅ Successfully arrived at {mission['name']} location")
        else:
            print(f"  ❌ Failed to travel to {mission['name']}")
        
        time.sleep(0.5)  # Simulate travel time


def demo_combat_engagement(bounty_hunter: BountyHunterTUnit) -> None:
    """Demonstrate combat engagement with different targets."""
    print("\n" + "="*60)
    print("⚔️ DEMO: Combat Engagement")
    print("="*60)
    
    sample_missions = create_sample_missions()
    
    for mission in sample_missions:
        print(f"\nEngaging: {mission['name']}")
        print(f"  Difficulty: {mission['difficulty']}")
        print(f"  Combat Profile: {mission['combat_profile']}")
        print(f"  Reward: {mission['reward_credits']} credits")
        
        # Simulate combat
        success = bounty_hunter.engage_target(mission)
        if success:
            print(f"  ✅ Successfully defeated {mission['name']}")
            
            # Send Discord alert
            if bounty_hunter.profile.get("enable_discord_alerts", False):
                location = f"{mission['location']['city']}, {mission['location']['planet']}"
                send_bounty_alert(mission['name'], location, mission['difficulty'])
                send_mission_complete_alert(mission['name'], mission['reward_credits'])
        else:
            print(f"  ❌ Failed to defeat {mission['name']}")
        
        time.sleep(0.5)  # Simulate combat time


def demo_mission_completion(bounty_hunter: BountyHunterTUnit) -> None:
    """Demonstrate mission completion and reward collection."""
    print("\n" + "="*60)
    print("💰 DEMO: Mission Completion and Rewards")
    print("="*60)
    
    sample_missions = create_sample_missions()
    total_credits = 0
    
    for mission in sample_missions:
        print(f"\nCompleting mission: {mission['name']}")
        print(f"  Reward: {mission['reward_credits']} credits")
        
        # Complete mission
        success = bounty_hunter.complete_mission(mission)
        if success:
            print(f"  ✅ Mission completed successfully")
            total_credits += mission['reward_credits']
        else:
            print(f"  ❌ Mission completion failed")
    
    print(f"\n📊 Session Summary:")
    print(f"  Total Missions Completed: {len(sample_missions)}")
    print(f"  Total Credits Earned: {total_credits}")
    print(f"  Average Reward per Mission: {total_credits // len(sample_missions)} credits")


def demo_discord_alerts() -> None:
    """Demonstrate Discord alert functionality."""
    print("\n" + "="*60)
    print("📢 DEMO: Discord Alerts")
    print("="*60)
    
    # Test different alert types
    alerts = [
        ("Rebel Scout", "Mos Eisley, Tatooine", "easy"),
        ("Smuggler Boss", "Imperial Outpost, Dantooine", "medium"),
        ("Elite Rebel Commander", "Theed, Naboo", "hard")
    ]
    
    for target_name, location, difficulty in alerts:
        print(f"\nSending alert for: {target_name}")
        success = send_bounty_alert(target_name, location, difficulty)
        if success:
            print(f"  ✅ Alert sent: T-Unit engaged {target_name} @ {location}")
        else:
            print(f"  ❌ Failed to send alert")
        
        time.sleep(0.3)


def demo_configuration_options() -> None:
    """Demonstrate configuration options."""
    print("\n" + "="*60)
    print("⚙️ DEMO: Configuration Options")
    print("="*60)
    
    # Show different configuration profiles
    configs = [
        {
            "name": "Aggressive Hunter",
            "max_active_missions": 5,
            "min_reward_credits": 300,
            "combat_behavior": "aggressive",
            "enable_discord_alerts": True
        },
        {
            "name": "Defensive Hunter",
            "max_active_missions": 2,
            "min_reward_credits": 1000,
            "combat_behavior": "defensive",
            "enable_discord_alerts": False
        },
        {
            "name": "Tactical Hunter",
            "max_active_missions": 3,
            "min_reward_credits": 500,
            "combat_behavior": "tactical",
            "enable_discord_alerts": True
        }
    ]
    
    for config in configs:
        print(f"\n{config['name']}:")
        print(f"  Max Active Missions: {config['max_active_missions']}")
        print(f"  Min Reward Credits: {config['min_reward_credits']}")
        print(f"  Combat Behavior: {config['combat_behavior']}")
        print(f"  Discord Alerts: {'Enabled' if config['enable_discord_alerts'] else 'Disabled'}")


def main() -> None:
    """Run the complete bounty hunter demo."""
    print("🎯 T-Unit Bounty Hunter Mode - Phase 1 Demo")
    print("="*60)
    print("This demo showcases the bounty hunter mode functionality")
    print("including mission acceptance, travel, combat, and completion.")
    print("="*60)
    
    # Initialize bounty hunter
    bounty_hunter = BountyHunterTUnit()
    
    # Run demos
    demo_mission_acceptance(bounty_hunter)
    demo_travel_to_targets(bounty_hunter)
    demo_combat_engagement(bounty_hunter)
    demo_mission_completion(bounty_hunter)
    demo_discord_alerts()
    demo_configuration_options()
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("The T-Unit Bounty Hunter mode is ready for deployment.")
    print("="*60)


if __name__ == "__main__":
    main() 