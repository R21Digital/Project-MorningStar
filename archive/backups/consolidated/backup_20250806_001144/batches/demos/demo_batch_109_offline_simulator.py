#!/usr/bin/env python3
"""
Demo script for Batch 109 - Offline Mode Simulator

This script demonstrates the capabilities of the offline simulator for testing
bot logic without launching the game. It showcases quest step testing, travel
path testing, and combat loop simulation with detailed decision tree visualization.

Author: SWG Bot Development Team
"""

import time
import json
from pathlib import Path
from core.simulator import (
    offline_simulator, SimulationMode, QuestType, TravelMethod, 
    CombatAction, ActionResult
)

def demo_quest_step_simulation():
    """Demonstrate quest step simulation."""
    print("\n" + "="*60)
    print("DEMO: Quest Step Simulation")
    print("="*60)
    
    # Create character and world state
    character = offline_simulator.create_character_config(
        name="QuestTester",
        profession="Brawler",
        level=15
    )
    
    world_state = offline_simulator.create_mock_world_state(
        location="Mos Eisley",
        population=75
    )
    
    # Simulate kill quest
    print("\n1. Simulating Kill Quest...")
    kill_quest_params = {
        "target_count": 5,
        "target_type": "Stormtrooper",
        "time_limit": 1800,
        "reward_xp": 500,
        "reward_credits": 1000
    }
    
    kill_result = offline_simulator.simulate_quest_step(
        quest_type=QuestType.KILL,
        character=character,
        world_state=world_state,
        quest_params=kill_quest_params
    )
    
    print(f"   Simulation ID: {kill_result.simulation_id}")
    print(f"   Total Duration: {kill_result.total_duration:.2f} seconds")
    print(f"   Success Rate: {kill_result.success_rate:.2%}")
    print(f"   XP Gained: {kill_result.xp_gained}")
    print(f"   Credits Earned: {kill_result.credits_earned}")
    print(f"   Steps Executed: {len(kill_result.steps)}")
    print(f"   Decisions Made: {kill_result.decisions_made}")
    print(f"   Errors Encountered: {kill_result.errors_encountered}")
    
    # Simulate collection quest
    print("\n2. Simulating Collection Quest...")
    collect_quest_params = {
        "item_name": "Ore",
        "required_count": 3,
        "time_limit": 1200,
        "reward_xp": 300,
        "reward_credits": 750
    }
    
    collect_result = offline_simulator.simulate_quest_step(
        quest_type=QuestType.COLLECT,
        character=character,
        world_state=world_state,
        quest_params=collect_quest_params
    )
    
    print(f"   Simulation ID: {collect_result.simulation_id}")
    print(f"   Total Duration: {collect_result.total_duration:.2f} seconds")
    print(f"   Success Rate: {collect_result.success_rate:.2%}")
    print(f"   XP Gained: {collect_result.xp_gained}")
    print(f"   Credits Earned: {collect_result.credits_earned}")
    print(f"   Steps Executed: {len(collect_result.steps)}")
    
    return kill_result, collect_result

