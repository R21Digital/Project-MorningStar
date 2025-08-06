"""AFK Reply Manager Service for MS11.

This module provides comprehensive AFK management including whisper scanning,
RP reply generation, and automatic AFK detection to maintain human-like behavior.
"""

import json
import random
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from android_ms11.utils.logging_utils import log_event


@dataclass
class WhisperScanning:
    """Whisper scanning configuration."""
    enabled: bool = True
    scan_interval: int = 5
    response_delay_min: int = 2
    response_delay_max: int = 15


@dataclass
class RPReplies:
    """RP reply configuration."""
    enabled: bool = True
    reply_templates: List[str] = None
    emote_templates: List[str] = None


@dataclass
class AutoAFKDetection:
    """Auto AFK detection configuration."""
    enabled: bool = True
    inactivity_threshold: int = 300
    afk_message: str = "I'll be back in a bit!"
    return_message: str = "I'm back!"


class AFKReplyManager:
    """Manages AFK behavior and whisper responses."""

    def __init__(self, config_path: str = "config/defense_config.json"):
        """Initialize the AFK reply manager.

        Parameters
        ----------
        config_path : str
            Path to the defense configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Initialize components
        afk_config = self.config.get("afk_reply_manager", {})
        
        # Map whisper scanning config
        whisper_config = afk_config.get("whisper_scanning", {})
        if "response_delay" in whisper_config:
            response_delay = whisper_config["response_delay"]
            whisper_config["response_delay_min"] = response_delay.get("min_seconds", 2)
            whisper_config["response_delay_max"] = response_delay.get("max_seconds", 15)
            del whisper_config["response_delay"]
        
        self.whisper_scanning = WhisperScanning(**whisper_config)
        self.rp_replies = RPReplies(**afk_config.get("rp_replies", {}))
        self.auto_afk_detection = AutoAFKDetection(**afk_config.get("auto_afk_detection", {}))
        
        # Set default values for lists
        if self.rp_replies.reply_templates is None:
            self.rp_replies.reply_templates = [
                "Sorry, I'm a bit busy right now. Can we chat later?",
                "Thanks for the message! I'm currently focused on some tasks.",
                "Hey there! I'm in the middle of something, but I'll get back to you soon.",
                "Appreciate the message! I'm a bit tied up at the moment.",
                "Thanks for reaching out! I'm currently occupied but will respond when I can."
            ]
        
        if self.rp_replies.emote_templates is None:
            self.rp_replies.emote_templates = [
                "/nod", "/wave", "/smile", "/bow", "/salute"
            ]
        
        # Initialize tracking
        self.last_activity = time.time()
        self.last_whisper_scan = 0
        self.whisper_history = []
        self.afk_status = False
        self.afk_start_time = None
        self.reply_history = []
        
        log_event("[AFK_REPLY_MANAGER] AFK reply manager initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                log_event(f"[AFK_REPLY_MANAGER] Config file not found: {self.config_path}")
                return {}
        except Exception as e:
            log_event(f"[AFK_REPLY_MANAGER] Error loading config: {e}")
            return {}

    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = time.time()
        
        # If we were AFK, mark as returned
        if self.afk_status:
            self._return_from_afk()

    def scan_for_whispers(self, chat_log: str = None) -> List[Dict[str, Any]]:
        """Scan for whispers in chat log or simulate scanning."""
        if not self.whisper_scanning.enabled:
            return []
        
        current_time = time.time()
        if current_time - self.last_whisper_scan < self.whisper_scanning.scan_interval:
            return []
        
        self.last_whisper_scan = current_time
        
        try:
            if chat_log:
                # Parse actual chat log for whispers
                whispers = self._parse_whispers_from_log(chat_log)
            else:
                # Simulate whisper detection (for demo/testing)
                whispers = self._simulate_whisper_detection()
            
            # Process each whisper
            for whisper in whispers:
                self._process_whisper(whisper)
            
            return whispers
            
        except Exception as e:
            log_event(f"[AFK_REPLY_MANAGER] Error scanning for whispers: {e}")
            return []

    def _parse_whispers_from_log(self, chat_log: str) -> List[Dict[str, Any]]:
        """Parse whispers from actual chat log."""
        whispers = []
        
        # Common whisper patterns in SWG
        whisper_patterns = [
            r"\[Whisper from (.+?)\]: (.+)",
            r"<(.+?) whispers>: (.+)",
            r"Whisper from (.+?): (.+)"
        ]
        
        for pattern in whisper_patterns:
            matches = re.findall(pattern, chat_log, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    whispers.append({
                        "sender": match[0].strip(),
                        "message": match[1].strip(),
                        "timestamp": time.time(),
                        "type": "whisper"
                    })
        
        return whispers

    def _simulate_whisper_detection(self) -> List[Dict[str, Any]]:
        """Simulate whisper detection for testing."""
        # 10% chance of receiving a whisper
        if random.random() < 0.1:
            senders = ["Player1", "Player2", "Player3", "Friend1", "GuildMember"]
            messages = [
                "Hey, are you there?",
                "Want to group up?",
                "How's it going?",
                "Are you busy?",
                "Can you help me with something?"
            ]
            
            return [{
                "sender": random.choice(senders),
                "message": random.choice(messages),
                "timestamp": time.time(),
                "type": "whisper"
            }]
        
        return []

    def _process_whisper(self, whisper: Dict[str, Any]) -> None:
        """Process a detected whisper and generate response."""
        try:
            # Store in history
            self.whisper_history.append(whisper)
            
            # Check if we should respond
            if self._should_respond_to_whisper(whisper):
                response = self._generate_rp_reply(whisper)
                
                # Add response delay
                delay = random.randint(
                    self.whisper_scanning.response_delay_min,
                    self.whisper_scanning.response_delay_max
                )
                
                reply_data = {
                    "whisper": whisper,
                    "response": response,
                    "delay": delay,
                    "timestamp": time.time()
                }
                
                self.reply_history.append(reply_data)
                
                log_event(f"[AFK_REPLY_MANAGER] Responding to whisper from {whisper['sender']}: {response}")
                
        except Exception as e:
            log_event(f"[AFK_REPLY_MANAGER] Error processing whisper: {e}")

    def _should_respond_to_whisper(self, whisper: Dict[str, Any]) -> bool:
        """Determine if we should respond to a whisper."""
        # Don't respond if we're AFK
        if self.afk_status:
            return False
        
        # Don't respond to spam (same sender within 60 seconds)
        recent_replies = [
            reply for reply in self.reply_history
            if reply["whisper"]["sender"] == whisper["sender"] and
            time.time() - reply["timestamp"] < 60
        ]
        
        if len(recent_replies) > 2:  # More than 2 replies to same person in 60s
            return False
        
        # 90% chance to respond to normal whispers
        return random.random() < 0.9

    def _generate_rp_reply(self, whisper: Dict[str, Any]) -> str:
        """Generate a roleplay-style reply to a whisper."""
        if not self.rp_replies.enabled:
            return "Thanks for the message!"
        
        try:
            # Choose a reply template
            reply = random.choice(self.rp_replies.reply_templates)
            
            # Sometimes add an emote
            if random.random() < 0.3:
                emote = random.choice(self.rp_replies.emote_templates)
                reply = f"{reply} {emote}"
            
            return reply
            
        except Exception as e:
            log_event(f"[AFK_REPLY_MANAGER] Error generating RP reply: {e}")
            return "Thanks for the message!"

    def check_afk_status(self) -> Dict[str, Any]:
        """Check if we should go AFK based on inactivity."""
        if not self.auto_afk_detection.enabled:
            return {"afk": False, "reason": "disabled"}
        
        try:
            current_time = time.time()
            inactivity_duration = current_time - self.last_activity
            
            # Check if we should go AFK
            if not self.afk_status and inactivity_duration > self.auto_afk_detection.inactivity_threshold:
                self._go_afk()
                return {
                    "afk": True,
                    "reason": "inactivity",
                    "duration": inactivity_duration,
                    "message": self.auto_afk_detection.afk_message
                }
            
            # Check if we should return from AFK
            elif self.afk_status and inactivity_duration < 60:  # Return after 1 minute of activity
                self._return_from_afk()
                return {
                    "afk": False,
                    "reason": "activity_resumed",
                    "message": self.auto_afk_detection.return_message
                }
            
            return {
                "afk": self.afk_status,
                "inactivity_duration": inactivity_duration,
                "threshold": self.auto_afk_detection.inactivity_threshold
            }
            
        except Exception as e:
            log_event(f"[AFK_REPLY_MANAGER] Error checking AFK status: {e}")
            return {"afk": False, "error": str(e)}

    def _go_afk(self) -> None:
        """Mark the character as AFK."""
        self.afk_status = True
        self.afk_start_time = time.time()
        log_event(f"[AFK_REPLY_MANAGER] Going AFK: {self.auto_afk_detection.afk_message}")

    def _return_from_afk(self) -> None:
        """Mark the character as returned from AFK."""
        self.afk_status = False
        afk_duration = time.time() - self.afk_start_time if self.afk_start_time else 0
        self.afk_start_time = None
        
        log_event(f"[AFK_REPLY_MANAGER] Returning from AFK after {afk_duration:.1f}s: {self.auto_afk_detection.return_message}")

    def get_afk_summary(self) -> Dict[str, Any]:
        """Get a summary of AFK status and whisper activity."""
        try:
            current_time = time.time()
            inactivity_duration = current_time - self.last_activity
            
            summary = {
                "afk_status": self.afk_status,
                "inactivity_duration": inactivity_duration,
                "whisper_history_count": len(self.whisper_history),
                "reply_history_count": len(self.reply_history),
                "last_whisper_scan": self.last_whisper_scan,
                "features_enabled": {
                    "whisper_scanning": self.whisper_scanning.enabled,
                    "rp_replies": self.rp_replies.enabled,
                    "auto_afk_detection": self.auto_afk_detection.enabled
                },
                "config_loaded": bool(self.config)
            }
            
            if self.afk_status and self.afk_start_time:
                summary["afk_duration"] = current_time - self.afk_start_time
            
            return summary
            
        except Exception as e:
            log_event(f"[AFK_REPLY_MANAGER] Error getting AFK summary: {e}")
            return {"error": str(e)}

    def simulate_activity(self) -> None:
        """Simulate activity to prevent AFK status."""
        self.update_activity()

    def get_recent_whispers(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get whispers from the last N minutes."""
        try:
            cutoff_time = time.time() - (minutes * 60)
            return [
                whisper for whisper in self.whisper_history
                if whisper["timestamp"] > cutoff_time
            ]
        except Exception as e:
            log_event(f"[AFK_REPLY_MANAGER] Error getting recent whispers: {e}")
            return []

    def get_reply_statistics(self) -> Dict[str, Any]:
        """Get statistics about whisper replies."""
        try:
            if not self.reply_history:
                return {"total_replies": 0, "average_delay": 0}
            
            total_replies = len(self.reply_history)
            total_delay = sum(reply["delay"] for reply in self.reply_history)
            average_delay = total_delay / total_replies
            
            # Group by sender
            sender_counts = {}
            for reply in self.reply_history:
                sender = reply["whisper"]["sender"]
                sender_counts[sender] = sender_counts.get(sender, 0) + 1
            
            return {
                "total_replies": total_replies,
                "average_delay": average_delay,
                "sender_counts": sender_counts,
                "reply_rate": total_replies / max(1, len(self.whisper_history))
            }
            
        except Exception as e:
            log_event(f"[AFK_REPLY_MANAGER] Error getting reply statistics: {e}")
            return {"error": str(e)}

    def clear_history(self) -> None:
        """Clear whisper and reply history."""
        self.whisper_history.clear()
        self.reply_history.clear()
        log_event("[AFK_REPLY_MANAGER] History cleared")


def create_afk_reply_manager(config_path: str = "config/defense_config.json") -> AFKReplyManager:
    """Create and return an AFKReplyManager instance."""
    return AFKReplyManager(config_path)


__all__ = [
    "AFKReplyManager",
    "create_afk_reply_manager",
    "WhisperScanning",
    "RPReplies",
    "AutoAFKDetection"
] 