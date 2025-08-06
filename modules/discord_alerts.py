"""Discord alerts module for bounty hunter notifications."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Discord configuration
DISCORD_CONFIG_PATH = "config/discord_config.json"


def load_discord_config() -> dict:
    """Load Discord configuration from file."""
    config_path = Path(DISCORD_CONFIG_PATH)
    if not config_path.exists():
        return {}
    
    try:
        with config_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:
        logger.error(f"[DiscordAlerts] Failed to load config: {e}")
        return {}


def send_discord_alert(message: str, config: Optional[dict] = None) -> bool:
    """Send a Discord alert message.
    
    Parameters
    ----------
    message : str
        The message to send
    config : dict, optional
        Discord configuration. If None, loads from config file.
        
    Returns
    -------
    bool
        True if message was sent successfully
    """
    if config is None:
        config = load_discord_config()
    
    # Check if Discord is enabled
    if not config.get("discord_token"):
        logger.debug("[DiscordAlerts] Discord not configured, skipping alert")
        return False
    
    try:
        # Here you would integrate with Discord API
        # For now, just log the message
        logger.info(f"[DiscordAlerts] Alert: {message}")
        
        # Future implementation would use discord.py or similar
        # import discord
        # bot = discord.Client()
        # channel = bot.get_channel(config.get("alert_channel_id"))
        # await channel.send(message)
        
        return True
        
    except Exception as e:
        logger.error(f"[DiscordAlerts] Failed to send alert: {e}")
        return False


def send_bounty_alert(target_name: str, location: str, difficulty: str = "medium") -> bool:
    """Send a specific bounty hunter alert.
    
    Parameters
    ----------
    target_name : str
        Name of the target being engaged
    location : str
        Location where the target was found
    difficulty : str
        Difficulty level of the target
        
    Returns
    -------
    bool
        True if alert was sent successfully
    """
    message = f"🎯 **T-Unit engaged target: {target_name} @ {location}** (Difficulty: {difficulty})"
    return send_discord_alert(message)


def send_mission_complete_alert(target_name: str, reward_credits: int) -> bool:
    """Send a mission completion alert.
    
    Parameters
    ----------
    target_name : str
        Name of the completed target
    reward_credits : int
        Credits earned from the mission
        
    Returns
    -------
    bool
        True if alert was sent successfully
    """
    message = f"✅ **Mission Complete: {target_name}** - Earned {reward_credits} credits"
    return send_discord_alert(message)


def send_mission_failed_alert(target_name: str, reason: str) -> bool:
    """Send a mission failure alert.
    
    Parameters
    ----------
    target_name : str
        Name of the failed target
    reason : str
        Reason for the failure
        
    Returns
    -------
    bool
        True if alert was sent successfully
    """
    message = f"❌ **Mission Failed: {target_name}** - {reason}"
    return send_discord_alert(message)


# Convenience function for bounty hunter mode
def send_bounty_hunter_alert(alert_type: str, **kwargs) -> bool:
    """Send a bounty hunter alert based on type.
    
    Parameters
    ----------
    alert_type : str
        Type of alert: "engage", "complete", "failed"
    **kwargs
        Additional parameters for the alert
        
    Returns
    -------
    bool
        True if alert was sent successfully
    """
    if alert_type == "engage":
        return send_bounty_alert(
            kwargs.get("target_name", "Unknown"),
            kwargs.get("location", "Unknown"),
            kwargs.get("difficulty", "medium")
        )
    elif alert_type == "complete":
        return send_mission_complete_alert(
            kwargs.get("target_name", "Unknown"),
            kwargs.get("reward_credits", 0)
        )
    elif alert_type == "failed":
        return send_mission_failed_alert(
            kwargs.get("target_name", "Unknown"),
            kwargs.get("reason", "Unknown error")
        )
    else:
        logger.warning(f"[DiscordAlerts] Unknown alert type: {alert_type}")
        return False 