def demo_travel_path_simulation():
    """Demonstrate travel path simulation."""
    print("\n" + "="*60)
    print("DEMO: Travel Path Simulation")
    print("="*60)
    
    # Create character and world state
    character = offline_simulator.create_character_config(
        name="TravelTester",
        profession="Scout",
        level=12
    )
    
    world_state = offline_simulator.create_mock_world_state(
        location="Mos Eisley",
        population=60
    )
    
    # Simulate short distance travel
    print("\n1. Simulating Short Distance Travel...")
    short_travel_result = offline_simulator.simulate_travel_path(
        character=character,
        world_state=world_state,
        destination="Anchorhead",
        travel_method=TravelMethod.WALK
    )
    
    print(f"   Simulation ID: {short_travel_result.simulation_id}")
    print(f"   From: {character.location}")
    print(f"   To: Anchorhead")
    print(f"   Method: Walk")
    print(f"   Total Duration: {short_travel_result.total_duration:.2f} seconds")
    print(f"   Success Rate: {short_travel_result.success_rate:.2%}")
    print(f"   Steps Executed: {len(short_travel_result.steps)}")
    
    # Simulate long distance travel
    print("\n2. Simulating Long Distance Travel...")
    long_travel_result = offline_simulator.simulate_travel_path(
        character=character,
        world_state=world_state,
        destination="Theed",
        travel_method=TravelMethod.MOUNT
    )
    
    print(f"   Simulation ID: {long_travel_result.simulation_id}")
    print(f"   From: {character.location}")
    print(f"   To: Theed")
    print(f"   Method: Mount")
    print(f"   Total Duration: {long_travel_result.total_duration:.2f} seconds")
    print(f"   Success Rate: {long_travel_result.success_rate:.2%}")
    print(f"   Steps Executed: {len(long_travel_result.steps)}")
    
    return short_travel_result, long_travel_result

def demo_combat_loop_simulation():
    """Demonstrate combat loop simulation."""
    print("\n" + "="*60)
    print("DEMO: Combat Loop Simulation")
    print("="*60)
    
    # Create character
    character = offline_simulator.create_character_config(
        name="CombatTester",
        profession="Brawler",
        level=20
    )
    
    # Simulate PvE combat
    print("\n1. Simulating PvE Combat...")
    pve_result = offline_simulator.simulate_combat_loop(
        character=character,
        enemy_count=3,
        enemy_level=8,
        difficulty="normal"
    )
    
    print(f"   Simulation ID: {pve_result.simulation_id}")
    print(f"   Enemy Count: 3")
    print(f"   Enemy Level: 8")
    print(f"   Difficulty: Normal")
    print(f"   Total Duration: {pve_result.total_duration:.2f} seconds")
    print(f"   Success Rate: {pve_result.success_rate:.2%}")
    print(f"   XP Gained: {pve_result.xp_gained}")
    print(f"   Credits Earned: {pve_result.credits_earned}")
    print(f"   Steps Executed: {len(pve_result.steps)}")
    print(f"   Decisions Made: {pve_result.decisions_made}")
    
    # Simulate PvP combat
    print("\n2. Simulating PvP Combat...")
    pvp_result = offline_simulator.simulate_combat_loop(
        character=character,
        enemy_count=1,
        enemy_level=18,
        difficulty="hard"
    )
    
    print(f"   Simulation ID: {pvp_result.simulation_id}")
    print(f"   Enemy Count: 1")
    print(f"   Enemy Level: 18")
    print(f"   Difficulty: Hard")
    print(f"   Total Duration: {pvp_result.total_duration:.2f} seconds")
    print(f"   Success Rate: {pvp_result.success_rate:.2%}")
    print(f"   XP Gained: {pvp_result.xp_gained}")
    print(f"   Credits Earned: {pvp_result.credits_earned}")
    print(f"   Steps Executed: {len(pvp_result.steps)}")
    print(f"   Decisions Made: {pvp_result.decisions_made}")
    
    return pve_result, pvp_result

def demo_decision_tree_generation():
    """Demonstrate decision tree generation."""
    print("\n" + "="*60)
    print("DEMO: Decision Tree Generation")
    print("="*60)
    
    # Create a combat simulation for decision tree analysis
    character = offline_simulator.create_character_config(
        name="DecisionTester",
        profession="Brawler",
        level=15
    )
    
    combat_result = offline_simulator.simulate_combat_loop(
        character=character,
        enemy_count=2,
        enemy_level=10,
        difficulty="normal"
    )
    
    # Generate decision tree
    decision_tree = offline_simulator.generate_decision_tree(combat_result)
    
    print(f"\nGenerated {len(decision_tree)} decision nodes:")
    for i, node in enumerate(decision_tree[:5]):  # Show first 5 nodes
        print(f"\n   Node {i+1}:")
        print(f"     Type: {node.decision_type}")
        print(f"     Chosen Option: {node.chosen_option}")
        print(f"     Confidence: {node.confidence:.2%}")
        print(f"     Reasoning: {node.reasoning}")
        print(f"     Available Options: {', '.join(node.options)}")
    
    if len(decision_tree) > 5:
        print(f"\n   ... and {len(decision_tree) - 5} more decision nodes")
    
    return decision_tree

