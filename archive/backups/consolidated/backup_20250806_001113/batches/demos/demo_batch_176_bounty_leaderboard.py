#!/usr/bin/env python3
"""
Demo script for Batch 176 - Seasonal Bounty Leaderboard Reset System
Demonstrates auto-reset, archiving, and MVP highlighting features
"""

import os
import sys
import json
import datetime
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.reset_bounty_leaderboard import SeasonalBountyLeaderboard, BountyHunter


def demo_basic_functionality():
    """Demonstrate basic leaderboard functionality"""
    print("🎯 Batch 176 - Seasonal Bounty Leaderboard Reset System Demo")
    print("=" * 60)
    
    # Initialize leaderboard
    leaderboard = SeasonalBountyLeaderboard()
    
    print("\n📊 Current Season Status:")
    print(f"Season: {leaderboard.current_season.get('season', 'Unknown')}")
    print(f"Start Date: {leaderboard.current_season.get('start_date', 'Unknown')}")
    print(f"Status: {leaderboard.current_season.get('status', 'Unknown')}")
    print(f"Active Hunters: {leaderboard.current_season.get('season_stats', {}).get('active_hunters', 0)}")
    
    return leaderboard


def demo_add_sample_data(leaderboard):
    """Add sample bounty hunter data"""
    print("\n🎮 Adding Sample Bounty Hunter Data...")
    
    # Sample hunters with different specializations
    sample_hunters = [
        ("D'rev", "JusticeCorp", ["jedi_hunter", "force_sensitive"]),
        ("Tyla", "Outlaws", ["jedi_hunter", "marksman"]),
        ("Vexx", "ShadowStalkers", ["jedi_hunter", "tracker"]),
        ("K'Rin", "CrimsonFang", ["jedi_hunter", "melee"]),
        ("Zara", "VoidHunters", ["jedi_hunter", "sniper"]),
        ("Mara", "ImperialElite", ["jedi_hunter", "tactician"]),
        ("Jax", "RebelAlliance", ["jedi_hunter", "scout"]),
        ("Nyx", "DarkOrder", ["jedi_hunter", "assassin"])
    ]
    
    # Add kills and deaths for each hunter
    for name, guild, specs in sample_hunters:
        # Add some kills
        kills = len(name) % 5 + 1  # Vary kills based on name length
        for i in range(kills):
            bounty = 3000 + (i * 500)  # Increasing bounty
            leaderboard.add_kill(name, guild, bounty, specs)
            time.sleep(0.1)  # Small delay for realistic timing
        
        # Add some deaths (fewer than kills)
        deaths = max(0, kills - 2)
        for i in range(deaths):
            leaderboard.add_death(name, guild, specs)
            time.sleep(0.1)
    
    print(f"✅ Added data for {len(sample_hunters)} hunters")


def demo_leaderboard_display(leaderboard):
    """Display current leaderboard"""
    print("\n🏆 Current Bounty Hunter Leaderboard:")
    print("-" * 80)
    print(f"{'Rank':<4} {'Name':<15} {'Guild':<20} {'Kills':<6} {'Deaths':<7} {'K/D':<6} {'Bounty':<10}")
    print("-" * 80)
    
    hunters = leaderboard.get_current_leaderboard()
    for hunter in hunters[:10]:  # Top 10
        print(f"{hunter['rank']:<4} {hunter['name']:<15} {hunter['guild']:<20} "
              f"{hunter['kills']:<6} {hunter['deaths']:<7} {hunter.get('kd_ratio', 0.0):<6.2f} "
              f"{hunter['total_bounty']:<10,}")


def demo_mvp_highlights(leaderboard):
    """Display MVP highlights"""
    print("\n🏅 Current Season MVP Highlights:")
    print("-" * 50)
    
    mvp_highlights = leaderboard._generate_mvp_highlights()
    
    for category, mvp in mvp_highlights.items():
        if mvp:
            category_name = category.replace('_', ' ').title()
            if category == 'most_kills':
                print(f"🎯 {category_name}: {mvp['name']} ({mvp['guild']}) - {mvp['kills']} kills")
            elif category == 'best_kd_ratio':
                print(f"⚔️ {category_name}: {mvp['name']} ({mvp['guild']}) - K/D: {mvp['kd_ratio']}")
            elif category == 'highest_bounty':
                print(f"💰 {category_name}: {mvp['name']} ({mvp['guild']}) - {mvp['total_bounty']:,} credits")
            elif category == 'most_active':
                print(f"🔥 {category_name}: {mvp['name']} ({mvp['guild']}) - Last active: {mvp['last_activity'][:10]}")


def demo_season_statistics(leaderboard):
    """Display season statistics"""
    print("\n📈 Season Statistics:")
    print("-" * 40)
    
    stats = leaderboard.current_season.get('season_stats', {})
    
    print(f"Total Kills: {stats.get('total_kills', 0)}")
    print(f"Total Deaths: {stats.get('total_deaths', 0)}")
    print(f"Total Bounty: {stats.get('total_bounty', 0):,} credits")
    print(f"Active Hunters: {stats.get('active_hunters', 0)}")
    print(f"Average Kills per Hunter: {stats.get('average_kills', 0.0)}")
    print(f"Average K/D Ratio: {stats.get('average_kd', 0.0)}")
    print(f"Top Guild: {stats.get('top_guild', 'None')}")
    print(f"MVP Hunter: {stats.get('mvp_hunter', 'None')} ({stats.get('mvp_kills', 0)} kills)")


