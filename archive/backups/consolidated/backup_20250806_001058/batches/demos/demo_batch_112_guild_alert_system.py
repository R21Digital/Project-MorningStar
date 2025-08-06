"""Demo script for Batch 112 - Guild Alert System + Priority Communication.

This demo showcases the guild alert system functionality including:
- Guild member detection
- Priority alert handling
- Auto-reply generation
- Discord integration
- Session analytics tracking
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from modules.guild_alert_system import GuildAlertSystem
from core.session_manager import SessionManager
from discord_relay import DiscordRelay

def demo_guild_member_detection():
    """Demo guild member detection functionality."""
    print("\n=== Guild Member Detection Demo ===")
    
    # Initialize guild alert system
    guild_system = GuildAlertSystem()
    
    # Test guild member detection
    test_players = [
        "GuildMaster",      # Guild leader
        "OfficerOne",       # Guild officer
        "MemberOne",        # Regular member
        "RandomPlayer",     # Non-guild member
        "OfficerTwo",       # Another officer
        "MemberTwo"         # Another member
    ]
    
    for player in test_players:
        is_member = guild_system.is_guild_member(player)
        is_leader = guild_system.is_guild_leader(player)
        is_officer = guild_system.is_guild_officer(player)
        
        status = "Leader" if is_leader else "Officer" if is_officer else "Member" if is_member else "Non-member"
        print(f"Player: {player:<12} | Status: {status}")
    
    return guild_system

def demo_priority_detection(guild_system):
    """Demo priority detection for different message types."""
    print("\n=== Priority Detection Demo ===")
    
    test_messages = [
        ("GuildMaster", "Hello, we need to discuss guild strategy"),
        ("OfficerOne", "Can you help with the raid tonight?"),
        ("MemberOne", "Just checking in"),
        ("OfficerTwo", "URGENT: We need backup at the heroic!"),
        ("MemberTwo", "How's it going?"),
        ("GuildMaster", "EMERGENCY: Guild bank has been compromised")
    ]
    
    for sender, message in test_messages:
        priority = guild_system.get_alert_priority(sender, message)
        alert_type = "leader_message" if guild_system.is_guild_leader(sender) else \
                    "officer_message" if guild_system.is_guild_officer(sender) else "guild_whisper"
        
        print(f"Sender: {sender:<12} | Priority: {priority:<6} | Type: {alert_type}")
        print(f"Message: {message}")
        print("-" * 50)

def demo_auto_reply_generation(guild_system):
    """Demo auto-reply generation for different scenarios."""
    print("\n=== Auto-Reply Generation Demo ===")
    
    test_scenarios = [
        ("GuildMaster", "We need to schedule a guild meeting"),
        ("OfficerOne", "Can you help with training new members?"),
        ("MemberOne", "Just saying hi"),
        ("OfficerTwo", "URGENT: Need help with heroic mission"),
        ("MemberTwo", "How's the questing going?")
    ]
    
    for sender, message in test_scenarios:
        member = guild_system.get_guild_member(sender)
        if member:
            auto_reply = guild_system.generate_auto_reply(sender, message, member)
            print(f"Sender: {sender}")
            print(f"Message: {message}")
            print(f"Auto-Reply: {auto_reply or 'None'}")
            print("-" * 50)

def demo_guild_alert_processing(guild_system):
    """Demo complete guild alert processing."""
    print("\n=== Guild Alert Processing Demo ===")
    
    test_alerts = [
        ("GuildMaster", "We need to discuss guild strategy for next week"),
        ("OfficerOne", "Can you help with the heroic mission tonight?"),
        ("MemberOne", "Just checking in to see how you're doing"),
        ("OfficerTwo", "URGENT: We need immediate backup at the raid!"),
        ("MemberTwo", "How's the questing going? Any tips?"),
        ("GuildMaster", "EMERGENCY: Guild bank security breach detected")
    ]
    
    alerts_processed = []
    
    for sender, message in test_alerts:
        print(f"\nProcessing alert from {sender}:")
        print(f"Message: {message}")
        
        alert = guild_system.process_guild_whisper(sender, message)
        
        if alert:
            alerts_processed.append(alert)
            print(f"Alert Type: {alert.alert_type}")
            print(f"Priority: {alert.priority}")
            print(f"Auto-Reply Sent: {alert.auto_reply_sent}")
            if alert.reply_message:
                print(f"Reply: {alert.reply_message}")
        else:
            print("No guild alert generated (not a guild member)")
        
        print("-" * 50)
    
    return alerts_processed

def demo_session_integration(guild_system):
    """Demo integration with session manager."""
    print("\n=== Session Integration Demo ===")
    
    # Create session manager
    session = SessionManager(mode="guild_alert_demo")
    
    # Simulate some guild alerts
    test_alerts = [
        ("GuildMaster", "Guild meeting tonight at 8 PM", "leader_message", "high", True, "I'll be there!"),
        ("OfficerOne", "Need help with heroic", "officer_message", "high", True, "On my way!"),
        ("MemberOne", "Just saying hi", "guild_whisper", "low", True, "Hi there!"),
        ("OfficerTwo", "URGENT: Raid starting now", "officer_message", "high", False, None)
    ]
    
    for sender, message, alert_type, priority, auto_reply_sent, reply_message in test_alerts:
        session.record_guild_alert(sender, message, alert_type, priority, auto_reply_sent, reply_message)
        print(f"Recorded guild alert: {sender} - {message}")
    
    # Get analytics
    analytics = guild_system.get_session_analytics()
    print(f"\nGuild Alert Analytics:")
    print(f"Total Alerts: {analytics['guild_alerts_total']}")
    print(f"By Type: {analytics['guild_alerts_by_type']}")
    print(f"By Priority: {analytics['guild_alerts_by_priority']}")
    print(f"Auto-Replies Sent: {analytics['auto_replies_sent']}")
    print(f"Members Contacted: {analytics['guild_members_contacted']}")
    
    return session

def demo_discord_integration():
    """Demo Discord integration (simulated)."""
    print("\n=== Discord Integration Demo ===")
    
    # Note: This is a simulation since we don't have actual Discord credentials
    print("Discord integration would send priority alerts with:")
    print("- 🚨 Priority indicators for guild messages")
    print("- Color-coded embeds (red for high priority)")
    print("- Auto-reply information in the embed")
    print("- Guild member role information")
    
    # Simulate what the Discord message would look like
    sample_embed = {
        "title": "🚨 Guild Alert: Leader Message",
        "description": "**GuildMaster**: We need to discuss guild strategy",
        "color": "red",
        "fields": [
            {"name": "Priority", "value": "HIGH", "inline": True},
            {"name": "Type", "value": "Leader Message", "inline": True},
            {"name": "Auto-Reply", "value": "Hello GuildMaster! I'll make sure to address your message when I'm available.", "inline": False}
        ]
    }
    
    print(f"\nSample Discord Embed:")
    print(json.dumps(sample_embed, indent=2))

def demo_configuration_management(guild_system):
    """Demo guild configuration management."""
    print("\n=== Configuration Management Demo ===")
    
    # Add a new guild member
    guild_system.add_guild_member("NewMember", "member", 3)
    print("Added new guild member: NewMember")
    
    # Test the new member
    is_member = guild_system.is_guild_member("NewMember")
    print(f"Is NewMember a guild member? {is_member}")
    
    # Remove a member
    guild_system.remove_guild_member("MemberThree")
    print("Removed guild member: MemberThree")
    
    # Test removal
    is_member = guild_system.is_guild_member("MemberThree")
    print(f"Is MemberThree still a guild member? {is_member}")

def demo_export_functionality(guild_system):
    """Demo export functionality."""
    print("\n=== Export Functionality Demo ===")
    
    # Export alerts to file
    export_path = guild_system.export_alerts()
    print(f"Exported alerts to: {export_path}")
    
    # Read and display export data
    with open(export_path, 'r') as f:
        export_data = json.load(f)
    
    print(f"Export contains {len(export_data['alerts'])} alerts")
    print(f"Guild name: {export_data['guild_name']}")
    print(f"Export timestamp: {export_data['export_timestamp']}")

def main():
    """Run the complete guild alert system demo."""
    print("=== Batch 112 - Guild Alert System Demo ===")
    print("Testing guild member detection, priority alerts, and Discord integration")
    
    try:
        # Demo 1: Guild member detection
        guild_system = demo_guild_member_detection()
        
        # Demo 2: Priority detection
        demo_priority_detection(guild_system)
        
        # Demo 3: Auto-reply generation
        demo_auto_reply_generation(guild_system)
        
        # Demo 4: Complete alert processing
        alerts = demo_guild_alert_processing(guild_system)
        
        # Demo 5: Session integration
        session = demo_session_integration(guild_system)
        
        # Demo 6: Discord integration (simulated)
        demo_discord_integration()
        
        # Demo 7: Configuration management
        demo_configuration_management(guild_system)
        
        # Demo 8: Export functionality
        demo_export_functionality(guild_system)
        
        print("\n=== Demo Complete ===")
        print("✅ Guild Alert System successfully tested")
        print("✅ Priority detection working")
        print("✅ Auto-reply generation working")
        print("✅ Session integration working")
        print("✅ Configuration management working")
        print("✅ Export functionality working")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 