def demo_report_generation():
    """Demonstrate simulation report generation."""
    print("\n" + "="*60)
    print("DEMO: Report Generation")
    print("="*60)
    
    # Create a comprehensive simulation
    character = offline_simulator.create_character_config(
        name="ReportTester",
        profession="Brawler",
        level=18
    )
    
    world_state = offline_simulator.create_mock_world_state(
        location="Mos Eisley",
        population=80
    )
    
    # Run a quest simulation
    quest_result = offline_simulator.simulate_quest_step(
        quest_type=QuestType.KILL,
        character=character,
        world_state=world_state,
        quest_params={
            "target_count": 8,
            "target_type": "Jawa",
            "time_limit": 2400,
            "reward_xp": 800,
            "reward_credits": 1500
        }
    )
    
    # Generate and export report
    print("\nGenerating comprehensive simulation report...")
    report_file = offline_simulator.export_simulation_report(quest_result)
    
    print(f"   Report saved to: {report_file}")
    
    # Load and display report summary
    with open(report_file, 'r') as f:
        report_data = json.load(f)
    
    print("\nReport Summary:")
    print(f"   Simulation ID: {report_data['simulation_summary']['simulation_id']}")
    print(f"   Mode: {report_data['simulation_summary']['mode']}")
    print(f"   Total Steps: {report_data['performance_metrics']['total_steps']}")
    print(f"   Success Rate: {report_data['performance_metrics']['success_rate']:.2%}")
    print(f"   Total Duration: {report_data['performance_metrics']['total_duration']:.2f} seconds")
    print(f"   XP per Minute: {report_data['performance_metrics']['xp_per_minute']:.1f}")
    print(f"   Credits per Minute: {report_data['performance_metrics']['credits_per_minute']:.1f}")
    print(f"   Decision Nodes: {len(report_data['decision_tree'])}")
    
    # Show recommendations
    recommendations = report_data['recommendations']
    print(f"\nRecommendations:")
    for category, recs in recommendations.items():
        if recs:
            print(f"   {category.title()}:")
            for rec in recs:
                print(f"     - {rec}")
    
    return report_file

def demo_performance_comparison():
    """Demonstrate performance comparison between different configurations."""
    print("\n" + "="*60)
    print("DEMO: Performance Comparison")
    print("="*60)
    
    # Test different character configurations
    configurations = [
        {"name": "LowLevel", "profession": "Brawler", "level": 5},
        {"name": "MidLevel", "profession": "Brawler", "level": 15},
        {"name": "HighLevel", "profession": "Brawler", "level": 25}
    ]
    
    results = []
    
    for config in configurations:
        print(f"\nTesting {config['name']} configuration...")
        
        character = offline_simulator.create_character_config(
            name=config['name'],
            profession=config['profession'],
            level=config['level']
        )
        
        world_state = offline_simulator.create_mock_world_state(
            location="Mos Eisley",
            population=70
        )
        
        result = offline_simulator.simulate_quest_step(
            quest_type=QuestType.KILL,
            character=character,
            world_state=world_state,
            quest_params={
                "target_count": 5,
                "target_type": "Stormtrooper",
                "time_limit": 1800,
                "reward_xp": 500,
                "reward_credits": 1000
            }
        )
        
        results.append({
            "config": config,
            "result": result
        })
        
        print(f"   Level {config['level']}: {result.total_duration:.2f}s, {result.success_rate:.2%} success")
    
    # Compare results
    print("\nPerformance Comparison:")
    print("   Level | Duration | Success Rate | XP/Min | Credits/Min")
    print("   " + "-" * 50)
    
    for result_data in results:
        config = result_data['config']
        result = result_data['result']
        xp_per_min = (result.xp_gained / (result.total_duration / 60)) if result.total_duration > 0 else 0
        credits_per_min = (result.credits_earned / (result.total_duration / 60)) if result.total_duration > 0 else 0
        
        print(f"   {config['level']:5d} | {result.total_duration:8.2f}s | {result.success_rate:11.2%} | {xp_per_min:6.1f} | {credits_per_min:10.1f}")
    
    return results