def demo_reset_check(leaderboard):
    """Demonstrate reset checking"""
    print("\n🔄 Season Reset Check:")
    print("-" * 30)
    
    if leaderboard.check_season_reset():
        print("🔄 Season reset is needed!")
        print("This would typically be triggered on the 1st of each month")
    else:
        print("ℹ️ No season reset needed at this time")
    
    # Show current date vs reset day
    now = datetime.datetime.now()
    settings = leaderboard.current_season.get('settings', {})
    reset_day = settings.get('reset_day', 1)
    
    print(f"Current Date: {now.strftime('%Y-%m-%d')}")
    print(f"Reset Day: {reset_day} of each month")
    print(f"Days until next reset: {(reset_day - now.day) % 30}")


def demo_archive_simulation(leaderboard):
    """Simulate season archiving"""
    print("\n📚 Season Archive Simulation:")
    print("-" * 40)
    
    # Check if we have any hunters to archive
    hunters = leaderboard.current_season.get('hunters', [])
    if hunters:
        print(f"Would archive {len(hunters)} hunters to history")
        
        # Show what would be archived
        archive_data = {
            'season_info': {
                'season': leaderboard.current_season.get('season'),
                'start_date': leaderboard.current_season.get('start_date'),
                'end_date': leaderboard.current_season.get('end_date'),
                'status': 'archived',
                'archived_at': datetime.datetime.now().isoformat()
            },
            'hunters': hunters,
            'season_stats': leaderboard.current_season.get('season_stats', {}),
            'mvp_highlights': leaderboard._generate_mvp_highlights()
        }
        
        # Show archive filename
        start_date = leaderboard.current_season.get('start_date', '')
        if start_date:
            year, month = start_date.split('-')[:2]
            archive_filename = f"{year}-{month}.json"
            print(f"Archive filename: {archive_filename}")
        
        print(f"Archive size: {len(json.dumps(archive_data, indent=2))} characters")
    else:
        print("No hunters to archive")


def demo_command_line_usage():
    """Demonstrate command line usage"""
    print("\n💻 Command Line Usage Examples:")
    print("-" * 40)
    
    examples = [
        ("Check if reset is needed", "python scripts/reset_bounty_leaderboard.py --check"),
        ("Force season reset", "python scripts/reset_bounty_leaderboard.py --reset"),
        ("Add a kill", "python scripts/reset_bounty_leaderboard.py --add-kill 'Drev' 'JusticeCorp' 3000"),
        ("Add a death", "python scripts/reset_bounty_leaderboard.py --add-death 'Drev' 'JusticeCorp'"),
        ("Show leaderboard", "python scripts/reset_bounty_leaderboard.py --leaderboard"),
        ("Show season history", "python scripts/reset_bounty_leaderboard.py --history"),
        ("Show MVP highlights", "python scripts/reset_bounty_leaderboard.py --mvp")
    ]
    
    for description, command in examples:
        print(f"• {description}:")
        print(f"  {command}")


def demo_cron_integration():
    """Demonstrate cron integration"""
    print("\n⏰ Cron Integration:")
    print("-" * 30)
    
    cron_examples = [
        "# Daily check at 2 AM",
        "0 2 * * * cd /path/to/project && python scripts/reset_bounty_leaderboard.py >> logs/bounty_cron.log 2>&1",
        "",
        "# Monthly check on 1st at 2 AM",
        "0 2 1 * * cd /path/to/project && python scripts/reset_bounty_leaderboard.py >> logs/bounty_cron.log 2>&1",
        "",
        "# Hourly check (for testing)",
        "0 * * * * cd /path/to/project && python scripts/reset_bounty_leaderboard.py >> logs/bounty_cron.log 2>&1"
    ]
    
    for example in cron_examples:
        print(example)


def demo_data_structure():
    """Show data structure examples"""
    print("\n📋 Data Structure Examples:")
    print("-" * 40)
    
    # Show BountyHunter structure
    hunter = BountyHunter(
        name="D'rev",
        guild="JusticeCorp",
        kills=8,
        deaths=2,
        total_bounty=24000,
        specializations=["jedi_hunter", "force_sensitive"],
        last_kill="2025-01-03T14:30:00Z",
        last_death="2025-01-02T10:15:00Z"
    )
    
    print("BountyHunter Data Structure:")
    print(json.dumps({
        "name": hunter.name,
        "guild": hunter.guild,
        "kills": hunter.kills,
        "deaths": hunter.deaths,
        "kd_ratio": hunter.kd_ratio,
        "total_bounty": hunter.total_bounty,
        "average_bounty": hunter.average_bounty,
        "specializations": hunter.specializations,
        "last_kill": hunter.last_kill,
        "last_death": hunter.last_death
    }, indent=2))


def main():
    """Main demo function"""
    try:
        # Initialize and show basic functionality
        leaderboard = demo_basic_functionality()
        
        # Add sample data
        demo_add_sample_data(leaderboard)
        
        # Display leaderboard
        demo_leaderboard_display(leaderboard)
        
        # Show MVP highlights
        demo_mvp_highlights(leaderboard)
        
        # Show season statistics
        demo_season_statistics(leaderboard)
        
        # Check reset status
        demo_reset_check(leaderboard)
        
        # Simulate archiving
        demo_archive_simulation(leaderboard)
        
        # Show command line usage
        demo_command_line_usage()
        
        # Show cron integration
        demo_cron_integration()
        
        # Show data structure
        demo_data_structure()
        
        print("\n✅ Batch 176 Demo Completed Successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("• Auto-reset BH leaderboard monthly")
        print("• Archive previous seasons to /bounty/history/YYYY-MM.json")
        print("• Highlight monthly MVPs and K/D logs")
        print("• Comprehensive bounty hunter tracking")
        print("• Command line interface for management")
        print("• Cron integration for automated resets")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 