"""Alert Manager for Stat Optimizer Module.

This module handles Discord alerts and CLI notifications for suboptimal stat pools,
integrating with the existing Discord alert system.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from android_ms11.utils.logging_utils import log_event

# Import Discord notifier if available
try:
    from modules.discord_alerts.discord_notifier import DiscordNotifier
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    DiscordNotifier = None

logger = logging.getLogger(__name__)

class AlertManager:
    """Manages alerts for suboptimal stat pools via Discord and CLI."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the alert manager.
        
        Parameters
        ----------
        config : dict, optional
            Configuration for alert settings
        """
        self.config = config or {}
        self.alert_history = []
        
        # Alert thresholds
        self.critical_score_threshold = self.config.get("critical_threshold", 50.0)
        self.warning_score_threshold = self.config.get("warning_threshold", 70.0)
        
        # Discord integration
        self.discord_notifier = None
        if DISCORD_AVAILABLE:
            try:
                self.discord_notifier = DiscordNotifier(
                    webhook_url=self.config.get("discord_webhook_url"),
                    bot_token=self.config.get("discord_bot_token"),
                    channel_id=self.config.get("discord_channel_id")
                )
                log_event("[ALERT_MANAGER] Discord notifier initialized")
            except Exception as e:
                log_event(f"[ALERT_MANAGER] Failed to initialize Discord notifier: {e}")
        
        # CLI alert settings
        self.cli_alerts_enabled = self.config.get("cli_alerts", True)
        self.alert_log_file = Path(self.config.get("alert_log_file", "logs/stat_alerts.json"))
        self.alert_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_event("[ALERT_MANAGER] Alert manager initialized")
    
    def check_and_alert(self, analysis: Dict[str, Any], character_name: str = "Unknown") -> bool:
        """Check analysis results and send alerts if needed.
        
        Parameters
        ----------
        analysis : dict
            Stat analysis results
        character_name : str, optional
            Name of the character being analyzed
            
        Returns
        -------
        bool
            True if alerts were sent, False otherwise
        """
        alerts_sent = False
        
        # Check if alerts are needed
        score = analysis.get("score", 0.0)
        issues = analysis.get("issues", [])
        warnings = analysis.get("warnings", [])
        
        # Determine alert level
        if score < self.critical_score_threshold or len(issues) > 0:
            alert_level = "critical"
            should_alert = True
        elif score < self.warning_score_threshold or len(warnings) > 0:
            alert_level = "warning"
            should_alert = True
        else:
            alert_level = "info"
            should_alert = False
        
        if should_alert:
            # Send Discord alert
            if self.discord_notifier:
                discord_sent = self._send_discord_alert(analysis, character_name, alert_level)
                alerts_sent = alerts_sent or discord_sent
            
            # Send CLI alert
            if self.cli_alerts_enabled:
                cli_sent = self._send_cli_alert(analysis, character_name, alert_level)
                alerts_sent = alerts_sent or cli_sent
            
            # Log alert
            self._log_alert(analysis, character_name, alert_level)
        
        return alerts_sent
    
    def _send_discord_alert(self, analysis: Dict[str, Any], character_name: str, 
                           alert_level: str) -> bool:
        """Send Discord alert for stat optimization issues.
        
        Parameters
        ----------
        analysis : dict
            Analysis results
        character_name : str
            Character name
        alert_level : str
            Alert level (critical, warning, info)
            
        Returns
        -------
        bool
            True if alert sent successfully
        """
        if not self.discord_notifier:
            return False
        
        try:
            # Create alert message
            title = f"Stat Optimization Alert - {character_name}"
            
            # Format message based on alert level
            if alert_level == "critical":
                title = f"🚨 CRITICAL: {title}"
                color = "red"
            elif alert_level == "warning":
                title = f"⚠️ WARNING: {title}"
                color = "orange"
            else:
                title = f"ℹ️ INFO: {title}"
                color = "blue"
            
            # Build message content
            message = self._format_discord_message(analysis, character_name)
            
            # Send via Discord notifier
            success = self.discord_notifier.send_simple_alert(title, message, color)
            
            if success:
                log_event(f"[ALERT_MANAGER] Discord alert sent for {character_name}")
            else:
                log_event(f"[ALERT_MANAGER] Failed to send Discord alert for {character_name}")
            
            return success
            
        except Exception as e:
            log_event(f"[ALERT_MANAGER] Error sending Discord alert: {e}")
            return False
    
    def _format_discord_message(self, analysis: Dict[str, Any], character_name: str) -> str:
        """Format analysis results for Discord message.
        
        Parameters
        ----------
        analysis : dict
            Analysis results
        character_name : str
            Character name
            
        Returns
        -------
        str
            Formatted Discord message
        """
        score = analysis.get("score", 0.0)
        optimization_type = analysis.get("optimization_type", "unknown")
        issues = analysis.get("issues", [])
        warnings = analysis.get("warnings", [])
        recommendations = analysis.get("recommendations", [])
        
        message = f"**Character:** {character_name}\n"
        message += f"**Optimization Type:** {optimization_type.replace('_', ' ').title()}\n"
        message += f"**Overall Score:** {score:.1f}/100\n\n"
        
        if issues:
            message += "**Critical Issues:**\n"
            for issue in issues[:5]:  # Limit to 5 issues
                message += f"• {issue}\n"
            message += "\n"
        
        if warnings:
            message += "**Warnings:**\n"
            for warning in warnings[:3]:  # Limit to 3 warnings
                message += f"• {warning}\n"
            message += "\n"
        
        if recommendations:
            message += "**Recommendations:**\n"
            for rec in recommendations[:3]:  # Limit to 3 recommendations
                message += f"• {rec}\n"
        
        return message
    
    def _send_cli_alert(self, analysis: Dict[str, Any], character_name: str, 
                        alert_level: str) -> bool:
        """Send CLI alert for stat optimization issues.
        
        Parameters
        ----------
        analysis : dict
            Analysis results
        character_name : str
            Character name
        alert_level : str
            Alert level
            
        Returns
        -------
        bool
            True if alert sent successfully
        """
        try:
            score = analysis.get("score", 0.0)
            optimization_type = analysis.get("optimization_type", "unknown")
            
            # Format CLI message
            if alert_level == "critical":
                prefix = "🚨 CRITICAL"
            elif alert_level == "warning":
                prefix = "⚠️ WARNING"
            else:
                prefix = "ℹ️ INFO"
            
            message = f"{prefix} - Stat Optimization Alert for {character_name}\n"
            message += f"Optimization Type: {optimization_type.replace('_', ' ').title()}\n"
            message += f"Overall Score: {score:.1f}/100\n"
            
            # Add key issues
            issues = analysis.get("issues", [])
            if issues:
                message += f"Critical Issues: {len(issues)}\n"
                for issue in issues[:2]:
                    message += f"  • {issue}\n"
            
            # Print to console
            print(message)
            
            log_event(f"[ALERT_MANAGER] CLI alert sent for {character_name}")
            return True
            
        except Exception as e:
            log_event(f"[ALERT_MANAGER] Error sending CLI alert: {e}")
            return False
    
    def _log_alert(self, analysis: Dict[str, Any], character_name: str, alert_level: str):
        """Log alert to file for tracking.
        
        Parameters
        ----------
        analysis : dict
            Analysis results
        character_name : str
            Character name
        alert_level : str
            Alert level
        """
        try:
            alert_entry = {
                "timestamp": datetime.now().isoformat(),
                "character_name": character_name,
                "alert_level": alert_level,
                "optimization_type": analysis.get("optimization_type"),
                "score": analysis.get("score", 0.0),
                "issues_count": len(analysis.get("issues", [])),
                "warnings_count": len(analysis.get("warnings", [])),
                "recommendations_count": len(analysis.get("recommendations", []))
            }
            
            # Load existing alerts
            alerts = []
            if self.alert_log_file.exists():
                try:
                    with open(self.alert_log_file, 'r') as f:
                        alerts = json.load(f)
                except Exception:
                    alerts = []
            
            # Add new alert
            alerts.append(alert_entry)
            
            # Keep only last 100 alerts
            if len(alerts) > 100:
                alerts = alerts[-100:]
            
            # Save alerts
            with open(self.alert_log_file, 'w') as f:
                json.dump(alerts, f, indent=2)
            
            # Add to history
            self.alert_history.append(alert_entry)
            
        except Exception as e:
            log_event(f"[ALERT_MANAGER] Error logging alert: {e}")
    
    def get_alert_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of recent alerts.
        
        Parameters
        ----------
        days : int, optional
            Number of days to look back
            
        Returns
        -------
        dict
            Alert summary statistics
        """
        try:
            if not self.alert_log_file.exists():
                return {"total_alerts": 0, "critical_alerts": 0, "warning_alerts": 0}
            
            with open(self.alert_log_file, 'r') as f:
                alerts = json.load(f)
            
            # Filter by date
            cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
            recent_alerts = [
                alert for alert in alerts
                if datetime.fromisoformat(alert["timestamp"]).timestamp() > cutoff_date
            ]
            
            # Calculate statistics
            total_alerts = len(recent_alerts)
            critical_alerts = len([a for a in recent_alerts if a["alert_level"] == "critical"])
            warning_alerts = len([a for a in recent_alerts if a["alert_level"] == "warning"])
            
            return {
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "warning_alerts": warning_alerts,
                "days_analyzed": days
            }
            
        except Exception as e:
            log_event(f"[ALERT_MANAGER] Error getting alert summary: {e}")
            return {"total_alerts": 0, "critical_alerts": 0, "warning_alerts": 0}
    
    def test_discord_connection(self) -> bool:
        """Test Discord connection.
        
        Returns
        -------
        bool
            True if connection successful
        """
        if not self.discord_notifier:
            return False
        
        try:
            return self.discord_notifier.test_connection()
        except Exception as e:
            log_event(f"[ALERT_MANAGER] Discord connection test failed: {e}")
            return False


def create_alert_manager(config: Dict[str, Any] = None) -> AlertManager:
    """Create an alert manager instance.
    
    Parameters
    ----------
    config : dict, optional
        Configuration for the alert manager
        
    Returns
    -------
    AlertManager
        Configured alert manager instance
    """
    return AlertManager(config) 