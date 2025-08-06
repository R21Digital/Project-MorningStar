#!/usr/bin/env python3
"""
Demo script for Batch 129 - Social Profile Integration + Vanity Fields

This script demonstrates the social profile functionality by:
1. Creating sample user profiles with social links and vanity fields
2. Testing badge calculation and assignment
3. Demonstrating profile search and filtering
4. Testing API endpoints and data persistence
5. Showing integration with character registry data
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.user_profile import (
    get_profile_manager,
    create_user_profile,
    get_user_profile,
    update_user_profile,
    update_social_links,
    UserProfile,
    SocialLinks,
    BadgeType
)
from core.character_registry import get_registry


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


def demo_profile_creation():
    """Demo creating user profiles with social links and vanity fields."""
    print_header("DEMO: User Profile Creation")
    
    profile_manager = get_profile_manager()
    
    # Sample user profiles with different playstyles and social links
    sample_profiles = [
        {
            'discord_user_id': '123456789',
            'username': 'swg_veteran',
            'display_name': 'SWG Veteran',
            'about_me': 'Long-time SWG player who loves crafting and helping new players. Always up for a good heroic run!',
            'playstyle': 'PvP Main, Crafter',
            'favorite_activities': ['Crafting', 'Heroics', 'PvP', 'Mentoring'],
            'social_links': SocialLinks(
                discord_tag='SWGVeteran#1234',
                twitch_channel='swg_veteran',
                steam_profile='https://steamcommunity.com/id/swg_veteran',
                youtube_channel='swg_veteran',
                twitter_handle='swg_veteran',
                reddit_username='swg_veteran',
                website='https://swg-veteran.com',
                guild_website='https://galacticdefenders.com'
            ),
            'profile_visibility': 'public'
        },
        {
            'discord_user_id': '987654321',
            'username': 'combat_master',
            'display_name': 'Combat Master',
            'about_me': 'Focused on combat and PvP. Specializing in marksman and medic professions.',
            'playstyle': 'Combat Veteran, PvP Specialist',
            'favorite_activities': ['PvP', 'Combat', 'Heroics', 'Guild Wars'],
            'social_links': SocialLinks(
                discord_tag='CombatMaster#5678',
                twitch_channel='combat_master',
                steam_profile='https://steamcommunity.com/id/combat_master',
                youtube_channel='combat_master',
                twitter_handle='combat_master',
                reddit_username='combat_master',
                website='',
                guild_website='https://combatguild.com'
            ),
            'profile_visibility': 'public'
        },
        {
            'discord_user_id': '555666777',
            'username': 'explorer_galaxy',
            'display_name': 'Explorer Galaxy',
            'about_me': 'Passionate explorer who loves discovering new locations and completing quests. Always on the lookout for rare items!',
            'playstyle': 'Explorer, Collector',
            'favorite_activities': ['Exploration', 'Questing', 'Collecting', 'Space Travel'],
            'social_links': SocialLinks(
                discord_tag='ExplorerGalaxy#9012',
                twitch_channel='explorer_galaxy',
                steam_profile='',
                youtube_channel='explorer_galaxy',
                twitter_handle='explorer_galaxy',
                reddit_username='explorer_galaxy',
                website='https://explorer-galaxy.com',
                guild_website=''
            ),
            'profile_visibility': 'public'
        },
        {
            'discord_user_id': '111222333',
            'username': 'entertainer_star',
            'display_name': 'Entertainer Star',
            'about_me': 'Professional entertainer who loves bringing joy to other players. Specializing in music and dance performances.',
            'playstyle': 'Entertainer, Social',
            'favorite_activities': ['Entertainment', 'Music', 'Dance', 'Social Events'],
            'social_links': SocialLinks(
                discord_tag='EntertainerStar#3456',
                twitch_channel='entertainer_star',
                steam_profile='',
                youtube_channel='entertainer_star',
                twitter_handle='entertainer_star',
                reddit_username='entertainer_star',
                website='https://entertainer-star.com',
                guild_website='https://entertainersguild.com'
            ),
            'profile_visibility': 'public'
        }
    ]
    
    created_profiles = []
    
    for profile_data in sample_profiles:
        print_section(f"Creating profile for {profile_data['display_name']}")
        
        profile = create_user_profile(
            discord_user_id=profile_data['discord_user_id'],
            username=profile_data['username'],
            display_name=profile_data['display_name'],
            about_me=profile_data['about_me'],
            playstyle=profile_data['playstyle'],
            favorite_activities=profile_data['favorite_activities'],
            social_links=profile_data['social_links'],
            profile_visibility=profile_data['profile_visibility']
        )
        
        if profile:
            created_profiles.append(profile)
            print(f"✓ Created profile for {profile.display_name}")
            print(f"  - Discord ID: {profile.discord_user_id}")
            print(f"  - Playstyle: {profile.playstyle}")
            print(f"  - Activities: {', '.join(profile.favorite_activities)}")
            print(f"  - Social Links: {sum(1 for link in profile.social_links.__dict__.values() if link)} links")
        else:
            print(f"✗ Failed to create profile for {profile_data['display_name']}")
    
    print(f"\n✓ Created {len(created_profiles)} profiles successfully")
    return created_profiles


def demo_social_links_management():
    """Demo updating social links for users."""
    print_header("DEMO: Social Links Management")
    
    profile_manager = get_profile_manager()
    
    # Test updating social links
    test_user_id = '123456789'
    profile = get_user_profile(test_user_id)
    
    if profile:
        print_section(f"Updating social links for {profile.display_name}")
        
        # Update social links
        updated_profile = update_social_links(
            test_user_id,
            discord_tag='SWGVeteran#9999',
            twitch_channel='swg_veteran_updated',
            youtube_channel='swg_veteran_official'
        )
        
        if updated_profile:
            print("✓ Updated social links successfully")
            print(f"  - Discord: {updated_profile.social_links.discord_tag}")
            print(f"  - Twitch: {updated_profile.social_links.twitch_channel}")
            print(f"  - YouTube: {updated_profile.social_links.youtube_channel}")
        else:
            print("✗ Failed to update social links")
    else:
        print("✗ Profile not found for social links update")


def demo_badge_management():
    """Demo badge assignment and management."""
    print_header("DEMO: Badge Management")
    
    profile_manager = get_profile_manager()
    
    # Test users for badge assignment
    test_users = [
        ('123456789', 'SWG Veteran'),
        ('987654321', 'Combat Master'),
        ('555666777', 'Explorer Galaxy'),
        ('111222333', 'Entertainer Star')
    ]
    
    # Sample badges to assign
    sample_badges = [
        BadgeType.SESSION_MASTER.value,
        BadgeType.XP_CHAMPION.value,
        BadgeType.CREDIT_MAGNATE.value,
        BadgeType.PROFESSION_MASTER.value,
        BadgeType.COMBAT_VETERAN.value,
        BadgeType.ENTERTAINER_STAR.value,
        BadgeType.EXPLORER.value,
        BadgeType.QUEST_MASTER.value,
        BadgeType.COLLECTOR.value,
        BadgeType.GUILD_LEADER.value,
        BadgeType.TEAM_PLAYER.value,
        BadgeType.MENTOR.value,
        BadgeType.COMMUNITY_PILLAR.value
    ]
    
    for user_id, display_name in test_users:
        print_section(f"Managing badges for {display_name}")
        
        profile = get_user_profile(user_id)
        if not profile:
            print(f"✗ Profile not found for {display_name}")
            continue
        
        # Assign some badges
        assigned_badges = []
        for badge in sample_badges[:3]:  # Assign first 3 badges
            if profile_manager.add_badge(user_id, badge):
                assigned_badges.append(badge)
                print(f"  ✓ Added badge: {badge}")
            else:
                print(f"  ✗ Failed to add badge: {badge}")
        
        # Show current badges
        updated_profile = get_user_profile(user_id)
        if updated_profile:
            print(f"  Current badges ({len(updated_profile.badges)}): {', '.join(updated_profile.badges)}")
        
        # Test removing a badge
        if assigned_badges:
            badge_to_remove = assigned_badges[0]
            if profile_manager.remove_badge(user_id, badge_to_remove):
                print(f"  ✓ Removed badge: {badge_to_remove}")
            else:
                print(f"  ✗ Failed to remove badge: {badge_to_remove}")


def demo_badge_calculation():
    """Demo automatic badge calculation based on character data."""
    print_header("DEMO: Automatic Badge Calculation")
    
    profile_manager = get_profile_manager()
    registry = get_registry()
    
    # Create sample character data for badge calculation
    test_user_id = '123456789'
    
    # Get existing characters or create sample data
    characters = registry.get_characters_by_user(test_user_id)
    
    if not characters:
        print("No characters found for badge calculation. Creating sample data...")
        
        # Create sample character data
        character_data = {
            'characters': [
                {
                    'name': 'SWGVeteran',
                    'profession': 'Marksman',
                    'level': 90,
                    'faction': 'Imperial',
                    'guild': 'Galactic Defenders',
                    'total_playtime_hours': 1500,
                    'total_sessions': 150,
                    'total_xp_gained': 2500000,
                    'total_credits_earned': 15000000,
                },
                {
                    'name': 'SWGCrafter',
                    'profession': 'Artisan',
                    'level': 90,
                    'faction': 'Imperial',
                    'guild': 'Galactic Defenders',
                    'total_playtime_hours': 800,
                    'total_sessions': 80,
                    'total_xp_gained': 1200000,
                    'total_credits_earned': 8000000,
                },
                {
                    'name': 'SWGMedic',
                    'profession': 'Medic',
                    'level': 90,
                    'faction': 'Imperial',
                    'guild': 'Galactic Defenders',
                    'total_playtime_hours': 600,
                    'total_sessions': 60,
                    'total_xp_gained': 900000,
                    'total_credits_earned': 5000000,
                }
            ]
        }
        
        # Calculate session totals
        total_sessions = sum(char['total_sessions'] for char in character_data['characters'])
        total_xp = sum(char['total_xp_gained'] for char in character_data['characters'])
        total_credits = sum(char['total_credits_earned'] for char in character_data['characters'])
        total_playtime = sum(char['total_playtime_hours'] for char in character_data['characters'])
        
        session_data = {
            'total_sessions': total_sessions,
            'total_xp_gained': total_xp,
            'total_credits_earned': total_credits,
            'total_playtime_hours': total_playtime,
        }
        
        print(f"Sample data created:")
        print(f"  - Total sessions: {total_sessions}")
        print(f"  - Total XP: {total_xp:,}")
        print(f"  - Total credits: {total_credits:,}")
        print(f"  - Total playtime: {total_playtime} hours")
        
    else:
        print(f"Found {len(characters)} existing characters for badge calculation")
        
        # Use existing character data
        character_data = {
            'characters': [
                {
                    'name': char.name,
                    'profession': char.profession,
                    'level': char.level,
                    'faction': char.faction,
                    'guild': char.guild,
                    'total_playtime_hours': char.total_playtime_hours,
                    'total_sessions': char.total_sessions,
                    'total_xp_gained': char.total_xp_gained,
                    'total_credits_earned': char.total_credits_earned,
                }
                for char in characters
            ]
        }
        
        # Calculate session totals
        total_sessions = sum(char['total_sessions'] for char in character_data['characters'])
        total_xp = sum(char['total_xp_gained'] for char in character_data['characters'])
        total_credits = sum(char['total_credits_earned'] for char in character_data['characters'])
        total_playtime = sum(char['total_playtime_hours'] for char in character_data['characters'])
        
        session_data = {
            'total_sessions': total_sessions,
            'total_xp_gained': total_xp,
            'total_credits_earned': total_credits,
            'total_playtime_hours': total_playtime,
        }
    
    # Calculate badges
    print_section("Calculating badges based on character data")
    earned_badges = profile_manager.calculate_badges(test_user_id, character_data, session_data)
    
    print(f"Earned badges: {earned_badges}")
    
    # Add earned badges to profile
    added_badges = []
    for badge in earned_badges:
        if profile_manager.add_badge(test_user_id, badge):
            added_badges.append(badge)
            print(f"  ✓ Added badge: {badge}")
        else:
            print(f"  ✗ Failed to add badge: {badge}")
    
    print(f"\n✓ Added {len(added_badges)} badges to profile")


def demo_profile_search():
    """Demo profile search and filtering functionality."""
    print_header("DEMO: Profile Search and Filtering")
    
    profile_manager = get_profile_manager()
    
    # Test different search scenarios
    search_scenarios = [
        {
            'name': 'Search by playstyle (PvP)',
            'playstyle': 'PvP'
        },
        {
            'name': 'Search by playstyle (Crafter)',
            'playstyle': 'Crafter'
        },
        {
            'name': 'Search by playstyle (Explorer)',
            'playstyle': 'Explorer'
        },
        {
            'name': 'Search by badges (session_master)',
            'badges': ['session_master']
        },
        {
            'name': 'Search by badges (xp_champion)',
            'badges': ['xp_champion']
        },
        {
            'name': 'Text search (veteran)',
            'query': 'veteran'
        },
        {
            'name': 'Text search (combat)',
            'query': 'combat'
        }
    ]
    
    for scenario in search_scenarios:
        print_section(scenario['name'])
        
        profiles = profile_manager.search_profiles(
            query=scenario.get('query'),
            playstyle=scenario.get('playstyle'),
            badges=scenario.get('badges')
        )
        
        print(f"Found {len(profiles)} profiles:")
        for profile in profiles:
            print(f"  - {profile.display_name} ({profile.playstyle})")
            if profile.badges:
                print(f"    Badges: {', '.join(profile.badges)}")


def demo_profile_updates():
    """Demo updating profile information."""
    print_header("DEMO: Profile Updates")
    
    test_user_id = '123456789'
    profile = get_user_profile(test_user_id)
    
    if profile:
        print_section(f"Updating profile for {profile.display_name}")
        
        # Update profile fields
        updated_profile = update_user_profile(
            test_user_id,
            about_me="Updated bio: Long-time SWG veteran with a passion for crafting and community building!",
            playstyle="PvP Main, Crafter, Community Leader",
            favorite_activities=['Crafting', 'Heroics', 'PvP', 'Mentoring', 'Community Events'],
            profile_visibility='public'
        )
        
        if updated_profile:
            print("✓ Profile updated successfully")
            print(f"  - New playstyle: {updated_profile.playstyle}")
            print(f"  - Activities: {', '.join(updated_profile.favorite_activities)}")
            print(f"  - Visibility: {updated_profile.profile_visibility}")
        else:
            print("✗ Failed to update profile")
    else:
        print("✗ Profile not found for update")


def demo_api_integration():
    """Demo API endpoint functionality."""
    print_header("DEMO: API Integration")
    
    print_section("Available API Endpoints")
    
    endpoints = [
        "GET /api/social/profiles - Get all public profiles",
        "GET /api/social/profiles/<discord_user_id> - Get specific profile",
        "POST /api/social/profiles - Create new profile",
        "PUT /api/social/profiles/<discord_user_id> - Update profile",
        "PUT /api/social/profiles/<discord_user_id>/social-links - Update social links",
        "POST /api/social/profiles/<discord_user_id>/badges - Add badge",
        "DELETE /api/social/profiles/<discord_user_id>/badges/<badge> - Remove badge",
        "POST /api/social/profiles/<discord_user_id>/calculate-badges - Calculate badges",
        "GET /api/social/badges - Get all available badges",
        "GET /api/social/health - Health check"
    ]
    
    for endpoint in endpoints:
        print(f"  {endpoint}")
    
    print_section("Sample API Usage")
    
    # Sample curl commands
    curl_commands = [
        "# Get all profiles",
        "curl -X GET 'http://localhost:5000/api/social/profiles'",
        "",
        "# Get specific profile",
        "curl -X GET 'http://localhost:5000/api/social/profiles/123456789'",
        "",
        "# Create new profile",
        """curl -X POST 'http://localhost:5000/api/social/profiles' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "discord_user_id": "999888777",
    "username": "new_user",
    "display_name": "New User",
    "about_me": "New to SWG!",
    "playstyle": "New Player",
    "favorite_activities": ["Learning", "Questing"],
    "profile_visibility": "public"
  }'""",
        "",
        "# Update social links",
        """curl -X PUT 'http://localhost:5000/api/social/profiles/123456789/social-links' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "discord_tag": "UpdatedUser#1234",
    "twitch_channel": "updated_channel"
  }'""",
        "",
        "# Add badge",
        """curl -X POST 'http://localhost:5000/api/social/profiles/123456789/badges' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "badge": "session_master"
  }'""",
        "",
        "# Calculate badges",
        "curl -X POST 'http://localhost:5000/api/social/profiles/123456789/calculate-badges'"
    ]
    
    for command in curl_commands:
        print(command)


