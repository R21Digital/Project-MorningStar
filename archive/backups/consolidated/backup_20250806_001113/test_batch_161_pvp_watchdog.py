#!/usr/bin/env python3
"""
Test Batch 161 - PvP Presence Detection & Auto-Avoidance

This test demonstrates the PvP watchdog system with various scenarios
including TEF flag detection, duel invites, overt players, and zone risk assessment.

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


class PvPWatchdogTester:
    """Test suite for PvP watchdog functionality."""
    
    def __init__(self):
        """Initialize the tester."""
        self.watchdog = PvPWatchdog()
        self.test_results = []
        self.scenarios = []
        
    def setup_test_scenarios(self):
        """Setup various test scenarios."""
        self.scenarios = [
            {
                'name': 'Safe Zone - No PvP Activity',
                'description': 'Test behavior in safe zones with no PvP activity',
                'players': [],
                'zone': {
                    'name': 'moenia_city',
                    'planet': 'naboo',
                    'coordinates': (4800, -4200),
                    'player_count': 3,
                    'faction_mix': {'imperial': 1, 'rebel': 1, 'neutral': 1}
                },
                'expected_risk': 'low',
                'expected_strategy': 'log_only'
            },
            {
                'name': 'Medium Risk - Crowded Zone',
                'description': 'Test behavior in crowded zones with mixed factions',
                'players': [
                    {'name': 'Player1', 'faction': 'imperial', 'distance': 25, 'risk_type': 'tef_flag'},
                    {'name': 'Player2', 'faction': 'rebel', 'distance': 40, 'risk_type': 'tef_flag'}
                ],
                'zone': {
                    'name': 'coronet_trade_district',
                    'planet': 'corellia',
                    'coordinates': (4000, -5000),
                    'player_count': 12,
                    'faction_mix': {'imperial': 5, 'rebel': 4, 'neutral': 3}
                },
                'expected_risk': 'medium',
                'expected_strategy': 'soft_path_deviation'
            },
            {
                'name': 'High Risk - GCW Hotspot',
                'description': 'Test behavior in GCW hotspots with active PvP',
                'players': [
                    {'name': 'Imperial1', 'faction': 'imperial', 'distance': 15, 'risk_type': 'overt_player'},
                    {'name': 'Rebel1', 'faction': 'rebel', 'distance': 20, 'risk_type': 'overt_player'},
                    {'name': 'Imperial2', 'faction': 'imperial', 'distance': 35, 'risk_type': 'tef_flag'},
                    {'name': 'Rebel2', 'faction': 'rebel', 'distance': 45, 'risk_type': 'tef_flag'}
                ],
                'zone': {
                    'name': 'battlefield',
                    'planet': 'dantooine',
                    'coordinates': (100, 200),
                    'player_count': 8,
                    'faction_mix': {'imperial': 4, 'rebel': 4}
                },
                'expected_risk': 'high',
                'expected_strategy': 'mount_escape'
            },
            {
                'name': 'Critical Risk - Restuss Zone',
                'description': 'Test behavior in critical PvP zones like Restuss',
                'players': [
                    {'name': 'ImperialElite', 'faction': 'imperial', 'distance': 10, 'risk_type': 'overt_player'},
                    {'name': 'RebelCommando', 'faction': 'rebel', 'distance': 12, 'risk_type': 'overt_player'},
                    {'name': 'ImperialVet', 'faction': 'imperial', 'distance': 18, 'risk_type': 'overt_player'},
                    {'name': 'RebelVet', 'faction': 'rebel', 'distance': 22, 'risk_type': 'overt_player'},
                    {'name': 'ImperialScout', 'faction': 'imperial', 'distance': 30, 'risk_type': 'tef_flag'},
                    {'name': 'RebelScout', 'faction': 'rebel', 'distance': 35, 'risk_type': 'tef_flag'}
                ],
                'zone': {
                    'name': 'restuss',
                    'planet': 'rori',
                    'coordinates': (5000, -3000),
                    'player_count': 15,
                    'faction_mix': {'imperial': 8, 'rebel': 7}
                },
                'expected_risk': 'critical',
                'expected_strategy': 'zone_change'
            },
            {
                'name': 'Duel Invite Scenario',
                'description': 'Test behavior when receiving duel invites',
                'players': [
                    {'name': 'DuelMaster', 'faction': 'imperial', 'distance': 0, 'risk_type': 'duel_invite'}
                ],
                'zone': {
                    'name': 'anchorhead_center',
                    'planet': 'tatooine',
                    'coordinates': (3520, -4800),
                    'player_count': 5,
                    'faction_mix': {'imperial': 2, 'rebel': 1, 'neutral': 2}
                },
                'expected_risk': 'medium',
                'expected_strategy': 'safe_spot_wait'
            }
        ]
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario."""
        print(f"\n{'='*60}")
        print(f"Running Scenario: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"{'='*60}")
        
        # Clear previous data
        self.watchdog.nearby_players.clear()
        self.watchdog.risk_zones.clear()
        
        # Simulate players
        for player_data in scenario['players']:
            if player_data['risk_type'] == 'tef_flag':
                self.watchdog.detect_tef_flag(
                    player_data['name'], 
                    player_data['faction'], 
                    player_data['distance']
                )
            elif player_data['risk_type'] == 'duel_invite':
                self.watchdog.detect_duel_invite(
                    player_data['name'], 
                    player_data['faction']
                )
            elif player_data['risk_type'] == 'overt_player':
                self.watchdog.detect_overt_player(
                    player_data['name'], 
                    player_data['faction'], 
                    player_data['distance']
                )
        
        # Assess zone risk
        zone_data = scenario['zone']
        self.watchdog.assess_zone_risk(
            zone_data['name'],
            zone_data['planet'],
            zone_data['coordinates'],
            zone_data['player_count'],
            zone_data['faction_mix']
        )
        
        # Calculate risk and get strategy
        risk_score = self.watchdog.calculate_risk_score()
        strategy = self.watchdog.get_avoidance_strategy()
        pvp_status = self.watchdog.get_pvp_status()
        
        # Execute strategy
        strategy_result = self.watchdog.execute_avoidance_strategy(strategy)
        
        # Display results
        print(f"\nResults:")
        print(f"  Risk Score: {risk_score:.3f} ({pvp_status['risk_level']})")
        print(f"  Expected Risk: {scenario['expected_risk']}")
        print(f"  Strategy: {strategy.value}")
        print(f"  Expected Strategy: {scenario['expected_strategy']}")
        print(f"  Nearby Players: {pvp_status['nearby_players']}")
        print(f"  Active Zones: {pvp_status['active_zones']}")
        print(f"  Recent Events: {pvp_status['recent_events']}")
        
        print(f"\nStrategy Actions:")
        for action in strategy_result['actions']:
            print(f"  - {action}")
        
        # Check if results match expectations
        risk_match = pvp_status['risk_level'] == scenario['expected_risk']
        strategy_match = strategy.value == scenario['expected_strategy']
        
        result = {
            'scenario_name': scenario['name'],
            'risk_score': risk_score,
            'actual_risk': pvp_status['risk_level'],
            'expected_risk': scenario['expected_risk'],
            'risk_match': risk_match,
            'actual_strategy': strategy.value,
            'expected_strategy': scenario['expected_strategy'],
            'strategy_match': strategy_match,
            'nearby_players': pvp_status['nearby_players'],
            'active_zones': pvp_status['active_zones'],
            'recent_events': pvp_status['recent_events'],
            'strategy_actions': strategy_result['actions']
        }
        
        self.test_results.append(result)
        
        # Print status
        status = "PASS" if risk_match and strategy_match else "FAIL"
        print(f"\nStatus: {status}")
        
        return result
    
    def run_all_scenarios(self):
        """Run all test scenarios."""
        print("PvP Watchdog Test Suite")
        print("=" * 60)
        
        self.setup_test_scenarios()
        
        for scenario in self.scenarios:
            self.run_scenario(scenario)
            time.sleep(1)  # Brief pause between scenarios
    
    def test_risk_calculation(self):
        """Test risk calculation with various inputs."""
        print(f"\n{'='*60}")
        print("Testing Risk Calculation")
        print(f"{'='*60}")
        
        # Test with no players
        self.watchdog.nearby_players.clear()
        risk_score = self.watchdog.calculate_risk_score()
        print(f"Empty scenario - Risk Score: {risk_score:.3f}")
        
        # Test with single TEF player
        self.watchdog.detect_tef_flag("TestPlayer", "imperial", 25)
        risk_score = self.watchdog.calculate_risk_score()
        print(f"Single TEF player - Risk Score: {risk_score:.3f}")
        
        # Test with multiple players
        self.watchdog.detect_overt_player("OvertPlayer", "rebel", 15)
        risk_score = self.watchdog.calculate_risk_score()
        print(f"Multiple players - Risk Score: {risk_score:.3f}")
        
        # Test risk decay over time
        print(f"\nTesting risk decay...")
        for i in range(5):
            time.sleep(0.5)
            risk_score = self.watchdog.calculate_risk_score()
            print(f"  After {i+1} intervals - Risk Score: {risk_score:.3f}")
    
    def test_avoidance_strategies(self):
        """Test all avoidance strategies."""
        print(f"\n{'='*60}")
        print("Testing Avoidance Strategies")
        print(f"{'='*60}")
        
        strategies = [
            AvoidanceStrategy.LOG_ONLY,
            AvoidanceStrategy.SOFT_PATH_DEVIATION,
            AvoidanceStrategy.SAFE_SPOT_WAIT,
            AvoidanceStrategy.MOUNT_ESCAPE,
            AvoidanceStrategy.ZONE_CHANGE,
            AvoidanceStrategy.SESSION_PAUSE
        ]
        
        for strategy in strategies:
            result = self.watchdog.execute_avoidance_strategy(strategy)
            print(f"\nStrategy: {strategy.value}")
            for action in result['actions']:
                print(f"  - {action}")
    
    def test_policy_configuration(self):
        """Test policy configuration changes."""
        print(f"\n{'='*60}")
        print("Testing Policy Configuration")
        print(f"{'='*60}")
        
        # Test with different evade thresholds
        original_threshold = self.watchdog.policy.evade_threshold
        
        for threshold in [0.3, 0.5, 0.7, 0.9]:
            self.watchdog.policy.evade_threshold = threshold
            strategy = self.watchdog.get_avoidance_strategy()
            print(f"Evade threshold {threshold} -> Strategy: {strategy.value}")
        
        # Reset to original
        self.watchdog.policy.evade_threshold = original_threshold
    
    def test_data_persistence(self):
        """Test data persistence functionality."""
        print(f"\n{'='*60}")
        print("Testing Data Persistence")
        print(f"{'='*60}")
        
        # Add some test data
        self.watchdog.detect_tef_flag("PersistTest", "imperial", 30)
        self.watchdog.assess_zone_risk(
            "test_zone", "test_planet", (100, 100), 5, {"imperial": 3, "rebel": 2}
        )
        
        # Save data
        self.watchdog._save_data()
        print("Data saved successfully")
        
        # Clear in-memory data
        original_players = len(self.watchdog.nearby_players)
        original_zones = len(self.watchdog.risk_zones)
        self.watchdog.nearby_players.clear()
        self.watchdog.risk_zones.clear()
        
        print(f"Cleared data - Players: {len(self.watchdog.nearby_players)}, Zones: {len(self.watchdog.risk_zones)}")
        
        # Reload data
        self.watchdog._load_data()
        print(f"Reloaded data - Players: {len(self.watchdog.nearby_players)}, Zones: {len(self.watchdog.risk_zones)}")
        
        # Verify data was restored
        assert len(self.watchdog.nearby_players) == original_players
        assert len(self.watchdog.risk_zones) == original_zones
        print("Data persistence test passed!")
    
    def test_statistics(self):
        """Test statistics functionality."""
        print(f"\n{'='*60}")
        print("Testing Statistics")
        print(f"{'='*60}")
        
        stats = self.watchdog.get_statistics()
        print("Current Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    def test_cleanup_functionality(self):
        """Test cleanup functionality."""
        print(f"\n{'='*60}")
        print("Testing Cleanup Functionality")
        print(f"{'='*60}")
        
        # Add old data
        old_time = datetime.now() - timedelta(hours=2)
        
        # Create old player entry
        from core.pvp_watchdog import PvPPlayer
        old_player = PvPPlayer(
            name="OldPlayer",
            faction="imperial",
            risk_type=PvPRiskType.TEF_FLAG,
            risk_level=RiskLevel.MEDIUM,
            distance=50,
            last_seen=old_time,
            threat_score=0.5
        )
        self.watchdog.nearby_players["OldPlayer"] = old_player
        
        print(f"Before cleanup - Players: {len(self.watchdog.nearby_players)}")
        
        # Run cleanup
        self.watchdog.cleanup_old_data()
        
        print(f"After cleanup - Players: {len(self.watchdog.nearby_players)}")
        
        # Verify old data was removed
        assert "OldPlayer" not in self.watchdog.nearby_players
        print("Cleanup test passed!")
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        print(f"\n{'='*60}")
        print("TEST REPORT")
        print(f"{'='*60}")
        
        total_scenarios = len(self.test_results)
        passed_scenarios = sum(1 for r in self.test_results if r['risk_match'] and r['strategy_match'])
        failed_scenarios = total_scenarios - passed_scenarios
        
        print(f"Total Scenarios: {total_scenarios}")
        print(f"Passed: {passed_scenarios}")
        print(f"Failed: {failed_scenarios}")
        print(f"Success Rate: {(passed_scenarios/total_scenarios)*100:.1f}%")
        
        print(f"\nDetailed Results:")
        for result in self.test_results:
            status = "PASS" if result['risk_match'] and result['strategy_match'] else "FAIL"
            print(f"  {result['scenario_name']}: {status}")
            if not result['risk_match']:
                print(f"    Risk mismatch: expected {result['expected_risk']}, got {result['actual_risk']}")
            if not result['strategy_match']:
                print(f"    Strategy mismatch: expected {result['expected_strategy']}, got {result['actual_strategy']}")
        
        # Save report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_scenarios': total_scenarios,
            'passed_scenarios': passed_scenarios,
            'failed_scenarios': failed_scenarios,
            'success_rate': (passed_scenarios/total_scenarios)*100,
            'results': self.test_results
        }
        
        report_file = Path("test_reports/pvp_watchdog_test_report.json")
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nTest report saved to: {report_file}")
        
        return report_data


def main():
    """Main test function."""
    print("Starting PvP Watchdog Test Suite")
    print("=" * 60)
    
    tester = PvPWatchdogTester()
    
    try:
        # Run all test scenarios
        tester.run_all_scenarios()
        
        # Run additional tests
        tester.test_risk_calculation()
        tester.test_avoidance_strategies()
        tester.test_policy_configuration()
        tester.test_data_persistence()
        tester.test_statistics()
        tester.test_cleanup_functionality()
        
        # Generate report
        report = tester.generate_test_report()
        
        print(f"\n{'='*60}")
        print("ALL TESTS COMPLETED")
        print(f"{'='*60}")
        
        if report['success_rate'] >= 80:
            print("✅ Test suite passed with high success rate!")
        else:
            print("❌ Test suite needs improvement.")
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 