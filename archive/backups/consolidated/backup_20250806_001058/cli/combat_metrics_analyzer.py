#!/usr/bin/env python3
"""Command-line interface for Combat Metrics Analyzer."""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.combat_metrics_analyzer import (
    CombatMetricsAnalyzer,
    SkillEffectiveness,
    DPSWindow
)


def print_session_summary(analyzer: CombatMetricsAnalyzer) -> None:
    """Print current session summary."""
    if not analyzer.current_session:
        print("No active session")
        return
    
    session = analyzer.current_session
    print("\n=== Combat Session Summary ===")
    print(f"Session ID: {session.session_id}")
    print(f"Start Time: {session.start_time}")
    print(f"Duration: {session.session_duration_minutes:.2f} minutes")
    print(f"State: {session.session_state}")
    
    print(f"\nCombat Metrics:")
    print(f"  Total Damage: {session.total_damage_dealt:,}")
    print(f"  Overall DPS: {session.overall_dps:.2f}")
    print(f"  Peak DPS: {session.peak_dps:.2f}")
    print(f"  Average DPS: {session.average_dps:.2f}")
    print(f"  Kills: {session.kills}")
    print(f"  Deaths: {session.deaths}")
    print(f"  KDR: {session.kills / max(session.deaths, 1):.2f}")
    
    print(f"\nEfficiency Metrics:")
    print(f"  Total XP: {session.total_xp_gained:,}")
    print(f"  Damage Efficiency: {session.damage_efficiency:.2f}")
    print(f"  Skill Utilization: {session.skill_utilization:.1f}%")
    
    print(f"\nTargets Engaged: {len(session.targets_engaged)}")
    if session.targets_engaged:
        print(f"  {', '.join(session.targets_engaged[:5])}")


def print_skill_analysis(analyzer: CombatMetricsAnalyzer, skill_name: str = None) -> None:
    """Print skill analysis."""
    if not analyzer.current_session or not analyzer.current_session.skill_analysis:
        print("No skill analysis available")
        return
    
    skill_analysis = analyzer.current_session.skill_analysis
    
    if skill_name:
        if skill_name not in skill_analysis:
            print(f"Skill '{skill_name}' not found in analysis")
            return
        
        analysis = skill_analysis[skill_name]
        print(f"\n=== Skill Analysis: {skill_name} ===")
        print(f"Usage Count: {analysis.usage_count}")
        print(f"Total Damage: {analysis.total_damage:,}")
        print(f"Average Damage: {analysis.average_damage:.1f}")
        print(f"Damage Range: {analysis.min_damage} - {analysis.max_damage}")
        print(f"Success Rate: {analysis.success_rate:.1%}")
        print(f"Total XP: {analysis.total_xp:,}")
        print(f"Average XP per Use: {analysis.average_xp_per_use:.1f}")
        print(f"Effectiveness: {analysis.effectiveness.value}")
        print(f"Cooldown Usage: {analysis.cooldown_usage:.1f}%")
        print(f"Damage per Second: {analysis.damage_per_second:.2f}")
        print(f"Damage per XP: {analysis.damage_per_xp:.2f}")
        
        if analysis.recommendations:
            print(f"\nRecommendations:")
            for rec in analysis.recommendations:
                print(f"  • {rec}")
    else:
        print(f"\n=== Skill Analysis ({len(skill_analysis)} skills) ===")
        
        # Sort by effectiveness
        effectiveness_order = [
            SkillEffectiveness.EXCELLENT,
            SkillEffectiveness.GOOD,
            SkillEffectiveness.AVERAGE,
            SkillEffectiveness.POOR,
            SkillEffectiveness.UNUSED
        ]
        
        for effectiveness in effectiveness_order:
            skills = [name for name, analysis in skill_analysis.items() 
                     if analysis.effectiveness == effectiveness]
            
            if skills:
                print(f"\n{effectiveness.value.title()} Skills:")
                for skill_name in skills:
                    analysis = skill_analysis[skill_name]
                    print(f"  {skill_name}: {analysis.usage_count} uses, "
                          f"{analysis.average_damage:.0f} avg damage, "
                          f"{analysis.cooldown_usage:.0f}% cooldown usage")