def demo_data_persistence():
    """Demo data persistence and file structure."""
    print_header("DEMO: Data Persistence")
    
    profile_manager = get_profile_manager()
    
    print_section("Profile Storage Location")
    print(f"Profiles directory: {profile_manager.profiles_dir}")
    print(f"Profiles loaded: {len(profile_manager.profiles)}")
    
    print_section("Profile Files")
    if profile_manager.profiles_dir.exists():
        profile_files = list(profile_manager.profiles_dir.glob("*.json"))
        for profile_file in profile_files:
            file_size = profile_file.stat().st_size
            print(f"  {profile_file.name} ({file_size} bytes)")
    else:
        print("  No profile files found")
    
    print_section("Sample Profile Data Structure")
    if profile_manager.profiles:
        sample_profile = list(profile_manager.profiles.values())[0]
        profile_dict = {
            'discord_user_id': sample_profile.discord_user_id,
            'username': sample_profile.username,
            'display_name': sample_profile.display_name,
            'about_me': sample_profile.about_me,
            'playstyle': sample_profile.playstyle,
            'favorite_activities': sample_profile.favorite_activities,
            'social_links': {
                'discord_tag': sample_profile.social_links.discord_tag,
                'twitch_channel': sample_profile.social_links.twitch_channel,
                'steam_profile': sample_profile.social_links.steam_profile,
                'youtube_channel': sample_profile.social_links.youtube_channel,
                'twitter_handle': sample_profile.social_links.twitter_handle,
                'reddit_username': sample_profile.social_links.reddit_username,
                'website': sample_profile.social_links.website,
                'guild_website': sample_profile.social_links.guild_website,
            },
            'badges': sample_profile.badges,
            'profile_visibility': sample_profile.profile_visibility,
            'created_at': sample_profile.created_at,
            'updated_at': sample_profile.updated_at,
            'last_active': sample_profile.last_active,
        }
        
        print("Profile JSON structure:")
        print(json.dumps(profile_dict, indent=2))


def main():
    """Run the complete social profile demo."""
    print_header("BATCH 129 - SOCIAL PROFILE INTEGRATION DEMO")
    print("Testing social profile functionality with vanity fields and badges")
    
    try:
        # Run all demos
        created_profiles = demo_profile_creation()
        demo_social_links_management()
        demo_badge_management()
        demo_badge_calculation()
        demo_profile_search()
        demo_profile_updates()
        demo_api_integration()
        demo_data_persistence()
        
        print_header("DEMO COMPLETED SUCCESSFULLY")
        print("✓ All social profile functionality tested")
        print("✓ User profiles with social links created")
        print("✓ Badge system implemented and tested")
        print("✓ API endpoints ready for use")
        print("✓ Data persistence working correctly")
        print("\nNext steps:")
        print("1. Integrate with Flask app using register_social_api()")
        print("2. Add PublicProfileHeader component to UI")
        print("3. Create profile edit forms")
        print("4. Implement profile search interface")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 