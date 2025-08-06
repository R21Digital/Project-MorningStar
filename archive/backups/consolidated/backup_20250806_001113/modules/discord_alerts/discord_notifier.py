"""Discord Notifier for sending advanced combat performance alerts.

This module handles sending formatted Discord messages with combat statistics,
build analysis, and performance recommendations.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import discord
from discord import Embed, Color

from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

class DiscordNotifier:
    """Handles sending Discord alerts with combat performance data."""
    
    def __init__(self, webhook_url: str = None, bot_token: str = None, channel_id: int = None):
        """Initialize the Discord notifier.
        
        Parameters
        ----------
        webhook_url : str, optional
            Discord webhook URL for sending messages
        bot_token : str, optional
            Discord bot token for bot-based messaging
        channel_id : int, optional
            Discord channel ID for sending messages
        """
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.bot = None
        
        # Load Discord configuration
        self._load_discord_config()
        
        # Message formatting settings
        self.max_embed_fields = 25
        self.max_field_length = 1024
        self.max_embed_length = 6000
        
        log_event("[DISCORD_NOTIFIER] Initialized Discord notifier")
    
    def _load_discord_config(self):
        """Load Discord configuration from config file."""
        try:
            config_path = Path("config/discord_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                self.bot_token = config.get("discord_token") or self.bot_token
                self.target_user_id = config.get("target_user_id")
                
                log_event("[DISCORD_NOTIFIER] Loaded Discord configuration")
            else:
                log_event("[DISCORD_NOTIFIER] No Discord config file found")
                
        except Exception as e:
            log_event(f"[DISCORD_NOTIFIER] Error loading Discord config: {e}")
    
    async def send_combat_performance_alert(self, performance_data: Dict[str, Any], 
                                          build_analysis: Dict[str, Any] = None) -> bool:
        """Send a comprehensive combat performance alert to Discord.
        
        Parameters
        ----------
        performance_data : dict
            Combat performance data from CombatStatsTracker
        build_analysis : dict, optional
            Build analysis data from BuildAnalyzer
            
        Returns
        -------
        bool
            True if message sent successfully, False otherwise
        """
        try:
            # Create main performance embed
            main_embed = self._create_performance_embed(performance_data)
            
            # Create build analysis embed if available
            build_embed = None
            if build_analysis:
                build_embed = self._create_build_analysis_embed(build_analysis)
            
            # Send the message(s)
            if self.webhook_url:
                return await self._send_via_webhook([main_embed, build_embed])
            elif self.bot_token and self.channel_id:
                return await self._send_via_bot([main_embed, build_embed])
            else:
                log_event("[DISCORD_NOTIFIER] No Discord configuration available")
                return False
                
        except Exception as e:
            log_event(f"[DISCORD_NOTIFIER] Error sending combat alert: {e}")
            return False
    
    def _create_performance_embed(self, performance_data: Dict[str, Any]) -> Embed:
        """Create the main performance embed.
        
        Parameters
        ----------
        performance_data : dict
            Combat performance data
            
        Returns
        -------
        Embed
            Formatted Discord embed
        """
        performance_summary = performance_data.get("performance_summary", {})
        skill_analysis = performance_data.get("skill_analysis", {})
        
        # Create embed
        embed = Embed(
            title="⚔️ Combat Performance Report",
            description=f"Session: {performance_data.get('session_id', 'Unknown')}",
            color=Color.blue(),
            timestamp=datetime.now()
        )
        
        # Add performance overview
        total_damage = performance_summary.get("total_damage", 0)
        total_kills = performance_summary.get("total_kills", 0)
        session_duration = performance_summary.get("session_duration", 0)
        average_dps = performance_summary.get("average_dps", 0)
        
        embed.add_field(
            name="📊 Performance Overview",
            value=f"**Total Damage:** {total_damage:,}\n"
                  f"**Total Kills:** {total_kills}\n"
                  f"**Session Duration:** {self._format_duration(session_duration)}\n"
                  f"**Average DPS:** {average_dps:.1f}",
            inline=False
        )
        
        # Add most used skills
        most_used_skills = performance_summary.get("most_used_skills", [])
        if most_used_skills:
            most_used_text = "\n".join([f"• {skill} ({count} uses)" for skill, count in most_used_skills[:5]])
            embed.add_field(
                name="🔥 Most Used Skills",
                value=most_used_text,
                inline=True
            )
        
        # Add least used skills
        least_used_skills = performance_summary.get("least_used_skills", [])
        if least_used_skills:
            least_used_text = "\n".join([f"• {skill} ({count} uses)" for skill, count in least_used_skills[:5]])
            embed.add_field(
                name="❄️ Least Used Skills",
                value=least_used_text,
                inline=True
            )
        
        # Add skill line uptime
        skill_line_uptime = performance_summary.get("skill_line_uptime", {})
        if skill_line_uptime:
            uptime_text = "\n".join([f"• {line}: {uptime:.1f}%" for line, uptime in skill_line_uptime.items()])
            embed.add_field(
                name="⏱️ Skill Line Uptime",
                value=uptime_text,
                inline=False
            )
        
        # Add efficiency score
        efficiency_score = performance_summary.get("efficiency_score", 0)
        embed.add_field(
            name="🎯 Efficiency Score",
            value=f"{efficiency_score:.2f}",
            inline=True
        )
        
        # Add footer
        embed.set_footer(text="MS11 Combat Analytics")
        
        return embed
    
    def _create_build_analysis_embed(self, build_analysis: Dict[str, Any]) -> Embed:
        """Create build analysis embed.
        
        Parameters
        ----------
        build_analysis : dict
            Build analysis data
            
        Returns
        -------
        Embed
            Formatted Discord embed
        """
        embed = Embed(
            title="🔧 Build Analysis Report",
            description=build_analysis.get("build_name", "Unknown Build"),
            color=Color.green(),
            timestamp=datetime.now()
        )
        
        # Add build statistics
        total_skill_points = build_analysis.get("total_skill_points", 0)
        skills_analyzed = build_analysis.get("skills_analyzed", 0)
        average_roi = build_analysis.get("average_roi", 0)
        build_efficiency_score = build_analysis.get("build_efficiency_score", 0)
        
        embed.add_field(
            name="📈 Build Statistics",
            value=f"**Total Skill Points:** {total_skill_points}\n"
                  f"**Skills Analyzed:** {skills_analyzed}\n"
                  f"**Average ROI:** {average_roi:.1f}\n"
                  f"**Build Efficiency:** {build_efficiency_score:.1f}/100",
            inline=False
        )
        
        # Add most efficient skills
        most_efficient_skills = build_analysis.get("most_efficient_skills", [])
        if most_efficient_skills:
            efficient_text = "\n".join([
                f"• {skill.skill_name}: {skill.roi_score:.1f} ROI ({skill.efficiency_rating})"
                for skill in most_efficient_skills[:3]
            ])
            embed.add_field(
                name="🏆 Most Efficient Skills",
                value=efficient_text,
                inline=True
            )
        
        # Add least efficient skills
        least_efficient_skills = build_analysis.get("least_efficient_skills", [])
        if least_efficient_skills:
            inefficient_text = "\n".join([
                f"• {skill.skill_name}: {skill.roi_score:.1f} ROI ({skill.efficiency_rating})"
                for skill in least_efficient_skills[:3]
            ])
            embed.add_field(
                name="⚠️ Least Efficient Skills",
                value=inefficient_text,
                inline=True
            )
        
        # Add unused skills
        unused_skills = build_analysis.get("unused_skills", [])
        if unused_skills:
            unused_text = ", ".join(unused_skills[:5])
            if len(unused_skills) > 5:
                unused_text += f" (+{len(unused_skills) - 5} more)"
            embed.add_field(
                name="🚫 Unused Skills",
                value=unused_text,
                inline=False
            )
        
        # Add optimization recommendations
        recommendations = build_analysis.get("optimization_recommendations", [])
        if recommendations:
            rec_text = "\n".join([f"• {rec}" for rec in recommendations[:3]])
            embed.add_field(
                name="💡 Optimization Tips",
                value=rec_text,
                inline=False
            )
        
        embed.set_footer(text="MS11 Build Analytics")
        
        return embed
    
    def _create_detailed_skill_analysis_embed(self, skill_analysis: Dict[str, Any]) -> Embed:
        """Create detailed skill analysis embed.
        
        Parameters
        ----------
        skill_analysis : dict
            Detailed skill analysis data
            
        Returns
        -------
        Embed
            Formatted Discord embed
        """
        embed = Embed(
            title="📋 Detailed Skill Analysis",
            color=Color.purple(),
            timestamp=datetime.now()
        )
        
        # Add skill usage breakdown
        skill_usage = skill_analysis.get("skill_usage", {})
        if skill_usage:
            # Get top 5 skills by damage
            top_skills = sorted(
                skill_usage.items(),
                key=lambda x: x[1].get("total_damage", 0),
                reverse=True
            )[:5]
            
            skill_text = "\n".join([
                f"• {skill}: {data.get('total_damage', 0):,} damage ({data.get('usage_count', 0)} uses)"
                for skill, data in top_skills
            ])
            
            embed.add_field(
                name="💥 Top Damage Skills",
                value=skill_text,
                inline=False
            )
        
        # Add effectiveness ranking
        effectiveness_ranking = skill_analysis.get("effectiveness_ranking", [])
        if effectiveness_ranking:
            effective_text = "\n".join([
                f"• {skill}: {effectiveness:.1f} avg damage"
                for skill, effectiveness, count in effectiveness_ranking[:5]
            ])
            
            embed.add_field(
                name="🎯 Most Effective Skills",
                value=effective_text,
                inline=False
            )
        
        embed.set_footer(text="MS11 Skill Analytics")
        
        return embed
    
    async def _send_via_webhook(self, embeds: List[Embed]) -> bool:
        """Send message via Discord webhook.
        
        Parameters
        ----------
        embeds : List[Embed]
            List of embeds to send
            
        Returns
        -------
        bool
            True if sent successfully
        """
        try:
            webhook = discord.SyncWebhook.from_url(self.webhook_url)
            
            for embed in embeds:
                if embed:
                    webhook.send(embed=embed)
                    await asyncio.sleep(1)  # Rate limiting
            
            log_event("[DISCORD_NOTIFIER] Sent message via webhook")
            return True
            
        except Exception as e:
            log_event(f"[DISCORD_NOTIFIER] Error sending via webhook: {e}")
            return False
    
    async def _send_via_bot(self, embeds: List[Embed]) -> bool:
        """Send message via Discord bot.
        
        Parameters
        ----------
        embeds : List[Embed]
            List of embeds to send
            
        Returns
        -------
        bool
            True if sent successfully
        """
        try:
            if not self.bot:
                self.bot = discord.Client(intents=discord.Intents.default())
                await self.bot.start(self.bot_token)
            
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                log_event("[DISCORD_NOTIFIER] Could not find channel")
                return False
            
            for embed in embeds:
                if embed:
                    await channel.send(embed=embed)
                    await asyncio.sleep(1)  # Rate limiting
            
            log_event("[DISCORD_NOTIFIER] Sent message via bot")
            return True
            
        except Exception as e:
            log_event(f"[DISCORD_NOTIFIER] Error sending via bot: {e}")
            return False
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human readable string.
        
        Parameters
        ----------
        seconds : float
            Duration in seconds
            
        Returns
        -------
        str
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def send_simple_alert(self, title: str, message: str, color: Color = Color.blue()) -> bool:
        """Send a simple alert message.
        
        Parameters
        ----------
        title : str
            Alert title
        message : str
            Alert message
        color : Color
            Embed color
            
        Returns
        -------
        bool
            True if sent successfully
        """
        try:
            embed = Embed(
                title=title,
                description=message,
                color=color,
                timestamp=datetime.now()
            )
            
            embed.set_footer(text="MS11 Alert System")
            
            # Send via available method
            if self.webhook_url:
                webhook = discord.SyncWebhook.from_url(self.webhook_url)
                webhook.send(embed=embed)
            elif self.bot_token and self.channel_id:
                # This would need async handling in practice
                log_event("[DISCORD_NOTIFIER] Bot sending not implemented for sync calls")
                return False
            else:
                log_event("[DISCORD_NOTIFIER] No Discord configuration available")
                return False
            
            log_event(f"[DISCORD_NOTIFIER] Sent simple alert: {title}")
            return True
            
        except Exception as e:
            log_event(f"[DISCORD_NOTIFIER] Error sending simple alert: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Discord connection.
        
        Returns
        -------
        bool
            True if connection successful
        """
        try:
            if self.webhook_url:
                webhook = discord.SyncWebhook.from_url(self.webhook_url)
                webhook.send(content="🔧 MS11 Discord integration test successful!")
                log_event("[DISCORD_NOTIFIER] Webhook connection test successful")
                return True
            else:
                log_event("[DISCORD_NOTIFIER] No webhook URL configured")
                return False
                
        except Exception as e:
            log_event(f"[DISCORD_NOTIFIER] Connection test failed: {e}")
            return False 