"""Guild Alert System for detecting guild members and sending priority notifications.

This module provides functionality to:
- Detect if a whisper is from a guild member
- Load and manage guild roster
- Send priority alerts for guild leader/officer messages
- Provide AI-enabled or RP-friendly auto-replies
- Track guild alerts in session logs for analytics
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import discord
from discord import Embed, Color
import asyncio

from android_ms11.utils.logging_utils import log_event
from modules.discord_alerts.discord_notifier import DiscordNotifier

logger = logging.getLogger(__name__)

@dataclass
class GuildMember:
    """Represents a guild member with their role and status."""
    name: str
    role: str  # leader, officer, member
    rank: int  # 1=leader, 2=officer, 3=member
    online: bool = False
    last_seen: Optional[str] = None

@dataclass
class GuildAlert:
    """Represents a guild alert event."""
    timestamp: str
    sender: str
    message: str
    alert_type: str  # guild_whisper, leader_message, officer_message
    priority: str  # high, medium, low
    auto_reply_sent: bool = False
    reply_message: Optional[str] = None

class GuildAlertSystem:
    """Handles guild member detection and priority alert system."""
    
    def __init__(self, config_path: str = "config/guild_config.json"):
        """Initialize the guild alert system.
        
        Parameters
        ----------
        config_path : str
            Path to guild configuration file
        """
        self.config_path = Path(config_path)
        self.guild_members: Dict[str, GuildMember] = {}
        self.guild_name: Optional[str] = None
        self.guild_leader: Optional[str] = None
        self.guild_officers: List[str] = []
        
        # Alert tracking
        self.alerts: List[GuildAlert] = []
        self.auto_reply_templates: Dict[str, str] = {}
        
        # Discord integration
        self.discord_notifier: Optional[DiscordNotifier] = None
        self._setup_discord_integration()
        
        # Load configuration
        self._load_guild_config()
        self._load_auto_reply_templates()
        
        log_event("[GUILD_ALERT] Guild alert system initialized")
    
    def _setup_discord_integration(self):
        """Setup Discord integration for alerts."""
        try:
            self.discord_notifier = DiscordNotifier()
            log_event("[GUILD_ALERT] Discord integration enabled")
        except Exception as e:
            log_event(f"[GUILD_ALERT] Discord integration failed: {e}")
            self.discord_notifier = None
    
    def _load_guild_config(self):
        """Load guild configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                self.guild_name = config.get("guild_name")
                self.guild_leader = config.get("guild_leader")
                self.guild_officers = config.get("guild_officers", [])
                
                # Load guild members
                members_data = config.get("members", {})
                for name, member_data in members_data.items():
                    self.guild_members[name] = GuildMember(
                        name=name,
                        role=member_data.get("role", "member"),
                        rank=member_data.get("rank", 3),
                        online=member_data.get("online", False),
                        last_seen=member_data.get("last_seen")
                    )
                
                log_event(f"[GUILD_ALERT] Loaded guild config: {len(self.guild_members)} members")
            else:
                log_event("[GUILD_ALERT] No guild config file found, creating default")
                self._create_default_config()
                
        except Exception as e:
            log_event(f"[GUILD_ALERT] Error loading guild config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create a default guild configuration."""
        default_config = {
            "guild_name": "Your Guild Name",
            "guild_leader": "",
            "guild_officers": [],
            "members": {},
            "auto_reply_enabled": True,
            "priority_alerts_enabled": True,
            "discord_integration": True
        }
        
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        log_event(f"[GUILD_ALERT] Created default config at {self.config_path}")
    
    def _load_auto_reply_templates(self):
        """Load auto-reply templates for different scenarios."""
        self.auto_reply_templates = {
            "guild_greeting": "Hey {sender}! Thanks for the message. I'm currently busy but will get back to you soon.",
            "guild_leader": "Hello {sender}! I'll make sure to address your message when I'm available.",
            "guild_officer": "Hi {sender}! I've noted your message and will respond when I can.",
            "guild_member": "Thanks for reaching out, {sender}! I'll get back to you shortly.",
            "afk_response": "I'm currently AFK but will respond when I return. Thanks for your patience!",
            "busy_response": "I'm in the middle of something right now, but I'll respond when I'm free."
        }
    
    def is_guild_member(self, player_name: str) -> bool:
        """Check if a player is a guild member.
        
        Parameters
        ----------
        player_name : str
            Name of the player to check
            
        Returns
        -------
        bool
            True if player is a guild member
        """
        return player_name.lower() in [name.lower() for name in self.guild_members.keys()]
    
    def get_guild_member(self, player_name: str) -> Optional[GuildMember]:
        """Get guild member information.
        
        Parameters
        ----------
        player_name : str
            Name of the player
            
        Returns
        -------
        GuildMember or None
            Guild member object if found
        """
        for name, member in self.guild_members.items():
            if name.lower() == player_name.lower():
                return member
        return None
    
    def is_guild_leader(self, player_name: str) -> bool:
        """Check if player is the guild leader."""
        if not self.guild_leader:
            return False
        return player_name.lower() == self.guild_leader.lower()
    
    def is_guild_officer(self, player_name: str) -> bool:
        """Check if player is a guild officer."""
        return player_name.lower() in [name.lower() for name in self.guild_officers]
    
    def get_alert_priority(self, sender: str, message: str) -> str:
        """Determine the priority level of a guild alert.
        
        Parameters
        ----------
        sender : str
            Name of the message sender
        message : str
            Content of the message
            
        Returns
        -------
        str
            Priority level: high, medium, or low
        """
        # High priority for guild leader
        if self.is_guild_leader(sender):
            return "high"
        
        # High priority for officers
        if self.is_guild_officer(sender):
            return "high"
        
        # Medium priority for urgent keywords
        urgent_keywords = ["urgent", "emergency", "help", "assist", "raid", "event"]
        if any(keyword in message.lower() for keyword in urgent_keywords):
            return "medium"
        
        # Low priority for regular guild members
        return "low"
    
    def generate_auto_reply(self, sender: str, message: str, member: GuildMember) -> Optional[str]:
        """Generate an appropriate auto-reply based on sender and context.
        
        Parameters
        ----------
        sender : str
            Name of the message sender
        message : str
            Content of the message
        member : GuildMember
            Guild member information
            
        Returns
        -------
        str or None
            Auto-reply message or None if no reply should be sent
        """
        # Check if auto-replies are enabled
        config = self._load_config()
        if not config.get("auto_reply_enabled", True):
            return None
        
        # Choose template based on sender role
        if self.is_guild_leader(sender):
            template = self.auto_reply_templates.get("guild_leader")
        elif self.is_guild_officer(sender):
            template = self.auto_reply_templates.get("guild_officer")
        else:
            template = self.auto_reply_templates.get("guild_member")
        
        if template:
            return template.format(sender=sender)
        
        return None
    
    def process_guild_whisper(self, sender: str, message: str) -> Optional[GuildAlert]:
        """Process a whisper and determine if it's a guild alert.
        
        Parameters
        ----------
        sender : str
            Name of the message sender
        message : str
            Content of the message
            
        Returns
        -------
        GuildAlert or None
            Guild alert object if it's a guild member, None otherwise
        """
        # Check if sender is a guild member
        if not self.is_guild_member(sender):
            return None
        
        member = self.get_guild_member(sender)
        if not member:
            return None
        
        # Determine alert type and priority
        alert_type = "guild_whisper"
        if self.is_guild_leader(sender):
            alert_type = "leader_message"
        elif self.is_guild_officer(sender):
            alert_type = "officer_message"
        
        priority = self.get_alert_priority(sender, message)
        
        # Generate auto-reply
        auto_reply = self.generate_auto_reply(sender, message, member)
        
        # Create alert
        alert = GuildAlert(
            timestamp=datetime.now().isoformat(),
            sender=sender,
            message=message,
            alert_type=alert_type,
            priority=priority,
            auto_reply_sent=bool(auto_reply),
            reply_message=auto_reply
        )
        
        # Add to alerts list
        self.alerts.append(alert)
        
        # Send Discord notification
        self._send_discord_alert(alert)
        
        # Log the alert
        log_event(f"[GUILD_ALERT] {alert_type.upper()} from {sender}: {message}")
        
        return alert
    
    def _send_discord_alert(self, alert: GuildAlert):
        """Send a Discord alert for the guild message.
        
        Parameters
        ----------
        alert : GuildAlert
            The guild alert to send
        """
        if not self.discord_notifier:
            return
        
        try:
            # Create Discord embed
            embed = self._create_guild_alert_embed(alert)
            
            # Send via Discord notifier
            asyncio.create_task(self.discord_notifier.send_simple_alert(
                title=f"Guild Alert: {alert.alert_type.replace('_', ' ').title()}",
                message=f"**{alert.sender}**: {alert.message}",
                color=self._get_priority_color(alert.priority)
            ))
            
        except Exception as e:
            log_event(f"[GUILD_ALERT] Failed to send Discord alert: {e}")
    
    def _create_guild_alert_embed(self, alert: GuildAlert) -> Embed:
        """Create a Discord embed for the guild alert.
        
        Parameters
        ----------
        alert : GuildAlert
            The guild alert
            
        Returns
        -------
        Embed
            Discord embed object
        """
        color = self._get_priority_color(alert.priority)
        
        embed = Embed(
            title=f"Guild Alert: {alert.alert_type.replace('_', ' ').title()}",
            description=f"**{alert.sender}**: {alert.message}",
            color=color,
            timestamp=datetime.fromisoformat(alert.timestamp)
        )
        
        embed.add_field(name="Priority", value=alert.priority.upper(), inline=True)
        embed.add_field(name="Type", value=alert.alert_type.replace('_', ' ').title(), inline=True)
        
        if alert.auto_reply_sent and alert.reply_message:
            embed.add_field(name="Auto-Reply", value=alert.reply_message, inline=False)
        
        return embed
    
    def _get_priority_color(self, priority: str) -> Color:
        """Get Discord color based on priority level."""
        colors = {
            "high": Color.red(),
            "medium": Color.orange(),
            "low": Color.blue()
        }
        return colors.get(priority, Color.blue())
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the current guild configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def add_guild_member(self, name: str, role: str = "member", rank: int = 3):
        """Add a new guild member to the roster.
        
        Parameters
        ----------
        name : str
            Name of the guild member
        role : str
            Role in the guild (leader, officer, member)
        rank : int
            Rank number (1=leader, 2=officer, 3=member)
        """
        self.guild_members[name] = GuildMember(
            name=name,
            role=role,
            rank=rank,
            online=False
        )
        
        # Update config file
        self._save_guild_config()
        
        log_event(f"[GUILD_ALERT] Added guild member: {name} ({role})")
    
    def remove_guild_member(self, name: str):
        """Remove a guild member from the roster.
        
        Parameters
        ----------
        name : str
            Name of the guild member to remove
        """
        if name in self.guild_members:
            del self.guild_members[name]
            self._save_guild_config()
            log_event(f"[GUILD_ALERT] Removed guild member: {name}")
    
    def _save_guild_config(self):
        """Save the current guild configuration to file."""
        try:
            config = self._load_config()
            
            # Update members
            members_data = {}
            for name, member in self.guild_members.items():
                members_data[name] = asdict(member)
            
            config["members"] = members_data
            config["guild_name"] = self.guild_name
            config["guild_leader"] = self.guild_leader
            config["guild_officers"] = self.guild_officers
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            log_event(f"[GUILD_ALERT] Error saving guild config: {e}")
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get guild alert analytics for session logging.
        
        Returns
        -------
        dict
            Analytics data for session logs
        """
        analytics = {
            "guild_alerts_total": len(self.alerts),
            "guild_alerts_by_type": {},
            "guild_alerts_by_priority": {},
            "auto_replies_sent": 0,
            "guild_members_contacted": set()
        }
        
        for alert in self.alerts:
            # Count by type
            alert_type = alert.alert_type
            analytics["guild_alerts_by_type"][alert_type] = analytics["guild_alerts_by_type"].get(alert_type, 0) + 1
            
            # Count by priority
            priority = alert.priority
            analytics["guild_alerts_by_priority"][priority] = analytics["guild_alerts_by_priority"].get(priority, 0) + 1
            
            # Count auto-replies
            if alert.auto_reply_sent:
                analytics["auto_replies_sent"] += 1
            
            # Track unique members
            analytics["guild_members_contacted"].add(alert.sender)
        
        # Convert set to list for JSON serialization
        analytics["guild_members_contacted"] = list(analytics["guild_members_contacted"])
        
        return analytics
    
    def export_alerts(self, filepath: str = None) -> str:
        """Export guild alerts to a JSON file.
        
        Parameters
        ----------
        filepath : str, optional
            Path to save the export file
            
        Returns
        -------
        str
            Path to the exported file
        """
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"logs/guild_alerts_{timestamp}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "guild_name": self.guild_name,
            "alerts": [asdict(alert) for alert in self.alerts],
            "analytics": self.get_session_analytics()
        }
        
        Path(filepath).parent.mkdir(exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        log_event(f"[GUILD_ALERT] Exported {len(self.alerts)} alerts to {filepath}")
        return filepath 