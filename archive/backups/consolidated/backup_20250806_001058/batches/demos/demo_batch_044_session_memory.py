#!/usr/bin/env python3
"""
Demo script for Batch 044 - Session Tracking + Memory System (v1)

This demo showcases the session memory system including:
- Session logging and tracking
- Event tracking and analytics
- Memory management and analysis
- Performance metrics and recommendations
"""

import time
import json
from datetime import datetime, timedelta
from core.session_memory import (
    SessionLogger, MemoryManager, EventTracker, SessionAnalyzer,
    log_event, log_combat_action, log_quest_completion,
    load_session_logs, analyze_session_data, track_xp_gain,
    track_death, track_travel_event, get_session_stats,
    get_performance_metrics
)
from core.session_memory.memory_template import (
    EventType, CombatType, QuestStatus, MemoryTemplate
)


def demo_session_logging():
    """Demo basic session logging functionality."""
    print("🎯 Demo: Session Logging")
    print("=" * 50)
    
    # Create a session logger
    session_id = f"demo_session_{int(time.time())}"
    logger = SessionLogger(session_id, character_name="DemoCharacter")
    
    print(f"✅ Created session logger for session: {session_id}")
    
    # Log various events
    print("\n📝 Logging events...")
    
    # Log XP gain
    logger.log_xp_gain(150, "quest_completion", location="Mos Eisley")
    logger.log_xp_gain(75, "combat", location="Tatooine Desert")
    
    # Log combat actions
    logger.log_combat_action(
        CombatType.ATTACK,
        target_name="Sand People",
        damage_dealt=250,
        damage_received=50,
        weapon_used="Blaster Rifle",
        victory=True,
        xp_gained=75,
        location="Tatooine Desert"
    )
    
    logger.log_combat_action(
        CombatType.SPECIAL_ABILITY,
        target_name="Jawa",
        damage_dealt=180,
        ability_used="Force Push",
        victory=True,
        xp_gained=50,
        location="Jawa Territory"
    )
    
    # Log quest completion
    logger.log_quest_completion(
        "Deliver Package to Mos Eisley",
        quest_id="quest_001",
        npc_name="Mos Eisley Merchant",
        xp_reward=150,
        credit_reward=500,
        location="Mos Eisley"
    )
    
    # Log travel events
    logger.log_travel_event("Mos Eisley", duration=120.5)
    logger.log_travel_event("Jawa Territory", duration=85.2)
    
    # Log errors
    logger.log_error("Pathfinding failed", "navigation", location="Tatooine Desert")
    logger.log_error("Quest NPC not found", "quest", location="Mos Eisley")
    
    # Log inventory changes
    logger.log_inventory_change(
        items_gained=["Blaster Rifle", "Credits"],
        items_lost=["Medpack"]
    )
    
    # Log skill gains
    logger.log_skill_gain("Rifleman", 5)
    logger.log_profession_level("Marksman", 3)
    
    # Finalize session
    session_data = logger.finalize_session()
    
    print(f"✅ Session finalized with {len(session_data.events)} events")
    print(f"📊 Session summary:")
    print(f"   - Total XP: {session_data.total_xp_gained}")
    print(f"   - Total Deaths: {session_data.total_deaths}")
    print(f"   - Total Quests: {session_data.total_quests_completed}")
    print(f"   - Total Combat: {session_data.total_combat_actions}")
    print(f"   - Efficiency Score: {session_data.efficiency_score:.2f}")
    
    return session_data


