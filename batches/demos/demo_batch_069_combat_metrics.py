#!/usr/bin/env python3
"""
Demo script for Batch 069 - Combat Metrics Logger + DPS Analysis

This demo showcases:
1. Combat session logging with detailed metrics
2. Real-time DPS calculation and analysis
3. Ability usage tracking and optimization
4. Session history management and analysis
5. Performance analysis and recommendations
6. Dead skills detection
7. Most efficient rotations identification

Features demonstrated:
- Comprehensive combat session tracking
- Advanced DPS analysis with burst/sustained calculations
- Performance benchmarking and optimization
- Rotation analysis and dead skills detection
- XP/damage per hour calculations
- Session comparison and trending
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import the combat metrics modules
from modules.combat_metrics import (
    CombatLogger,
    DPSAnalyzer,
    CombatSessionManager,
    PerformanceAnalyzer,
    RotationOptimizer
)


def create_mock_combat_session(session_id: str, duration: float = 300.0) -> Dict[str, Any]:
    """Create a mock combat session for demonstration.
    
    Parameters
    ----------
    session_id : str
        Session ID
    duration : float
        Session duration in seconds
        
    Returns
    -------
    dict
        Mock session data
    """
    # Mock abilities and their characteristics
    abilities = {
        "headshot": {"damage": 400, "xp": 255, "cooldown": 5.0},
        "burst_fire": {"damage": 400, "xp": 382, "cooldown": 8.0},
        "rifle_shot": {"damage": 183, "xp": 172, "cooldown": 2.0},
        "sniper_shot": {"damage": 600, "xp": 450, "cooldown": 12.0},
        "grenade": {"damage": 300, "xp": 200, "cooldown": 15.0},
        "melee_attack": {"damage": 150, "xp": 100, "cooldown": 1.0},
        "shield_bash": {"damage": 200, "xp": 150, "cooldown": 6.0},
        "energy_blast": {"damage": 350, "xp": 280, "cooldown": 10.0}
    }
    
    # Mock enemies
    enemies = ["stormtrooper", "imperial_officer", "scout_trooper", "elite_trooper", "bounty_hunter"]
    
    # Generate session events
    events = []
    start_time = datetime.now() - timedelta(seconds=duration)
    
    total_damage = 0
    total_xp = 0
    kills = 0
    abilities_used = {}
    
    current_time = start_time
    while current_time < datetime.now():
        # Randomly select ability
        ability = random.choice(list(abilities.keys()))
        enemy = random.choice(enemies)
        
        # Get ability stats
        ability_stats = abilities[ability]
        damage = ability_stats["damage"]
        xp = ability_stats["xp"]
        
        # Add some randomness
        damage = int(damage * random.uniform(0.8, 1.2))
        xp = int(xp * random.uniform(0.9, 1.1))
        
        # Create event
        event = {
            "event_type": "ability_use",
            "timestamp": current_time.isoformat(),
            "ability_name": ability,
            "target": enemy,
            "damage_dealt": damage,
            "damage_type": "physical",
            "success": True,
            "cooldown_remaining": ability_stats["cooldown"],
            "xp_gained": xp
        }
        events.append(event)
        
        # Update totals
        total_damage += damage
        total_xp += xp
        
        # Track ability usage
        if ability not in abilities_used:
            abilities_used[ability] = 0
        abilities_used[ability] += 1
        
        # Randomly add kills
        if random.random() < 0.3:  # 30% chance of kill
            kill_event = {
                "event_type": "enemy_killed",
                "timestamp": current_time.isoformat(),
                "enemy_type": enemy,
                "xp_gained": xp * 2
            }
            events.append(kill_event)
            kills += 1
            total_xp += xp * 2
        
        # Advance time
        current_time += timedelta(seconds=random.uniform(2, 8))
    
    # Add session start/end events
    events.insert(0, {
        "event_type": "session_start",
        "timestamp": start_time.isoformat(),
        "session_id": session_id
    })
    
    events.append({
        "event_type": "session_end",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id
    })
    
    return {
        "session_id": session_id,
        "start_time": start_time.isoformat(),
        "end_time": datetime.now().isoformat(),
        "duration": duration,
        "events": events,
        "total_damage_dealt": total_damage,
        "total_xp_gained": total_xp,
        "kills": kills,
        "deaths": 0,
        "abilities_used": abilities_used,
        "targets_engaged": list(set(enemies)),
        "session_state": "completed"
    }


def demo_combat_logging():
    """Demonstrate combat session logging."""
    print("\n" + "="*60)
    print("⚔️  COMBAT SESSION LOGGING")
    print("="*60)
    
    # Initialize combat logger
    logger = CombatLogger()
    
    # Start a combat session
    session_id = logger.start_session("demo_combat_session_001")
    print(f"✅ Started combat session: {session_id}")
    
    # Simulate combat events
    print("\n🗡️  Simulating combat events:")
    
    # Mock abilities and enemies
    abilities = ["headshot", "burst_fire", "rifle_shot", "sniper_shot", "grenade"]
    enemies = ["stormtrooper", "imperial_officer", "scout_trooper"]
    
    for i in range(10):
        ability = random.choice(abilities)
        enemy = random.choice(enemies)
        damage = random.randint(100, 500)
        xp = random.randint(50, 300)
        
        # Log ability use
        logger.log_ability_use(
            ability_name=ability,
            target=enemy,
            damage_dealt=damage,
            damage_type="physical",
            success=True,
            cooldown_remaining=random.uniform(1, 10),
            xp_gained=xp
        )
        
        print(f"  • Used {ability} on {enemy} - {damage} damage, {xp} XP")
        
        # Randomly log kills
        if random.random() < 0.3:
            logger.log_enemy_kill(enemy, xp * 2)
            print(f"    💀 Killed {enemy}!")
        
        time.sleep(0.1)  # Simulate time passing
    
    # Get current session stats
    stats = logger.get_session_stats()
    print(f"\n📊 Current Session Stats:")
    print(f"  Duration: {stats['duration']:.1f} seconds")
    print(f"  Total Damage: {stats['total_damage_dealt']}")
    print(f"  Total XP: {stats['total_xp_gained']}")
    print(f"  Kills: {stats['kills']}")
    print(f"  Current DPS: {stats['current_dps']:.1f}")
    print(f"  Average DPS: {stats['average_dps']:.1f}")
    print(f"  Abilities Used: {stats['abilities_used']}")
    
    # End session
    summary = logger.end_session()
    print(f"\n🏁 Session ended!")
    print(f"  Final DPS: {summary['average_dps']:.1f}")
    print(f"  XP per Hour: {summary['xp_per_hour']:.1f}")
    print(f"  Damage per Hour: {summary['damage_per_hour']:.1f}")


def demo_dps_analysis():
    """Demonstrate DPS analysis capabilities."""
    print("\n" + "="*60)
    print("📊 DPS ANALYSIS")
    print("="*60)
    
    # Initialize DPS analyzer
    analyzer = DPSAnalyzer()
    
    # Create mock damage events
    print("\n🗡️  Adding damage events for analysis:")
    
    current_time = datetime.now()
    for i in range(20):
        damage = random.randint(100, 600)
        ability = random.choice(["headshot", "burst_fire", "rifle_shot", "sniper_shot"])
        
        # Add damage event
        analyzer.add_damage_event(
            damage=damage,
            timestamp=current_time - timedelta(seconds=random.uniform(0, 60)),
            ability_name=ability,
            target="enemy"
        )
        
        print(f"  • {ability}: {damage} damage")
    
    # Calculate various DPS metrics
    current_dps = analyzer.calculate_current_dps()
    burst_dps = analyzer.calculate_burst_dps()
    sustained_dps = analyzer.calculate_sustained_dps()
    
    print(f"\n📈 DPS Analysis Results:")
    print(f"  Current DPS: {current_dps:.1f}")
    print(f"  Burst DPS: {burst_dps:.1f}")
    print(f"  Sustained DPS: {sustained_dps:.1f}")
    
    # Analyze DPS trends
    trends = analyzer.analyze_dps_trends()
    print(f"\n📊 DPS Trends:")
    print(f"  Average DPS: {trends.get('average_dps', 0):.1f}")
    print(f"  Peak DPS: {trends.get('peak_dps', 0):.1f}")
    print(f"  Trend Direction: {trends.get('trend_direction', 'unknown')}")
    print(f"  Consistency: {trends.get('consistency', 'unknown')}")
    
    # Calculate damage efficiency
    efficiency = analyzer.calculate_damage_efficiency()
    print(f"\n⚡ Damage Efficiency:")
    for metric, value in efficiency.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.1f}")
        else:
            print(f"  {metric}: {value}")


def demo_session_management():
    """Demonstrate session management capabilities."""
    print("\n" + "="*60)
    print("📁 SESSION MANAGEMENT")
    print("="*60)
    
    # Initialize session manager
    manager = CombatSessionManager()
    
    # Create multiple mock sessions
    print("\n🗂️  Creating mock sessions:")
    
    sessions = []
    for i in range(5):
        session_data = create_mock_combat_session(f"demo_session_{i+1:03d}")
        sessions.append(session_data)
        
        # Save session
        success = manager.save_session(session_data)
        if success:
            print(f"  ✅ Saved session: {session_data['session_id']}")
        else:
            print(f"  ❌ Failed to save session: {session_data['session_id']}")
    
    # Get session statistics
    stats = manager.get_session_statistics()
    print(f"\n📊 Session Statistics:")
    print(f"  Total Sessions: {stats['total_sessions']}")
    print(f"  Total Duration: {stats['total_duration']:.1f} seconds")
    print(f"  Total Damage: {stats['total_damage_dealt']}")
    print(f"  Total XP: {stats['total_xp_gained']}")
    print(f"  Average DPS: {stats['average_dps']:.1f}")
    print(f"  Average XP per Session: {stats['average_xp_per_session']:.1f}")
    
    # Get recent sessions
    recent = manager.get_recent_sessions(3)
    print(f"\n🕒 Recent Sessions:")
    for session in recent:
        print(f"  • {session.session_id}: {session.average_dps:.1f} DPS, {session.xp_per_hour:.1f} XP/hour")
    
    # Compare sessions
    if len(sessions) >= 2:
        comparison = manager.compare_sessions([s['session_id'] for s in sessions[:2]])
        print(f"\n🔄 Session Comparison:")
        print(f"  Sessions Compared: {comparison['sessions_compared']}")
        print(f"  DPS Range: {comparison['dps_range']['min']:.1f} - {comparison['dps_range']['max']:.1f}")
        print(f"  XP Range: {comparison['xp_per_hour_range']['min']:.1f} - {comparison['xp_per_hour_range']['max']:.1f}")
        print(f"  Best Performing: {comparison['best_performing_session']}")


def demo_performance_analysis():
    """Demonstrate performance analysis capabilities."""
    print("\n" + "="*60)
    print("🎯 PERFORMANCE ANALYSIS")
    print("="*60)
    
    # Initialize performance analyzer
    analyzer = PerformanceAnalyzer()
    
    # Create mock session data
    session_data = create_mock_combat_session("performance_demo_session")
    
    # Analyze session performance
    performance = analyzer.analyze_session_performance(session_data)
    print(f"\n📊 Performance Analysis:")
    print(f"  Session ID: {performance.session_id}")
    print(f"  Duration: {performance.duration:.1f} seconds")
    print(f"  DPS: {performance.dps:.1f}")
    print(f"  XP per Hour: {performance.xp_per_hour:.1f}")
    print(f"  Efficiency Score: {performance.efficiency_score:.3f}")
    print(f"  Performance Grade: {performance.performance_grade}")
    
    # Compare to benchmarks
    print(f"\n🏆 Benchmark Comparison:")
    benchmarks = ["beginner", "intermediate", "advanced"]
    for benchmark in benchmarks:
        comparison = analyzer.compare_to_benchmark(performance, benchmark)
        print(f"  {benchmark.title()} Benchmark:")
        print(f"    Meets Benchmark: {comparison['meets_benchmark']}")
        print(f"    DPS Ratio: {comparison['metrics']['dps']['ratio']:.2f}")
        print(f"    XP Ratio: {comparison['metrics']['xp_per_hour']['ratio']:.2f}")
    
    # Calculate efficiency metrics
    xp_efficiency = analyzer.calculate_xp_efficiency(session_data)
    damage_efficiency = analyzer.calculate_damage_efficiency(session_data)
    
    print(f"\n⚡ Efficiency Metrics:")
    print(f"  XP per Hour: {xp_efficiency.get('xp_per_hour', 0):.1f}")
    print(f"  XP per Kill: {xp_efficiency.get('xp_per_kill', 0):.1f}")
    print(f"  Kill Efficiency: {xp_efficiency.get('kill_efficiency', 0):.1f}")
    print(f"  Damage per Ability: {damage_efficiency.get('damage_per_ability', 0):.1f}")
    print(f"  Abilities per Minute: {damage_efficiency.get('abilities_per_minute', 0):.1f}")
    
    # Get recommendations
    recommendations = analyzer.get_performance_recommendations(performance)
    print(f"\n💡 Performance Recommendations:")
    for rec in recommendations:
        print(f"  • {rec}")


def demo_rotation_optimization():
    """Demonstrate rotation optimization capabilities."""
    print("\n" + "="*60)
    print("🔄 ROTATION OPTIMIZATION")
    print("="*60)
    
    # Initialize rotation optimizer
    optimizer = RotationOptimizer()
    
    # Create multiple mock sessions for analysis
    print("\n🗂️  Analyzing combat rotations:")
    
    sessions = []
    for i in range(8):
        session_data = create_mock_combat_session(f"rotation_demo_{i+1:03d}")
        sessions.append(session_data)
        
        # Analyze rotation
        rotation = optimizer.analyze_session_rotation(session_data)
        print(f"  ✅ Analyzed rotation: {rotation.rotation_id}")
        print(f"    DPS: {rotation.dps:.1f}, XP/Hour: {rotation.xp_per_hour:.1f}")
    
    # Find dead skills
    dead_skills = optimizer.find_dead_skills(sessions)
    print(f"\n💀 Dead Skills Detection:")
    for skill in dead_skills[:3]:  # Show top 3
        print(f"  • {skill.skill_name}: {skill.usage_percentage:.1f}% usage")
        print(f"    Recommendation: {skill.recommended_action}")
    
    # Find most efficient rotations
    efficient_rotations = optimizer.find_most_efficient_rotations(sessions, 3)
    print(f"\n🏆 Most Efficient Rotations:")
    for i, rotation in enumerate(efficient_rotations, 1):
        print(f"  {i}. {rotation.rotation_id}")
        print(f"    Efficiency Score: {rotation.efficiency_score:.3f}")
        print(f"    DPS: {rotation.dps:.1f}, XP/Hour: {rotation.xp_per_hour:.1f}")
        print(f"    Abilities: {', '.join(rotation.abilities_used[:5])}")
    
    # Analyze ability synergy
    synergy = optimizer.analyze_ability_synergy(sessions)
    print(f"\n🤝 Ability Synergy Analysis:")
    print(f"  Most Used Combinations:")
    for combo in synergy['most_used_combinations'][:3]:
        print(f"    • {', '.join(combo['abilities'])} ({combo['usage_count']} times)")
    
    # Optimize a rotation
    current_abilities = ["headshot", "burst_fire", "rifle_shot", "sniper_shot", "grenade"]
    optimization = optimizer.optimize_rotation(current_abilities)
    print(f"\n🔧 Rotation Optimization:")
    print(f"  Current Abilities: {', '.join(optimization['current_abilities'])}")
    print(f"  Target DPS: {optimization['target_dps']}")
    print(f"  Target XP/Hour: {optimization['target_xp_per_hour']}")
    print(f"  Recommendations:")
    for rec in optimization['recommendations']:
        print(f"    • {rec}")
    
    # Get rotation statistics
    stats = optimizer.get_rotation_statistics()
    print(f"\n📊 Rotation Statistics:")
    print(f"  Total Rotations Analyzed: {stats['total_rotations_analyzed']}")
    print(f"  Average DPS: {stats['average_dps']:.1f}")
    print(f"  Average XP/Hour: {stats['average_xp_per_hour']:.1f}")
    print(f"  Dead Skills Found: {stats['dead_skills_found']}")


def demo_integrated_system():
    """Demonstrate the integrated combat metrics system."""
    print("\n" + "="*60)
    print("🎮 INTEGRATED COMBAT METRICS SYSTEM")
    print("="*60)
    
    # Initialize all components
    logger = CombatLogger()
    analyzer = DPSAnalyzer()
    manager = CombatSessionManager()
    performance_analyzer = PerformanceAnalyzer()
    optimizer = RotationOptimizer()
    
    print("\n🚀 Starting integrated combat session:")
    
    # Start session
    session_id = logger.start_session("integrated_demo_session")
    print(f"  ✅ Session started: {session_id}")
    
    # Simulate combat with real-time analysis
    print("\n⚔️  Simulating combat with real-time analysis:")
    
    abilities = ["headshot", "burst_fire", "rifle_shot", "sniper_shot", "grenade"]
    enemies = ["stormtrooper", "imperial_officer", "scout_trooper"]
    
    for i in range(15):
        ability = random.choice(abilities)
        enemy = random.choice(enemies)
        damage = random.randint(150, 600)
        xp = random.randint(100, 400)
        
        # Log ability use
        logger.log_ability_use(
            ability_name=ability,
            target=enemy,
            damage_dealt=damage,
            xp_gained=xp
        )
        
        # Add to DPS analyzer
        analyzer.add_damage_event(damage, ability_name=ability, target=enemy)
        
        # Show real-time stats
        if i % 5 == 0:
            current_dps = logger.get_current_dps()
            analyzer_dps = analyzer.calculate_current_dps()
            print(f"    📊 Real-time DPS: {current_dps:.1f} (Logger) / {analyzer_dps:.1f} (Analyzer)")
        
        # Random kills
        if random.random() < 0.25:
            logger.log_enemy_kill(enemy, xp * 2)
        
        time.sleep(0.1)
    
    # End session and get summary
    summary = logger.end_session()
    print(f"\n🏁 Session completed!")
    print(f"  Final DPS: {summary['average_dps']:.1f}")
    print(f"  XP per Hour: {summary['xp_per_hour']:.1f}")
    print(f"  Damage per Hour: {summary['damage_per_hour']:.1f}")
    
    # Save session
    session_data = manager.load_session(session_id)
    if session_data:
        print(f"  ✅ Session saved and loaded successfully")
        
        # Perform comprehensive analysis
        performance = performance_analyzer.analyze_session_performance(session_data)
        rotation = optimizer.analyze_session_rotation(session_data)
        
        print(f"\n📊 Comprehensive Analysis:")
        print(f"  Performance Grade: {performance.performance_grade}")
        print(f"  Efficiency Score: {performance.efficiency_score:.3f}")
        print(f"  Rotation Efficiency: {rotation.efficiency_score:.3f}")
        print(f"  Abilities Used: {len(rotation.abilities_used)}")
        
        # Get recommendations
        print(f"\n💡 Recommendations:")
        for rec in performance.recommendations[:3]:
            print(f"  • {rec}")
        for rec in rotation.recommendations[:3]:
            print(f"  • {rec}")


def main():
    """Main demonstration function."""
    print("⚔️ BATCH 069 - COMBAT METRICS LOGGER + DPS ANALYSIS")
    print("="*80)
    print("Comprehensive combat session tracking and analysis:")
    print("• Real-time DPS calculation and analysis")
    print("• Ability usage tracking and optimization")
    print("• Session history management")
    print("• Performance analysis and benchmarking")
    print("• Dead skills detection")
    print("• Most efficient rotations identification")
    print("• XP/damage per hour calculations")
    print("="*80)
    
    try:
        # Run demonstrations
        demo_combat_logging()
        demo_dps_analysis()
        demo_session_management()
        demo_performance_analysis()
        demo_rotation_optimization()
        demo_integrated_system()
        
        print("\n" + "="*80)
        print("✅ BATCH 069 DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*80)
        print("Key Features Demonstrated:")
        print("• Comprehensive combat session logging")
        print("• Advanced DPS analysis with burst/sustained calculations")
        print("• Performance benchmarking and optimization")
        print("• Rotation analysis and dead skills detection")
        print("• Session comparison and trending analysis")
        print("• XP/damage per hour calculations")
        print("• Integrated combat metrics system")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 