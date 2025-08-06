#!/usr/bin/env python3
"""
Demo Batch 161 - PvP Presence Detection & Auto-Avoidance

This demo shows how to use the PvP watchdog system in practice,
demonstrating real-world scenarios and integration with the MS11 system.

Author: SWG Bot Development Team
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import the PvP watchdog
from core.pvp_watchdog import PvPWatchdog, PvPRiskType, RiskLevel, AvoidanceStrategy


class PvPWatchdogDemo:
    """Demo class for PvP watchdog functionality."""
    
    def __init__(self):
        """Initialize the demo."""
        self.watchdog = PvPWatchdog()
        self.demo_scenarios = []
        self.current_location = "moenia_city"
        self.current_planet = "naboo"
        self.current_coordinates = (4800, -4200)
        
    def setup_demo_scenarios(self):
        """Setup realistic demo scenarios."""
        self.demo_scenarios = [
            {
                'name': 'Safe City Exploration',
                'description': 'Exploring safe cities with minimal PvP risk',
                'duration': 30,
                'locations': [
                    {'zone': 'moenia_city', 'planet': 'naboo', 'coords': (4800, -4200)},
                    {'zone': 'tyrena_city', 'planet': 'corellia', 'coords': (4200, -5200)},
                    {'zone': 'bestine_city', 'planet': 'tatooine', 'coords': (3800, -4600)}
                ],
                'events': [
                    {'time': 5, 'type': 'player_detected', 'data': {'name': 'Trader1', 'faction': 'neutral', 'distance': 50}},
                    {'time': 15, 'type': 'player_detected', 'data': {'name': 'Crafting2', 'faction': 'neutral', 'distance': 35}},
                    {'time': 25, 'type': 'zone_change', 'data': {'from': 'moenia_city', 'to': 'tyrena_city'}}
                ]
            },
            {
                'name': 'Trade District Visit',
                'description': 'Visiting busy trade districts with moderate risk',
                'duration': 45,
                'locations': [
                    {'zone': 'coronet_trade_district', 'planet': 'corellia', 'coords': (4000, -5000)},
                    {'zone': 'theed_palace', 'planet': 'naboo', 'coords': (5000, -4000)}
                ],
                'events': [
                    {'time': 8, 'type': 'tef_flag', 'data': {'name': 'ImperialTrader', 'faction': 'imperial', 'distance': 30}},
                    {'time': 12, 'type': 'tef_flag', 'data': {'name': 'RebelTrader', 'faction': 'rebel', 'distance': 45}},
                    {'time': 20, 'type': 'duel_invite', 'data': {'name': 'PvPPlayer', 'faction': 'imperial'}},
                    {'time': 35, 'type': 'zone_change', 'data': {'from': 'coronet_trade_district', 'to': 'theed_palace'}}
                ]
            },
            {
                'name': 'GCW Hotspot Approach',
                'description': 'Approaching GCW hotspots with high PvP activity',
                'duration': 60,
                'locations': [
                    {'zone': 'battlefield', 'planet': 'dantooine', 'coords': (100, 200)},
                    {'zone': 'restuss', 'planet': 'rori', 'coords': (5000, -3000)}
                ],
                'events': [
                    {'time': 10, 'type': 'overt_player', 'data': {'name': 'ImperialElite', 'faction': 'imperial', 'distance': 25}},
                    {'time': 15, 'type': 'overt_player', 'data': {'name': 'RebelCommando', 'faction': 'rebel', 'distance': 30}},
                    {'time': 25, 'type': 'tef_flag', 'data': {'name': 'ImperialScout', 'faction': 'imperial', 'distance': 40}},
                    {'time': 35, 'type': 'tef_flag', 'data': {'name': 'RebelScout', 'faction': 'rebel', 'distance': 35}},
                    {'time': 45, 'type': 'zone_change', 'data': {'from': 'battlefield', 'to': 'restuss'}},
                    {'time': 55, 'type': 'overt_player', 'data': {'name': 'ImperialVet', 'faction': 'imperial', 'distance': 15}},
                    {'time': 58, 'type': 'overt_player', 'data': {'name': 'RebelVet', 'faction': 'rebel', 'distance': 18}}
                ]
            },
            {
                'name': 'Emergency Escape',
                'description': 'Demonstrating emergency escape protocols',
                'duration': 30,
                'locations': [
                    {'zone': 'restuss', 'planet': 'rori', 'coords': (5000, -3000)},
                    {'zone': 'moenia_city', 'planet': 'naboo', 'coords': (4800, -4200)}
                ],
                'events': [
                    {'time': 5, 'type': 'overt_player', 'data': {'name': 'ImperialHunter', 'faction': 'imperial', 'distance': 10}},
                    {'time': 8, 'type': 'overt_player', 'data': {'name': 'RebelHunter', 'faction': 'rebel', 'distance': 12}},
                    {'time': 12, 'type': 'overt_player', 'data': {'name': 'ImperialBackup', 'faction': 'imperial', 'distance': 8}},
                    {'time': 15, 'type': 'emergency_escape', 'data': {'target_zone': 'moenia_city', 'reason': 'Critical PvP risk detected'}}
                ]
            }
        ]
    
    def run_demo_scenario(self, scenario: Dict[str, Any]):
        """Run a single demo scenario."""
        print(f"\n{'='*80}")
        print(f"DEMO SCENARIO: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Duration: {scenario['duration']} seconds")
        print(f"{'='*80}")
        
        # Clear previous data
        self.watchdog.nearby_players.clear()
        self.watchdog.risk_zones.clear()
        
        # Initialize starting location
        start_location = scenario['locations'][0]
        self.current_location = start_location['zone']
        self.current_planet = start_location['planet']
        self.current_coordinates = start_location['coords']
        
        print(f"Starting location: {self.current_location} on {self.current_planet}")
        
        # Simulate time progression
        for second in range(scenario['duration']):
            # Check for events at this time
            events_at_time = [e for e in scenario['events'] if e['time'] == second]
            
            for event in events_at_time:
                self.handle_demo_event(event)
            
            # Update zone assessment periodically
            if second % 10 == 0:
                self.update_zone_assessment()
            
            # Display status every 5 seconds
            if second % 5 == 0:
                self.display_status(second)
            
            # Simulate time passing
            time.sleep(0.1)  # 0.1 second = 1 demo second
        
        # Final status display
        self.display_final_status()
    
    def handle_demo_event(self, event: Dict[str, Any]):
        """Handle a demo event."""
        event_type = event['type']
        data = event['data']
        
        print(f"\n[Event at {event['time']}s] {event_type.upper()}: {data}")
        
        if event_type == 'player_detected':
            # Neutral player detected - no PvP risk
            print(f"  -> Neutral player {data['name']} detected at {data['distance']}m")
            
        elif event_type == 'tef_flag':
            # TEF flag detected
            self.watchdog.detect_tef_flag(data['name'], data['faction'], data['distance'])
            print(f"  -> TEF flag detected on {data['name']} ({data['faction']}) at {data['distance']}m")
            
        elif event_type == 'duel_invite':
            # Duel invite received
            self.watchdog.detect_duel_invite(data['name'], data['faction'])
            print(f"  -> Duel invite from {data['name']} ({data['faction']})")
            
        elif event_type == 'overt_player':
            # Overt player detected
            self.watchdog.detect_overt_player(data['name'], data['faction'], data['distance'])
            print(f"  -> Overt player {data['name']} ({data['faction']}) detected at {data['distance']}m")
            
        elif event_type == 'zone_change':
            # Zone change
            old_zone = data['from']
            new_zone = data['to']
            self.current_location = new_zone
            print(f"  -> Zone change: {old_zone} -> {new_zone}")
            
        elif event_type == 'emergency_escape':
            # Emergency escape triggered
            target_zone = data['target_zone']
            reason = data['reason']
            print(f"  -> EMERGENCY ESCAPE: {reason}")
            print(f"  -> Moving to safe zone: {target_zone}")
            self.current_location = target_zone
    
    def update_zone_assessment(self):
        """Update zone risk assessment."""
        # Simulate player count and faction mix based on current zone
        zone_configs = {
            'moenia_city': {'player_count': 3, 'faction_mix': {'imperial': 1, 'rebel': 1, 'neutral': 1}},
            'tyrena_city': {'player_count': 4, 'faction_mix': {'imperial': 1, 'rebel': 1, 'neutral': 2}},
            'bestine_city': {'player_count': 2, 'faction_mix': {'imperial': 1, 'neutral': 1}},
            'coronet_trade_district': {'player_count': 12, 'faction_mix': {'imperial': 5, 'rebel': 4, 'neutral': 3}},
            'theed_palace': {'player_count': 8, 'faction_mix': {'imperial': 3, 'rebel': 4, 'neutral': 1}},
            'battlefield': {'player_count': 8, 'faction_mix': {'imperial': 4, 'rebel': 4}},
            'restuss': {'player_count': 15, 'faction_mix': {'imperial': 8, 'rebel': 7}}
        }
        
        config = zone_configs.get(self.current_location, {'player_count': 5, 'faction_mix': {'neutral': 5}})
        
        self.watchdog.assess_zone_risk(
            self.current_location,
            self.current_planet,
            self.current_coordinates,
            config['player_count'],
            config['faction_mix']
        )
    
    def display_status(self, elapsed_time: int):
        """Display current PvP status."""
        risk_score = self.watchdog.calculate_risk_score()
        strategy = self.watchdog.get_avoidance_strategy()
        pvp_status = self.watchdog.get_pvp_status()
        
        print(f"\n[{elapsed_time:2d}s] Status Update:")
        print(f"  Location: {self.current_location} on {self.current_planet}")
        print(f"  Risk Score: {risk_score:.3f} ({pvp_status['risk_level']})")
        print(f"  Strategy: {strategy.value}")
        print(f"  Nearby Players: {pvp_status['nearby_players']}")
        print(f"  Active Zones: {pvp_status['active_zones']}")
        
        # Show recent players if any
        if self.watchdog.nearby_players:
            print(f"  Recent Players:")
            for player in list(self.watchdog.nearby_players.values())[:3]:
                print(f"    - {player.name} ({player.faction}) - {player.risk_type.value} at {player.distance}m")
    
    def display_final_status(self):
        """Display final status after scenario completion."""
        print(f"\n{'='*80}")
        print("SCENARIO COMPLETED - FINAL STATUS")
        print(f"{'='*80}")
        
        risk_score = self.watchdog.calculate_risk_score()
        strategy = self.watchdog.get_avoidance_strategy()
        pvp_status = self.watchdog.get_pvp_status()
        stats = self.watchdog.get_statistics()
        
        print(f"Final Location: {self.current_location} on {self.current_planet}")
        print(f"Final Risk Score: {risk_score:.3f} ({pvp_status['risk_level']})")
        print(f"Final Strategy: {strategy.value}")
        print(f"Total Events: {stats['total_events']}")
        print(f"Active Players: {len(self.watchdog.nearby_players)}")
        print(f"Active Zones: {len(self.watchdog.risk_zones)}")
        
        # Show strategy actions
        strategy_result = self.watchdog.execute_avoidance_strategy(strategy)
        print(f"\nStrategy Actions:")
        for action in strategy_result['actions']:
            print(f"  - {action}")
        
        print(f"{'='*80}")
    
    def run_all_demos(self):
        """Run all demo scenarios."""
        print("PvP Watchdog Demo Suite")
        print("=" * 80)
        print("This demo shows the PvP watchdog system in action with realistic scenarios.")
        print("Each scenario simulates different PvP risk levels and avoidance strategies.")
        print("=" * 80)
        
        self.setup_demo_scenarios()
        
        for i, scenario in enumerate(self.demo_scenarios, 1):
            print(f"\n\nDemo {i}/{len(self.demo_scenarios)}")
            self.run_demo_scenario(scenario)
            
            if i < len(self.demo_scenarios):
                print(f"\nPress Enter to continue to next demo...")
                input()
    
    def demonstrate_policy_changes(self):
        """Demonstrate how policy changes affect behavior."""
        print(f"\n{'='*80}")
        print("POLICY CONFIGURATION DEMO")
        print(f"{'='*80}")
        
        # Test different evade thresholds
        original_threshold = self.watchdog.policy.evade_threshold
        
        print("Testing different evade thresholds:")
        for threshold in [0.3, 0.5, 0.7, 0.9]:
            self.watchdog.policy.evade_threshold = threshold
            
            # Simulate some risk
            self.watchdog.detect_tef_flag("TestPlayer", "imperial", 25)
            risk_score = self.watchdog.calculate_risk_score()
            strategy = self.watchdog.get_avoidance_strategy()
            
            print(f"  Evade threshold {threshold}: Risk {risk_score:.3f} -> Strategy {strategy.value}")
        
        # Reset to original
        self.watchdog.policy.evade_threshold = original_threshold
        
        # Test log_only mode
        print(f"\nTesting log_only mode:")
        self.watchdog.policy.log_only = True
        self.watchdog.detect_overt_player("TestOvert", "rebel", 15)
        risk_score = self.watchdog.calculate_risk_score()
        strategy = self.watchdog.get_avoidance_strategy()
        print(f"  Log-only mode: Risk {risk_score:.3f} -> Strategy {strategy.value}")
        
        # Reset
        self.watchdog.policy.log_only = False
    
    def demonstrate_dashboard_integration(self):
        """Demonstrate dashboard integration."""
        print(f"\n{'='*80}")
        print("DASHBOARD INTEGRATION DEMO")
        print(f"{'='*80}")
        
        # Simulate some activity
        self.watchdog.detect_tef_flag("DashboardTest1", "imperial", 30)
        self.watchdog.detect_overt_player("DashboardTest2", "rebel", 20)
        self.watchdog.assess_zone_risk("demo_zone", "demo_planet", (100, 100), 8, {"imperial": 4, "rebel": 4})
        
        # Get dashboard data
        pvp_status = self.watchdog.get_pvp_status()
        stats = self.watchdog.get_statistics()
        
        print("Dashboard Status Data:")
        print(json.dumps(pvp_status, indent=2))
        
        print(f"\nStatistics Data:")
        print(json.dumps(stats, indent=2))
        
        print(f"\nThis data would be sent to the dashboard component for real-time display.")
    
    def demonstrate_emergency_protocols(self):
        """Demonstrate emergency protocols."""
        print(f"\n{'='*80}")
        print("EMERGENCY PROTOCOLS DEMO")
        print(f"{'='*80}")
        
        # Simulate critical situation
        print("Simulating critical PvP situation...")
        
        self.watchdog.detect_overt_player("ImperialElite", "imperial", 10)
        self.watchdog.detect_overt_player("RebelCommando", "rebel", 12)
        self.watchdog.detect_overt_player("ImperialBackup", "imperial", 8)
        self.watchdog.detect_overt_player("RebelBackup", "rebel", 15)
        
        risk_score = self.watchdog.calculate_risk_score()
        strategy = self.watchdog.get_avoidance_strategy()
        
        print(f"Critical Risk Score: {risk_score:.3f}")
        print(f"Emergency Strategy: {strategy.value}")
        
        # Execute emergency protocol
        strategy_result = self.watchdog.execute_avoidance_strategy(strategy)
        
        print(f"\nEmergency Actions:")
        for action in strategy_result['actions']:
            print(f"  🚨 {action}")
        
        print(f"\nEmergency protocols would trigger:")
        print(f"  - Immediate session pause")
        print(f"  - Logout for safety")
        print(f"  - Alert notifications")
        print(f"  - Emergency zone change")


def main():
    """Main demo function."""
    print("Starting PvP Watchdog Demo")
    print("=" * 80)
    
    demo = PvPWatchdogDemo()
    
    try:
        # Run all demo scenarios
        demo.run_all_demos()
        
        # Demonstrate additional features
        demo.demonstrate_policy_changes()
        demo.demonstrate_dashboard_integration()
        demo.demonstrate_emergency_protocols()
        
        print(f"\n{'='*80}")
        print("DEMO COMPLETED SUCCESSFULLY")
        print(f"{'='*80}")
        print("The PvP watchdog system is ready for integration with MS11!")
        print("Key features demonstrated:")
        print("  ✅ TEF flag detection")
        print("  ✅ Duel invite monitoring")
        print("  ✅ Overt player detection")
        print("  ✅ Zone risk assessment")
        print("  ✅ Dynamic avoidance strategies")
        print("  ✅ Policy configuration")
        print("  ✅ Dashboard integration")
        print("  ✅ Emergency protocols")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 