def print_skill_rankings(analyzer: CombatMetricsAnalyzer) -> None:
    """Print skill rankings."""
    rankings = analyzer.get_skill_rankings()
    
    if not rankings:
        print("No skill rankings available")
        return
    
    print(f"\n=== Skill Rankings ===")
    for i, (skill_name, score) in enumerate(rankings, 1):
        print(f"{i:2d}. {skill_name}: {score:.2f}")


def print_dps_analysis(analyzer: CombatMetricsAnalyzer) -> None:
    """Print DPS analysis."""
    if not analyzer.current_session or not analyzer.current_session.dps_data:
        print("No DPS data available")
        return
    
    dps_data = analyzer.current_session.dps_data
    
    print(f"\n=== DPS Analysis ===")
    print(f"Total DPS Data Points: {len(dps_data)}")
    
    if dps_data:
        dps_values = [point.dps for point in dps_data]
        print(f"Average DPS: {analyzer.current_session.average_dps:.2f}")
        print(f"Peak DPS: {analyzer.current_session.peak_dps:.2f}")
        print(f"Min DPS: {min(dps_values):.2f}")
        print(f"Max DPS: {max(dps_values):.2f}")
        
        # Show recent DPS values
        print(f"\nRecent DPS Values:")
        for point in dps_data[-10:]:  # Last 10 points
            print(f"  {point.timestamp.strftime('%H:%M:%S')}: {point.dps:.2f}")


def print_recommendations(analyzer: CombatMetricsAnalyzer) -> None:
    """Print combat recommendations."""
    if not analyzer.current_session:
        print("No session data available")
        return
    
    # Get recommendations from analysis
    analysis = analyzer._generate_comprehensive_analysis()
    recommendations = analysis.get('recommendations', {})
    
    print(f"\n=== Combat Recommendations ===")
    
    for category, recs in recommendations.items():
        if recs:
            print(f"\n{category.replace('_', ' ').title()}:")
            for rec in recs:
                print(f"  • {rec}")
    
    # Get unused skills recommendation
    unused_skills = analyzer.get_unused_skills_recommendation()
    if unused_skills:
        print(f"\nSkill Optimization:")
        print(f"  • Consider removing unused skills: {', '.join(unused_skills)}")


def print_ai_tuning(analyzer: CombatMetricsAnalyzer) -> None:
    """Print AI behavior tuning recommendations."""
    tuning = analyzer.get_ai_behavior_tuning()
    
    if not tuning:
        print("No AI tuning recommendations available")
        return
    
    print(f"\n=== AI Behavior Tuning ===")
    
    if tuning.get('skill_priorities'):
        print(f"\nSkill Priorities:")
        for skill_name, priority in tuning['skill_priorities'].items():
            print(f"  {skill_name}: Priority {priority}")
    
    if tuning.get('cooldown_adjustments'):
        print(f"\nCooldown Adjustments:")
        for skill_name, adjustment in tuning['cooldown_adjustments'].items():
            print(f"  {skill_name}: {adjustment}")
    
    if tuning.get('spacing_recommendations'):
        print(f"\nSpacing Recommendations:")
        for aspect, recommendation in tuning['spacing_recommendations'].items():
            print(f"  {aspect}: {recommendation}")


def start_session(analyzer: CombatMetricsAnalyzer, session_id: str = None) -> None:
    """Start a new combat session."""
    session_id = analyzer.start_session(session_id)
    print(f"Started combat session: {session_id}")


def end_session(analyzer: CombatMetricsAnalyzer) -> None:
    """End the current combat session."""
    analysis = analyzer.end_session()
    if analysis:
        print(f"Session ended. Analysis saved.")
        print(f"Session ID: {analysis['session_id']}")
        print(f"Duration: {analysis['duration_minutes']:.2f} minutes")
        print(f"Total Damage: {analysis['total_damage_dealt']:,}")
        print(f"Overall DPS: {analysis['overall_dps']:.2f}")
    else:
        print("No active session to end")


