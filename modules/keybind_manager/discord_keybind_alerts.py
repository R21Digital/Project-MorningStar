"""
MS11 Batch 066 - Discord Keybind Alerts

Sends Discord alerts when keybinds break core bot functions.
Provides real-time notifications for critical keybind issues.
"""

import asyncio
import json
from dataclasses import dataclass
from typing import List, Optional
from .keybind_validator import KeybindValidationResult


@dataclass
class KeybindAlert:
    """Represents a keybind alert for Discord."""
    title: str
    message: str
    severity: str  # "critical", "warning", "info"
    keybinds_affected: List[str]
    recommendations: List[str]
    timestamp: str


class DiscordKeybindAlerts:
    """Handles Discord alerts for keybind issues."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize Discord alerts.
        
        Args:
            webhook_url: Discord webhook URL for sending alerts
        """
        self.webhook_url = webhook_url
        self.alerts: List[KeybindAlert] = []
        self.enabled = bool(webhook_url)
    
    async def send_keybind_alert(self, alert: KeybindAlert) -> bool:
        """Send a keybind alert to Discord.
        
        Args:
            alert: KeybindAlert object to send
            
        Returns:
            True if alert was sent successfully
        """
        if not self.enabled or not self.webhook_url:
            print(f"Discord alerts disabled or no webhook URL configured")
            return False
        
        try:
            # Add alert to history
            self.alerts.append(alert)
            
            # Create Discord embed
            embed = self._create_discord_embed(alert)
            
            # Send to Discord
            await self._send_discord_message(embed)
            
            return True
            
        except Exception as e:
            print(f"Error sending Discord alert: {e}")
            return False
    
    def _create_discord_embed(self, alert: KeybindAlert) -> dict:
        """Create Discord embed for the alert."""
        # Color based on severity
        color_map = {
            "critical": 0xFF0000,  # Red
            "warning": 0xFFA500,   # Orange
            "info": 0x00BFFF       # Blue
        }
        
        color = color_map.get(alert.severity, 0x808080)  # Gray default
        
        embed = {
            "title": alert.title,
            "description": alert.message,
            "color": color,
            "fields": [],
            "timestamp": alert.timestamp
        }
        
        # Add affected keybinds field
        if alert.keybinds_affected:
            embed["fields"].append({
                "name": "Affected Keybinds",
                "value": ", ".join(alert.keybinds_affected),
                "inline": True
            })
        
        # Add recommendations field
        if alert.recommendations:
            recommendations_text = "\n".join([f"• {rec}" for rec in alert.recommendations[:5]])
            if len(alert.recommendations) > 5:
                recommendations_text += f"\n... and {len(alert.recommendations) - 5} more"
            
            embed["fields"].append({
                "name": "Recommendations",
                "value": recommendations_text,
                "inline": False
            })
        
        return embed
    
    async def _send_discord_message(self, embed: dict) -> None:
        """Send message to Discord webhook."""
        import aiohttp
        
        payload = {
            "embeds": [embed]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status != 204:
                    raise Exception(f"Discord webhook returned status {response.status}")
    
    def create_critical_alert(self, validation_result: KeybindValidationResult) -> KeybindAlert:
        """Create a critical alert for keybind issues.
        
        Args:
            validation_result: KeybindValidationResult with issues
            
        Returns:
            KeybindAlert for critical issues
        """
        import datetime
        
        # Extract affected keybinds
        affected_keybinds = []
        for issue in validation_result.critical_issues:
            if "missing" in issue.lower():
                # Extract keybind name from "Missing required keybind: attack"
                parts = issue.split(":")
                if len(parts) > 1:
                    affected_keybinds.append(parts[1].strip())
            elif "conflict" in issue.lower():
                # Extract key from "Key conflict: F1 bound to attack, use"
                parts = issue.split(":")
                if len(parts) > 1:
                    key_part = parts[1].strip()
                    if "bound to" in key_part:
                        key = key_part.split("bound to")[0].strip()
                        affected_keybinds.append(key)
        
        title = "🚨 Critical Keybind Issues Detected"
        message = f"MS11 has detected critical keybind issues that may break core bot functionality."
        
        if validation_result.missing_keybinds > 0:
            message += f"\n\n**Missing Keybinds:** {validation_result.missing_keybinds}"
        
        if validation_result.conflicting_keybinds > 0:
            message += f"\n\n**Key Conflicts:** {validation_result.conflicting_keybinds}"
        
        return KeybindAlert(
            title=title,
            message=message,
            severity="critical",
            keybinds_affected=affected_keybinds,
            recommendations=validation_result.recommendations,
            timestamp=datetime.datetime.now().isoformat()
        )
    
    def create_warning_alert(self, validation_result: KeybindValidationResult) -> KeybindAlert:
        """Create a warning alert for non-critical keybind issues.
        
        Args:
            validation_result: KeybindValidationResult with issues
            
        Returns:
            KeybindAlert for warning issues
        """
        import datetime
        
        title = "⚠️ Keybind Configuration Warning"
        message = f"MS11 has detected potential keybind issues that may affect bot performance."
        
        if validation_result.missing_keybinds > 0:
            message += f"\n\n**Missing Optional Keybinds:** {validation_result.missing_keybinds}"
        
        if validation_result.unknown_keybinds > 0:
            message += f"\n\n**Unknown Keybinds:** {validation_result.unknown_keybinds}"
        
        return KeybindAlert(
            title=title,
            message=message,
            severity="warning",
            keybinds_affected=[],
            recommendations=validation_result.recommendations,
            timestamp=datetime.datetime.now().isoformat()
        )
    
    def should_send_alert(self, validation_result: KeybindValidationResult) -> bool:
        """Determine if an alert should be sent based on validation results.
        
        Args:
            validation_result: KeybindValidationResult to check
            
        Returns:
            True if alert should be sent
        """
        # Send critical alert for critical issues
        if validation_result.critical_issues:
            return True
        
        # Send warning alert for significant issues
        if (validation_result.missing_keybinds > 2 or 
            validation_result.conflicting_keybinds > 1):
            return True
        
        return False
    
    def get_alert_severity(self, validation_result: KeybindValidationResult) -> str:
        """Get the severity level for validation results.
        
        Args:
            validation_result: KeybindValidationResult to check
            
        Returns:
            Severity string: "critical", "warning", or "info"
        """
        if validation_result.critical_issues:
            return "critical"
        elif (validation_result.missing_keybinds > 2 or 
              validation_result.conflicting_keybinds > 1):
            return "warning"
        else:
            return "info"
    
    def list_alerts(self) -> List[KeybindAlert]:
        """List all sent alerts.
        
        Returns:
            List of all KeybindAlert objects
        """
        return self.alerts.copy()
    
    def clear_alerts(self) -> None:
        """Clear alert history."""
        self.alerts.clear() 