def demo_event_tracking():
    """Demo specialized event tracking."""
    print("\n🎯 Demo: Event Tracking")
    print("=" * 50)
    
    # Create session logger and event tracker
    session_id = f"tracking_demo_{int(time.time())}"
    logger = SessionLogger(session_id, character_name="TrackingDemo")
    tracker = EventTracker(logger)
    
    print(f"✅ Created event tracker for session: {session_id}")
    
    # Track XP gains with analytics
    print("\n📈 Tracking XP gains...")
    tracker.track_xp_gain(200, "quest_completion", location="Mos Eisley")
    tracker.track_xp_gain(100, "combat", location="Tatooine Desert")
    tracker.track_xp_gain(300, "crafting", location="Crafting Station")
    
    # Track deaths with analysis
    print("\n💀 Tracking deaths...")
    tracker.track_death("Killed by Sand People", location="Tatooine Desert")
    tracker.track_death("Fell off cliff", location="Mountain Pass")
    
    # Track travel events with efficiency
    print("\n🚀 Tracking travel events...")
    tracker.track_travel_event("Mos Eisley", duration=120.5)
    tracker.track_travel_event("Jawa Territory", duration=85.2)
    tracker.track_travel_event("Crafting Station", duration=45.8)
    
    # Track combat performance
    print("\n⚔️ Tracking combat performance...")
    tracker.track_combat_performance(
        "attack", "Sand People", damage_dealt=250, damage_received=50, victory=True
    )
    tracker.track_combat_performance(
        "special_ability", "Jawa", damage_dealt=180, damage_received=0, victory=True
    )
    
    # Track quest progress
    print("\n📋 Tracking quest progress...")
    tracker.track_quest_progress("Deliver Package", "completed", xp_reward=200, credit_reward=500)
    tracker.track_quest_progress("Gather Resources", "in_progress", xp_reward=0, credit_reward=0)
    
    # Track errors with categorization
    print("\n❌ Tracking errors...")
    tracker.track_error("Pathfinding failed", "navigation")
    tracker.track_error("Quest NPC not found", "quest")
    tracker.track_error("Connection timeout", "system")
    
    # Get tracking summary
    summary = tracker.get_tracking_summary()
    print(f"\n📊 Tracking Summary:")
    print(f"   - Total XP: {summary['total_xp_gained']}")
    print(f"   - Total Deaths: {summary['total_deaths']}")
    print(f"   - Total Travel: {summary['total_travel_events']}")
    print(f"   - XP per Hour: {summary['xp_per_hour']:.2f}")
    print(f"   - Death Rate: {summary['death_rate_per_hour']:.2f}")
    
    # Finalize session
    session_data = logger.finalize_session()
    return session_data


def demo_memory_management():
    """Demo memory management and analysis."""
    print("\n🎯 Demo: Memory Management")
    print("=" * 50)
    
    # Create memory manager
    manager = MemoryManager()
    
    # Load all session logs
    print("📂 Loading session logs...")
    sessions = manager.load_session_logs()
    print(f"✅ Loaded {len(sessions)} sessions")
    
    if sessions:
        # Analyze session data
        print("\n📊 Analyzing session data...")
        analysis = manager.analyze_session_data(sessions)
        
        print(f"📈 Analysis Results:")
        print(f"   - Total Sessions: {analysis.get('total_sessions', 0)}")
        print(f"   - Total XP Gained: {analysis.get('total_xp_gained', 0)}")
        print(f"   - Total Quests: {analysis.get('total_quests_completed', 0)}")
        print(f"   - Total Combat: {analysis.get('total_combat_actions', 0)}")
        print(f"   - Average Efficiency: {analysis.get('average_efficiency_score', 0):.2f}")
        
        # Get session statistics for first session
        if sessions:
            first_session = sessions[0]
            stats = manager.get_session_statistics(first_session.session_id)
            print(f"\n📋 Session Statistics for {first_session.session_id}:")
            print(f"   - Duration: {stats.get('duration_seconds', 0):.1f} seconds")
            print(f"   - XP per Hour: {stats.get('xp_per_hour', 0):.1f}")
            print(f"   - Success Rate: {stats.get('success_rate', 0):.2f}")
    
    # Demo export functionality
    if sessions:
        print("\n📤 Exporting session data...")
        session_id = sessions[0].session_id
        exported_data = manager.export_session_data(session_id, "json")
        if exported_data:
            print(f"✅ Exported session {session_id} to JSON format")
            print(f"📄 Data length: {len(exported_data)} characters")


