#!/usr/bin/env python3
"""Demo script for Batch 059 - Combat Metrics Logger + DPS Analysis.

This demo showcases the combat metrics tracking system including:
- Combat session tracking
- Skill usage monitoring
- DPS analysis
- Performance recommendations
- JSON log generation
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

from core.combat_metrics_logger import CombatMetricsLogger
from core.dps_analyzer import DPSAnalyzer
from core.combat_metrics_integration import CombatMetricsIntegration
from android_ms11.utils.logging_utils import log_event

def simulate_combat_session(metrics_logger: CombatMetricsLogger, 
                          session_name: str = "Demo Combat Session") -> None:
    """Simulate a combat session with various skills and enemies.
    
    Parameters
    ----------
    metrics_logger : CombatMetricsLogger
        Metrics logger to record combat data
    session_name : str
        Name for the combat session
    """
    print(f"\n{'='*60}")
    print(f"SIMULATING COMBAT SESSION: {session_name}")
    print(f"{'='*60}")
    
    # Enemy types and their characteristics
    enemies = [
        {"type": "Stormtrooper", "level": 5, "hp": 80},
        {"type": "Bounty Hunter", "level": 8, "hp": 120},
        {"type": "Jedi Knight", "level": 12, "hp": 150},
        {"type": "Sith Lord", "level": 15, "hp": 200},
        {"type": "Droid Commander", "level": 10, "hp": 100}
    ]
    
    # Available skills with damage ranges
    skills = {
        "Rifle Shot": {"damage_range": (20, 35), "cooldown": 1.5},
        "Heavy Blast": {"damage_range": (40, 60), "cooldown": 3.0},
        "Precision Strike": {"damage_range": (50, 80), "cooldown": 8.0},
        "Rapid Fire": {"damage_range": (15, 25), "cooldown": 0.8},
        "Sniper Shot": {"damage_range": (70, 100), "cooldown": 12.0},
        "Grenade Toss": {"damage_range": (30, 50), "cooldown": 5.0},
        "Medic Heal": {"damage_range": (0, 0), "cooldown": 10.0},
        "Combat Buff": {"damage_range": (0, 0), "cooldown": 15.0}
    }
    
    # Simulate multiple combat encounters
    for i, enemy in enumerate(enemies):
        print(f"\n--- Combat {i+1}: vs {enemy['type']} (Level {enemy['level']}) ---")
        
        # Start combat session
        combat_id = metrics_logger.start_combat_session(
            enemy_type=enemy["type"], 
            enemy_level=enemy["level"]
        )
        
        enemy_hp = enemy["hp"]
        combat_rounds = 0
        max_rounds = 15  # Prevent infinite combat
        
        while enemy_hp > 0 and combat_rounds < max_rounds:
            combat_rounds += 1
            
            # Select a skill to use
            skill_name = random.choice(list(skills.keys()))
            skill_data = skills[skill_name]
            
            # Calculate damage
            damage = random.randint(*skill_data["damage_range"])
            
            # Apply damage to enemy
            enemy_hp = max(0, enemy_hp - damage)
            
            # Record skill usage
            metrics_logger.record_skill_usage(
                skill_name=skill_name,
                damage_dealt=damage,
                target=enemy["type"],
                cooldown=skill_data["cooldown"]
            )
            
            print(f"  Round {combat_rounds}: Used {skill_name} - {damage} damage")
            print(f"    Enemy HP: {enemy_hp}/{enemy['hp']}")
            
            # Small delay to simulate combat timing
            time.sleep(0.1)
        
        # End combat session
        result = "victory" if enemy_hp <= 0 else "timeout"
        combat_summary = metrics_logger.end_combat_session(
            result=result,
            enemy_hp_remaining=enemy_hp
        )
        
        print(f"  Combat ended: {result}")
        if combat_summary:
            print(f"  Duration: {combat_summary.get('duration', 0):.1f}s")
            print(f"  Total Damage: {combat_summary.get('damage_dealt', 0)}")
            print(f"  Average DPS: {combat_summary.get('average_dps', 0):.1f}")

def demonstrate_metrics_analysis(metrics_logger: CombatMetricsLogger) -> None:
    """Demonstrate the metrics analysis capabilities.
    
    Parameters
    ----------
    metrics_logger : CombatMetricsLogger
        Metrics logger with combat data
    """
    print(f"\n{'='*60}")
    print("METRICS ANALYSIS DEMONSTRATION")
    print(f"{'='*60}")
    
    # Create DPS analyzer
    dps_analyzer = DPSAnalyzer(metrics_logger)
    
    # Save session log
    log_path = metrics_logger.save_session_log()
    print(f"Session log saved to: {log_path}")
    
    # Load session data
    session_data = metrics_logger.load_session_log(log_path)
    
    # Analyze performance
    analysis = dps_analyzer.analyze_session_performance(session_data)
    
    # Display analysis results
    print("\n--- PERFORMANCE ANALYSIS ---")
    
    # Overall performance
    overall = analysis.get("overall_performance", {})
    print(f"Total Damage: {overall.get('total_damage', 0):,}")
    print(f"Total Combats: {overall.get('total_combats', 0)}")
    print(f"Session Duration: {overall.get('session_duration', 0):.1f}s")
    print(f"Overall DPS: {overall.get('overall_dps', 0):.1f}")
    
    # Skill analysis
    skill_analysis = analysis.get("skill_analysis", {})
    if skill_analysis:
        print("\n--- SKILL PERFORMANCE ---")
        # Sort skills by effectiveness
        skill_ranking = sorted(skill_analysis.items(), 
                             key=lambda x: x[1]["effectiveness_ratio"], 
                             reverse=True)
        
        for skill_name, stats in skill_ranking:
            print(f"{skill_name}:")
            print(f"  Usage: {stats['usage_count']} times")
            print(f"  Total Damage: {stats['total_damage']:,}")
            print(f"  Average Damage: {stats['average_damage']:.1f}")
            print(f"  Effectiveness: {stats['effectiveness_ratio']:.3f}")
    
    # Combat efficiency
    combat_efficiency = analysis.get("combat_efficiency", {})
    if combat_efficiency:
        print("\n--- COMBAT EFFICIENCY ---")
        print(f"Average Combat Duration: {combat_efficiency.get('average_combat_duration', 0):.1f}s")
        print(f"Damage Consistency: {combat_efficiency.get('damage_consistency', 0):.1f}")
        print(f"Average Damage per Combat: {combat_efficiency.get('average_damage_per_combat', 0):.1f}")
    
    # Recommendations
    recommendations = analysis.get("recommendations", {})
    if recommendations:
        print("\n--- OPTIMIZATION RECOMMENDATIONS ---")
    for category, recs in recommendations.items():
        if recs:
                print(f"{category.replace('_', ' ').title()}:")
            for rec in recs:
                print(f"  • {rec}")
    
def demonstrate_skill_ranking(metrics_logger: CombatMetricsLogger) -> None:
    """Demonstrate skill effectiveness ranking.
    
    Parameters
    ----------
    metrics_logger : CombatMetricsLogger
        Metrics logger with combat data
    """
    print(f"\n{'='*60}")
    print("SKILL EFFECTIVENESS RANKING")
    print(f"{'='*60}")
    
    # Get skill effectiveness ranking
    skill_ranking = metrics_logger.get_skill_effectiveness_ranking()
    
    if skill_ranking:
        print("\nRanking of skills by effectiveness:")
        for i, (skill_name, stats) in enumerate(skill_ranking, 1):
            print(f"{i}. {skill_name}")
            print(f"   Total Damage: {stats['total_damage']:,}")
            print(f"   Usage Count: {stats['usage_count']}")
            print(f"   Average Damage: {stats['average_damage']:.1f}")
            print(f"   Effectiveness Score: {stats['effectiveness_score']:.1f}")
            print()
    else:
        print("No skills used in this session.")

def demonstrate_ai_recommendations(metrics_logger: CombatMetricsLogger) -> None:
    """Demonstrate AI combat behavior recommendations.
    
    Parameters
    ----------
    metrics_logger : CombatMetricsLogger
        Metrics logger with combat data
    """
    print(f"\n{'='*60}")
    print("AI COMBAT RECOMMENDATIONS")
    print(f"{'='*60}")
    
    # Get AI recommendations
    recommendations = metrics_logger.get_ai_combat_recommendations()
    
    if recommendations:
        for category, data in recommendations.items():
            if data:
                print(f"\n{category.replace('_', ' ').title()}:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            print(f"  {key}:")
                            for sub_key, sub_value in value.items():
                                print(f"    {sub_key}: {sub_value}")
                        else:
                            print(f"  {key}: {value}")
                elif isinstance(data, list):
                    for item in data:
                        print(f"  • {item}")
                else:
                    print(f"  {data}")
        else:
        print("No AI recommendations available for this session.")

def demonstrate_unused_abilities(metrics_logger: CombatMetricsLogger) -> None:
    """Demonstrate unused abilities detection.
    
    Parameters
    ----------
    metrics_logger : CombatMetricsLogger
        Metrics logger with combat data
    """
    print(f"\n{'='*60}")
    print("UNUSED ABILITIES DETECTION")
    print(f"{'='*60}")
    
    # Define all available abilities
    all_abilities = [
        "Rifle Shot", "Heavy Blast", "Precision Strike", "Rapid Fire",
        "Sniper Shot", "Grenade Toss", "Medic Heal", "Combat Buff",
        "Stealth Mode", "Shield Wall", "Energy Drain", "Force Push"
    ]
    
    # Get unused abilities
    unused_abilities = metrics_logger.get_unused_abilities_recommendations(all_abilities)
    
    if unused_abilities:
        print(f"\nUnused abilities that could be pruned ({len(unused_abilities)}):")
        for ability in unused_abilities:
            print(f"  • {ability}")
    else:
        print("\nAll abilities were used in this session.")

def demonstrate_session_summary(metrics_logger: CombatMetricsLogger) -> None:
    """Demonstrate session summary capabilities.
    
    Parameters
    ----------
    metrics_logger : CombatMetricsLogger
        Metrics logger with combat data
    """
    print(f"\n{'='*60}")
    print("SESSION SUMMARY")
    print(f"{'='*60}")
    
    # Get session summary
    summary = metrics_logger.get_session_summary()
    
    print(f"\nSession ID: {summary.get('session_id', 'Unknown')}")
    print(f"Duration: {summary.get('duration', 0):.1f}s")
    print(f"Total Combats: {summary.get('total_combats', 0)}")
    print(f"Total Damage: {summary.get('total_damage', 0):,}")
    print(f"Current DPS: {summary.get('current_dps', 0):.1f}")
    print(f"Skills Used: {summary.get('skills_used_count', 0)}")
    print(f"Enemies Killed: {summary.get('enemies_killed_count', 0)}")
    
    top_skill = summary.get('top_skill')
    if top_skill:
        print(f"Top Skill: {top_skill}")

def main():
    """Main demo function."""
    print("BATCH 059 - COMBAT METRICS LOGGER + DPS ANALYSIS DEMO")
    print("=" * 60)
    print("This demo showcases the combat metrics tracking system")
    print("including damage tracking, skill analysis, and DPS optimization.")
    print()
    
    # Create metrics logger
    metrics_logger = CombatMetricsLogger(session_id="demo_session_001")
    
    try:
        # Simulate combat sessions
        simulate_combat_session(metrics_logger, "Primary Combat Session")
        
        # Demonstrate various analysis features
        demonstrate_session_summary(metrics_logger)
        demonstrate_skill_ranking(metrics_logger)
        demonstrate_ai_recommendations(metrics_logger)
        demonstrate_unused_abilities(metrics_logger)
        demonstrate_metrics_analysis(metrics_logger)
        
        # Generate and save analysis report
        print(f"\n{'='*60}")
        print("GENERATING ANALYSIS REPORT")
        print(f"{'='*60}")
        
        dps_analyzer = DPSAnalyzer(metrics_logger)
        log_path = metrics_logger.save_session_log()
        session_data = metrics_logger.load_session_log(log_path)
        
        report = dps_analyzer.generate_report(session_data)
        print("\n" + report)
        
        # Save report to file
        report_path = dps_analyzer.save_analysis_report(session_data)
        print(f"\nAnalysis report saved to: {report_path}")
        
        print(f"\n{'='*60}")
        print("DEMO COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print("The combat metrics system is now ready for integration")
        print("with the main combat engine for automatic tracking.")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 