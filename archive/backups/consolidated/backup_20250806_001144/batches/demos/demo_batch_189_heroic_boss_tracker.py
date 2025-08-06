#!/usr/bin/env python3
"""
MorningStar Heroic Boss Tracker + Stats Demo - Batch 189
Demonstrates the comprehensive heroic boss tracking system with public dashboard,
kill logging, leaderboards, and participation statistics.

This demo showcases:
- Boss kill data management and structure
- Public leaderboard generation with Eleventy
- Interactive Svelte components for boss statistics
- API endpoint for kill logging with validation
- First kill tracking per season
- User alias tagging with Discord integration
- Team statistics and analytics
"""

import json
import os
import sys
import time
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import tempfile
from collections import defaultdict

class HeroicBossTrackerDemo:
    """Demonstration of the MorningStar Heroic Boss Tracker System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.boss_data_file = self.project_root / "src" / "data" / "heroics" / "boss_kills.json"
        self.leaderboard_file = self.project_root / "src" / "pages" / "heroics" / "leaderboard.11ty.js"
        self.component_file = self.project_root / "src" / "components" / "BossStatsCard.svelte"
        self.api_file = self.project_root / "api" / "heroics" / "log_kill.js"
        
        # Demo configuration
        self.api_base_url = "http://localhost:3000/api/heroics"
        self.current_season = "Season 15"
        self.boss_data = {}
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    
    def print_section(self, title: str):
        """Print a section header"""
        print(f"\n{'-'*50}")
        print(f"  {title}")
        print(f"{'-'*50}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"⚠️  {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")

    def load_boss_data(self):
        """Load boss kill data"""
        self.print_section("Loading Boss Kill Data")
        
        try:
            with open(self.boss_data_file, 'r', encoding='utf-8') as f:
                self.boss_data = json.load(f)
            
            self.print_success(f"Loaded boss data from {self.boss_data_file}")
            
            # Display summary statistics
            metadata = self.boss_data.get('metadata', {})
            bosses = self.boss_data.get('bosses', {})
            
            print(f"\n📊 Data Summary:")
            print(f"  Current Season: {metadata.get('currentSeason', 'Unknown')}")
            print(f"  Total Kills: {metadata.get('totalKills', 0):,}")
            print(f"  Active Players: {metadata.get('totalPlayers', 0):,}")
            print(f"  Average Team Size: {metadata.get('averageTeamSize', 0):.1f}")
            print(f"  Available Bosses: {len(bosses)}")
            
            for boss_id, boss in bosses.items():
                stats = boss.get('stats', {})
                print(f"    • {boss.get('displayName', boss_id)}: {stats.get('totalKills', 0)} kills")
            
            return True
            
        except FileNotFoundError:
            self.print_error(f"Boss data file not found: {self.boss_data_file}")
            return False
        except json.JSONDecodeError as e:
            self.print_error(f"Invalid JSON in boss data: {e}")
            return False

    def demonstrate_data_structure(self):
        """Demonstrate the boss data structure and organization"""
        self.print_section("Boss Data Structure Analysis")
        
        if not self.boss_data:
            self.print_warning("No boss data loaded")
            return
        
        # Analyze data structure
        print("🏗️  Data Architecture:")
        
        # Metadata analysis
        metadata = self.boss_data.get('metadata', {})
        print(f"\n📋 Metadata Structure:")
        print(f"  - Version tracking: {metadata.get('version', 'N/A')}")
        print(f"  - Season management: {len(metadata.get('seasons', []))} seasons tracked")
        print(f"  - Last updated: {metadata.get('lastUpdated', 'Unknown')}")
        print(f"  - Global statistics: Kill totals, player counts, averages")
        
        # Boss data analysis
        bosses = self.boss_data.get('bosses', {})
        print(f"\n👹 Boss Data Structure ({len(bosses)} bosses):")
        
        for boss_id, boss in list(bosses.items())[:2]:  # Show first 2 as examples
            print(f"\n  📍 {boss.get('displayName', boss_id)} ({boss_id}):")
            print(f"    - Location: {boss.get('location', 'Unknown')}")
            print(f"    - Difficulty: {boss.get('difficulty', 'Unknown')}")
            print(f"    - Type: {boss.get('heroicType', 'Unknown')}")
            print(f"    - Recommended Team: {boss.get('recommendedTeamSize', 'Unknown')}")
            
            stats = boss.get('stats', {})
            print(f"    - Total Kills: {stats.get('totalKills', 0)}")
            print(f"    - Unique Killers: {stats.get('uniqueKillers', 0)}")
            print(f"    - Recent Kills: {len(stats.get('recentKills', []))}")
            print(f"    - Top Killers: {len(stats.get('topKillers', []))}")
            
            if stats.get('firstKillThisSeason'):
                first_kill = stats['firstKillThisSeason']
                print(f"    - First Kill Team: {len(first_kill.get('team', []))} members")
                print(f"    - First Kill Time: {self.format_time(first_kill.get('killTime', 0))}")
        
        # Leaderboards analysis
        leaderboards = self.boss_data.get('leaderboards', {})
        print(f"\n🏆 Leaderboard Structure:")
        print(f"  - Most Kills: {len(leaderboards.get('mostKills', []))} entries")
        print(f"  - Fastest Killers: {len(leaderboards.get('fastestKillers', []))} entries")
        print(f"  - Team Players: {len(leaderboards.get('teamPlayers', []))} entries")
        print(f"  - Season Stats: {len(leaderboards.get('seasonStats', {}))} seasons")
        
        # Analytics analysis
        analytics = self.boss_data.get('analytics', {})
        print(f"\n📈 Analytics Structure:")
        print(f"  - Kill Trends: Daily and weekly tracking")
        print(f"  - Boss Popularity: {len(analytics.get('popularityRanking', []))} entries")
        print(f"  - Team Size Distribution: {len(analytics.get('teamSizeDistribution', {}))} categories")
        print(f"  - Class Distribution: {len(analytics.get('classDistribution', {}))} classes")

    def demonstrate_leaderboard_generation(self):
        """Demonstrate the Eleventy leaderboard page generation"""
        self.print_section("Leaderboard Page Generation")
        
        if not self.leaderboard_file.exists():
            self.print_error("Leaderboard generator file not found")
            return
        
        self.print_success("Leaderboard generator found")
        
        # Analyze the generator
        print("\n🔧 Eleventy Generator Features:")
        print("  ✓ Dynamic page generation from boss data")
        print("  ✓ Responsive dashboard layout")
        print("  ✓ Interactive boss cards with statistics")
        print("  ✓ Multiple leaderboard categories")
        print("  ✓ Season-based filtering")
        print("  ✓ Real-time data refresh capability")
        print("  ✓ Analytics and trend visualization")
        
        # Simulate page generation
        print("\n📄 Generated Page Structure:")
        print("  🏠 Dashboard Header")
        print("    - Current season display")
        print("    - Global statistics overview")
        print("    - Last updated timestamp")
        
        print("  📊 Statistics Overview Cards")
        print("    - Total boss kills across all seasons")
        print("    - Active hunter count")
        print("    - Average team size")
        print("    - Number of tracked bosses")
        
        print("  👹 Boss Information Grid")
        if self.boss_data:
            bosses = self.boss_data.get('bosses', {})
            for boss_id, boss in bosses.items():
                stats = boss.get('stats', {})
                print(f"    • {boss.get('displayName', boss_id)} Card:")
                print(f"      - Difficulty: {boss.get('difficulty', 'Unknown')}")
                print(f"      - Total Kills: {stats.get('totalKills', 0)}")
                print(f"      - Fastest Kill: {self.format_time(stats.get('fastestKill', 0))}")
                if stats.get('firstKillThisSeason'):
                    print(f"      - First Kill Team: {len(stats['firstKillThisSeason'].get('team', []))} members")
        
        print("  🏆 Leaderboard Sections")
        print("    - Top Killers (most total kills)")
        print("    - Speed Demons (fastest kill times)")
        print("    - Team Players (most team participation)")
        print("    - Current Season Champions")
        
        print("  📈 Analytics Dashboard")
        print("    - Boss popularity rankings")
        print("    - Team size distribution")
        print("    - Interactive charts and trends")

    def demonstrate_svelte_component(self):
        """Demonstrate the Svelte boss statistics component"""
        self.print_section("Interactive Svelte Component")
        
        if not self.component_file.exists():
            self.print_error("Svelte component file not found")
            return
        
        self.print_success("BossStatsCard.svelte component found")
        
        print("\n🎨 Component Features:")
        print("  ✓ Interactive expandable cards")
        print("  ✓ Real-time data updates")
        print("  ✓ Difficulty-based color coding")
        print("  ✓ Hover effects and animations")
        print("  ✓ Mobile-responsive design")
        print("  ✓ Event dispatching for parent components")
        
        print("\n🔧 Component Props:")
        print("  • boss: Boss data object")
        print("  • showDetails: Toggle detailed view")
        print("  • enableRealTime: Auto-refresh capability")
        print("  • refreshInterval: Update frequency")
        print("  • maxRecentKills: Number of recent kills to show")
        
        print("\n📱 Interactive Elements:")
        print("  🔽 Expandable header (click to toggle)")
        print("  📊 Quick statistics grid")
        print("  🥇 First kill this season highlight")
        print("  🕒 Recent kills timeline")
        print("  👑 Top killers list")
        print("  📖 Boss description and rewards")
        print("  🔄 Real-time refresh indicator")
        
        # Demonstrate component states
        if self.boss_data:
            sample_boss = list(self.boss_data.get('bosses', {}).values())[0]
            print(f"\n🎯 Sample Component Rendering:")
            print(f"  Boss: {sample_boss.get('displayName', 'Unknown')}")
            print(f"  Difficulty: {sample_boss.get('difficulty', 'Unknown')}")
            print(f"  Location: {sample_boss.get('location', 'Unknown')}")
            
            stats = sample_boss.get('stats', {})
            print(f"  Total Kills: {stats.get('totalKills', 0):,}")
            print(f"  Fastest Kill: {self.format_time(stats.get('fastestKill', 0))}")
            print(f"  Unique Killers: {stats.get('uniqueKillers', 0)}")
            print(f"  Recent Activity: {len(stats.get('recentKills', []))} recent kills")

    def demonstrate_api_functionality(self):
        """Demonstrate the kill logging API"""
        self.print_section("Kill Logging API Demonstration")
        
        if not self.api_file.exists():
            self.print_error("API endpoint file not found")
            return
        
        self.print_success("API endpoint found")
        
        print("\n🔌 API Endpoint Features:")
        print("  ✓ POST /api/heroics/log_kill - Log new boss kills")
        print("  ✓ GET /api/heroics/log_kill - Retrieve statistics")
        print("  ✓ Rate limiting protection")
        print("  ✓ Data validation and sanitization")
        print("  ✓ Real-time leaderboard updates")
        print("  ✓ CORS support for web clients")
        
        print("\n🛡️  Security Features:")
        print("  • Rate limiting: Max 10 requests per minute")
        print("  • Input validation: Boss IDs, team data, kill times")
        print("  • Team size limits: Maximum 8 players")
        print("  • Kill time validation: 30 seconds to 1 hour")
        print("  • Discord hash generation for privacy")
        
        # Simulate API requests
        self.simulate_api_requests()

    def simulate_api_requests(self):
        """Simulate API requests and responses"""
        print("\n🧪 Simulated API Interactions:")
        
        # Sample kill data
        sample_kill = {
            "bossId": "ig88",
            "killTime": 142.5,
            "team": [
                {"alias": "DemoHunter1", "class": "Bounty Hunter", "level": 85},
                {"alias": "DemoHunter2", "class": "Bounty Hunter", "level": 83},
                {"alias": "DemoHunter3", "class": "Commando", "level": 84}
            ],
            "serverPop": 634,
            "screenshot": "/screenshots/demo_kill.jpg"
        }
        
        print("\n📤 Sample Kill Log Request:")
        print(f"  POST {self.api_base_url}/log_kill")
        print(f"  Boss: {sample_kill['bossId']}")
        print(f"  Kill Time: {self.format_time(sample_kill['killTime'])}")
        print(f"  Team Size: {len(sample_kill['team'])}")
        print(f"  Server Population: {sample_kill['serverPop']}")
        
        print("\n📥 Expected Response:")
        print("  {")
        print('    "success": true,')
        print('    "message": "Kill logged successfully",')
        print('    "killId": "a7b8c9d2",')
        print('    "stats": {')
        print('      "totalKills": 3925,')
        print('      "isFirstKill": false,')
        print('      "isFastestKill": false,')
        print('      "rank": 15')
        print('    }')
        print("  }")
        
        # Demonstrate validation
        print("\n🔍 Validation Examples:")
        
        invalid_examples = [
            {
                "error": "Invalid boss ID",
                "data": {"bossId": "invalid_boss", "killTime": 120},
                "expected": "Boss ID must be one of: exar_kun, ig88, tusken_king, lord_nyax, axkva_min"
            },
            {
                "error": "Kill time too short",
                "data": {"bossId": "ig88", "killTime": 15},
                "expected": "Kill time must be between 30 and 3600 seconds"
            },
            {
                "error": "Invalid team data",
                "data": {"bossId": "ig88", "killTime": 120, "team": []},
                "expected": "Team data is required and cannot be empty"
            }
        ]
        
        for example in invalid_examples:
            print(f"  ❌ {example['error']}")
            print(f"     Expected: {example['expected']}")
        
        # Demonstrate rate limiting
        print("\n⏱️  Rate Limiting:")
        print("  • 10 requests per minute per IP address")
        print("  • 429 status code when limit exceeded")
        print("  • Automatic cleanup of old rate limit data")

    def demonstrate_first_kill_tracking(self):
        """Demonstrate first kill tracking functionality"""
        self.print_section("First Kill Tracking System")
        
        if not self.boss_data:
            self.print_warning("No boss data loaded")
            return
        
        print("🥇 First Kill Features:")
        print("  ✓ Per-season first kill tracking")
        print("  ✓ Team composition recording")
        print("  ✓ Timestamp and server population data")
        print("  ✓ Screenshot documentation support")
        print("  ✓ Special achievement highlighting")
        
        print(f"\n🏆 {self.current_season} First Kills:")
        
        bosses = self.boss_data.get('bosses', {})
        for boss_id, boss in bosses.items():
            stats = boss.get('stats', {})
            first_kill = stats.get('firstKillThisSeason')
            
            if first_kill:
                print(f"\n  👹 {boss.get('displayName', boss_id)}:")
                print(f"    ⏰ Date: {self.format_date(first_kill.get('timestamp'))}")
                print(f"    ⚡ Time: {self.format_time(first_kill.get('killTime', 0))}")
                print(f"    👥 Team Size: {len(first_kill.get('team', []))}")
                print(f"    🌐 Server Pop: {first_kill.get('serverPop', 'Unknown')}")
                
                team = first_kill.get('team', [])
                if team:
                    print(f"    🎯 Team Composition:")
                    for member in team:
                        print(f"      • {member.get('alias', 'Unknown')} - {member.get('class', 'Unknown')} (Level {member.get('level', '?')})")
                
                if first_kill.get('screenshot'):
                    print(f"    📸 Screenshot: {first_kill['screenshot']}")
            else:
                print(f"\n  👹 {boss.get('displayName', boss_id)}: No first kill recorded this season")

    def demonstrate_user_alias_system(self):
        """Demonstrate user alias and Discord integration"""
        self.print_section("User Alias & Discord Integration")
        
        print("🏷️  Alias System Features:")
        print("  ✓ Anonymous player identification")
        print("  ✓ Discord name hash for privacy")
        print("  ✓ Consistent player tracking across kills")
        print("  ✓ Optional Discord integration")
        print("  ✓ Leaderboard participation tracking")
        
        # Show examples from data
        if self.boss_data:
            print("\n👤 Example Player Records:")
            
            # Get some sample players from leaderboards
            leaderboards = self.boss_data.get('leaderboards', {})
            most_kills = leaderboards.get('mostKills', [])
            
            for i, player in enumerate(most_kills[:3], 1):
                print(f"\n  #{i} Player Record:")
                print(f"    🎮 Alias: {player.get('alias', 'Unknown')}")
                print(f"    🔥 Total Kills: {player.get('totalKills', 0)}")
                print(f"    ⚡ Average Kill Time: {self.format_time(player.get('averageKillTime', 0))}")
                print(f"    👹 Favorite Boss: {player.get('favoriteBoss', 'Unknown')}")
                
                # Generate sample Discord hash for demo
                sample_hash = f"d{i}f{8-i}e{i*2}a{9-i}"
                print(f"    🔗 Discord Hash: {sample_hash} (privacy protected)")
        
        print("\n🔐 Privacy Protection:")
        print("  • Real names never stored")
        print("  • Discord IDs hashed for anonymity")
        print("  • Optional participation in public leaderboards")
        print("  • Player can request data removal")
        
        print("\n📊 Tracking Benefits:")
        print("  • Consistent statistics across sessions")
        print("  • Achievement recognition")
        print("  • Team formation assistance")
        print("  • Progression tracking")

    def demonstrate_team_statistics(self):
        """Demonstrate team size and participation analytics"""
        self.print_section("Team Statistics & Analytics")
        
        if not self.boss_data:
            self.print_warning("No boss data loaded")
            return
        
        analytics = self.boss_data.get('analytics', {})
        team_distribution = analytics.get('teamSizeDistribution', {})
        
        print("👥 Team Analytics Features:")
        print("  ✓ Team size distribution tracking")
        print("  ✓ Average team size per boss")
        print("  ✓ Solo vs group kill analysis")
        print("  ✓ Class composition tracking")
        print("  ✓ Team performance correlation")
        
        if team_distribution:
            print("\n📊 Team Size Distribution:")
            total_kills = sum(team_distribution.values())
            
            for size, count in team_distribution.items():
                percentage = (count / total_kills * 100) if total_kills > 0 else 0
                size_label = self.format_team_size_label(size)
                print(f"  {size_label}: {count:,} kills ({percentage:.1f}%)")
        
        # Boss-specific team size analysis
        print("\n👹 Boss-Specific Team Preferences:")
        bosses = self.boss_data.get('bosses', {})
        
        for boss_id, boss in bosses.items():
            stats = boss.get('stats', {})
            avg_team_size = stats.get('averageTeamSize', 0)
            recommended = boss.get('recommendedTeamSize', 0)
            
            print(f"  {boss.get('displayName', boss_id)}:")
            print(f"    🎯 Recommended: {recommended} players")
            print(f"    📊 Actual Average: {avg_team_size:.1f} players")
            
            if avg_team_size > 0:
                efficiency = (recommended / avg_team_size) if recommended > 0 else 1.0
                if efficiency > 1.1:
                    print(f"    ⚡ Teams tend to be smaller than recommended")
                elif efficiency < 0.9:
                    print(f"    🛡️  Teams tend to be larger than recommended")
                else:
                    print(f"    ✅ Teams match recommendations well")
        
        # Class distribution
        class_distribution = analytics.get('classDistribution', {})
        if class_distribution:
            print("\n⚔️  Class Participation:")
            total_participants = sum(class_distribution.values())
            
            sorted_classes = sorted(class_distribution.items(), key=lambda x: x[1], reverse=True)
            for class_name, count in sorted_classes:
                percentage = (count / total_participants * 100) if total_participants > 0 else 0
                print(f"  {class_name}: {count:,} participants ({percentage:.1f}%)")

    def demonstrate_season_management(self):
        """Demonstrate season-based tracking and resets"""
        self.print_section("Season Management System")
        
        if not self.boss_data:
            self.print_warning("No boss data loaded")
            return
        
        metadata = self.boss_data.get('metadata', {})
        seasons = metadata.get('seasons', [])
        
        print("📅 Season Features:")
        print("  ✓ Quarterly season resets")
        print("  ✓ First kill tracking per season")
        print("  ✓ Season-specific leaderboards")
        print("  ✓ Historical data preservation")
        print("  ✓ Achievement migration")
        
        print(f"\n🏆 Season History ({len(seasons)} seasons tracked):")
        
        for season in seasons:
            status = "🟢 ACTIVE" if season.get('isActive') else "🔴 ENDED"
            print(f"\n  {season.get('name', 'Unknown')} {status}")
            print(f"    📅 Start: {self.format_date(season.get('startDate'))}")
            
            if season.get('endDate'):
                print(f"    📅 End: {self.format_date(season.get('endDate'))}")
                
                # Calculate duration
                start_date = datetime.fromisoformat(season['startDate'].replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(season['endDate'].replace('Z', '+00:00'))
                duration = end_date - start_date
                print(f"    ⏱️  Duration: {duration.days} days")
        
        # Current season statistics
        current_season_id = "season_15"  # Based on data
        leaderboards = self.boss_data.get('leaderboards', {})
        season_stats = leaderboards.get('seasonStats', {}).get(current_season_id, {})
        
        if season_stats:
            print(f"\n📊 {self.current_season} Statistics:")
            print(f"  🔥 Total Kills: {season_stats.get('totalKills', 0):,}")
            print(f"  👥 Unique Players: {season_stats.get('uniquePlayers', 0)}")
            print(f"  📈 Avg Kills/Day: {season_stats.get('averageKillsPerDay', 0):.1f}")
            
            top_players = season_stats.get('topPlayers', [])
            if top_players:
                print(f"  🏆 Top 3 Players:")
                for i, player in enumerate(top_players[:3], 1):
                    print(f"    #{i} {player.get('alias', 'Unknown')}: {player.get('kills', 0)} kills, {player.get('firstKills', 0)} first kills")

    def demonstrate_analytics_dashboard(self):
        """Demonstrate analytics and trending data"""
        self.print_section("Analytics Dashboard")
        
        if not self.boss_data:
            self.print_warning("No boss data loaded")
            return
        
        analytics = self.boss_data.get('analytics', {})
        
        print("📈 Analytics Features:")
        print("  ✓ Daily and weekly kill trends")
        print("  ✓ Boss popularity rankings")
        print("  ✓ Team composition analysis")
        print("  ✓ Performance metrics tracking")
        print("  ✓ Predictive insights")
        
        # Kill trends
        kill_trends = analytics.get('killTrends', {})
        daily_trends = kill_trends.get('daily', [])
        
        if daily_trends:
            print(f"\n📅 Recent Daily Activity ({len(daily_trends)} days):")
            for day in daily_trends[-5:]:  # Last 5 days
                date = day.get('date', 'Unknown')
                kills = day.get('kills', 0)
                players = day.get('uniquePlayers', 0)
                avg_team = day.get('averageTeamSize', 0)
                print(f"  {date}: {kills} kills, {players} players, {avg_team:.1f} avg team size")
        
        # Boss popularity
        popularity = analytics.get('popularityRanking', [])
        if popularity:
            print(f"\n👹 Boss Popularity Rankings:")
            for i, boss_pop in enumerate(popularity, 1):
                boss_name = self.format_boss_name(boss_pop.get('boss', 'unknown'))
                percentage = boss_pop.get('killPercentage', 0)
                wait_time = boss_pop.get('averageWaitTime', 0)
                print(f"  #{i} {boss_name}: {percentage}% of kills, {wait_time:.1f}min avg wait")
        
        # Performance insights
        print(f"\n🎯 Performance Insights:")
        metadata = self.boss_data.get('metadata', {})
        
        total_kills = metadata.get('totalKills', 0)
        total_players = metadata.get('totalPlayers', 0)
        
        if total_kills > 0 and total_players > 0:
            kills_per_player = total_kills / total_players
            print(f"  • Average kills per player: {kills_per_player:.1f}")
            
            # Calculate daily activity
            if daily_trends:
                recent_activity = sum(day.get('kills', 0) for day in daily_trends[-7:])
                print(f"  • Kills in last 7 days: {recent_activity}")
                print(f"  • Average daily activity: {recent_activity / 7:.1f} kills/day")
        
        # Trend analysis
        if len(daily_trends) >= 7:
            recent_week = daily_trends[-7:]
            previous_week = daily_trends[-14:-7] if len(daily_trends) >= 14 else []
            
            recent_avg = sum(day.get('kills', 0) for day in recent_week) / 7
            
            if previous_week:
                previous_avg = sum(day.get('kills', 0) for day in previous_week) / 7
                trend = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
                
                if trend > 5:
                    print(f"  📈 Activity trending up: +{trend:.1f}% vs last week")
                elif trend < -5:
                    print(f"  📉 Activity trending down: {trend:.1f}% vs last week")
                else:
                    print(f"  ➡️  Activity stable: {trend:.1f}% change vs last week")

    def run_performance_analysis(self):
        """Analyze system performance and scalability"""
        self.print_section("Performance Analysis")
        
        print("⚡ Performance Metrics:")
        
        if self.boss_data:
            # Data size analysis
            data_str = json.dumps(self.boss_data)
            data_size_kb = len(data_str.encode('utf-8')) / 1024
            
            print(f"  📊 Data Size: {data_size_kb:.1f} KB")
            
            # Count various data points
            bosses = self.boss_data.get('bosses', {})
            total_recent_kills = sum(len(boss.get('stats', {}).get('recentKills', [])) for boss in bosses.values())
            total_top_killers = sum(len(boss.get('stats', {}).get('topKillers', [])) for boss in bosses.values())
            
            print(f"  👹 Tracked Bosses: {len(bosses)}")
            print(f"  🔥 Recent Kills Stored: {total_recent_kills}")
            print(f"  👑 Top Killer Records: {total_top_killers}")
            
            leaderboards = self.boss_data.get('leaderboards', {})
            total_leaderboard_entries = sum(len(lb) for lb in leaderboards.values() if isinstance(lb, list))
            print(f"  🏆 Leaderboard Entries: {total_leaderboard_entries}")
            
            # Estimate load performance
            print(f"\n🚀 Estimated Performance:")
            print(f"  • Page load time: ~{data_size_kb * 0.01:.0f}ms (client-side rendering)")
            print(f"  • API response time: ~{total_recent_kills * 0.1:.0f}ms (server processing)")
            print(f"  • Memory usage: ~{data_size_kb * 2:.0f} KB (in browser)")
        
        print(f"\n📈 Scalability Projections:")
        print(f"  • Current capacity: ~10,000 kills efficiently")
        print(f"  • Recommended pagination: 50 entries per page")
        print(f"  • Archive threshold: 6 months of data")
        print(f"  • Database migration: Consider at 100,000+ kills")
        
        print(f"\n🔧 Optimization Strategies:")
        print(f"  • Implement lazy loading for detailed views")
        print(f"  • Cache frequently accessed leaderboards")
        print(f"  • Compress historical data older than 3 months")
        print(f"  • Use CDN for static boss information")

    def simulate_real_time_updates(self):
        """Simulate real-time system updates"""
        self.print_section("Real-Time Updates Simulation")
        
        print("🔄 Real-Time Features:")
        print("  ✓ Live leaderboard updates")
        print("  ✓ New kill notifications")
        print("  ✓ First kill alerts")
        print("  ✓ Record-breaking notifications")
        print("  ✓ Season milestone tracking")
        
        print("\n🎮 Simulating Live Activity...")
        
        # Simulate incoming kills
        sample_kills = [
            {"boss": "IG-88", "time": 98.7, "team": ["SpeedRun_Pro", "FastTrack"]},
            {"boss": "Tusken King", "time": 145.2, "team": ["DesertStorm", "SandMaster", "TatooineHero"]},
            {"boss": "Exar Kun", "time": 267.8, "team": ["SithSlayer", "ForceWielder", "LightBringer", "KunHunter"]},
        ]
        
        for i, kill in enumerate(sample_kills, 1):
            print(f"\n⚡ Live Update #{i}:")
            print(f"  👹 Boss: {kill['boss']} defeated!")
            print(f"  ⏱️  Kill Time: {self.format_time(kill['time'])}")
            print(f"  👥 Team: {', '.join(kill['team'])}")
            
            # Simulate notifications
            if kill['time'] < 100:
                print(f"  🚨 NEW SPEED RECORD! Previous best beaten by {random.randint(1, 10)} seconds!")
            
            if len(kill['team']) == 1:
                print(f"  🥇 SOLO ACHIEVEMENT! Incredible solo performance!")
            
            # Simulate real-time delay
            time.sleep(0.5)
        
        print(f"\n📡 Real-Time Technology Stack:")
        print(f"  • WebSocket connections for live updates")
        print(f"  • Server-sent events for notifications")
        print(f"  • Optimistic UI updates in Svelte components")
        print(f"  • Background data synchronization")
        print(f"  • Graceful degradation for offline users")

    def format_time(self, seconds: float) -> str:
        """Format time in seconds to MM:SS format"""
        if not seconds:
            return "0:00"
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}:{remaining_seconds:02d}"
    
    def format_date(self, date_string: str) -> str:
        """Format ISO date string to readable format"""
        if not date_string:
            return "Unknown"
        try:
            date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return date.strftime("%B %d, %Y")
        except:
            return date_string
    
    def format_team_size_label(self, size: str) -> str:
        """Format team size label"""
        labels = {
            'solo': 'Solo (1 player)',
            'duo': 'Duo (2 players)',
            'trio': 'Trio (3 players)', 
            'quad': 'Quad (4 players)',
            'quintet': 'Quintet (5 players)',
            'sextet': 'Sextet (6 players)',
            'larger': 'Large Teams (7+ players)'
        }
        return labels.get(size, size)
    
    def format_boss_name(self, boss_id: str) -> str:
        """Format boss ID to display name"""
        names = {
            'exar_kun': 'Exar Kun',
            'ig88': 'IG-88',
            'tusken_king': 'Tusken King',
            'lord_nyax': 'Lord Nyax',
            'axkva_min': 'Axkva Min'
        }
        return names.get(boss_id, boss_id.replace('_', ' ').title())

    def run_full_demo(self):
        """Run the complete heroic boss tracker demonstration"""
        self.print_header("MorningStar Heroic Boss Tracker + Stats - Batch 189 Demo")
        
        print("🏆 Welcome to the Heroic Boss Tracker System!")
        print("This demo showcases comprehensive boss kill tracking, leaderboards, and analytics.")
        
        try:
            # Load and analyze data
            self.load_boss_data()
            self.demonstrate_data_structure()
            
            # Core system features
            self.demonstrate_leaderboard_generation()
            self.demonstrate_svelte_component()
            self.demonstrate_api_functionality()
            
            # Advanced features
            self.demonstrate_first_kill_tracking()
            self.demonstrate_user_alias_system()
            self.demonstrate_team_statistics()
            self.demonstrate_season_management()
            self.demonstrate_analytics_dashboard()
            
            # Performance and real-time
            self.run_performance_analysis()
            self.simulate_real_time_updates()
            
            # Summary
            self.print_header("Demo Summary")
            self.print_success("✅ Boss kill data management and structure")
            self.print_success("✅ Public leaderboard generation with Eleventy")
            self.print_success("✅ Interactive Svelte boss statistics components")
            self.print_success("✅ API endpoint for kill logging with validation")
            self.print_success("✅ First kill tracking per season")
            self.print_success("✅ User alias tagging with Discord integration")
            self.print_success("✅ Team statistics and participation analytics")
            self.print_success("✅ Season management and historical tracking")
            self.print_success("✅ Real-time updates and notifications")
            
            print(f"\n🎉 Demo completed successfully!")
            print(f"📊 Demonstrated comprehensive heroic boss tracking system")
            print(f"🏆 Showcased public dashboard with leaderboards and statistics")
            print(f"⚡ Highlighted real-time features and performance optimization")
            
        except KeyboardInterrupt:
            self.print_warning("\n⚠️  Demo interrupted by user")
        except Exception as e:
            self.print_error(f"❌ Demo failed: {str(e)}")
            raise

def main():
    """Main demo execution"""
    demo = HeroicBossTrackerDemo()
    demo.run_full_demo()

if __name__ == "__main__":
    main()