#!/usr/bin/env python3
"""
Demo script for Batch 130 - Reputation + Build Voting System

This script demonstrates the voting system functionality by:
1. Creating sample votes for builds, guides, and profiles
2. Testing anti-abuse protection and IP tracking
3. Demonstrating vote summaries and popularity rankings
4. Testing reputation score calculations
5. Showing API endpoints and data persistence
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import random

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.voting_system import (
    get_voting_system,
    ContentType,
    VoteType,
    submit_vote,
    get_vote_summary,
    get_top_content
)


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


def demo_vote_submission():
    """Demo submitting votes on different content types."""
    print_header("DEMO: Vote Submission")
    
    voting_system = get_voting_system()
    
    # Sample content to vote on
    sample_content = [
        {
            'content_type': ContentType.BUILD,
            'content_id': 'marksman_dps_build_001',
            'title': 'Marksman DPS Build',
            'creator_discord_id': '123456789'
        },
        {
            'content_type': ContentType.GUIDE,
            'content_id': 'heroic_completion_guide',
            'title': 'Heroic Mission Completion Guide',
            'creator_discord_id': '987654321'
        },
        {
            'content_type': ContentType.PROFILE,
            'content_id': 'swg_veteran_profile',
            'title': 'SWG Veteran Profile',
            'creator_discord_id': '555666777'
        },
        {
            'content_type': ContentType.BUILD,
            'content_id': 'medic_support_build',
            'title': 'Medic Support Build',
            'creator_discord_id': '111222333'
        },
        {
            'content_type': ContentType.GUIDE,
            'content_id': 'pvp_strategy_guide',
            'title': 'PvP Strategy Guide',
            'creator_discord_id': '444555666'
        }
    ]
    
    # Sample voters with different IPs
    sample_voters = [
        {'ip': '192.168.1.100', 'discord_id': 'voter_001', 'name': 'Player Alpha'},
        {'ip': '192.168.1.101', 'discord_id': 'voter_002', 'name': 'Player Beta'},
        {'ip': '192.168.1.102', 'discord_id': 'voter_003', 'name': 'Player Gamma'},
        {'ip': '192.168.1.103', 'discord_id': 'voter_004', 'name': 'Player Delta'},
        {'ip': '192.168.1.104', 'discord_id': 'voter_005', 'name': 'Player Epsilon'}
    ]
    
    vote_types = [VoteType.THUMBS_UP, VoteType.THUMBS_DOWN, VoteType.NEUTRAL]
    reasons = [
        "Great build, very effective!",
        "Could use some improvements",
        "Not bad, but needs work",
        "Excellent guide, very helpful",
        "Missing some key information",
        "Perfect for my playstyle",
        "Too complex for beginners",
        "Well-balanced and versatile"
    ]
    
    feedback_options = [
        "Consider adding more detail about skill progression",
        "Maybe include alternative gear options",
        "Great job on the explanations",
        "Could benefit from more examples",
        "Very comprehensive and well-written",
        "Needs better formatting",
        "Excellent tips and tricks",
        "Consider adding video demonstrations"
    ]
    
    successful_votes = 0
    failed_votes = 0
    
    print("Submitting votes for different content...")
    
    for content in sample_content:
        print_section(f"Voting on {content['title']}")
        
        # Submit multiple votes for each content
        for i in range(random.randint(3, 8)):  # 3-8 votes per content
            voter = random.choice(sample_voters)
            vote_type = random.choice(vote_types)
            reason = random.choice(reasons)
            feedback = random.choice(feedback_options)
            
            success, message, vote_id = submit_vote(
                content_type=content['content_type'],
                content_id=content['content_id'],
                voter_ip=voter['ip'],
                vote_type=vote_type,
                voter_discord_id=voter['discord_id'],
                reason=reason,
                feedback=feedback
            )
            
            if success:
                successful_votes += 1
                print(f"  ✓ {voter['name']} voted {vote_type.value} on {content['title']}")
                print(f"    Reason: {reason[:50]}...")
            else:
                failed_votes += 1
                print(f"  ✗ Failed vote: {message}")
    
    print(f"\nVote submission summary:")
    print(f"  ✓ Successful votes: {successful_votes}")
    print(f"  ✗ Failed votes: {failed_votes}")
    print(f"  📊 Total votes processed: {successful_votes + failed_votes}")


def demo_abuse_protection():
    """Demo anti-abuse protection features."""
    print_header("DEMO: Anti-Abuse Protection")
    
    voting_system = get_voting_system()
    
    # Test rapid voting (should be blocked)
    print_section("Testing rapid voting protection")
    
    test_ip = '192.168.1.999'
    test_content = {
        'content_type': ContentType.BUILD,
        'content_id': 'test_build_001',
        'title': 'Test Build'
    }
    
    # Try to submit votes rapidly
    rapid_votes = 0
    for i in range(10):
        success, message, vote_id = submit_vote(
            content_type=test_content['content_type'],
            content_id=test_content['content_id'],
            voter_ip=test_ip,
            vote_type=VoteType.THUMBS_UP,
            voter_discord_id='test_user',
            reason=f"Rapid vote {i+1}"
        )
        
        if success:
            rapid_votes += 1
            print(f"  ✓ Vote {i+1} submitted")
        else:
            print(f"  ✗ Vote {i+1} blocked: {message}")
            break
    
    print(f"Rapid voting test: {rapid_votes} votes submitted before blocking")
    
    # Test Discord user abuse
    print_section("Testing Discord user abuse protection")
    
    test_discord_id = 'abuse_test_user'
    discord_votes = 0
    
    for i in range(15):
        success, message, vote_id = submit_vote(
            content_type=ContentType.GUIDE,
            content_id=f'guide_{i:03d}',
            voter_ip=f'192.168.1.{100+i}',
            vote_type=VoteType.THUMBS_UP,
            voter_discord_id=test_discord_id,
            reason=f"Discord abuse test {i+1}"
        )
        
        if success:
            discord_votes += 1
            print(f"  ✓ Discord vote {i+1} submitted")
        else:
            print(f"  ✗ Discord vote {i+1} blocked: {message}")
            break
    
    print(f"Discord abuse test: {discord_votes} votes submitted before blocking")


def demo_vote_summaries():
    """Demo vote summary generation and popularity rankings."""
    print_header("DEMO: Vote Summaries and Rankings")
    
    voting_system = get_voting_system()
    
    # Get vote summaries for all content types
    for content_type in ContentType:
        print_section(f"Top {content_type.value} content")
        
        top_content = get_top_content(content_type, limit=5)
        
        if top_content:
            for i, summary in enumerate(top_content, 1):
                print(f"  {i}. {summary.content_id}")
                print(f"     Score: {summary.score} | Votes: {summary.total_votes}")
                print(f"     👍 {summary.thumbs_up} | 👎 {summary.thumbs_down} | ➖ {summary.neutral}")
                print(f"     Rank: #{summary.popularity_rank}")
                print()
        else:
            print(f"  No {content_type.value} content found")
    
    # Show detailed vote summary for a specific content
    print_section("Detailed vote summary example")
    
    test_content_id = 'marksman_dps_build_001'
    summary = get_vote_summary(ContentType.BUILD, test_content_id)
    
    if summary:
        print(f"Content: {test_content_id}")
        print(f"Total votes: {summary.total_votes}")
        print(f"Score: {summary.score}")
        print(f"Thumbs up: {summary.thumbs_up}")
        print(f"Thumbs down: {summary.thumbs_down}")
        print(f"Neutral: {summary.neutral}")
        print(f"Popularity rank: #{summary.popularity_rank}")
        print(f"Last updated: {summary.last_updated}")
    else:
        print(f"No votes found for {test_content_id}")


def demo_reputation_system():
    """Demo reputation score calculations."""
    print_header("DEMO: Reputation System")
    
    voting_system = get_voting_system()
    
    # Test reputation scores for different users
    test_users = [
        'voter_001',
        'voter_002', 
        'voter_003',
        'voter_004',
        'voter_005'
    ]
    
    print_section("User reputation scores")
    
    for user_id in test_users:
        reputation = voting_system.get_reputation_score(user_id)
        
        if reputation:
            print(f"User: {user_id}")
            print(f"  Total score: {reputation.total_score}")
            print(f"  Positive votes given: {reputation.positive_votes_given}")
            print(f"  Negative votes given: {reputation.negative_votes_given}")
            print(f"  Reputation level: {reputation.reputation_level}")
            print(f"  Created: {reputation.created_at}")
            print(f"  Updated: {reputation.updated_at}")
            print()
        else:
            print(f"User {user_id}: No reputation data found")
    
    # Show reputation statistics
    print_section("Reputation statistics")
    
    reputation_scores = list(voting_system.reputation_scores.values())
    
    if reputation_scores:
        total_users = len(reputation_scores)
        avg_score = sum(r.total_score for r in reputation_scores) / total_users
        max_score = max(r.total_score for r in reputation_scores)
        min_score = min(r.total_score for r in reputation_scores)
        
        level_counts = {}
        for rep in reputation_scores:
            level = rep.reputation_level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print(f"Total users with reputation: {total_users}")
        print(f"Average score: {avg_score:.2f}")
        print(f"Highest score: {max_score}")
        print(f"Lowest score: {min_score}")
        print("Reputation level distribution:")
        for level, count in level_counts.items():
            print(f"  {level}: {count} users")
    else:
        print("No reputation data available")


def demo_api_endpoints():
    """Demo API endpoint usage."""
    print_header("DEMO: API Endpoints")
    
    print_section("Available API endpoints")
    
    endpoints = [
        "POST /api/votes/submit - Submit a vote",
        "GET /api/votes/summary/{content_type}/{content_id} - Get vote summary",
        "GET /api/votes/user-vote/{content_type}/{content_id} - Get user's vote",
        "GET /api/votes/top/{content_type} - Get top content",
        "GET /api/votes/statistics - Get vote statistics",
        "GET /api/votes/reputation/{discord_id} - Get user reputation",
        "DELETE /api/votes/delete/{vote_id} - Delete a vote",
        "POST /api/votes/flag/{vote_id} - Flag a vote for review",
        "GET /api/votes/health - Health check"
    ]
    
    for endpoint in endpoints:
        print(f"  {endpoint}")
    
    print_section("Sample API usage")
    
    # Sample curl commands
    curl_examples = [
        {
            'description': 'Submit a thumbs up vote',
            'command': '''curl -X POST http://localhost:5000/api/votes/submit \\
  -H "Content-Type: application/json" \\
  -d '{
    "content_type": "build",
    "content_id": "marksman_dps_build_001",
    "vote_type": "thumbs_up",
    "voter_discord_id": "user123",
    "reason": "Great build!",
    "feedback": "Very effective for PvP"
  }' '''
        },
        {
            'description': 'Get vote summary',
            'command': '''curl http://localhost:5000/api/votes/summary/build/marksman_dps_build_001'''
        },
        {
            'description': 'Get top builds',
            'command': '''curl "http://localhost:5000/api/votes/top/build?limit=10&min_votes=1"'''
        },
        {
            'description': 'Get vote statistics',
            'command': '''curl http://localhost:5000/api/votes/statistics'''
        }
    ]
    
    for example in curl_examples:
        print(f"\n{example['description']}:")
        print(f"  {example['command']}")


def demo_data_persistence():
    """Demo data persistence and file structure."""
    print_header("DEMO: Data Persistence")
    
    voting_system = get_voting_system()
    
    print_section("Data directory structure")
    
    data_dir = voting_system.data_dir
    print(f"Data directory: {data_dir}")
    
    if data_dir.exists():
        print("\nFiles in data directory:")
        for file_path in data_dir.rglob("*.json"):
            relative_path = file_path.relative_to(data_dir)
            file_size = file_path.stat().st_size
            print(f"  {relative_path} ({file_size} bytes)")
    
    print_section("Vote statistics")
    
    stats = voting_system.get_vote_statistics()
    
    print(f"Total votes: {stats['total_votes']}")
    print(f"Active votes: {stats['active_votes']}")
    print(f"Flagged votes: {stats['flagged_votes']}")
    print(f"Thumbs up: {stats['thumbs_up']}")
    print(f"Thumbs down: {stats['thumbs_down']}")
    print(f"Neutral: {stats['neutral']}")
    print(f"Total summaries: {stats['total_summaries']}")
    print(f"Total reputation scores: {stats['total_reputation_scores']}")
    
    print("\nContent type breakdown:")
    for content_type, count in stats['content_breakdown'].items():
        print(f"  {content_type}: {count} votes")


def demo_popularity_features():
    """Demo popularity features and rankings."""
    print_header("DEMO: Popularity Features")
    
    voting_system = get_voting_system()
    
    print_section("Most voted content by type")
    
    for content_type in ContentType:
        top_content = get_top_content(content_type, limit=3, min_votes=1)
        
        if top_content:
            print(f"\nTop {content_type.value}:")
            for i, summary in enumerate(top_content, 1):
                print(f"  {i}. {summary.content_id}")
                print(f"     Score: {summary.score} | Votes: {summary.total_votes}")
                print(f"     Rank: #{summary.popularity_rank}")
        else:
            print(f"\nNo {content_type.value} content with votes")
    
    print_section("Popularity badges")
    
    # Simulate popularity badges based on vote counts
    popularity_badges = {
        "Most Voted Crafter Build": "marksman_dps_build_001",
        "Top PvP Rifleman Guide": "pvp_strategy_guide", 
        "Community Favorite Profile": "swg_veteran_profile",
        "Highly Rated Support Build": "medic_support_build"
    }
    
    for badge_name, content_id in popularity_badges.items():
        summary = get_vote_summary(ContentType.BUILD, content_id)
        if summary:
            print(f"🏆 {badge_name}: {content_id}")
            print(f"   Score: {summary.score} | Votes: {summary.total_votes}")
        else:
            print(f"🏆 {badge_name}: {content_id} (No votes yet)")


def main():
    """Run the complete voting system demo."""
    print_header("BATCH 130 - REPUTATION + BUILD VOTING SYSTEM DEMO")
    
    try:
        # Run all demo functions
        demo_vote_submission()
        demo_abuse_protection()
        demo_vote_summaries()
        demo_reputation_system()
        demo_api_endpoints()
        demo_data_persistence()
        demo_popularity_features()
        
        print_header("DEMO COMPLETED SUCCESSFULLY")
        print("\n✅ All voting system features demonstrated:")
        print("  ✓ Vote submission with IP tracking")
        print("  ✓ Anti-abuse protection")
        print("  ✓ Vote summaries and rankings")
        print("  ✓ Reputation score calculations")
        print("  ✓ API endpoints and data persistence")
        print("  ✓ Popularity features and badges")
        
        print("\n🎯 Key Features Implemented:")
        print("  • Thumbs up/down/neutral voting")
        print("  • IP and Discord ID tracking")
        print("  • Anti-abuse protection (rate limiting)")
        print("  • Vote summaries and popularity rankings")
        print("  • Reputation system with levels")
        print("  • RESTful API endpoints")
        print("  • Data persistence in JSON files")
        print("  • Guide creator reply support")
        
        print("\n📊 System Statistics:")
        voting_system = get_voting_system()
        stats = voting_system.get_vote_statistics()
        print(f"  • Total votes: {stats['total_votes']}")
        print(f"  • Active votes: {stats['active_votes']}")
        print(f"  • Content types: {len(stats['content_breakdown'])}")
        print(f"  • Users with reputation: {stats['total_reputation_scores']}")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 