def demo_session_analysis():
    """Demo session analysis and recommendations."""
    print("\n🎯 Demo: Session Analysis")
    print("=" * 50)
    
    # Create analyzer
    analyzer = SessionAnalyzer()
    
    # Create a sample session for analysis
    session_id = f"analysis_demo_{int(time.time())}"
    logger = SessionLogger(session_id, character_name="AnalysisDemo")
    
    # Add some events to analyze
    logger.log_xp_gain(500, "quest_completion")
    logger.log_xp_gain(200, "combat")
    logger.log_combat_action(CombatType.ATTACK, target_name="Enemy", victory=True)
    logger.log_quest_completion("Test Quest", xp_reward=500)
    logger.log_error("Test error", "general")
    logger.log_death("Test death", location="Test location")
    
    # Finalize and analyze
    session_data = logger.finalize_session()
    
    # Get session statistics
    print("📊 Getting session statistics...")
    stats = analyzer.get_session_stats(session_data)
    
    print(f"📈 Session Statistics:")
    print(f"   - Duration: {stats.get('duration_hours', 0):.2f} hours")
    print(f"   - XP per Hour: {stats.get('xp_per_hour', 0):.1f}")
    print(f"   - Quests per Hour: {stats.get('quests_per_hour', 0):.1f}")
    print(f"   - Combat per Hour: {stats.get('combat_per_hour', 0):.1f}")
    print(f"   - Efficiency Score: {stats.get('efficiency_score', 0):.2f}")
    
    # Get recommendations
    print("\n💡 Getting recommendations...")
    recommendations = analyzer.get_recommendations(session_data)
    
    print("📋 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Demo performance metrics across multiple sessions
    print("\n📊 Demo performance metrics...")
    performance_metrics = analyzer.get_performance_metrics([session_data])
    
    print(f"📈 Performance Metrics:")
    print(f"   - Total Sessions: {performance_metrics.get('total_sessions', 0)}")
    print(f"   - Average XP per Hour: {performance_metrics.get('average_xp_per_hour', 0):.1f}")
    print(f"   - Average Efficiency: {performance_metrics.get('average_efficiency_score', 0):.2f}")


def demo_memory_template():
    """Demo memory template functionality."""
    print("\n🎯 Demo: Memory Template")
    print("=" * 50)
    
    # Create memory template
    template = MemoryTemplate()
    
    # Create session data
    session_data = template.create_session_data("template_demo", "TemplateDemo")
    template.session_data = session_data
    
    print("✅ Created memory template with session data")
    
    # Add events
    print("\n📝 Adding events to template...")
    
    from core.session_memory.memory_template import EventData, EventType
    
    # Add some sample events
    event1 = EventData(
        event_type=EventType.XP_GAIN,
        timestamp=datetime.now(),
        description="Gained XP from quest",
        xp_gained=100
    )
    
    event2 = EventData(
        event_type=EventType.COMBAT_ACTION,
        timestamp=datetime.now(),
        description="Combat action",
        success=True
    )
    
    template.add_event(event1)
    template.add_event(event2)
    
    # Get session summary
    summary = template.get_session_summary()
    print(f"📊 Template Session Summary:")
    print(f"   - Session ID: {summary.get('session_id', 'N/A')}")
    print(f"   - Character: {summary.get('character_name', 'N/A')}")
    print(f"   - Total XP: {summary.get('total_xp_gained', 0)}")
    print(f"   - Total Events: {len(template.session_data.events)}")
    
    # Finalize session
    finalized_session = template.finalize_session()
    print(f"✅ Session finalized with efficiency score: {finalized_session.efficiency_score:.2f}")


def demo_integration():
    """Demo integration with other modules."""
    print("\n🎯 Demo: Integration")
    print("=" * 50)
    
    # Create multiple sessions to demonstrate analysis
    sessions = []
    
    for i in range(3):
        session_id = f"integration_demo_{i}_{int(time.time())}"
        logger = SessionLogger(session_id, character_name=f"IntegrationDemo{i}")
        
        # Add some events
        logger.log_xp_gain(100 * (i + 1), "quest_completion")
        logger.log_combat_action(CombatType.ATTACK, target_name=f"Enemy{i}", victory=True)
        logger.log_quest_completion(f"Quest {i}", xp_reward=100 * (i + 1))
        
        if i % 2 == 0:
            logger.log_error(f"Error {i}", "general")
        
        # Finalize session
        session_data = logger.finalize_session()
        sessions.append(session_data)
    
    print(f"✅ Created {len(sessions)} sessions for integration demo")
    
    # Analyze all sessions
    analyzer = SessionAnalyzer()
    performance_metrics = analyzer.get_performance_metrics(sessions)
    
    print(f"📊 Integration Analysis:")
    print(f"   - Total Sessions: {performance_metrics.get('total_sessions', 0)}")
    print(f"   - Total XP: {performance_metrics.get('total_xp_gained', 0)}")
    print(f"   - Average Efficiency: {performance_metrics.get('average_efficiency_score', 0):.2f}")
    
    # Analyze learning patterns
    learning_patterns = analyzer.analyze_learning_patterns(sessions)
    print(f"📈 Learning Patterns:")
    print(f"   - Sessions Analyzed: {learning_patterns.get('total_sessions_analyzed', 0)}")
    print(f"   - Time Span: {learning_patterns.get('time_span_days', 0)} days")
    
    # Load sessions using memory manager
    manager = MemoryManager()
    loaded_sessions = manager.load_session_logs()
    print(f"📂 Loaded {len(loaded_sessions)} sessions from disk")


def demo_error_handling():
    """Demo error handling in session memory system."""
    print("\n🎯 Demo: Error Handling")
    print("=" * 50)
    
    # Create session logger
    session_id = f"error_demo_{int(time.time())}"
    logger = SessionLogger(session_id, character_name="ErrorDemo")
    
    print("✅ Created session logger for error handling demo")
    
    # Log various types of errors
    print("\n❌ Logging different error types...")
    
    error_types = [
        ("Pathfinding failed", "navigation"),
        ("Quest NPC not found", "quest"),
        ("Connection timeout", "system"),
        ("Inventory full", "inventory"),
        ("Combat ability failed", "combat"),
        ("UI element not found", "ui")
    ]
    
    for error_msg, error_type in error_types:
        logger.log_error(error_msg, error_type)
        print(f"   ✅ Logged {error_type} error: {error_msg}")
    
    # Create event tracker for error analysis
    tracker = EventTracker(logger)
    
    # Track errors with categorization
    for error_msg, error_type in error_types:
        tracker.track_error(error_msg, error_type)
    
    # Get tracking summary to see error patterns
    summary = tracker.get_tracking_summary()
    print(f"\n📊 Error Analysis:")
    print(f"   - Total Errors: {summary.get('total_errors', 0)}")
    print(f"   - Error Rate per Hour: {summary.get('error_rate_per_hour', 0):.2f}")
    
    # Finalize session
    session_data = logger.finalize_session()
    print(f"✅ Session finalized with {session_data.total_errors} errors")


def main():
    """Run all demos."""
    print("🚀 Batch 044 - Session Tracking + Memory System (v1) Demo")
    print("=" * 70)
    print("This demo showcases the session memory system for tracking")
    print("every action and result during a session for analysis,")
    print("learning, and smart decision making.")
    print()
    
    try:
        # Run all demos
        demo_session_logging()
        demo_event_tracking()
        demo_memory_management()
        demo_session_analysis()
        demo_memory_template()
        demo_integration()
        demo_error_handling()
        
        print("\n" + "=" * 70)
        print("✅ All demos completed successfully!")
        print("📁 Check the 'session_logs/' directory for generated log files")
        print("📊 Session data is stored in JSON format for analysis")
        print("🎯 The session memory system is ready for integration")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 