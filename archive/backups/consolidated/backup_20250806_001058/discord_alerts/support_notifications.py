"""Discord Support Notifications for MS11.

This module handles sending Discord notifications for support tickets,
including new ticket alerts, status updates, and priority notifications.
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import discord
from discord import Embed, Color

from android_ms11.utils.logging_utils import log_event


@dataclass
class SupportNotification:
    """Support notification data structure."""
    ticket_id: str
    notification_type: str  # 'new_ticket', 'status_update', 'priority_alert'
    title: str
    description: str
    priority: str
    category: str
    timestamp: str
    metadata: Dict[str, Any]


class SupportDiscordNotifier:
    """Handles Discord notifications for support tickets."""
    
    def __init__(self, webhook_url: str = None, bot_token: str = None, channel_id: int = None):
        """Initialize the support Discord notifier.
        
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
        
        # Notification settings
        self.enable_priority_alerts = True
        self.enable_status_updates = True
        self.enable_new_ticket_alerts = True
        
        # Rate limiting
        self.last_notification_time = {}
        self.min_notification_interval = 60  # seconds
        
        log_event("[SUPPORT_DISCORD] Support Discord notifier initialized")

    def _load_discord_config(self):
        """Load Discord configuration from config file."""
        try:
            config_path = Path("config/discord_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                self.webhook_url = config.get("support_webhook_url") or self.webhook_url
                self.bot_token = config.get("discord_token") or self.bot_token
                self.channel_id = config.get("support_channel_id") or self.channel_id
                
                log_event("[SUPPORT_DISCORD] Loaded Discord configuration")
            else:
                log_event("[SUPPORT_DISCORD] No Discord config file found")
                
        except Exception as e:
            log_event(f"[SUPPORT_DISCORD] Error loading Discord config: {e}")

    def _get_priority_color(self, priority: str) -> Color:
        """Get Discord color for priority level."""
        colors = {
            'low': Color.green(),
            'medium': Color.gold(),
            'high': Color.red(),
            'urgent': Color.dark_red()
        }
        return colors.get(priority.lower(), Color.blue())

    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for ticket category."""
        emojis = {
            'account': '👤',
            'software': '💻',
            'general': '❓',
            'bug': '🐛',
            'feature': '✨'
        }
        return emojis.get(category.lower(), '📋')

    def _can_send_notification(self, notification_type: str) -> bool:
        """Check if we can send a notification (rate limiting)."""
        now = datetime.now()
        last_time = self.last_notification_time.get(notification_type)
        
        if last_time:
            time_diff = (now - last_time).total_seconds()
            if time_diff < self.min_notification_interval:
                return False
        
        self.last_notification_time[notification_type] = now
        return True

    async def send_new_ticket_notification(self, ticket_data: Dict[str, Any]) -> bool:
        """Send notification for a new support ticket.
        
        Parameters
        ----------
        ticket_data : dict
            Ticket data including all ticket fields
            
        Returns
        -------
        bool
            True if notification sent successfully
        """
        try:
            if not self.enable_new_ticket_alerts:
                return False
            
            if not self._can_send_notification('new_ticket'):
                log_event("[SUPPORT_DISCORD] Rate limited: skipping new ticket notification")
                return False
            
            # Create embed
            embed = Embed(
                title=f"🎫 New Support Ticket: {ticket_data['ticket_id']}",
                description=ticket_data.get('subject', 'No subject'),
                color=self._get_priority_color(ticket_data.get('priority', 'medium')),
                timestamp=datetime.fromisoformat(ticket_data['created_at'])
            )
            
            # Add fields
            embed.add_field(
                name="👤 Customer",
                value=ticket_data.get('name', 'Unknown'),
                inline=True
            )
            embed.add_field(
                name="📧 Email",
                value=ticket_data.get('email', 'No email'),
                inline=True
            )
            embed.add_field(
                name="📂 Category",
                value=f"{self._get_category_emoji(ticket_data.get('category', 'general'))} {ticket_data.get('category', 'general').title()}",
                inline=True
            )
            embed.add_field(
                name="⚡ Priority",
                value=f"{'🔴' if ticket_data.get('priority') == 'high' else '🟡' if ticket_data.get('priority') == 'medium' else '🟢'} {ticket_data.get('priority', 'medium').title()}",
                inline=True
            )
            embed.add_field(
                name="📅 Created",
                value=datetime.fromisoformat(ticket_data['created_at']).strftime("%Y-%m-%d %H:%M"),
                inline=True
            )
            embed.add_field(
                name="📊 Status",
                value=f"🟢 {ticket_data.get('status', 'open').title()}",
                inline=True
            )
            
            # Add message preview
            message = ticket_data.get('message', '')
            if len(message) > 500:
                message = message[:500] + "..."
            
            embed.add_field(
                name="💬 Message",
                value=message,
                inline=False
            )
            
            # Add footer
            embed.set_footer(text="MS11 Support System", icon_url="https://example.com/ms11-icon.png")
            
            # Send notification
            if self.webhook_url:
                return await self._send_via_webhook([embed])
            elif self.bot_token and self.channel_id:
                return await self._send_via_bot([embed])
            else:
                log_event("[SUPPORT_DISCORD] No Discord configuration available")
                return False
                
        except Exception as e:
            log_event(f"[SUPPORT_DISCORD] Error sending new ticket notification: {e}")
            return False

    async def send_priority_alert(self, ticket_data: Dict[str, Any]) -> bool:
        """Send priority alert for high/urgent tickets.
        
        Parameters
        ----------
        ticket_data : dict
            Ticket data
            
        Returns
        -------
        bool
            True if alert sent successfully
        """
        try:
            priority = ticket_data.get('priority', 'medium')
            if priority not in ['high', 'urgent']:
                return False
            
            if not self.enable_priority_alerts:
                return False
            
            if not self._can_send_notification('priority_alert'):
                return False
            
            # Create urgent embed
            embed = Embed(
                title=f"🚨 URGENT: {ticket_data['ticket_id']}",
                description=f"**{ticket_data.get('subject', 'No subject')}**",
                color=Color.red(),
                timestamp=datetime.fromisoformat(ticket_data['created_at'])
            )
            
            embed.add_field(
                name="⚠️ Priority Level",
                value=f"🔴 {priority.upper()}",
                inline=False
            )
            embed.add_field(
                name="👤 Customer",
                value=ticket_data.get('name', 'Unknown'),
                inline=True
            )
            embed.add_field(
                name="📧 Contact",
                value=ticket_data.get('email', 'No email'),
                inline=True
            )
            embed.add_field(
                name="📂 Category",
                value=f"{self._get_category_emoji(ticket_data.get('category', 'general'))} {ticket_data.get('category', 'general').title()}",
                inline=True
            )
            
            # Add urgent message
            message = ticket_data.get('message', '')
            if len(message) > 300:
                message = message[:300] + "..."
            
            embed.add_field(
                name="💬 Issue Description",
                value=message,
                inline=False
            )
            
            embed.set_footer(text="URGENT - Requires Immediate Attention", icon_url="https://example.com/urgent-icon.png")
            
            # Send with ping
            if self.webhook_url:
                return await self._send_via_webhook([embed], content="@here URGENT Support Ticket!")
            elif self.bot_token and self.channel_id:
                return await self._send_via_bot([embed], content="@here URGENT Support Ticket!")
            else:
                return False
                
        except Exception as e:
            log_event(f"[SUPPORT_DISCORD] Error sending priority alert: {e}")
            return False

    async def send_status_update_notification(self, ticket_data: Dict[str, Any], 
                                           old_status: str, new_status: str) -> bool:
        """Send notification for ticket status updates.
        
        Parameters
        ----------
        ticket_data : dict
            Ticket data
        old_status : str
            Previous status
        new_status : str
            New status
            
        Returns
        -------
        bool
            True if notification sent successfully
        """
        try:
            if not self.enable_status_updates:
                return False
            
            if not self._can_send_notification('status_update'):
                return False
            
            # Determine status emoji and color
            status_emojis = {
                'open': '🟢',
                'in_progress': '🟡',
                'waiting': '🟠',
                'resolved': '✅',
                'closed': '🔒',
                'cancelled': '❌'
            }
            
            status_colors = {
                'open': Color.green(),
                'in_progress': Color.gold(),
                'waiting': Color.orange(),
                'resolved': Color.green(),
                'closed': Color.dark_grey(),
                'cancelled': Color.red()
            }
            
            old_emoji = status_emojis.get(old_status, '❓')
            new_emoji = status_emojis.get(new_status, '❓')
            color = status_colors.get(new_status, Color.blue())
            
            # Create embed
            embed = Embed(
                title=f"📊 Status Update: {ticket_data['ticket_id']}",
                description=f"Status changed from {old_emoji} **{old_status.title()}** to {new_emoji} **{new_status.title()}**",
                color=color,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📋 Subject",
                value=ticket_data.get('subject', 'No subject'),
                inline=False
            )
            embed.add_field(
                name="👤 Customer",
                value=ticket_data.get('name', 'Unknown'),
                inline=True
            )
            embed.add_field(
                name="📂 Category",
                value=f"{self._get_category_emoji(ticket_data.get('category', 'general'))} {ticket_data.get('category', 'general').title()}",
                inline=True
            )
            embed.add_field(
                name="⚡ Priority",
                value=f"{'🔴' if ticket_data.get('priority') == 'high' else '🟡' if ticket_data.get('priority') == 'medium' else '🟢'} {ticket_data.get('priority', 'medium').title()}",
                inline=True
            )
            
            # Add response if available
            if ticket_data.get('response'):
                response = ticket_data['response']
                if len(response) > 500:
                    response = response[:500] + "..."
                embed.add_field(
                    name="💬 Response",
                    value=response,
                    inline=False
                )
            
            embed.set_footer(text="MS11 Support System", icon_url="https://example.com/ms11-icon.png")
            
            # Send notification
            if self.webhook_url:
                return await self._send_via_webhook([embed])
            elif self.bot_token and self.channel_id:
                return await self._send_via_bot([embed])
            else:
                return False
                
        except Exception as e:
            log_event(f"[SUPPORT_DISCORD] Error sending status update notification: {e}")
            return False

    async def send_daily_summary(self, tickets_data: List[Dict[str, Any]]) -> bool:
        """Send daily summary of support tickets.
        
        Parameters
        ----------
        tickets_data : list
            List of ticket data for the day
            
        Returns
        -------
        bool
            True if summary sent successfully
        """
        try:
            if not tickets_data:
                return False
            
            # Calculate statistics
            total_tickets = len(tickets_data)
            open_tickets = len([t for t in tickets_data if t.get('status') == 'open'])
            resolved_tickets = len([t for t in tickets_data if t.get('status') in ['resolved', 'closed']])
            
            # Priority breakdown
            priorities = {}
            for ticket in tickets_data:
                priority = ticket.get('priority', 'unknown')
                priorities[priority] = priorities.get(priority, 0) + 1
            
            # Category breakdown
            categories = {}
            for ticket in tickets_data:
                category = ticket.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            # Create summary embed
            embed = Embed(
                title="📊 Daily Support Summary",
                description=f"Support activity for {datetime.now().strftime('%Y-%m-%d')}",
                color=Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📈 Total Tickets",
                value=f"🎫 {total_tickets}",
                inline=True
            )
            embed.add_field(
                name="🟢 Open Tickets",
                value=f"📋 {open_tickets}",
                inline=True
            )
            embed.add_field(
                name="✅ Resolved Tickets",
                value=f"🎯 {resolved_tickets}",
                inline=True
            )
            
            # Priority breakdown
            priority_text = ""
            for priority, count in priorities.items():
                emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                priority_text += f"{emoji} {priority.title()}: {count}\n"
            
            if priority_text:
                embed.add_field(
                    name="⚡ Priority Breakdown",
                    value=priority_text,
                    inline=True
                )
            
            # Category breakdown
            category_text = ""
            for category, count in categories.items():
                emoji = self._get_category_emoji(category)
                category_text += f"{emoji} {category.title()}: {count}\n"
            
            if category_text:
                embed.add_field(
                    name="📂 Category Breakdown",
                    value=category_text,
                    inline=True
                )
            
            embed.set_footer(text="MS11 Support System - Daily Report", icon_url="https://example.com/ms11-icon.png")
            
            # Send summary
            if self.webhook_url:
                return await self._send_via_webhook([embed])
            elif self.bot_token and self.channel_id:
                return await self._send_via_bot([embed])
            else:
                return False
                
        except Exception as e:
            log_event(f"[SUPPORT_DISCORD] Error sending daily summary: {e}")
            return False

    async def _send_via_webhook(self, embeds: List[Embed], content: str = None) -> bool:
        """Send message via Discord webhook."""
        try:
            import aiohttp
            
            payload = {
                "embeds": [embed.to_dict() for embed in embeds]
            }
            
            if content:
                payload["content"] = content
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        log_event("[SUPPORT_DISCORD] Webhook message sent successfully")
                        return True
                    else:
                        log_event(f"[SUPPORT_DISCORD] Webhook failed: {response.status}")
                        return False
                        
        except Exception as e:
            log_event(f"[SUPPORT_DISCORD] Error sending via webhook: {e}")
            return False

    async def _send_via_bot(self, embeds: List[Embed], content: str = None) -> bool:
        """Send message via Discord bot."""
        try:
            if not self.bot:
                self.bot = discord.Client(intents=discord.Intents.default())
            
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                for embed in embeds:
                    await channel.send(content=content, embed=embed)
                log_event("[SUPPORT_DISCORD] Bot message sent successfully")
                return True
            else:
                log_event("[SUPPORT_DISCORD] Could not find channel")
                return False
                
        except Exception as e:
            log_event(f"[SUPPORT_DISCORD] Error sending via bot: {e}")
            return False

    def test_connection(self) -> bool:
        """Test Discord connection."""
        try:
            if self.webhook_url or (self.bot_token and self.channel_id):
                log_event("[SUPPORT_DISCORD] Discord configuration available")
                return True
            else:
                log_event("[SUPPORT_DISCORD] No Discord configuration found")
                return False
        except Exception as e:
            log_event(f"[SUPPORT_DISCORD] Error testing connection: {e}")
            return False


def create_support_notifier(webhook_url: str = None, bot_token: str = None, 
                          channel_id: int = None) -> SupportDiscordNotifier:
    """Create and return a SupportDiscordNotifier instance."""
    return SupportDiscordNotifier(webhook_url, bot_token, channel_id)


__all__ = [
    "SupportDiscordNotifier",
    "create_support_notifier",
    "SupportNotification"
] 