def demo_error_handling():
    """Demonstrate error handling and edge cases."""
    print("\n" + "="*60)
    print("DEMO: Error Handling & Edge Cases")
    print("="*60)
    
    # Test with invalid parameters
    print("\n1. Testing with invalid character level...")
    try:
        character = offline_simulator.create_character_config(
            name="ErrorTester",
            profession="Brawler",
            level=-5  # Invalid level
        )
        print("   ✓ Invalid level handled gracefully")
    except Exception as e:
        print(f"   ✗ Error with invalid level: {e}")
    
    # Test with empty world state
    print("\n2. Testing with minimal world state...")
    try:
        minimal_world = offline_simulator.create_mock_world_state(
            location="TestLocation",
            population=0
        )
        print("   ✓ Minimal world state created successfully")
    except Exception as e:
        print(f"   ✗ Error with minimal world state: {e}")
    
    # Test simulation timeout
    print("\n3. Testing simulation timeout handling...")
    try:
        # Create a character that might cause long simulation
        character = offline_simulator.create_character_config(
            name="TimeoutTester",
            profession="Brawler",
            level=50  # High level for longer simulation
        )
        
        world_state = offline_simulator.create_mock_world_state(
            location="Mos Eisley",
            population=100
        )
        
        # This should complete within reasonable time
        result = offline_simulator.simulate_quest_step(
            quest_type=QuestType.KILL,
            character=character,
            world_state=world_state,
            quest_params={
                "target_count": 1,  # Small target to avoid timeout
                "target_type": "NPC",
                "time_limit": 300,
                "reward_xp": 100,
                "reward_credits": 200
            }
        )
        
        print(f"   ✓ Simulation completed in {result.total_duration:.2f} seconds")
        print(f"   ✓ Success rate: {result.success_rate:.2%}")
        
    except Exception as e:
        print(f"   ✗ Error during simulation: {e}")
    
    return True

def main():
    """Run all demonstration functions."""
    print("BATCH 109 - OFFLINE MODE SIMULATOR DEMONSTRATION")
    print("="*60)
    print("This demo showcases the offline simulator's capabilities for testing")
    print("bot logic without launching the game.")
    print("="*60)
    
    # Run all demos
    try:
        # Quest step simulation
        kill_result, collect_result = demo_quest_step_simulation()
        
        # Travel path simulation
        short_travel_result, long_travel_result = demo_travel_path_simulation()
        
        # Combat loop simulation
        pve_result, pvp_result = demo_combat_loop_simulation()
        
        # Decision tree generation
        decision_tree = demo_decision_tree_generation()
        
        # Report generation
        report_file = demo_report_generation()
        
        # Performance comparison
        performance_results = demo_performance_comparison()
        
        # Error handling
        error_handling_result = demo_error_handling()
        
        # Summary
        print("\n" + "="*60)
        print("DEMONSTRATION SUMMARY")
        print("="*60)
        print("✓ Quest Step Simulation: Completed")
        print("✓ Travel Path Simulation: Completed")
        print("✓ Combat Loop Simulation: Completed")
        print("✓ Decision Tree Generation: Completed")
        print("✓ Report Generation: Completed")
        print("✓ Performance Comparison: Completed")
        print("✓ Error Handling: Completed")
        print("\nAll simulation modes working correctly!")
        print("Reports saved to logs/simulator/ directory")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 