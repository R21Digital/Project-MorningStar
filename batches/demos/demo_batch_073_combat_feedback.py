#!/usr/bin/env python3
"""
Demo script for Batch 073 - Combat Feedback + Respec Tracker

This demo showcases the comprehensive combat feedback and respec tracking system
that provides session feedback and tracks when a respec may be beneficial.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from modules.combat_feedback import create_combat_feedback


def create_sample_session_data():
    """Create sample session data for demonstration."""
    return {
        "session_id": f"demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "dps": 150.0,
        "xp_per_hour": 2500.0,
        "damage_per_hour": 15000.0,
        "kills": 25,
        "deaths": 2,
        "duration": 3600,  # 1 hour
        "skills_used": ["rifle_shot", "rifle_hit", "sniper_shot"],
        "skills_learned": [],
        "efficiency_score": 0.75
    }


def create_sample_previous_sessions():
    """Create sample previous sessions for comparison."""
    sessions = []
    
    # Create sessions with declining performance
    for i in range(5):
        session = {
            "session_id": f"previous_session_{i}",
            "timestamp": (datetime.now() - timedelta(days=i+1)).isoformat(),
            "dps": 200.0 - (i * 10),  # Declining DPS
            "xp_per_hour": 3000.0 - (i * 100),  # Declining XP
            "damage_per_hour": 20000.0 - (i * 1000),
            "kills": 30 - i,
            "deaths": 1,
            "duration": 3600,
            "skills_used": ["rifle_shot", "rifle_hit", "sniper_shot"],
            "skills_learned": [],
            "efficiency_score": 0.85 - (i * 0.02)
        }
        sessions.append(session)
    
    return sessions


def create_sample_skills():
    """Create sample skill data."""
    return {
        "current_skills": [
            "rifle_shot", "rifle_hit", "sniper_shot", "pistol_shot", "pistol_hit",
            "heal_light", "heal_medium", "heal_heavy", "buff_accuracy", "buff_damage"
        ],
        "build_skills": [
            "rifle_shot", "rifle_hit", "sniper_shot", "heal_light", "heal_medium"
        ]
    }


def demo_session_comparison():
    """Demonstrate session comparison functionality."""
    print("\n" + "="*60)
    print("DEMO: Session Comparison")
    print("="*60)
    
    combat_feedback = create_combat_feedback()
    
    # Record previous sessions
    previous_sessions = create_sample_previous_sessions()
    for session in previous_sessions:
        combat_feedback.performance_tracker.record_session(session)
    
    # Analyze current session
    current_session = create_sample_session_data()
    feedback = combat_feedback.analyze_combat_session(
        current_session,
        current_skills=create_sample_skills()["current_skills"],
        build_skills=create_sample_skills()["build_skills"]
    )
    
    print(f"Session ID: {feedback['session_id']}")
    print(f"Status: {feedback['session_comparison']['status']}")
    
    if feedback['session_comparison']['alerts']:
        print("\n⚠️  ALERTS:")
        for alert in feedback['session_comparison']['alerts']:
            print(f"  {alert}")
    
    if feedback['session_comparison']['recommendations']:
        print("\n💡 RECOMMENDATIONS:")
        for rec in feedback['session_comparison']['recommendations']:
            print(f"  {rec}")
    
    print(f"\nPerformance Comparison:")
    comparison = feedback['session_comparison']['comparison']
    for metric, data in comparison.items():
        if isinstance(data, dict) and 'change_percentage' in data:
            change_pct = data['change_percentage'] * 100
            direction = "📈" if change_pct > 0 else "📉"
            print(f"  {metric.upper()}: {direction} {change_pct:+.1f}%")


def demo_skill_analysis():
    """Demonstrate skill analysis functionality."""
    print("\n" + "="*60)
    print("DEMO: Skill Analysis")
    print("="*60)
    
    combat_feedback = create_combat_feedback()
    
    # Create sample session history
    session_history = create_sample_previous_sessions()
    for session in session_history:
        combat_feedback.performance_tracker.record_session(session)
    
    skills_data = create_sample_skills()
    
    # Analyze skill tree
    skill_analysis = combat_feedback.skill_analyzer.analyze_skill_tree(
        skills_data["current_skills"],
        skills_data["build_skills"],
        session_history
    )
    
    print(f"Skill Count: {skill_analysis['skill_count']}")
    print(f"Build Completion: {skill_analysis['build_completion']:.1%}")
    print(f"Health Score: {skill_analysis['health_score']:.2f}")
    
    # Stagnation analysis
    stagnation = skill_analysis['stagnation']
    print(f"\nStagnation Detected: {stagnation['stagnation_detected']}")
    if stagnation['indicators']:
        print(f"Indicators: {', '.join(stagnation['indicators'])}")
    
    # Overlap analysis
    overlap = skill_analysis['overlap']
    print(f"\nOverlap Groups: {overlap['total_overlaps']}")
    print(f"Redundant Skills: {overlap['total_redundant']}")
    
    # Inefficiency analysis
    inefficiency = skill_analysis['inefficiency']
    print(f"\nInefficient Skills: {inefficiency['total_inefficient']}")
    print(f"Underutilized Skills: {inefficiency['total_underutilized']}")
    
    if skill_analysis['recommendations']:
        print("\n💡 SKILL RECOMMENDATIONS:")
        for rec in skill_analysis['recommendations']:
            print(f"  {rec}")


def demo_respec_advisor():
    """Demonstrate respec advisor functionality."""
    print("\n" + "="*60)
    print("DEMO: Respec Advisor")
    print("="*60)
    
    combat_feedback = create_combat_feedback()
    
    # Create sample data
    current_build = {
        "type": "rifleman_medic",
        "skills": ["rifle_shot", "rifle_hit", "sniper_shot", "heal_light", "heal_medium"]
    }
    
    # Record some sessions
    previous_sessions = create_sample_previous_sessions()
    for session in previous_sessions:
        combat_feedback.performance_tracker.record_session(session)
    
    skills_data = create_sample_skills()
    
    # Get respec recommendations
    recommendations = combat_feedback.get_respec_recommendations(
        current_build,
        skills_data["current_skills"]
    )
    
    respec_analysis = recommendations['respec_analysis']
    print(f"Respec Recommended: {respec_analysis['respec_recommended']}")
    print(f"Confidence: {respec_analysis['confidence']:.1%}")
    
    if respec_analysis['reasons']:
        print("\n🔍 REASONS:")
        for reason in respec_analysis['reasons']:
            print(f"  {reason['description']} (Severity: {reason['severity']})")
    
    if respec_analysis['recommendations']:
        print("\n💡 RESPEC RECOMMENDATIONS:")
        for rec in respec_analysis['recommendations']:
            print(f"  {rec}")
    
    if respec_analysis['alternative_suggestions']:
        print("\n💡 ALTERNATIVE SUGGESTIONS:")
        for suggestion in respec_analysis['alternative_suggestions']:
            print(f"  {suggestion}")
    
    # Check urgency
    urgency = combat_feedback.check_respec_urgency(respec_analysis)
    print(f"\nUrgency Level: {urgency.upper()}")
    
    # Timing recommendations
    timing = recommendations['timing_recommendations']
    print(f"Timing: {timing['recommendation']}")


def demo_performance_tracking():
    """Demonstrate performance tracking functionality."""
    print("\n" + "="*60)
    print("DEMO: Performance Tracking")
    print("="*60)
    
    combat_feedback = create_combat_feedback()
    
    # Record multiple sessions
    sessions = []
    for i in range(10):
        session = create_sample_session_data()
        session["dps"] = 150.0 + (i * 5)  # Increasing DPS
        session["xp_per_hour"] = 2500.0 + (i * 50)  # Increasing XP
        session["session_id"] = f"tracking_session_{i}"
        sessions.append(session)
        combat_feedback.performance_tracker.record_session(session)
    
    # Get performance summary
    summary = combat_feedback.performance_tracker.get_performance_summary(days=7)
    print(f"Status: {summary['status']}")
    print(f"Sessions Analyzed: {summary['sessions_count']}")
    
    if summary['status'] == 'summary_calculated':
        print(f"\nDPS Summary:")
        dps_data = summary['dps']
        print(f"  Average: {dps_data['average']:.1f}")
        print(f"  Range: {dps_data['min']:.1f} - {dps_data['max']:.1f}")
        print(f"  Trend: {dps_data['trend']:+.3f}")
        
        print(f"\nXP/Hour Summary:")
        xp_data = summary['xp_per_hour']
        print(f"  Average: {xp_data['average']:.1f}")
        print(f"  Range: {xp_data['min']:.1f} - {xp_data['max']:.1f}")
        print(f"  Trend: {xp_data['trend']:+.3f}")
    
    # Get performance trends
    trends = combat_feedback.performance_tracker.calculate_performance_trends(days=7)
    print(f"\nPerformance Trends:")
    for metric, trend in trends['trends'].items():
        direction = "📈" if trend > 0 else "📉"
        print(f"  {metric.upper()}: {direction} {trend:+.3f}")
    
    # Detect anomalies
    anomalies = combat_feedback.performance_tracker.detect_performance_anomalies(days=7)
    print(f"\nAnomaly Detection:")
    print(f"  Anomalies Found: {anomalies['anomalies_found']}")
    for anomaly in anomalies['anomalies']:
        print(f"  {anomaly['type']}: {anomaly['value']} (Expected: {anomaly['expected_range']})")


def demo_comprehensive_feedback():
    """Demonstrate comprehensive feedback system."""
    print("\n" + "="*60)
    print("DEMO: Comprehensive Feedback")
    print("="*60)
    
    combat_feedback = create_combat_feedback()
    
    # Record some sessions
    previous_sessions = create_sample_previous_sessions()
    for session in previous_sessions:
        combat_feedback.performance_tracker.record_session(session)
    
    # Analyze current session with comprehensive feedback
    current_session = create_sample_session_data()
    feedback = combat_feedback.analyze_combat_session(
        current_session,
        current_skills=create_sample_skills()["current_skills"],
        build_skills=create_sample_skills()["build_skills"]
    )
    
    print(f"Session Analysis Complete")
    print(f"Session ID: {feedback['session_id']}")
    
    # Display all alerts
    if feedback['alerts']:
        print(f"\n⚠️  ALL ALERTS ({len(feedback['alerts'])}):")
        for alert in feedback['alerts']:
            print(f"  {alert}")
    
    # Display all recommendations
    if feedback['recommendations']:
        print(f"\n💡 ALL RECOMMENDATIONS ({len(feedback['recommendations'])}):")
        for rec in feedback['recommendations']:
            print(f"  {rec}")
    
    # Get performance feedback
    performance_feedback = combat_feedback.get_performance_feedback(days=7)
    print(f"\nPerformance Feedback:")
    print(f"  Days Analyzed: {performance_feedback['days_analyzed']}")
    print(f"  Sessions Analyzed: {performance_feedback['sessions_analyzed']}")
    
    if performance_feedback['alerts']:
        print(f"  Performance Alerts: {len(performance_feedback['alerts'])}")
    
    if performance_feedback['recommendations']:
        print(f"  Performance Recommendations: {len(performance_feedback['recommendations'])}")
    
    # Get feedback summary
    summary = combat_feedback.get_feedback_summary()
    print(f"\nFeedback Summary:")
    print(f"  Total Feedback Entries: {summary['total_feedback_entries']}")
    print(f"  Recent Feedback Count: {summary['recent_feedback_count']}")
    print(f"  Alerts Generated: {summary['alerts_generated']}")
    print(f"  Recommendations Generated: {summary['recommendations_generated']}")
    print(f"  Respec Recommendations: {summary['respec_recommendations']}")


def demo_export_functionality():
    """Demonstrate export functionality."""
    print("\n" + "="*60)
    print("DEMO: Export Functionality")
    print("="*60)
    
    combat_feedback = create_combat_feedback()
    
    # Record some data
    previous_sessions = create_sample_previous_sessions()
    for session in previous_sessions:
        combat_feedback.performance_tracker.record_session(session)
    
    current_session = create_sample_session_data()
    combat_feedback.analyze_combat_session(
        current_session,
        current_skills=create_sample_skills()["current_skills"],
        build_skills=create_sample_skills()["build_skills"]
    )
    
    # Export performance data
    performance_export = combat_feedback.performance_tracker.export_performance_data()
    print(f"Performance Data Exported: {performance_export}")
    
    # Export feedback report
    feedback_report = combat_feedback.export_feedback_report()
    print(f"Feedback Report Exported: {feedback_report}")
    
    # Verify exports
    if Path(performance_export).exists():
        print(f"✓ Performance export file created successfully")
    
    if Path(feedback_report).exists():
        print(f"✓ Feedback report file created successfully")


def main():
    """Run the comprehensive demo."""
    print("MS11 Batch 073 - Combat Feedback + Respec Tracker Demo")
    print("="*60)
    print("This demo showcases the comprehensive combat feedback and respec tracking system.")
    print("Features demonstrated:")
    print("  • Session performance comparison over time")
    print("  • DPS vs session analysis")
    print("  • Skill tree stagnation detection")
    print("  • Overlap/inefficiency analysis")
    print("  • Respec recommendations based on performance trends")
    print("  • Performance tracking and anomaly detection")
    print("  • Export functionality")
    print()
    
    try:
        # Run all demos
        demo_session_comparison()
        demo_skill_analysis()
        demo_respec_advisor()
        demo_performance_tracking()
        demo_comprehensive_feedback()
        demo_export_functionality()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("✓ All combat feedback and respec tracking features demonstrated successfully!")
        print("✓ The system provides comprehensive analysis and recommendations for combat performance.")
        print("✓ Respec recommendations are based on multiple factors including performance drops,")
        print("  skill stagnation, and build inefficiency.")
        print("✓ Performance tracking maintains historical data for trend analysis.")
        print("✓ Export functionality allows for detailed reporting and analysis.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 