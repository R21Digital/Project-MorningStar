#!/usr/bin/env python3
"""
Batch 110 - Public Quest Tracker Widget Demo

This demo showcases the public quest tracker widget functionality,
including quest filtering, progress tracking, and widget embedding.

Author: SWG Bot Development Team
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import quest tracker components
from core.quest_tracker import (
    QuestTracker, QuestDefinition, QuestProgress, QuestStatistics,
    QuestCategory, QuestDifficulty, QuestStatus, Planet, RewardType
)

def demo_quest_tracker_initialization():
    """Demo the quest tracker initialization and data loading."""
    print("🚀 Initializing Quest Tracker...")
    
    # Initialize quest tracker
    tracker = QuestTracker(
        data_dir="data/quest_tracker",
        quests_file="quests.json",
        progress_file="progress.json",
        stats_file="statistics.json"
    )
    
    # Load data
    tracker.load_data()
    
    print(f"✅ Loaded {len(tracker.quests)} quests")
    print(f"✅ Loaded {len(tracker.progress)} progress entries")
    print(f"✅ Loaded {len(tracker.statistics)} statistics entries")
    
    return tracker

def demo_quest_filtering(tracker: QuestTracker):
    """Demo quest filtering functionality."""
    print("\n🔍 Demo: Quest Filtering")
    
    # Filter by category
    legacy_filter = tracker.filter_quests(tracker.QuestFilter(categories=[QuestCategory.LEGACY]))
    print(f"📜 Legacy Quests: {len(legacy_filter)}")
    
    theme_park_filter = tracker.filter_quests(tracker.QuestFilter(categories=[QuestCategory.THEME_PARK]))
    print(f"🎡 Theme Park Quests: {len(theme_park_filter)}")
    
    space_filter = tracker.filter_quests(tracker.QuestFilter(categories=[QuestCategory.SPACE]))
    print(f"🚀 Space Quests: {len(space_filter)}")
    
    kashyyyk_filter = tracker.filter_quests(tracker.QuestFilter(categories=[QuestCategory.KASHYYYK]))
    print(f"🌳 Kashyyyk Quests: {len(kashyyyk_filter)}")
    
    mustafar_filter = tracker.filter_quests(tracker.QuestFilter(categories=[QuestCategory.MUSTAFAR]))
    print(f"🔥 Mustafar Quests: {len(mustafar_filter)}")
    
    # Filter by difficulty
    heroic_filter = tracker.filter_quests(tracker.QuestFilter(difficulties=[QuestDifficulty.HEROIC]))
    print(f"⚔️ Heroic Quests: {len(heroic_filter)}")
    
    legendary_filter = tracker.filter_quests(tracker.QuestFilter(difficulties=[QuestDifficulty.LEGENDARY]))
    print(f"👑 Legendary Quests: {len(legendary_filter)}")
    
    # Filter by planet
    tatooine_filter = tracker.filter_quests(tracker.QuestFilter(planets=[Planet.TATOOINE]))
    print(f"🏜️ Tatooine Quests: {len(tatooine_filter)}")
    
    # Filter by reward type
    xp_filter = tracker.filter_quests(tracker.QuestFilter(reward_types=[RewardType.XP]))
    print(f"📈 XP Reward Quests: {len(xp_filter)}")
    
    credits_filter = tracker.filter_quests(tracker.QuestFilter(reward_types=[RewardType.CREDITS]))
    print(f"💰 Credit Reward Quests: {len(credits_filter)}")

def demo_quest_progress_tracking(tracker: QuestTracker):
    """Demo quest progress tracking functionality."""
    print("\n📊 Demo: Quest Progress Tracking")
    
    # Get user progress
    user_progress = tracker.get_user_progress("player_001")
    print(f"👤 Player 001 Progress: {len(user_progress)} quests")
    
    for progress in user_progress:
        quest = tracker.get_quest(progress.quest_id)
        if quest:
            print(f"  - {quest.name}: {progress.status.value}")
    
    # Get quest progress
    legacy_progress = tracker.get_quest_progress("legacy_001")
    print(f"📜 Legacy Quest Progress: {len(legacy_progress)} players")
    
    for progress in legacy_progress:
        print(f"  - Player {progress.user_id}: {progress.status.value}")

def demo_popular_quests(tracker: QuestTracker):
    """Demo popular quests functionality."""
    print("\n🔥 Demo: Popular Quests")
    
    popular_quests = tracker.get_popular_quests(5)
    print("Top 5 Popular Quests:")
    
    for i, (quest, stats) in enumerate(popular_quests, 1):
        print(f"  {i}. {quest.name}")
        print(f"     Category: {quest.category.value}")
        print(f"     Difficulty: {quest.difficulty.value}")
        print(f"     Planet: {quest.planet.value}")
        print(f"     Popularity Score: {stats.popularity_score:.2f}")
        print(f"     Current Players: {stats.current_players}")
        print(f"     Completion Rate: {(stats.successful_completions/stats.total_attempts*100):.1f}%")
        print()

def demo_recent_activity(tracker: QuestTracker):
    """Demo recent activity functionality."""
    print("\n⏰ Demo: Recent Activity")
    
    recent_activity = tracker.get_recent_activity(24)  # Last 24 hours
    print(f"Recent Activity (Last 24h): {len(recent_activity)} events")
    
    for activity in recent_activity[:5]:  # Show first 5
        quest = tracker.get_quest(activity['quest_id'])
        if quest:
            print(f"  - {activity['user_id']} completed {quest.name}")
            print(f"    Time: {activity['completion_time']}")

def demo_quest_statistics(tracker: QuestTracker):
    """Demo quest statistics functionality."""
    print("\n📈 Demo: Quest Statistics")
    
    overall_stats = tracker.get_overall_statistics()
    print("Overall Quest Statistics:")
    print(f"  Total Quests: {overall_stats['total_quests']}")
    print(f"  Total Attempts: {overall_stats['total_attempts']}")
    print(f"  Total Completions: {overall_stats['total_completions']}")
    print(f"  Average Completion Rate: {overall_stats['average_completion_rate']:.1f}%")
    print(f"  Active Players: {overall_stats['active_players']}")
    print(f"  Average Completion Time: {overall_stats['average_completion_time']:.1f} minutes")

def demo_widget_data(tracker: QuestTracker):
    """Demo widget data generation."""
    print("\n🖥️ Demo: Widget Data Generation")
    
    # Simulate widget data generation
    popular_quests = tracker.get_popular_quests(5)
    recent_activity = tracker.get_recent_activity(6)
    stats = tracker.get_overall_statistics()
    
    widget_data = {
        'popular_quests': [],
        'recent_activity': [],
        'statistics': stats
    }
    
    # Format popular quests for widget
    for quest, quest_stats in popular_quests:
        widget_data['popular_quests'].append({
            'id': quest.quest_id,
            'name': quest.name,
            'category': quest.category.value,
            'difficulty': quest.difficulty.value,
            'planet': quest.planet.value,
            'popularity_score': quest_stats.popularity_score,
            'current_players': quest_stats.current_players
        })
    
    # Format recent activity for widget
    for activity in recent_activity[:5]:
        quest = tracker.get_quest(activity['quest_id'])
        if quest:
            widget_data['recent_activity'].append({
                'user_id': activity['user_id'],
                'quest_name': quest.name,
                'category': quest.category.value,
                'completion_time': activity['completion_time'].isoformat()
            })
    
    print("Widget Data Generated:")
    print(f"  Popular Quests: {len(widget_data['popular_quests'])}")
    print(f"  Recent Activity: {len(widget_data['recent_activity'])}")
    print(f"  Statistics: {len(widget_data['statistics'])} metrics")

def demo_quest_progress_update(tracker: QuestTracker):
    """Demo quest progress update functionality."""
    print("\n✏️ Demo: Quest Progress Update")
    
    # Create a new progress entry
    new_progress = QuestProgress(
        quest_id="space_001",
        user_id="demo_player",
        status=QuestStatus.IN_PROGRESS,
        current_step=1,
        steps_completed=["space_001_01"],
        start_time=datetime.now(),
        notes="Testing space combat mechanics"
    )
    
    # Update progress
    success = tracker.update_progress("demo_player", "space_001", new_progress)
    
    if success:
        print("✅ Progress updated successfully")
        
        # Verify the update
        updated_progress = tracker.get_user_progress("demo_player")
        for progress in updated_progress:
            if progress.quest_id == "space_001":
                print(f"  - Quest: {progress.quest_id}")
                print(f"  - Status: {progress.status.value}")
                print(f"  - Current Step: {progress.current_step}")
                print(f"  - Notes: {progress.notes}")
    else:
        print("❌ Failed to update progress")

def demo_embed_widget():
    """Demo widget embedding functionality."""
    print("\n🔗 Demo: Widget Embedding")
    
    widget_code = '<iframe src="/tools/quest-tracker/widget" width="100%" height="400" frameborder="0"></iframe>'
    
    print("Widget Embed Code:")
    print(f"  {widget_code}")
    print()
    print("Features:")
    print("  ✅ Responsive design")
    print("  ✅ Auto-refresh every 5 minutes")
    print("  ✅ Shows popular quests")
    print("  ✅ Displays recent activity")
    print("  ✅ Real-time statistics")
    print("  ✅ Progress bars")
    print("  ✅ Category icons")
    print("  ✅ Difficulty badges")

def demo_web_interface():
    """Demo web interface functionality."""
    print("\n🌐 Demo: Web Interface")
    
    print("Available Pages:")
    print("  📄 Main Quest Tracker: /tools/quest-tracker")
    print("  🖥️ Widget Page: /tools/quest-tracker/widget")
    print()
    print("API Endpoints:")
    print("  📊 Quest List: /api/quest-tracker/quests")
    print("  📈 Statistics: /api/quest-tracker/statistics")
    print("  🔥 Popular Quests: /api/quest-tracker/popular")
    print("  ⏰ Recent Activity: /api/quest-tracker/recent-activity")
    print("  🖥️ Widget Data: /api/quest-tracker/widget-data")
    print()
    print("Features:")
    print("  ✅ Advanced filtering (category, difficulty, planet, rewards)")
    print("  ✅ Search functionality")
    print("  ✅ Sort by name, difficulty, popularity")
    print("  ✅ Progress tracking")
    print("  ✅ Real-time statistics")
    print("  ✅ Recent activity feed")
    print("  ✅ Popular quests section")
    print("  ✅ Widget embedding")
    print("  ✅ Mobile responsive design")

def main():
    """Run the quest tracker demo."""
    print("=" * 60)
    print("🎯 BATCH 110 - PUBLIC QUEST TRACKER WIDGET DEMO")
    print("=" * 60)
    
    try:
        # Initialize quest tracker
        tracker = demo_quest_tracker_initialization()
        
        # Run demos
        demo_quest_filtering(tracker)
        demo_quest_progress_tracking(tracker)
        demo_popular_quests(tracker)
        demo_recent_activity(tracker)
        demo_quest_statistics(tracker)
        demo_widget_data(tracker)
        demo_quest_progress_update(tracker)
        demo_embed_widget()
        demo_web_interface()
        
        print("\n" + "=" * 60)
        print("✅ BATCH 110 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("🎯 Key Features Implemented:")
        print("  ✅ Public quest tracker web interface")
        print("  ✅ Advanced filtering system")
        print("  ✅ Progress tracking")
        print("  ✅ Popular quests display")
        print("  ✅ Recent activity feed")
        print("  ✅ Embeddable widget")
        print("  ✅ Real-time statistics")
        print("  ✅ Mobile responsive design")
        print()
        print("🌐 Access the Quest Tracker at: /tools/quest-tracker")
        print("🖥️ Embed the widget on any website")
        print("📊 View real-time quest statistics")
        print("🔥 See what's hot in the galaxy!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 