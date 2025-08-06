#!/usr/bin/env python3
"""
Demo script for Batch 107 - AI Tactical Engine (PvE & PvP Fight Decisions)

This script demonstrates the AI Tactical Engine's capabilities:
- Learning from combat logs
- Analyzing weapon effectiveness vs enemy types
- Discovering optimal tactical patterns
- Providing tactical recommendations
- Syncing data to user sessions
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from core.combat_tactics_engine import (
    CombatTacticsEngine,
    CombatEvent,
    CombatSession,
    CombatResult,
    TacticalAction
)


def create_sample_combat_data():
    """Create sample combat data for demonstration."""
    
    # Create sample combat events
    sample_events = [
        {
            "event_type": "ability_use",
            "timestamp": "2025-08-01T12:13:24.806066",
            "ability_name": "rifle_shot",
            "target": "stormtrooper",
            "damage_dealt": 215,
            "damage_type": "physical",
            "success": True,
            "enemy_type": "stormtrooper",
            "xp_gained": 185,
            "player_health": 100,
            "target_health": 100
        },
        {
            "event_type": "ability_use",
            "timestamp": "2025-08-01T12:13:31.549268",
            "ability_name": "headshot",
            "target": "stormtrooper",
            "damage_dealt": 478,
            "damage_type": "physical",
            "success": True,
            "enemy_type": "stormtrooper",
            "xp_gained": 271,
            "player_health": 85,
            "target_health": 30
        },
        {
            "event_type": "enemy_killed",
            "timestamp": "2025-08-01T12:13:44.566865",
            "enemy_type": "stormtrooper",
            "xp_gained": 542,
            "player_health": 85,
            "target_health": 0
        },
        {
            "event_type": "ability_use",
            "timestamp": "2025-08-01T12:13:48.904984",
            "ability_name": "heal_self",
            "target": "self",
            "damage_dealt": 0,
            "damage_type": "healing",
            "success": True,
            "enemy_type": "imperial_officer",
            "xp_gained": 50,
            "player_health": 30,
            "target_health": 100
        },
        {
            "event_type": "ability_use",
            "timestamp": "2025-08-01T12:13:51.266846",
            "ability_name": "shield_bash",
            "target": "imperial_officer",
            "damage_dealt": 196,
            "damage_type": "physical",
            "success": True,
            "enemy_type": "imperial_officer",
            "xp_gained": 156,
            "player_health": 95,
            "target_health": 80
        }
    ]
    
    # Create sample combat sessions
    sample_sessions = [
        {
            "session_id": "demo_combat_001",
            "start_time": "2025-08-01T12:13:24.806066",
            "end_time": "2025-08-01T12:14:24.806066",
            "duration": 60.0,
            "events": sample_events,
            "result": "victory",
            "player_build": {
                "weapon_type": "rifle",
                "role": "rifleman",
                "primary_weapon": "rifle"
            },
            "enemy_type": "stormtrooper",
            "tactics_used": ["opening_burst", "defensive"],
            "success_rate": 0.8,
            "damage_efficiency": 1.2
        },
        {
            "session_id": "demo_combat_002",
            "start_time": "2025-08-01T12:15:24.806066",
            "end_time": "2025-08-01T12:16:24.806066",
            "duration": 60.0,
            "events": sample_events,
            "result": "victory",
            "player_build": {
                "weapon_type": "pistol",
                "role": "pistoleer",
                "primary_weapon": "pistol"
            },
            "enemy_type": "imperial_officer",
            "tactics_used": ["defensive", "heal"],
            "success_rate": 0.9,
            "damage_efficiency": 0.8
        },
        {
            "session_id": "demo_combat_003",
            "start_time": "2025-08-01T12:17:24.806066",
            "end_time": "2025-08-01T12:18:24.806066",
            "duration": 60.0,
            "events": sample_events,
            "result": "defeat",
            "player_build": {
                "weapon_type": "melee",
                "role": "brawler",
                "primary_weapon": "sword"
            },
            "enemy_type": "scout_trooper",
            "tactics_used": ["aggressive", "burst"],
            "success_rate": 0.3,
            "damage_efficiency": 0.5
        }
    ]
    
    return sample_sessions


def create_sample_combat_logs():
    """Create sample combat log files for the engine to analyze."""
    
    # Ensure logs directory exists
    logs_dir = Path("logs/combat")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    sample_sessions = create_sample_combat_data()
    
    # Write sample combat log files
    for i, session_data in enumerate(sample_sessions, 1):
        log_file = logs_dir / f"combat_stats_demo_session_{i:03d}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"[DEMO] Created combat log: {log_file}")
    
    return len(sample_sessions)


def demo_engine_initialization():
    """Demonstrate engine initialization."""
    print("\n" + "="*60)
    print("DEMO: AI Tactical Engine Initialization")
    print("="*60)
    
    # Initialize the engine
    engine = CombatTacticsEngine(
        combat_logs_dir="logs/combat",
        tactics_data_dir="data/combat_tactics",
        session_logs_dir="logs/sessions"
    )
    
    print(f"[DEMO] Engine initialized successfully")
    print(f"[DEMO] Loaded {len(engine.combat_sessions)} combat sessions")
    print(f"[DEMO] Loaded {len(engine.weapon_resist_data)} weapon resistance entries")
    print(f"[DEMO] Loaded {len(engine.tactical_insights)} tactical insights")
    
    return engine


def demo_combat_analysis(engine):
    """Demonstrate combat log analysis."""
    print("\n" + "="*60)
    print("DEMO: Combat Log Analysis")
    print("="*60)
    
    # Analyze combat logs
    engine.analyze_combat_logs()
    
    print(f"[DEMO] Analysis completed")
    print(f"[DEMO] Updated weapon resistance data: {len(engine.weapon_resist_data)} entries")
    print(f"[DEMO] Updated tactical insights: {len(engine.tactical_insights)} insights")
    
    # Show some weapon resistance data
    print("\n[DEMO] Weapon Resistance Data:")
    for key, resist in list(engine.weapon_resist_data.items())[:3]:
        print(f"  {key}: effectiveness={resist.effectiveness:.2f}, samples={resist.sample_size}")
    
    # Show some tactical insights
    print("\n[DEMO] Tactical Insights:")
    for key, insight in list(engine.tactical_insights.items())[:3]:
        print(f"  {key}: {insight.best_action.value} (success_rate={insight.success_rate:.2f})")


def demo_tactical_recommendations(engine):
    """Demonstrate tactical recommendations."""
    print("\n" + "="*60)
    print("DEMO: Tactical Recommendations")
    print("="*60)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Rifleman vs Stormtrooper (Opening)",
            "enemy_type": "stormtrooper",
            "player_build": {"weapon_type": "rifle", "role": "rifleman"},
            "situation": "opening",
            "player_health": 100,
            "target_health": 100
        },
        {
            "name": "Pistoleer vs Imperial Officer (Low Health)",
            "enemy_type": "imperial_officer",
            "player_build": {"weapon_type": "pistol", "role": "pistoleer"},
            "situation": "low_health",
            "player_health": 25,
            "target_health": 60
        },
        {
            "name": "Brawler vs Scout Trooper (High Damage)",
            "enemy_type": "scout_trooper",
            "player_build": {"weapon_type": "melee", "role": "brawler"},
            "situation": "high_damage",
            "player_health": 70,
            "target_health": 80
        }
    ]
    
    for scenario in test_scenarios:
        action = engine.get_optimal_action(
            enemy_type=scenario["enemy_type"],
            player_build=scenario["player_build"],
            situation=scenario["situation"],
            player_health=scenario["player_health"],
            target_health=scenario["target_health"]
        )
        
        print(f"[DEMO] {scenario['name']}: {action.value}")


def demo_combat_metrics(engine):
    """Demonstrate combat metrics calculation."""
    print("\n" + "="*60)
    print("DEMO: Combat Metrics")
    print("="*60)
    
    metrics = engine.get_combat_metrics()
    
    print(f"[DEMO] Total Combats: {metrics.total_combats}")
    print(f"[DEMO] Victories: {metrics.victories}")
    print(f"[DEMO] Defeats: {metrics.defeats}")
    print(f"[DEMO] Victory Rate: {metrics.victories / metrics.total_combats * 100:.1f}%" if metrics.total_combats > 0 else "[DEMO] Victory Rate: N/A")
    print(f"[DEMO] Average Damage Dealt: {metrics.avg_damage_dealt:.1f}")
    print(f"[DEMO] Average Damage Taken: {metrics.avg_damage_taken:.1f}")
    print(f"[DEMO] Average Combat Duration: {metrics.avg_combat_duration:.1f}s")
    
    print("\n[DEMO] Most Effective Weapons:")
    for weapon, effectiveness in metrics.most_effective_weapons:
        print(f"  {weapon}: {effectiveness:.2f}")
    
    print("\n[DEMO] Most Effective Tactics:")
    for tactic, success_rate in metrics.most_effective_tactics:
        print(f"  {tactic}: {success_rate:.2f}")
    
    print("\n[DEMO] Enemy Type Performance:")
    for enemy, win_rate in metrics.enemy_type_performance.items():
        print(f"  {enemy}: {win_rate:.1%}")


def demo_session_sync(engine):
    """Demonstrate syncing tactical data to user sessions."""
    print("\n" + "="*60)
    print("DEMO: Session Sync")
    print("="*60)
    
    # Create a sample session file
    session_dir = Path("logs/sessions")
    session_dir.mkdir(parents=True, exist_ok=True)
    
    sample_session = {
        "session_id": "demo_session_001",
        "discord_id": "demo_user_123",
        "start_time": "2025-08-01T12:00:00.000000",
        "end_time": "2025-08-01T13:00:00.000000",
        "total_xp": 1500,
        "quests_completed": 3,
        "locations_visited": ["Mos Eisley", "Anchorhead"],
        "mode": "combat"
    }
    
    session_file = session_dir / "session_demo_001.json"
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(sample_session, f, indent=2)
    
    print(f"[DEMO] Created sample session: {session_file}")
    
    # Sync tactical data
    success = engine.sync_to_user_sessions("demo_user_123")
    
    if success:
        print("[DEMO] Successfully synced tactical data to user sessions")
        
        # Show updated session data
        with open(session_file, 'r', encoding='utf-8') as f:
            updated_session = json.load(f)
        
        if 'tactical_metrics' in updated_session:
            tactical_metrics = updated_session['tactical_metrics']
            print(f"[DEMO] Added tactical metrics:")
            print(f"  Total Combats: {tactical_metrics['total_combats']}")
            print(f"  Victory Rate: {tactical_metrics['victory_rate']:.1%}")
            print(f"  Damage Efficiency: {tactical_metrics['avg_damage_efficiency']:.2f}")
            print(f"  Most Effective Weapon: {tactical_metrics['most_effective_weapon']}")
            print(f"  Most Effective Tactic: {tactical_metrics['most_effective_tactic']}")
    else:
        print("[DEMO] Failed to sync tactical data")


def demo_report_export(engine):
    """Demonstrate tactical report export."""
    print("\n" + "="*60)
    print("DEMO: Tactical Report Export")
    print("="*60)
    
    # Export JSON report
    json_report = engine.export_tactical_report(format='json')
    print(f"[DEMO] Exported JSON report: {json_report}")
    
    # Export text report
    txt_report = engine.export_tactical_report(format='txt')
    print(f"[DEMO] Exported text report: {txt_report}")
    
    # Show report content
    print("\n[DEMO] Text Report Preview:")
    with open(txt_report, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[:20]:  # Show first 20 lines
            print(line.rstrip())


def demo_learning_progression():
    """Demonstrate how the engine learns over time."""
    print("\n" + "="*60)
    print("DEMO: Learning Progression")
    print("="*60)
    
    # Create engine with minimal data
    engine = CombatTacticsEngine()
    
    print("[DEMO] Initial state:")
    print(f"  Weapon resistance entries: {len(engine.weapon_resist_data)}")
    print(f"  Tactical insights: {len(engine.tactical_insights)}")
    
    # Add more combat data
    print("\n[DEMO] Adding more combat data...")
    create_sample_combat_logs()
    
    # Re-analyze
    engine.analyze_combat_logs()
    
    print("\n[DEMO] After learning:")
    print(f"  Weapon resistance entries: {len(engine.weapon_resist_data)}")
    print(f"  Tactical insights: {len(engine.tactical_insights)}")
    
    # Show learning progression
    print("\n[DEMO] Learning Progression:")
    for key, insight in engine.tactical_insights.items():
        print(f"  Learned: {key} -> {insight.best_action.value} (confidence: {insight.confidence:.2f})")


def main():
    """Run the complete demonstration."""
    print("AI Tactical Engine (Batch 107) - Demonstration")
    print("="*60)
    
    # Create sample data
    print("\n[DEMO] Creating sample combat data...")
    num_logs = create_sample_combat_logs()
    print(f"[DEMO] Created {num_logs} sample combat logs")
    
    # Initialize engine
    engine = demo_engine_initialization()
    
    # Run demonstrations
    demo_combat_analysis(engine)
    demo_tactical_recommendations(engine)
    demo_combat_metrics(engine)
    demo_session_sync(engine)
    demo_report_export(engine)
    demo_learning_progression()
    
    print("\n" + "="*60)
    print("DEMO: Integration with Existing Combat System")
    print("="*60)
    
    print("[DEMO] The AI Tactical Engine integrates with existing systems:")
    print("  - Uses existing combat logs from logs/combat/")
    print("  - Works with current session management")
    print("  - Provides tactical recommendations to existing combat AI")
    print("  - Syncs data to user session logs")
    print("  - Exports reports for analysis")
    
    print("\n[DEMO] To use in production:")
    print("  1. Import: from core.combat_tactics_engine import combat_tactics_engine")
    print("  2. Get recommendations: action = engine.get_optimal_action(...)")
    print("  3. Analyze logs: engine.analyze_combat_logs()")
    print("  4. Sync to sessions: engine.sync_to_user_sessions(discord_id)")
    
    print("\n[DEMO] Demonstration completed successfully!")


if __name__ == "__main__":
    main() 