#!/usr/bin/env python3
"""
MS11 Batch 079 Demo - Heroics Instance Entry + Group Coordination Logic

This demo showcases the heroics coordination system including:
- Heroic instance detection from /heroiclock
- Group formation and role assignment
- Entry sequence execution (Axkva Min example)
- Role-based behaviors (DPS, Healer, Tank, Support)
- Discord integration for multi-bot coordination
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Batch 079 modules
try:
    from core.heroics.heroic_detector import HeroicDetector, HeroicEntryStatus
    from core.heroics.heroic_coordinator import HeroicCoordinator, GroupFormation, GroupMember
    from core.heroics.role_behaviors import RoleBehaviorManager
    from core.heroics.discord_integration import DiscordIntegration
except ImportError as e:
    print(f"Error importing Batch 079 modules: {e}")
    print("Please ensure all modules are properly installed")
    exit(1)


class HeroicsCoordinationDemo:
    """Demo class for Batch 079 heroics coordination system."""
    
    def __init__(self):
        """Initialize the demo."""
        self.heroic_detector = HeroicDetector()
        self.heroic_coordinator = HeroicCoordinator()
        self.role_behavior_manager = RoleBehaviorManager()
        
        # Demo configuration
        self.demo_config = {
            "character_name": "DemoCharacter",
            "character_level": 85,
            "character_profession": "commando",
            "preferred_role": "dps"
        }
        
        # Demo group members
        self.demo_group_members = [
            {
                "name": "DemoCharacter",
                "level": 85,
                "profession": "commando",
                "preferred_role": "dps"
            },
            {
                "name": "HealerBot",
                "level": 82,
                "profession": "medic",
                "preferred_role": "healer"
            },
            {
                "name": "TankBot",
                "level": 88,
                "profession": "brawler",
                "preferred_role": "tank"
            },
            {
                "name": "SupportBot",
                "level": 80,
                "profession": "entertainer",
                "preferred_role": "support"
            }
        ]
        
        print("🎮 MS11 Batch 079 Demo - Heroics Coordination System")
        print("=" * 60)

    def run_demo(self):
        """Run the complete demo."""
        try:
            print("\n📋 Demo Overview:")
            print("1. Detect available heroics from /heroiclock")
            print("2. Create group formation for Axkva Min")
            print("3. Assign roles to group members")
            print("4. Execute entry sequence")
            print("5. Demonstrate role-based behaviors")
            print("6. Show Discord integration capabilities")
            
            # Step 1: Detect available heroics
            self._demo_heroic_detection()
            
            # Step 2: Group formation
            self._demo_group_formation()
            
            # Step 3: Role assignment
            self._demo_role_assignment()
            
            # Step 4: Entry sequence execution
            self._demo_entry_sequence()
            
            # Step 5: Role-based behaviors
            self._demo_role_behaviors()
            
            # Step 6: Discord integration
            self._demo_discord_integration()
            
            print("\n✅ Demo completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            logger.error(f"Demo error: {e}")

    def _demo_heroic_detection(self):
        """Demo heroic instance detection."""
        print("\n🔍 Step 1: Heroic Instance Detection")
        print("-" * 40)
        
        # Simulate /heroiclock command output
        heroiclock_text = """
        Axkva Min - Normal - Available - 0 hours
        Ancient Jedi Temple - Normal - Available - 0 hours
        Sith Academy - Normal - Locked - 12 hours
        Mandalorian Bunker - Hard - Available - 0 hours
        """
        
        print(f"📜 /heroiclock output:")
        print(heroiclock_text)
        
        # Detect available heroics
        available_heroics = self.heroic_detector.detect_available_heroics(heroiclock_text)
        
        print(f"🎯 Detected {len(available_heroics)} available heroics:")
        for heroic in available_heroics:
            print(f"  • {heroic.heroic_id}: {'✅ Available' if heroic.can_enter else '❌ Locked'}")
            if heroic.missing_prerequisites:
                print(f"    Missing: {', '.join(heroic.missing_prerequisites)}")
        
        # Get detailed info for Axkva Min
        axkva_info = self.heroic_detector.get_heroic_info("axkva_min")
        if axkva_info:
            print(f"\n📖 Axkva Min Details:")
            print(f"  • Planet: {axkva_info.planet}")
            print(f"  • Location: {axkva_info.location}")
            print(f"  • Coordinates: {axkva_info.coordinates}")
            print(f"  • Level Requirement: {axkva_info.level_requirement}")
            print(f"  • Group Size: {axkva_info.group_size}")
            print(f"  • Lockout Timer: {axkva_info.lockout_timer} seconds")

    def _demo_group_formation(self):
        """Demo group formation."""
        print("\n👥 Step 2: Group Formation")
        print("-" * 40)
        
        # Create group formation for Axkva Min
        formation = self.heroic_coordinator.create_group_formation(
            heroic_id="axkva_min",
            difficulty="normal",
            leader_name="DemoCharacter"
        )
        
        if formation:
            print(f"✅ Created group formation: {formation.group_id}")
            print(f"  • Heroic: {formation.heroic_id}")
            print(f"  • Difficulty: {formation.difficulty}")
            print(f"  • Target Size: {formation.target_size}")
            print(f"  • Current Size: {formation.current_size}")
            print(f"  • Status: {formation.status}")
            
            # Add group members
            for member_info in self.demo_group_members[1:]:  # Skip leader
                success = self.heroic_coordinator.add_member_to_group(
                    formation.group_id,
                    member_info["name"],
                    member_info
                )
                
                if success:
                    print(f"  ✅ Added {member_info['name']} to group")
                else:
                    print(f"  ❌ Failed to add {member_info['name']}")
            
            # Check final group status
            final_formation = self.heroic_coordinator.get_group_status(formation.group_id)
            if final_formation:
                print(f"\n📊 Final Group Status:")
                print(f"  • Members: {final_formation.current_size}/{final_formation.target_size}")
                print(f"  • Status: {final_formation.status}")
                
                for member in final_formation.members:
                    print(f"    - {member.player_name} ({member.role}) - {'✅ Ready' if member.is_ready else '⏳ Not Ready'}")

    def _demo_role_assignment(self):
        """Demo role assignment."""
        print("\n🎭 Step 3: Role Assignment")
        print("-" * 40)
        
        # Demonstrate role assignment for each member
        for member_info in self.demo_group_members:
            role_assignment = self.heroic_coordinator.assign_role(
                member_info["name"],
                member_info
            )
            
            print(f"👤 {member_info['name']} ({member_info['profession']} L{member_info['level']}):")
            print(f"  • Preferred Role: {role_assignment.preferred_role}")
            print(f"  • Assigned Role: {role_assignment.assigned_role}")
            print(f"  • Confidence: {role_assignment.confidence:.2f}")
            print(f"  • Reasoning: {role_assignment.reasoning}")
            print()

    def _demo_entry_sequence(self):
        """Demo entry sequence execution."""
        print("\n🚪 Step 4: Entry Sequence Execution")
        print("-" * 40)
        
        # Get entry sequence for Axkva Min
        sequence = self.heroic_coordinator.get_entry_sequence("axkva_min", "normal")
        
        print(f"🗺️ Entry sequence for Axkva Min (Normal):")
        for step in sequence:
            print(f"  Step {step['step']}: {step['description']}")
            print(f"    Action: {step['action']}")
            
            if 'coordinates' in step:
                print(f"    Coordinates: {step['coordinates']}")
            if 'planet' in step:
                print(f"    Planet: {step['planet']}")
            if 'target' in step:
                print(f"    Target: {step['target']}")
            if 'required_items' in step:
                print(f"    Required Items: {step['required_items']}")
            print()
        
        # Simulate executing the sequence
        print("🎬 Simulating entry sequence execution...")
        
        # Create a demo group for execution
        formation = self.heroic_coordinator.create_group_formation(
            heroic_id="axkva_min",
            difficulty="normal",
            leader_name="DemoCharacter"
        )
        
        if formation:
            # Add all members
            for member_info in self.demo_group_members[1:]:
                self.heroic_coordinator.add_member_to_group(
                    formation.group_id,
                    member_info["name"],
                    member_info
                )
            
            # Execute sequence
            success = self.heroic_coordinator.execute_entry_sequence(formation.group_id, sequence)
            
            if success:
                print("✅ Entry sequence completed successfully!")
            else:
                print("❌ Entry sequence failed!")

    def _demo_role_behaviors(self):
        """Demo role-based behaviors."""
        print("\n⚔️ Step 5: Role-Based Behaviors")
        print("-" * 40)
        
        # Simulate game state for different scenarios
        game_states = [
            {
                "name": "DPS Scenario",
                "state": {
                    "has_target": True,
                    "target_in_range": True,
                    "target_is_boss": True,
                    "self_health": 0.9,
                    "target_health": 0.8
                }
            },
            {
                "name": "Healer Scenario",
                "state": {
                    "target_low_health": True,
                    "target_friendly": True,
                    "group_average_health": 0.5,
                    "tank_health": 0.3,
                    "target_has_debuff": False
                }
            },
            {
                "name": "Tank Scenario",
                "state": {
                    "has_target": True,
                    "aggro_lost": True,
                    "self_health": 0.6,
                    "target_in_range": True
                }
            },
            {
                "name": "Support Scenario",
                "state": {
                    "group_needs_buff": True,
                    "target_exists": True,
                    "target_enemy": True,
                    "group_buffed": False
                }
            }
        ]
        
        for scenario in game_states:
            print(f"\n🎯 {scenario['name']}:")
            
            # Test each role behavior
            roles = ["dps", "healer", "tank", "support"]
            for role in roles:
                if role == "dps":
                    result = self.role_behavior_manager.execute_dps_behavior(scenario['state'])
                elif role == "healer":
                    result = self.role_behavior_manager.execute_healer_behavior(scenario['state'])
                elif role == "tank":
                    result = self.role_behavior_manager.execute_tank_behavior(scenario['state'])
                elif role == "support":
                    result = self.role_behavior_manager.execute_support_behavior(scenario['state'])
                
                if result.get("success"):
                    print(f"  {role.upper()}: ✅ {result['action']} -> {result['target']}")
                else:
                    print(f"  {role.upper()}: ❌ {result.get('reason', 'No action available')}")

    def _demo_discord_integration(self):
        """Demo Discord integration capabilities."""
        print("\n💬 Step 6: Discord Integration")
        print("-" * 40)
        
        # Load Discord config
        config_path = Path("config/group_profiles/group_heroics.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            discord_config = config.get("group_coordination", {}).get("discord_integration", {})
            
            print("📋 Discord Integration Configuration:")
            print(f"  • Enabled: {discord_config.get('enabled', False)}")
            print(f"  • Webhook URL: {'✅ Set' if discord_config.get('webhook_url') else '❌ Not set'}")
            print(f"  • Channel ID: {'✅ Set' if discord_config.get('channel_id') else '❌ Not set'}")
            print(f"  • Bot Token: {'✅ Set' if discord_config.get('bot_token') else '❌ Not set'}")
            
            if discord_config.get('enabled'):
                print("\n🤖 Discord Bot Commands:")
                print("  • !heroic available - Show available heroics")
                print("  • !heroic form <heroic> <difficulty> - Form group")
                print("  • !heroic join <group_id> - Join group")
                print("  • !group status - Show group status")
                print("  • !group ready <group_id> - Mark ready")
                print("  • !role request <role> - Request role")
                print("  • !status <health> <energy> <location> <target> - Update status")
                print("  • !heartbeat <character> - Send heartbeat")
                
                print("\n📊 Multi-Bot Coordination Features:")
                print("  • Real-time group formation")
                print("  • Automatic role assignment")
                print("  • Status synchronization")
                print("  • Group ready checks")
                print("  • Heroic instance coordination")
            else:
                print("\n⚠️ Discord integration is disabled")
                print("   Enable it in config/group_profiles/group_heroics.json")
        else:
            print("❌ Group configuration file not found")

    def _generate_demo_report(self):
        """Generate a demo report."""
        report = {
            "demo_name": "MS11 Batch 079 - Heroics Coordination",
            "timestamp": datetime.now().isoformat(),
            "features_demonstrated": [
                "Heroic instance detection from /heroiclock",
                "Group formation and management",
                "Role assignment based on profession and level",
                "Entry sequence execution (Axkva Min example)",
                "Role-based behaviors (DPS, Healer, Tank, Support)",
                "Discord integration for multi-bot coordination"
            ],
            "heroics_supported": [
                "Axkva Min",
                "Ancient Jedi Temple", 
                "Sith Academy",
                "Mandalorian Bunker",
                "Imperial Fortress"
            ],
            "roles_supported": [
                "DPS - Damage output optimization",
                "Healer - Group health management", 
                "Tank - Aggro and positioning management",
                "Support - Buff/debuff management"
            ],
            "discord_commands": [
                "!heroic available",
                "!heroic form <heroic> <difficulty>",
                "!heroic join <group_id>",
                "!group status",
                "!group ready <group_id>",
                "!role request <role>",
                "!status <health> <energy> <location> <target>",
                "!heartbeat <character>"
            ]
        }
        
        # Save report
        report_path = Path("reports/batch_079_demo_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Demo report saved to: {report_path}")
        return report


def main():
    """Main demo function."""
    print("🎮 MS11 Batch 079 Demo - Heroics Coordination System")
    print("=" * 60)
    
    # Create and run demo
    demo = HeroicsCoordinationDemo()
    demo.run_demo()
    
    # Generate report
    report = demo._generate_demo_report()
    
    print("\n🎉 Demo completed!")
    print("Batch 079 successfully demonstrates:")
    print("✅ Heroic instance detection and entry")
    print("✅ Group coordination and role assignment") 
    print("✅ Role-based behaviors for different professions")
    print("✅ Discord integration for multi-bot coordination")
    print("✅ Entry sequence execution (Axkva Min example)")


if __name__ == "__main__":
    main() 