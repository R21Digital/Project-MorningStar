#!/usr/bin/env python3
"""
Batch 112 - Guild Discord Bridge

This module provides Discord integration for guild alerts, extending the
existing Discord relay system with guild-specific functionality.

Author: SWG Bot Development Team
"""

import asyncio
import discord
from discord.ext import commands
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from pathlib import Path

from core.guild_alert_system import GuildAlertSystem, GuildMessage, AlertPriority, GuildRole


@dataclass
class GuildDiscordConfig:
    """Configuration for guild Discord integration."""
    guild_name: str = ""
    enable_guild_alerts: bool = True
    enable_priority_pings: bool = True
    enable_auto_replies: bool = False
    alert_channel_id: Optional[int] = None
    priority_channel_id: Optional[int] = None
    guild_leader_id: Optional[int] = None
    guild_officer_ids: List[int] = None
    ping_roles: List[str] = None
    alert_cooldown: int = 30  # seconds between alerts for same sender


class GuildDiscordBridge:
    """Discord bridge for guild alerts and priority communication."""
    
    def __init__(self, bot: commands.Bot, config: GuildDiscordConfig):
        """Initialize guild Discord bridge.
        
        Parameters
        ----------
        bot : commands.Bot
            Discord bot instance
        config : GuildDiscordConfig
            Configuration for guild Discord integration
        """
        self.bot = bot
        self.config = config
        self.guild_alert_system = None
        self.alert_cooldowns: Dict[str, float] = {}
        
        # Load configuration
        self._load_config()
        
        print(f"[GUILD_DISCORD] Guild Discord bridge initialized for guild: {config.guild_name}")
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            config_file = Path(f"config/guilds/{self.config.guild_name}_discord.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    self.config.alert_channel_id = config_data.get("alert_channel_id")
                    self.config.priority_channel_id = config_data.get("priority_channel_id")
                    self.config.guild_leader_id = config_data.get("guild_leader_id")
                    self.config.guild_officer_ids = config_data.get("guild_officer_ids", [])
                    self.config.ping_roles = config_data.get("ping_roles", [])
        except Exception as e:
            print(f"[GUILD_DISCORD] Failed to load config: {e}")
    
    def set_guild_alert_system(self, guild_alert_system: GuildAlertSystem):
        """Set the guild alert system.
        
        Parameters
        ----------
        guild_alert_system : GuildAlertSystem
            Guild alert system instance
        """
        self.guild_alert_system = guild_alert_system
    
    async def send_alert(self, guild_message: GuildMessage) -> bool:
        """Send a Discord alert for a guild message.
        
        Parameters
        ----------
        guild_message : GuildMessage
            The guild message to alert about
            
        Returns
        -------
        bool
            True if alert was sent successfully
        """
        if not self.config.enable_guild_alerts:
            return False
        
        # Check cooldown
        if not self._check_cooldown(guild_message.sender):
            return False
        
        try:
            # Create Discord embed
            embed = self._create_alert_embed(guild_message)
            
            # Determine channel
            channel_id = self._get_alert_channel_id(guild_message)
            if not channel_id:
                return False
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                print(f"[GUILD_DISCORD] Could not find channel {channel_id}")
                return False
            
            # Add priority ping if needed
            content = self._get_priority_content(guild_message)
            
            # Send message
            await channel.send(content=content, embed=embed)
            
            # Update cooldown
            self._update_cooldown(guild_message.sender)
            
            print(f"[GUILD_DISCORD] Sent alert for {guild_message.sender}: {guild_message.message}")
            return True
            
        except Exception as e:
            print(f"[GUILD_DISCORD] Failed to send alert: {e}")
            return False
    
    def _create_alert_embed(self, guild_message: GuildMessage) -> discord.Embed:
        """Create a Discord embed for the guild alert.
        
        Parameters
        ----------
        guild_message : GuildMessage
            The guild message to create embed for
            
        Returns
        -------
        discord.Embed
            Discord embed for the alert
        """
        # Set color based on priority
        color_map = {
            AlertPriority.LOW: 0x3498db,      # Blue
            AlertPriority.NORMAL: 0xf39c12,   # Orange
            AlertPriority.HIGH: 0xe74c3c,     # Red
            AlertPriority.URGENT: 0x9b59b6    # Purple
        }
        
        color = color_map.get(guild_message.priority, 0x95a5a6)
        
        # Create embed
        embed = discord.Embed(
            title=f"Guild Alert - {guild_message.priority.value.upper()}",
            description=guild_message.message,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        
        # Add fields
        embed.add_field(name="Sender", value=guild_message.sender, inline=True)
        embed.add_field(name="Type", value=guild_message.message_type.value, inline=True)
        
        if guild_message.sender_role:
            embed.add_field(name="Role", value=guild_message.sender_role.value, inline=True)
        
        embed.add_field(name="Guild Member", value="✅" if guild_message.is_guild_member else "❌", inline=True)
        
        if guild_message.requires_reply:
            embed.add_field(name="Requires Reply", value="⚠️ Yes", inline=True)
        
        # Add footer
        embed.set_footer(text=f"Guild: {self.config.guild_name}")
        
        return embed
    
    def _get_alert_channel_id(self, guild_message: GuildMessage) -> Optional[int]:
        """Get the appropriate channel ID for the alert.
        
        Parameters
        ----------
        guild_message : GuildMessage
            The guild message
            
        Returns
        -------
        int or None
            Channel ID for the alert
        """
        # Use priority channel for high/urgent messages
        if guild_message.priority in [AlertPriority.HIGH, AlertPriority.URGENT]:
            return self.config.priority_channel_id or self.config.alert_channel_id
        
        # Use regular alert channel for other messages
        return self.config.alert_channel_id
    
    def _get_priority_content(self, guild_message: GuildMessage) -> str:
        """Get priority content for the message.
        
        Parameters
        ----------
        guild_message : GuildMessage
            The guild message
            
        Returns
        -------
        str
            Priority content (pings, etc.)
        """
        content_parts = []
        
        # Add role pings
        if self.config.ping_roles:
            for role_name in self.config.ping_roles:
                content_parts.append(f"<@&{role_name}>")
        
        # Add user pings for priority members
        if guild_message.priority in [AlertPriority.HIGH, AlertPriority.URGENT]:
            if self.config.guild_leader_id:
                content_parts.append(f"<@{self.config.guild_leader_id}>")
            
            if self.config.guild_officer_ids:
                for officer_id in self.config.guild_officer_ids:
                    content_parts.append(f"<@{officer_id}>")
        
        # Add urgent indicator
        if guild_message.priority == AlertPriority.URGENT:
            content_parts.append("🚨 **URGENT** 🚨")
        
        return " ".join(content_parts) if content_parts else ""
    
    def _check_cooldown(self, sender: str) -> bool:
        """Check if sender is on cooldown.
        
        Parameters
        ----------
        sender : str
            Name of the sender
            
        Returns
        -------
        bool
            True if not on cooldown
        """
        if sender not in self.alert_cooldowns:
            return True
        
        time_since_last = asyncio.get_event_loop().time() - self.alert_cooldowns[sender]
        return time_since_last >= self.config.alert_cooldown
    
    def _update_cooldown(self, sender: str):
        """Update cooldown for sender.
        
        Parameters
        ----------
        sender : str
            Name of the sender
        """
        self.alert_cooldowns[sender] = asyncio.get_event_loop().time()
    
    async def send_guild_status(self, guild_stats: Dict[str, Any]) -> bool:
        """Send guild status to Discord.
        
        Parameters
        ----------
        guild_stats : dict
            Guild statistics
            
        Returns
        -------
        bool
            True if status was sent successfully
        """
        if not self.config.alert_channel_id:
            return False
        
        try:
            channel = self.bot.get_channel(self.config.alert_channel_id)
            if not channel:
                return False
            
            embed = discord.Embed(
                title=f"Guild Status - {self.config.guild_name}",
                color=0x2ecc71,
                timestamp=discord.utils.utcnow()
            )
            
            # Add statistics
            embed.add_field(name="Total Members", value=guild_stats["total_members"], inline=True)
            embed.add_field(name="Online Members", value=guild_stats["online_members"], inline=True)
            embed.add_field(name="Recent Messages", value=guild_stats["recent_messages"], inline=True)
            embed.add_field(name="Priority Messages", value=guild_stats["priority_messages"], inline=True)
            
            # Add role distribution
            role_dist = guild_stats.get("role_distribution", {})
            role_text = "\n".join([f"{role}: {count}" for role, count in role_dist.items()])
            if role_text:
                embed.add_field(name="Role Distribution", value=role_text, inline=False)
            
            embed.set_footer(text=f"Guild: {self.config.guild_name}")
            
            await channel.send(embed=embed)
            return True
            
        except Exception as e:
            print(f"[GUILD_DISCORD] Failed to send guild status: {e}")
            return False
    
    async def send_guild_roster_update(self, member_name: str, action: str, role: Optional[GuildRole] = None) -> bool:
        """Send guild roster update to Discord.
        
        Parameters
        ----------
        member_name : str
            Name of the member
        action : str
            Action performed (add, remove, update)
        role : GuildRole or None
            Role of the member
            
        Returns
        -------
        bool
            True if update was sent successfully
        """
        if not self.config.alert_channel_id:
            return False
        
        try:
            channel = self.bot.get_channel(self.config.alert_channel_id)
            if not channel:
                return False
            
            # Set color based on action
            color_map = {
                "add": 0x2ecc71,      # Green
                "remove": 0xe74c3c,   # Red
                "update": 0xf39c12    # Orange
            }
            
            color = color_map.get(action, 0x95a5a6)
            
            embed = discord.Embed(
                title=f"Guild Roster Update - {action.upper()}",
                description=f"**Member:** {member_name}",
                color=color,
                timestamp=discord.utils.utcnow()
            )
            
            if role:
                embed.add_field(name="Role", value=role.value, inline=True)
            
            embed.set_footer(text=f"Guild: {self.config.guild_name}")
            
            await channel.send(embed=embed)
            return True
            
        except Exception as e:
            print(f"[GUILD_DISCORD] Failed to send roster update: {e}")
            return False


class GuildDiscordCog(commands.Cog):
    """Discord cog for guild alerts."""
    
    def __init__(self, bot: commands.Bot, config: GuildDiscordConfig):
        """Initialize guild Discord cog.
        
        Parameters
        ----------
        bot : commands.Bot
            Discord bot instance
        config : GuildDiscordConfig
            Configuration for guild Discord integration
        """
        self.bot = bot
        self.config = config
        self.bridge = GuildDiscordBridge(bot, config)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f"[GUILD_DISCORD] Guild Discord cog ready for guild: {self.config.guild_name}")
    
    @commands.command(name="guildstatus")
    async def guild_status(self, ctx):
        """Get guild status."""
        if not self.bridge.guild_alert_system:
            await ctx.send("Guild alert system not connected.")
            return
        
        stats = self.bridge.guild_alert_system.get_guild_statistics()
        await self.bridge.send_guild_status(stats)
    
    @commands.command(name="guildroster")
    async def guild_roster(self, ctx):
        """Get guild roster."""
        if not self.bridge.guild_alert_system:
            await ctx.send("Guild alert system not connected.")
            return
        
        roster = self.bridge.guild_alert_system.guild_roster
        
        if not roster:
            await ctx.send("No guild members found.")
            return
        
        embed = discord.Embed(
            title=f"Guild Roster - {self.config.guild_name}",
            color=0x3498db,
            timestamp=discord.utils.utcnow()
        )
        
        # Group by role
        role_members = {}
        for member in roster.values():
            role = member.role.value
            if role not in role_members:
                role_members[role] = []
            role_members[role].append(member)
        
        for role, members in role_members.items():
            member_list = []
            for member in members:
                status = "🟢" if member.is_online else "🔴"
                member_list.append(f"{status} {member.name} (Lvl {member.level})")
            
            embed.add_field(
                name=f"{role.title()} ({len(members)})",
                value="\n".join(member_list) if member_list else "No members",
                inline=True
            )
        
        embed.set_footer(text=f"Guild: {self.config.guild_name}")
        await ctx.send(embed=embed)


def setup_guild_discord_bridge(bot: commands.Bot, guild_name: str = "default") -> GuildDiscordBridge:
    """Set up guild Discord bridge.
    
    Parameters
    ----------
    bot : commands.Bot
        Discord bot instance
    guild_name : str
        Name of the guild
        
    Returns
    -------
    GuildDiscordBridge
        Guild Discord bridge instance
    """
    config = GuildDiscordConfig(guild_name=guild_name)
    bridge = GuildDiscordBridge(bot, config)
    
    # Add cog to bot
    cog = GuildDiscordCog(bot, config)
    cog.bridge = bridge
    bot.add_cog(cog)
    
    return bridge 