def log_combat_event(analyzer: CombatMetricsAnalyzer, event_type: str, **kwargs) -> None:
    """Log a combat event."""
    if event_type == "skill":
        analyzer.log_skill_usage(
            skill_name=kwargs.get('skill_name', 'unknown'),
            skill_type=kwargs.get('skill_type', 'weapon'),
            target=kwargs.get('target'),
            cooldown=kwargs.get('cooldown'),
            damage_dealt=kwargs.get('damage_dealt'),
            xp_gained=kwargs.get('xp_gained')
        )
        print(f"Logged skill usage: {kwargs.get('skill_name')}")
    
    elif event_type == "damage":
        analyzer.log_damage_event(
            damage_amount=kwargs.get('damage_amount', 0),
            damage_type=kwargs.get('damage_type', 'unknown'),
            target=kwargs.get('target'),
            skill_name=kwargs.get('skill_name')
        )
        print(f"Logged damage event: {kwargs.get('damage_amount')}")
    
    elif event_type == "kill":
        analyzer.log_kill(
            target=kwargs.get('target', 'unknown'),
            target_type=kwargs.get('target_type')
        )
        print(f"Logged kill: {kwargs.get('target')}")
    
    elif event_type == "death":
        analyzer.log_death()
        print("Logged death")


def export_analysis(analyzer: CombatMetricsAnalyzer, output_file: str) -> None:
    """Export analysis to JSON file."""
    if not analyzer.current_session:
        print("No session data to export")
        return
    
    analysis = analyzer._generate_comprehensive_analysis()
    
    try:
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"Analysis exported to: {output_file}")
    except Exception as e:
        print(f"Error exporting analysis: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Combat Metrics Analyzer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Session commands
    session_parser = subparsers.add_parser("session", help="Session management")
    session_parser.add_argument("action", choices=["start", "end", "summary"], help="Session action")
    session_parser.add_argument("--session-id", help="Session ID for start action")
    
    # Analysis commands
    analysis_parser = subparsers.add_parser("analysis", help="Analysis commands")
    analysis_parser.add_argument("type", choices=["skills", "rankings", "dps", "recommendations", "ai-tuning"], 
                               help="Analysis type")
    analysis_parser.add_argument("--skill", help="Specific skill name for skill analysis")
    
    # Logging commands
    log_parser = subparsers.add_parser("log", help="Log combat events")
    log_parser.add_argument("event_type", choices=["skill", "damage", "kill", "death"], help="Event type")
    log_parser.add_argument("--skill-name", help="Skill name")
    log_parser.add_argument("--skill-type", help="Skill type")
    log_parser.add_argument("--target", help="Target name")
    log_parser.add_argument("--cooldown", type=float, help="Cooldown time")
    log_parser.add_argument("--damage-amount", type=int, help="Damage amount")
    log_parser.add_argument("--damage-dealt", type=int, help="Damage dealt (for skill events)")
    log_parser.add_argument("--damage-type", help="Damage type")
    log_parser.add_argument("--xp-gained", type=int, help="XP gained")
    log_parser.add_argument("--target-type", help="Target type")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export analysis")
    export_parser.add_argument("output_file", help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize analyzer
    analyzer = CombatMetricsAnalyzer()
    
    try:
        if args.command == "session":
            if args.action == "start":
                start_session(analyzer, args.session_id)
            elif args.action == "end":
                end_session(analyzer)
            elif args.action == "summary":
                print_session_summary(analyzer)
        
        elif args.command == "analysis":
            if args.type == "skills":
                print_skill_analysis(analyzer, args.skill)
            elif args.type == "rankings":
                print_skill_rankings(analyzer)
            elif args.type == "dps":
                print_dps_analysis(analyzer)
            elif args.type == "recommendations":
                print_recommendations(analyzer)
            elif args.type == "ai-tuning":
                print_ai_tuning(analyzer)
        
        elif args.command == "log":
            kwargs = {}
            if args.skill_name:
                kwargs['skill_name'] = args.skill_name
            if args.skill_type:
                kwargs['skill_type'] = args.skill_type
            if args.target:
                kwargs['target'] = args.target
            if args.cooldown:
                kwargs['cooldown'] = args.cooldown
            if args.damage_amount:
                kwargs['damage_amount'] = args.damage_amount
            if args.damage_dealt:
                kwargs['damage_dealt'] = args.damage_dealt
            if args.damage_type:
                kwargs['damage_type'] = args.damage_type
            if args.xp_gained:
                kwargs['xp_gained'] = args.xp_gained
            if args.target_type:
                kwargs['target_type'] = args.target_type
            
            log_combat_event(analyzer, args.event_type, **kwargs)
        
        elif args.command == "export":
            export_analysis(analyzer, args.output_file)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 