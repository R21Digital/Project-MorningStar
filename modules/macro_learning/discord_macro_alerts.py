"""Discord Macro Alerts for sending macro and alias alerts via Discord.

This module provides Discord integration for sending alerts about missing
critical macros and recommendations.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from discord import Embed, Color

from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

@dataclass
class MacroAlert:
    """Data class for macro alerts."""
    alert_type: str
    title: str
    message: str
    priority: str
    missing_items: List[str]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class AlertSummary:
    """Data class for alert summary."""
    total_alerts: int
    critical_alerts: int
    warning_alerts: int
    info_alerts: int
    alerts_by_category: Dict[str, int]
    recent_alerts: List[MacroAlert]

class DiscordMacroAlerts:
    """Discord alerts for macro and alias issues."""
    
    def __init__(self, webhook_url: str = None, bot_token: str = None, channel_id: int = None):
        """Initialize Discord macro alerts.
        
        Parameters
        ----------
        webhook_url : str, optional
            Discord webhook URL
        bot_token : str, optional
            Discord bot token
        channel_id : int, optional
            Discord channel ID
        """
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.alerts = []
        self.alert_history = []
        
        # Load Discord configuration
        self._load_discord_config()
        
        # Alert thresholds
        self.critical_threshold = 3  # Number of missing critical items to trigger alert
        self.warning_threshold = 5   # Number of missing items to trigger warning
        
        # Alert categories
        self.alert_categories = {
            "critical": {
                "color": Color.red(),
                "icon": "🚨",
                "description": "Critical macro/alias missing"
            },
            "warning": {
                "color": Color.orange(),
                "icon": "⚠️",
                "description": "Important macro/alias missing"
            },
            "info": {
                "color": Color.blue(),
                "icon": "ℹ️",
                "description": "Information about macros/aliases"
            },
            "recommendation": {
                "color": Color.green(),
                "icon": "💡",
                "description": "Macro/alias recommendations"
            }
        }
        
        log_event("[DISCORD_MACRO_ALERTS] Initialized Discord macro alerts")
    
    def _load_discord_config(self) -> None:
        """Load Discord configuration from file."""
        try:
            with open("config/discord_config.json", 'r') as f:
                config = json.load(f)
            
            self.webhook_url = config.get("webhook_url", "")
            self.bot_token = config.get("bot_token", "")
            self.channel_id = config.get("channel_id", 0)
            
        except Exception as e:
            log_event(f"[DISCORD_MACRO_ALERTS] Error loading Discord config: {e}")
    
    def create_missing_macros_alert(self, missing_macros: List[str], 
                                   missing_aliases: List[str],
                                   recommendations: List[str] = None) -> MacroAlert:
        """Create alert for missing macros and aliases.
        
        Parameters
        ----------
        missing_macros : list
            List of missing macro names
        missing_aliases : list
            List of missing alias names
        recommendations : list, optional
            List of recommendations
            
        Returns
        -------
        MacroAlert
            Created alert
        """
        total_missing = len(missing_macros) + len(missing_aliases)
        
        if total_missing >= self.critical_threshold:
            alert_type = "critical"
            title = "🚨 Critical Macros/Aliases Missing"
            priority = "high"
        elif total_missing >= self.warning_threshold:
            alert_type = "warning"
            title = "⚠️ Important Macros/Aliases Missing"
            priority = "medium"
        else:
            alert_type = "info"
            title = "ℹ️ Macro/Alias Status"
            priority = "low"
        
        message = f"Found {total_missing} missing items:\n"
        if missing_macros:
            message += f"• Missing Macros: {', '.join(missing_macros)}\n"
        if missing_aliases:
            message += f"• Missing Aliases: {', '.join(missing_aliases)}\n"
        
        if recommendations:
            message += f"\nRecommendations:\n"
            for rec in recommendations[:5]:  # Limit to 5 recommendations
                message += f"• {rec}\n"
        
        return MacroAlert(
            alert_type=alert_type,
            title=title,
            message=message,
            priority=priority,
            missing_items=missing_macros + missing_aliases,
            recommendations=recommendations or [],
            timestamp=datetime.now()
        )
    
    def create_recommendation_alert(self, recommendations: List[str],
                                   category: str = "general") -> MacroAlert:
        """Create alert for macro/alias recommendations.
        
        Parameters
        ----------
        recommendations : list
            List of recommendations
        category : str
            Category of recommendations
            
        Returns
        -------
        MacroAlert
            Created alert
        """
        title = f"💡 {category.title()} Macro/Alias Recommendations"
        message = f"Found {len(recommendations)} recommendations:\n\n"
        
        for i, rec in enumerate(recommendations[:10], 1):  # Limit to 10 recommendations
            message += f"{i}. {rec}\n"
        
        return MacroAlert(
            alert_type="recommendation",
            title=title,
            message=message,
            priority="medium",
            missing_items=[],
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def create_fallback_map_alert(self, fallback_maps: List[Dict[str, Any]]) -> MacroAlert:
        """Create alert for fallback maps.
        
        Parameters
        ----------
        fallback_maps : list
            List of fallback map data
            
        Returns
        -------
        MacroAlert
            Created alert
        """
        title = "🔄 Macro Fallback Maps Created"
        message = f"Created {len(fallback_maps)} fallback maps:\n\n"
        
        for fallback in fallback_maps[:5]:  # Limit to 5 fallbacks
            original = fallback.get("original_macro", "unknown")
            fallback_macro = fallback.get("fallback_macro", "unknown")
            confidence = fallback.get("confidence", 0.0)
            
            message += f"• {original} → {fallback_macro} ({confidence:.1%})\n"
        
        return MacroAlert(
            alert_type="info",
            title=title,
            message=message,
            priority="low",
            missing_items=[],
            recommendations=[f"Use fallback maps for missing macros"],
            timestamp=datetime.now()
        )
    
    async def send_macro_alert(self, alert: MacroAlert) -> bool:
        """Send macro alert to Discord.
        
        Parameters
        ----------
        alert : MacroAlert
            Alert to send
            
        Returns
        -------
        bool
            True if sent successfully
        """
        try:
            # Create Discord embed
            embed = self._create_alert_embed(alert)
            
            # Send via webhook or bot
            if self.webhook_url:
                success = await self._send_via_webhook([embed])
            elif self.bot_token and self.channel_id:
                success = await self._send_via_bot([embed])
            else:
                log_event("[DISCORD_MACRO_ALERTS] No Discord configuration found")
                return False
            
            if success:
                self.alerts.append(alert)
                self.alert_history.append(alert)
                log_event(f"[DISCORD_MACRO_ALERTS] Sent {alert.alert_type} alert: {alert.title}")
            
            return success
            
        except Exception as e:
            log_event(f"[DISCORD_MACRO_ALERTS] Error sending alert: {e}")
            return False
    
    def _create_alert_embed(self, alert: MacroAlert) -> Embed:
        """Create Discord embed for alert.
        
        Parameters
        ----------
        alert : MacroAlert
            Alert to create embed for
            
        Returns
        -------
        Embed
            Discord embed
        """
        category_info = self.alert_categories.get(alert.alert_type, {})
        color = category_info.get("color", Color.blue())
        icon = category_info.get("icon", "ℹ️")
        
        embed = Embed(
            title=f"{icon} {alert.title}",
            description=alert.message,
            color=color,
            timestamp=alert.timestamp
        )
        
        # Add fields
        if alert.missing_items:
            embed.add_field(
                name="Missing Items",
                value="\n".join(f"• {item}" for item in alert.missing_items[:10]),
                inline=False
            )
        
        if alert.recommendations:
            embed.add_field(
                name="Recommendations",
                value="\n".join(f"• {rec}" for rec in alert.recommendations[:5]),
                inline=False
            )
        
        # Add footer
        embed.set_footer(text=f"Priority: {alert.priority.upper()} | Macro Learning System")
        
        return embed
    
    async def _send_via_webhook(self, embeds: List[Embed]) -> bool:
        """Send embeds via Discord webhook.
        
        Parameters
        ----------
        embeds : list
            List of Discord embeds
            
        Returns
        -------
        bool
            True if sent successfully
        """
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "embeds": [embed.to_dict() for embed in embeds]
                }
                
                async with session.post(self.webhook_url, json=payload) as response:
                    return response.status == 204
                    
        except Exception as e:
            log_event(f"[DISCORD_MACRO_ALERTS] Webhook error: {e}")
            return False
    
    async def _send_via_bot(self, embeds: List[Embed]) -> bool:
        """Send embeds via Discord bot.
        
        Parameters
        ----------
        embeds : list
            List of Discord embeds
            
        Returns
        -------
        bool
            True if sent successfully
        """
        try:
            import discord
            from discord.ext import commands
            
            bot = commands.Bot(command_prefix="!")
            channel = bot.get_channel(self.channel_id)
            
            if channel:
                for embed in embeds:
                    await channel.send(embed=embed)
                return True
            else:
                log_event("[DISCORD_MACRO_ALERTS] Could not find Discord channel")
                return False
                
        except Exception as e:
            log_event(f"[DISCORD_MACRO_ALERTS] Bot error: {e}")
            return False
    
    def send_comprehensive_alert(self, missing_macros: List[str],
                               missing_aliases: List[str],
                               recommendations: List[str] = None,
                               fallback_maps: List[Dict[str, Any]] = None) -> bool:
        """Send comprehensive macro alert.
        
        Parameters
        ----------
        missing_macros : list
            List of missing macro names
        missing_aliases : list
            List of missing alias names
        recommendations : list, optional
            List of recommendations
        fallback_maps : list, optional
            List of fallback map data
            
        Returns
        -------
        bool
            True if sent successfully
        """
        try:
            # Create main alert
            main_alert = self.create_missing_macros_alert(
                missing_macros, missing_aliases, recommendations
            )
            
            # Send main alert
            asyncio.create_task(self.send_macro_alert(main_alert))
            
            # Send fallback map alert if available
            if fallback_maps:
                fallback_alert = self.create_fallback_map_alert(fallback_maps)
                asyncio.create_task(self.send_macro_alert(fallback_alert))
            
            # Send recommendation alert if available
            if recommendations and len(recommendations) > 5:
                rec_alert = self.create_recommendation_alert(recommendations[5:])
                asyncio.create_task(self.send_macro_alert(rec_alert))
            
            return True
            
        except Exception as e:
            log_event(f"[DISCORD_MACRO_ALERTS] Error sending comprehensive alert: {e}")
            return False
    
    def get_alert_summary(self) -> AlertSummary:
        """Get summary of alerts.
        
        Returns
        -------
        AlertSummary
            Alert summary
        """
        # Count alerts by type
        alerts_by_category = {}
        critical_count = 0
        warning_count = 0
        info_count = 0
        
        for alert in self.alert_history:
            alert_type = alert.alert_type
            alerts_by_category[alert_type] = alerts_by_category.get(alert_type, 0) + 1
            
            if alert_type == "critical":
                critical_count += 1
            elif alert_type == "warning":
                warning_count += 1
            else:
                info_count += 1
        
        # Get recent alerts (last 10)
        recent_alerts = self.alert_history[-10:] if self.alert_history else []
        
        return AlertSummary(
            total_alerts=len(self.alert_history),
            critical_alerts=critical_count,
            warning_alerts=warning_count,
            info_alerts=info_count,
            alerts_by_category=alerts_by_category,
            recent_alerts=recent_alerts
        )
    
    def save_alert_history(self, file_path: str = None) -> str:
        """Save alert history to file.
        
        Parameters
        ----------
        file_path : str, optional
            Path to save file
            
        Returns
        -------
        str
            Path to saved file
        """
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"logs/macro_alerts_{timestamp}.json"
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        history_data = {
            "timestamp": datetime.now().isoformat(),
            "total_alerts": len(self.alert_history),
            "alerts": [asdict(alert) for alert in self.alert_history],
            "summary": asdict(self.get_alert_summary())
        }
        
        with open(file_path, 'w') as f:
            json.dump(history_data, f, indent=2, default=str)
        
        log_event(f"[DISCORD_MACRO_ALERTS] Saved alert history to {file_path}")
        return file_path
    
    def test_discord_connection(self) -> bool:
        """Test Discord connection.
        
        Returns
        -------
        bool
            True if connection successful
        """
        try:
            test_alert = MacroAlert(
                alert_type="info",
                title="🔧 Discord Connection Test",
                message="This is a test alert to verify Discord integration is working.",
                priority="low",
                missing_items=[],
                recommendations=[],
                timestamp=datetime.now()
            )
            
            # Try to send test alert
            asyncio.create_task(self.send_macro_alert(test_alert))
            return True
            
        except Exception as e:
            log_event(f"[DISCORD_MACRO_ALERTS] Discord connection test failed: {e}")
            return False 