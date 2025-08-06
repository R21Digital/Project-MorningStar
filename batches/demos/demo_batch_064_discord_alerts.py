#!/usr/bin/env python3
"""Demo script for Batch 064 - Discord Alert: Advanced Combat/Build Stats.

This demo showcases the complete Discord alerts system including:
- Combat stats tracking and performance analysis
- Build analysis and skill point ROI calculations
- Discord integration and alert formatting
- Performance analyzer coordination
- Integration with existing combat and build systems
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

from modules.discord_alerts.combat_stats_tracker import CombatStatsTracker
from modules.discord_alerts.build_analyzer import BuildAnalyzer
from modules.discord_alerts.discord_notifier import DiscordNotifier
from modules.discord_alerts.performance_analyzer import PerformanceAnalyzer

def demo_combat_stats_tracking():
    """Demo combat stats tracking functionality."""
    print("\n" + "="*60)
    print("📊 DEMO: Combat Stats Tracking")
    print("="*60)
    
    # Initialize combat stats tracker
    tracker = CombatStatsTracker(session_id="demo_session")
    print(f"✅ Initialized tracker for session: {tracker.session_id}")
    
    # Simulate combat session
    print("\n⚔️ Starting combat session...")
    session_id = tracker.start_combat_session("Stormtrooper", 5)
    print(f"✅ Started combat session: {session_id}")
    
    # Record skill usage
    skills_data = [
        ("Rifle Shot", 25, "combat"),
        ("Rifle Shot", 30, "combat"),
        ("Pistol Shot", 15, "combat"),
        ("Sniper Shot", 40, "combat"),
        ("Heal", 0, "support"),
        ("Cure Poison", 0, "support")
    ]
    
    print("\n🎯 Recording skill usage...")
    for skill_name, damage, skill_line in skills_data:
        tracker.record_skill_usage(skill_name, damage, "Stormtrooper", 2.0, skill_line)
        print(f"  • Used {skill_name}: {damage} damage ({skill_line})")
    
    # Record enemy kills
    print("\n💀 Recording enemy kills...")
    tracker.record_enemy_kill("Stormtrooper", 110)
    tracker.record_enemy_kill("Imperial Officer", 150)
    print(f"  • Killed 2 enemies")
    
    # End combat session
    print("\n🏁 Ending combat session...")
    session_summary = tracker.end_combat_session("victory", 0)
    print(f"✅ Combat session ended")
    
    # Get performance summary
    print("\n📈 Generating performance summary...")
    performance_summary = tracker.get_performance_summary()
    
    print(f"\n📊 Performance Summary:")
    print(f"  • Total Damage: {performance_summary.total_damage:,}")
    print(f"  • Total Kills: {performance_summary.total_kills}")
    print(f"  • Session Duration: {performance_summary.session_duration:.1f}s")
    print(f"  • Average DPS: {performance_summary.average_dps:.2f}")
    print(f"  • Efficiency Score: {performance_summary.efficiency_score:.2f}")
    
    print(f"\n🔥 Most Used Skills:")
    for skill, count in performance_summary.most_used_skills:
        print(f"  • {skill}: {count} uses")
    
    print(f"\n❄️ Least Used Skills:")
    for skill, count in performance_summary.least_used_skills:
        print(f"  • {skill}: {count} uses")
    
    print(f"\n⏱️ Skill Line Uptime:")
    for line, uptime in performance_summary.skill_line_uptime.items():
        print(f"  • {line}: {uptime:.1f}%")
    
    return tracker


def demo_build_analysis():
    """Demo build analysis functionality."""
    print("\n" + "="*60)
    print("🔧 DEMO: Build Analysis")
    print("="*60)
    
    # Initialize build analyzer
    analyzer = BuildAnalyzer()
    print("✅ Initialized build analyzer")
    
    # Create test build data
    test_build_data = {
        "build_summary": "Rifleman + Medic Hybrid | Weapons: rifle, pistol | Combat Style: Hybrid",
        "abilities_granted": ["Rifle Shot", "Pistol Shot", "Heal", "Cure Poison", "Sniper Shot", "Med Shot"],
        "profession_boxes": ["rifleman", "medic"],
        "weapons_supported": ["rifle", "pistol"],
        "combat_style": "hybrid",
        "minimum_attack_distance": 3
    }
    
    # Save test build file
    build_file = Path("demo_build.json")
    with open(build_file, 'w') as f:
        json.dump(test_build_data, f, indent=2)
    
    print(f"✅ Created test build file: {build_file}")
    
    # Load build
    print("\n📥 Loading build from file...")
    build_data = analyzer.load_build_from_file(str(build_file))
    print(f"✅ Loaded build: {build_data['build_summary']}")
    
    # Create test combat data
    combat_data = {
        "skill_usage": {
            "Rifle Shot": {"total_damage": 800, "usage_count": 12},
            "Pistol Shot": {"total_damage": 400, "usage_count": 8},
            "Sniper Shot": {"total_damage": 600, "usage_count": 4},
            "Heal": {"total_damage": 0, "usage_count": 6},
            "Cure Poison": {"total_damage": 0, "usage_count": 2}
        },
        "session_duration": 600.0
    }
    
    # Analyze skill point ROI
    print("\n💰 Analyzing skill point ROI...")
    roi_analysis = analyzer.analyze_skill_point_roi(combat_data)
    
    print(f"\n📊 Skill Point ROI Analysis:")
    for roi in roi_analysis[:3]:  # Show top 3
        print(f"  • {roi.skill_name}: {roi.roi_score:.1f} ROI ({roi.efficiency_rating})")
        print(f"    - Damage: {roi.damage_dealt}, Uses: {roi.usage_count}")
        print(f"    - Recommendation: {roi.recommendation}")
    
    # Analyze build efficiency
    print("\n🔍 Analyzing build efficiency...")
    build_analysis = analyzer.analyze_build_efficiency(combat_data)
    
    print(f"\n📈 Build Efficiency Analysis:")
    print(f"  • Build: {build_analysis.build_name}")
    print(f"  • Total Skill Points: {build_analysis.total_skill_points}")
    print(f"  • Skills Analyzed: {build_analysis.skills_analyzed}")
    print(f"  • Average ROI: {build_analysis.average_roi:.1f}")
    print(f"  • Build Efficiency Score: {build_analysis.build_efficiency_score:.1f}/100")
    
    print(f"\n🏆 Most Efficient Skills:")
    for skill in build_analysis.most_efficient_skills[:3]:
        print(f"  • {skill.skill_name}: {skill.roi_score:.1f} ROI")
    
    print(f"\n⚠️ Least Efficient Skills:")
    for skill in build_analysis.least_efficient_skills[:3]:
        print(f"  • {skill.skill_name}: {skill.roi_score:.1f} ROI")
    
    print(f"\n🚫 Unused Skills:")
    for skill in build_analysis.unused_skills:
        print(f"  • {skill}")
    
    print(f"\n💡 Optimization Recommendations:")
    for rec in build_analysis.optimization_recommendations:
        print(f"  • {rec}")
    
    # Cleanup
    build_file.unlink()
    
    return analyzer


def demo_discord_integration():
    """Demo Discord integration functionality."""
    print("\n" + "="*60)
    print("📢 DEMO: Discord Integration")
    print("="*60)
    
    # Initialize Discord notifier
    notifier = DiscordNotifier()
    print("✅ Initialized Discord notifier")
    
    # Create test performance data
    performance_data = {
        "session_id": "demo_session_001",
        "performance_summary": {
            "total_damage": 2500,
            "total_kills": 8,
            "session_duration": 600.0,
            "average_dps": 4.17,
            "most_used_skills": [
                ("Rifle Shot", 15),
                ("Pistol Shot", 12),
                ("Sniper Shot", 5),
                ("Heal", 3),
                ("Cure Poison", 1)
            ],
            "least_used_skills": [
                ("Med Shot", 0),
                ("Sniper Shot", 5),
                ("Cure Poison", 1)
            ],
            "skill_line_uptime": {
                "combat": 75.0,
                "support": 25.0
            },
            "efficiency_score": 82.5
        },
        "skill_analysis": {
            "skill_usage": {
                "Rifle Shot": {
                    "total_damage": 1200,
                    "usage_count": 15,
                    "average_damage": 80.0,
                    "uptime_percentage": 45.0
                },
                "Pistol Shot": {
                    "total_damage": 800,
                    "usage_count": 12,
                    "average_damage": 66.7,
                    "uptime_percentage": 30.0
                },
                "Sniper Shot": {
                    "total_damage": 500,
                    "usage_count": 5,
                    "average_damage": 100.0,
                    "uptime_percentage": 15.0
                }
            }
        }
    }
    
    # Create test build analysis data
    build_analysis = {
        "build_name": "Rifleman + Medic Hybrid",
        "total_skill_points": 128,
        "skills_analyzed": 5,
        "average_roi": 520.5,
        "build_efficiency_score": 78.5,
        "most_efficient_skills": [
            type('obj', (object,), {
                'skill_name': 'Sniper Shot',
                'roi_score': 800.0,
                'efficiency_rating': 'Excellent'
            })(),
            type('obj', (object,), {
                'skill_name': 'Rifle Shot',
                'roi_score': 600.0,
                'efficiency_rating': 'Good'
            })()
        ],
        "least_efficient_skills": [
            type('obj', (object,), {
                'skill_name': 'Cure Poison',
                'roi_score': 0.0,
                'efficiency_rating': 'Poor'
            })()
        ],
        "unused_skills": ["Med Shot"],
        "optimization_recommendations": [
            "Consider using 1 unused skills from your build",
            "Build efficiency is good - minor optimizations only",
            "Consider investing more points in 2 high-performing skills"
        ]
    }
    
    # Create performance embed
    print("\n📊 Creating performance embed...")
    performance_embed = notifier._create_performance_embed(performance_data)
    print(f"✅ Created performance embed with {len(performance_embed.fields)} fields")
    
    # Create build analysis embed
    print("\n🔧 Creating build analysis embed...")
    build_embed = notifier._create_build_analysis_embed(build_analysis)
    print(f"✅ Created build analysis embed with {len(build_embed.fields)} fields")
    
    # Display embed information
    print(f"\n📋 Performance Embed Details:")
    print(f"  • Title: {performance_embed.title}")
    print(f"  • Description: {performance_embed.description}")
    print(f"  • Color: {performance_embed.color}")
    print(f"  • Fields: {len(performance_embed.fields)}")
    
    print(f"\n📋 Build Analysis Embed Details:")
    print(f"  • Title: {build_embed.title}")
    print(f"  • Description: {build_embed.description}")
    print(f"  • Color: {build_embed.color}")
    print(f"  • Fields: {len(build_embed.fields)}")
    
    # Test Discord connection (will fail without proper config)
    print("\n🔗 Testing Discord connection...")
    success = notifier.test_connection()
    if success:
        print("✅ Discord connection successful")
    else:
        print("⚠️ Discord connection failed (expected without proper configuration)")
    
    return notifier


def demo_performance_analyzer():
    """Demo performance analyzer functionality."""
    print("\n" + "="*60)
    print("📈 DEMO: Performance Analyzer")
    print("="*60)
    
    # Initialize performance analyzer
    analyzer = PerformanceAnalyzer()
    print("✅ Initialized performance analyzer")
    
    # Start analysis session
    session_id = analyzer.start_analysis_session("demo_performance_session")
    print(f"✅ Started analysis session: {session_id}")
    
    # Load test build
    test_build_file = Path("demo_build.json")
    test_build_data = {
        "build_summary": "Rifleman + Medic Hybrid",
        "abilities_granted": ["Rifle Shot", "Pistol Shot", "Heal", "Cure Poison", "Sniper Shot"],
        "profession_boxes": ["rifleman", "medic"],
        "weapons_supported": ["rifle", "pistol"],
        "combat_style": "hybrid"
    }
    
    with open(test_build_file, 'w') as f:
        json.dump(test_build_data, f, indent=2)
    
    success = analyzer.load_build_for_analysis(build_file=str(test_build_file))
    print(f"✅ Loaded build: {success}")
    
    # Simulate combat events
    print("\n⚔️ Recording combat events...")
    combat_events = [
        ("combat_start", {"enemy_type": "Stormtrooper", "enemy_level": 5}),
        ("skill_usage", {"skill_name": "Rifle Shot", "damage_dealt": 25, 
                       "target": "Stormtrooper", "cooldown": 1.5, "skill_line": "combat"}),
        ("skill_usage", {"skill_name": "Pistol Shot", "damage_dealt": 15, 
                       "target": "Stormtrooper", "cooldown": 1.0, "skill_line": "combat"}),
        ("skill_usage", {"skill_name": "Heal", "damage_dealt": 0, 
                       "target": "Self", "cooldown": 2.0, "skill_line": "support"}),
        ("enemy_kill", {"enemy_type": "Stormtrooper", "damage_dealt": 40}),
        ("combat_end", {"result": "victory", "enemy_hp_remaining": 0})
    ]
    
    for event_type, event_data in combat_events:
        analyzer.record_combat_event(event_type, **event_data)
        print(f"  • Recorded {event_type}: {event_data}")
    
    # Get current status
    print("\n📊 Current Analysis Status:")
    status = analyzer.get_analysis_status()
    for key, value in status.items():
        print(f"  • {key}: {value}")
    
    # Generate comprehensive report
    print("\n📋 Generating comprehensive report...")
    report = analyzer.generate_comprehensive_report()
    
    print(f"\n📈 Report Summary:")
    print(f"  • Session ID: {report.session_id}")
    print(f"  • Timestamp: {report.timestamp}")
    print(f"  • Discord Sent: {report.discord_sent}")
    print(f"  • Report File: {report.report_file}")
    print(f"  • Recommendations: {len(report.recommendations)}")
    
    print(f"\n💡 Recommendations:")
    for rec in report.recommendations:
        print(f"  • {rec}")
    
    # Cleanup
    test_build_file.unlink()
    
    return analyzer


def demo_integration_workflow():
    """Demo complete integration workflow."""
    print("\n" + "="*60)
    print("🔗 DEMO: Complete Integration Workflow")
    print("="*60)
    
    # Initialize performance analyzer
    analyzer = PerformanceAnalyzer()
    print("✅ Initialized performance analyzer")
    
    # Start session
    session_id = analyzer.start_analysis_session("integration_demo")
    print(f"✅ Started session: {session_id}")
    
    # Load build
    build_file = Path("integration_build.json")
    build_data = {
        "build_summary": "Rifleman + Medic + Scout Hybrid",
        "abilities_granted": [
            "Rifle Shot", "Pistol Shot", "Sniper Shot", "Heal", "Cure Poison",
            "Med Shot", "Scout Shot", "Trap", "Camouflage"
        ],
        "profession_boxes": ["rifleman", "medic", "scout"],
        "weapons_supported": ["rifle", "pistol", "carbine"],
        "combat_style": "hybrid"
    }
    
    with open(build_file, 'w') as f:
        json.dump(build_data, f, indent=2)
    
    analyzer.load_build_for_analysis(build_file=str(build_file))
    print("✅ Loaded build for analysis")
    
    # Simulate extended combat session
    print("\n⚔️ Simulating extended combat session...")
    
    enemies = ["Stormtrooper", "Imperial Officer", "Bounty Hunter", "Sith Apprentice"]
    skills = [
        ("Rifle Shot", 25, "combat"),
        ("Pistol Shot", 15, "combat"),
        ("Sniper Shot", 40, "combat"),
        ("Heal", 0, "support"),
        ("Cure Poison", 0, "support"),
        ("Scout Shot", 20, "combat"),
        ("Trap", 0, "support")
    ]
    
    for i, enemy in enumerate(enemies):
        print(f"\n🎯 Combat {i+1}: vs {enemy}")
        
        # Start combat
        analyzer.record_combat_event("combat_start", enemy_type=enemy, enemy_level=5+i)
        
        # Use skills
        for skill_name, damage, skill_line in skills:
            if random.random() > 0.3:  # 70% chance to use skill
                analyzer.record_combat_event("skill_usage", 
                                          skill_name=skill_name, 
                                          damage_dealt=damage + random.randint(-5, 5),
                                          target=enemy, 
                                          cooldown=1.5 + random.random(),
                                          skill_line=skill_line)
        
        # Kill enemy
        analyzer.record_combat_event("enemy_kill", enemy_type=enemy, damage_dealt=100 + i*20)
        
        # End combat
        analyzer.record_combat_event("combat_end", result="victory", enemy_hp_remaining=0)
        
        print(f"  ✅ Completed combat {i+1}")
    
    # Generate final report
    print("\n📋 Generating final comprehensive report...")
    report = analyzer.generate_comprehensive_report()
    
    print(f"\n🎉 Integration Demo Complete!")
    print(f"  • Session ID: {report.session_id}")
    print(f"  • Combat Sessions: {len(report.combat_performance.get('combat_sessions', []))}")
    print(f"  • Total Damage: {report.combat_performance.get('total_damage', 0):,}")
    print(f"  • Total Kills: {report.combat_performance.get('total_kills', 0)}")
    print(f"  • Build Analysis: {'Yes' if report.build_analysis else 'No'}")
    print(f"  • Recommendations: {len(report.recommendations)}")
    print(f"  • Discord Alert: {'Sent' if report.discord_sent else 'Not Sent'}")
    print(f"  • Report Saved: {'Yes' if report.report_file else 'No'}")
    
    # Cleanup
    build_file.unlink()
    
    return analyzer


def demo_configuration_management():
    """Demo configuration management."""
    print("\n" + "="*60)
    print("⚙️ DEMO: Configuration Management")
    print("="*60)
    
    # Load Discord alerts configuration
    config_file = Path("config/discord_alerts_config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("✅ Loaded Discord alerts configuration")
        
        print(f"\n📢 Discord Integration Settings:")
        discord_config = config.get("discord_integration", {})
        print(f"  • Enabled: {discord_config.get('enabled', False)}")
        print(f"  • Alert Mode: {discord_config.get('alert_mode', 'webhook')}")
        print(f"  • Webhook URL: {'Configured' if discord_config.get('webhook_url') else 'Not Set'}")
        print(f"  • Bot Token: {'Configured' if discord_config.get('bot_token') else 'Not Set'}")
        
        print(f"\n🔔 Alert Settings:")
        alert_config = config.get("alerts", {})
        print(f"  • Auto Send Alerts: {alert_config.get('auto_send_alerts', True)}")
        print(f"  • Alert on Session End: {alert_config.get('alert_on_session_end', True)}")
        print(f"  • Alert on Milestone: {alert_config.get('alert_on_milestone', True)}")
        print(f"  • Include Build Analysis: {alert_config.get('include_build_analysis', True)}")
        print(f"  • Include Skill Analysis: {alert_config.get('include_skill_analysis', True)}")
        
        print(f"\n📊 Analysis Settings:")
        analysis_config = config.get("analysis", {})
        print(f"  • Track Combat Stats: {analysis_config.get('track_combat_stats', True)}")
        print(f"  • Track Skill Usage: {analysis_config.get('track_skill_usage', True)}")
        print(f"  • Track Build Efficiency: {analysis_config.get('track_build_efficiency', True)}")
        print(f"  • Calculate ROI: {analysis_config.get('calculate_roi', True)}")
        print(f"  • Save Reports: {analysis_config.get('save_reports', True)}")
        
        print(f"\n🎯 Performance Tracking Settings:")
        perf_config = config.get("performance_tracking", {})
        print(f"  • Track Total Damage: {perf_config.get('track_total_damage', True)}")
        print(f"  • Track DPS: {perf_config.get('track_dps', True)}")
        print(f"  • Track Kill Count: {perf_config.get('track_kill_count', True)}")
        print(f"  • Track Skill Frequency: {perf_config.get('track_skill_frequency', True)}")
        print(f"  • Real-time Updates: {perf_config.get('real_time_updates', False)}")
        
    else:
        print("⚠️ Discord alerts configuration file not found")
    
    # Load session configuration
    session_config_file = Path("config/session_config.json")
    if session_config_file.exists():
        with open(session_config_file, 'r') as f:
            session_config = json.load(f)
        
        print(f"\n🎮 Session Configuration:")
        discord_alerts_config = session_config.get("discord_alerts", {})
        print(f"  • Discord Alerts Enabled: {discord_alerts_config.get('enabled', False)}")
        print(f"  • Auto Send Alerts: {discord_alerts_config.get('auto_send_alerts', True)}")
        print(f"  • Alert on Session End: {discord_alerts_config.get('alert_on_session_end', True)}")
        print(f"  • Milestone Damage: {discord_alerts_config.get('milestone_damage', 10000):,}")
        print(f"  • Milestone Kills: {discord_alerts_config.get('milestone_kills', 50)}")
    
    return config


def main():
    """Run all demos."""
    print("🚀 Batch 064 - Discord Alert: Advanced Combat/Build Stats Demo")
    print("=" * 80)
    print("This demo showcases the complete Discord alerts system for advanced")
    print("combat performance tracking and build analysis with Discord integration.")
    print("=" * 80)
    
    try:
        # Run individual demos
        demo_combat_stats_tracking()
        demo_build_analysis()
        demo_discord_integration()
        demo_performance_analyzer()
        demo_integration_workflow()
        demo_configuration_management()
        
        print("\n" + "="*80)
        print("🎉 All Demos Completed Successfully!")
        print("="*80)
        print("\n📋 Demo Summary:")
        print("  ✅ Combat Stats Tracking - Advanced performance monitoring")
        print("  ✅ Build Analysis - Skill point ROI and efficiency analysis")
        print("  ✅ Discord Integration - Formatted alert generation")
        print("  ✅ Performance Analyzer - Coordinated analysis system")
        print("  ✅ Integration Workflow - Complete end-to-end workflow")
        print("  ✅ Configuration Management - Settings and configuration")
        
        print("\n🔧 Key Features Demonstrated:")
        print("  • Total damage, DPS, kill count, skill frequency tracking")
        print("  • Skill data comparison to build (via SkillCalc)")
        print("  • Discord alerts with most used/unused skills")
        print("  • Uptime per skill line analysis")
        print("  • Skill point ROI estimates")
        print("  • Build efficiency scoring")
        print("  • Optimization recommendations")
        print("  • Comprehensive reporting system")
        
        print("\n📁 Generated Files:")
        print("  • Combat stats logs in logs/combat_stats/")
        print("  • Performance reports in logs/performance_reports/")
        print("  • Configuration files in config/")
        
        print("\n🎯 Next Steps:")
        print("  1. Configure Discord webhook URL in config/discord_alerts_config.json")
        print("  2. Enable Discord alerts in config/session_config.json")
        print("  3. Load your actual build from SkillCalc URL")
        print("  4. Start combat sessions to see real-time analysis")
        print("  5. Check Discord for automated performance alerts")
        
    except Exception as e:
        print(f"\n❌ Demo Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 