#!/usr/bin/env python3
"""
Batch 179 - Dual Mode Support for Same Account

This module provides dual-character support functionality for MS11:
- Primary character can lead (questing), second can follow (medic/dancer)
- Shared Discord channel for both (with tag)
- Session monitor to detect dropped client
- Simultaneous quest + support operation
"""

import os
import json
import time
import threading
import socket
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

import pygetwindow
import pyautogui

from utils.license_hooks import requires_license
from core.profile_loader import assert_profile_ready
from profession_logic.utils.logger import logger


class DualModeType(Enum):
    """Types of dual mode operations."""
    QUEST_MEDIC = "quest_medic"           # Quest + Medic support
    QUEST_DANCER = "quest_dancer"         # Quest + Dancer support
    QUEST_ENTERTAINER = "quest_entertainer"  # Quest + Entertainer support
    COMBAT_PAIR = "combat_pair"           # Combat + Combat support
    CRAFTING_SUPPORT = "crafting_support" # Crafting + Support


@dataclass
class DualModeConfig:
    """Configuration for dual mode support."""
    dual_mode_enabled: bool = False
    primary_character: str = "PrimaryChar"
    secondary_character: str = "SecondaryChar"
    primary_window: str = "SWG - Primary"
    secondary_window: str = "SWG - Secondary"
    dual_mode_type: DualModeType = DualModeType.QUEST_MEDIC
    shared_discord_enabled: bool = False
    discord_channel_id: str = ""
    discord_tag_format: str = "[{character}] {message}"
    session_monitor_enabled: bool = True
    monitor_interval: int = 30
    drop_threshold: int = 60
    auto_reconnect: bool = True
    sync_positions: bool = True
    sync_combat: bool = True
    sync_quests: bool = True


class DualModeSupport:
    """Dual mode support manager for same account characters."""
    
    def __init__(self, config: Optional[DualModeConfig] = None):
        """Initialize dual mode support."""
        self.config = config or DualModeConfig()
        self.primary_session = None
        self.secondary_session = None
        self.shared_session_id = None
        self.is_running = False
        
        # Communication
        self.communication_socket = None
        self.communication_port = 12348
        
        # Monitoring
        self.monitor_thread = None
        self.last_health_check = datetime.now()
        
        # Discord relay
        self.discord_thread = None
        
        logger.info("[DUAL_MODE] Dual mode support initialized")
    
    def start_dual_mode(self, primary_char: str, secondary_char: str) -> bool:
        """Start dual mode with specified characters."""
        try:
            if not self.config.dual_mode_enabled:
                logger.warning("[DUAL_MODE] Dual mode not enabled in config")
                return False
            
            # Create shared session ID
            self.shared_session_id = f"dual_{int(time.time())}"
            
            # Initialize character sessions
            self.primary_session = self._create_character_session(
                primary_char, self.config.primary_window, "leader"
            )
            self.secondary_session = self._create_character_session(
                secondary_char, self.config.secondary_window, "follower"
            )
            
            # Start monitoring and communication
            self._start_session_monitor()
            self._start_discord_relay()
            self._start_communication()
            
            self.is_running = True
            logger.info(f"[DUAL_MODE] Started dual mode session: {self.shared_session_id}")
            return True
            
        except Exception as e:
            logger.error(f"[DUAL_MODE] Failed to start dual mode: {e}")
            return False
    
    def _create_character_session(self, char_name: str, window_title: str, role: str) -> Dict[str, Any]:
        """Create a character session."""
        return {
            "character_name": char_name,
            "window_title": window_title,
            "role": role,
            "session_id": self.shared_session_id,
            "window_handle": None,
            "is_active": False,
            "last_activity": datetime.now(),
            "position": None,
            "current_planet": "",
            "current_city": "",
            "status": "idle",
            "xp_gained": 0,
            "credits_earned": 0,
            "quests_completed": 0,
            "combat_kills": 0
        }
    
    def _start_session_monitor(self) -> None:
        """Start session monitoring thread."""
        if not self.config.session_monitor_enabled:
            return
        
        self.monitor_thread = threading.Thread(
            target=self._session_monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("[DUAL_MODE] Session monitor started")
    
    def _session_monitor_loop(self) -> None:
        """Monitor session health and detect dropped clients."""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check primary character
                if self.primary_session:
                    self._check_character_health(self.primary_session, "Primary")
                
                # Check secondary character
                if self.secondary_session:
                    self._check_character_health(self.secondary_session, "Secondary")
                
                self.last_health_check = current_time
                time.sleep(self.config.monitor_interval)
                
            except Exception as e:
                logger.error(f"[DUAL_MODE] Error in session monitor: {e}")
                time.sleep(self.config.monitor_interval)
    
    def _check_character_health(self, session: Dict[str, Any], char_type: str) -> None:
        """Check health of a character session."""
        try:
            if session["window_handle"]:
                # Check if window is still active
                if not session["window_handle"].isActive:
                    time_since_activity = (datetime.now() - session["last_activity"]).total_seconds()
                    if time_since_activity > self.config.drop_threshold:
                        logger.warning(f"[DUAL_MODE] {char_type} character appears to be dropped")
                        self._handle_character_drop(session, char_type)
            else:
                # Try to find window
                windows = pygetwindow.getWindowsWithTitle(session["window_title"])
                if windows:
                    session["window_handle"] = windows[0]
                    session["is_active"] = True
                    session["last_activity"] = datetime.now()
                    logger.info(f"[DUAL_MODE] Found window for {char_type} character")
                    
        except Exception as e:
            logger.error(f"[DUAL_MODE] Error checking {char_type} character: {e}")
            self._handle_character_drop(session, char_type)
    
    def _handle_character_drop(self, session: Dict[str, Any], char_type: str) -> None:
        """Handle dropped character detection."""
        logger.warning(f"[DUAL_MODE] {char_type} character dropped - attempting recovery")
        
        if self.config.auto_reconnect:
            self._attempt_reconnect(session, char_type)
        
        # Send Discord alert
        self._send_discord_alert(f"{char_type} character dropped from session")
    
    def _attempt_reconnect(self, session: Dict[str, Any], char_type: str) -> None:
        """Attempt to reconnect dropped character."""
        try:
            windows = pygetwindow.getWindowsWithTitle(session["window_title"])
            if windows:
                session["window_handle"] = windows[0]
                session["is_active"] = True
                session["last_activity"] = datetime.now()
                logger.info(f"[DUAL_MODE] Successfully reconnected {char_type} character")
            else:
                logger.error(f"[DUAL_MODE] Could not find window for {char_type} character")
                
        except Exception as e:
            logger.error(f"[DUAL_MODE] Failed to reconnect {char_type} character: {e}")
    
    def _start_discord_relay(self) -> None:
        """Start Discord relay thread."""
        if not self.config.shared_discord_enabled:
            return
        
        self.discord_thread = threading.Thread(
            target=self._discord_relay_loop,
            daemon=True
        )
        self.discord_thread.start()
        logger.info("[DUAL_MODE] Discord relay started")
    
    def _discord_relay_loop(self) -> None:
        """Handle Discord relay for dual characters."""
        while self.is_running:
            try:
                # Process Discord messages (placeholder for actual Discord integration)
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"[DUAL_MODE] Error in Discord relay: {e}")
                time.sleep(5)
    
    def _send_discord_alert(self, message: str) -> None:
        """Send alert to Discord channel."""
        if not self.config.shared_discord_enabled:
            return
        
        formatted_message = self.config.discord_tag_format.format(
            character="System",
            message=message
        )
        logger.info(f"[DISCORD] {formatted_message}")
    
    def _start_communication(self) -> None:
        """Start inter-character communication."""
        try:
            self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.communication_socket.bind(('localhost', self.communication_port))
            self.communication_socket.listen(2)
            
            comm_thread = threading.Thread(
                target=self._communication_loop,
                daemon=True
            )
            comm_thread.start()
            logger.info(f"[DUAL_MODE] Communication started on port {self.communication_port}")
            
        except Exception as e:
            logger.error(f"[DUAL_MODE] Failed to start communication: {e}")
    
    def _communication_loop(self) -> None:
        """Handle inter-character communication."""
        while self.is_running and self.communication_socket:
            try:
                client, addr = self.communication_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client,),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if self.is_running:
                    logger.error(f"[DUAL_MODE] Communication error: {e}")
    
    def _handle_client(self, client: socket.socket) -> None:
        """Handle communication client."""
        try:
            while self.is_running:
                data = client.recv(4096)
                if not data:
                    break
                
                message = pickle.loads(data)
                self._process_message(message)
                
        except Exception as e:
            logger.error(f"[DUAL_MODE] Client handling error: {e}")
        finally:
            client.close()
    
    def _process_message(self, message: Dict[str, Any]) -> None:
        """Process inter-character message."""
        try:
            msg_type = message.get("type")
            sender = message.get("sender")
            data = message.get("data", {})
            
            if msg_type == "position_update":
                self._update_character_position(sender, data)
            elif msg_type == "status_update":
                self._update_character_status(sender, data)
            elif msg_type == "xp_gain":
                self._handle_xp_gain(sender, data)
            elif msg_type == "quest_complete":
                self._handle_quest_complete(sender, data)
            elif msg_type == "combat_kill":
                self._handle_combat_kill(sender, data)
            elif msg_type == "discord_message":
                self._handle_discord_message(sender, data)
                
        except Exception as e:
            logger.error(f"[DUAL_MODE] Message processing error: {e}")
    
    def _update_character_position(self, char_name: str, position_data: Dict[str, Any]) -> None:
        """Update character position."""
        session = self._get_character_session(char_name)
        if session:
            session["position"] = position_data.get("position")
            session["current_planet"] = position_data.get("planet", "")
            session["current_city"] = position_data.get("city", "")
            session["last_activity"] = datetime.now()
    
    def _update_character_status(self, char_name: str, status_data: Dict[str, Any]) -> None:
        """Update character status."""
        session = self._get_character_session(char_name)
        if session:
            session["status"] = status_data.get("status", "idle")
            session["last_activity"] = datetime.now()
    
    def _handle_xp_gain(self, char_name: str, xp_data: Dict[str, Any]) -> None:
        """Handle XP gain from character."""
        session = self._get_character_session(char_name)
        if session:
            xp_amount = xp_data.get("xp", 0)
            session["xp_gained"] += xp_amount
            
            # Send Discord alert for significant XP gains
            if xp_amount > 100:
                self._send_discord_alert(f"{char_name} gained {xp_amount} XP")
    
    def _handle_quest_complete(self, char_name: str, quest_data: Dict[str, Any]) -> None:
        """Handle quest completion."""
        session = self._get_character_session(char_name)
        if session:
            session["quests_completed"] += 1
            
            quest_name = quest_data.get("quest_name", "Unknown Quest")
            self._send_discord_alert(f"{char_name} completed: {quest_name}")
    
    def _handle_combat_kill(self, char_name: str, combat_data: Dict[str, Any]) -> None:
        """Handle combat kill."""
        session = self._get_character_session(char_name)
        if session:
            session["combat_kills"] += 1
            
            target = combat_data.get("target", "Unknown")
            self._send_discord_alert(f"{char_name} defeated: {target}")
    
    def _handle_discord_message(self, char_name: str, message_data: Dict[str, Any]) -> None:
        """Handle Discord message from character."""
        message = message_data.get("message", "")
        formatted_message = self.config.discord_tag_format.format(
            character=char_name,
            message=message
        )
        logger.info(f"[DISCORD] {formatted_message}")
    
    def _get_character_session(self, char_name: str) -> Optional[Dict[str, Any]]:
        """Get character session by name."""
        if self.primary_session and self.primary_session["character_name"] == char_name:
            return self.primary_session
        elif self.secondary_session and self.secondary_session["character_name"] == char_name:
            return self.secondary_session
        return None
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        if not self.shared_session_id:
            return {"status": "not_started"}
        
        status = {
            "session_id": self.shared_session_id,
            "dual_mode_type": self.config.dual_mode_type.value,
            "characters": {}
        }
        
        if self.primary_session:
            status["characters"]["primary"] = {
                "name": self.primary_session["character_name"],
                "role": self.primary_session["role"],
                "is_active": self.primary_session["is_active"],
                "status": self.primary_session["status"],
                "position": self.primary_session["position"],
                "current_planet": self.primary_session["current_planet"],
                "current_city": self.primary_session["current_city"],
                "xp_gained": self.primary_session["xp_gained"],
                "quests_completed": self.primary_session["quests_completed"],
                "combat_kills": self.primary_session["combat_kills"],
                "last_activity": self.primary_session["last_activity"].isoformat()
            }
        
        if self.secondary_session:
            status["characters"]["secondary"] = {
                "name": self.secondary_session["character_name"],
                "role": self.secondary_session["role"],
                "is_active": self.secondary_session["is_active"],
                "status": self.secondary_session["status"],
                "position": self.secondary_session["position"],
                "current_planet": self.secondary_session["current_planet"],
                "current_city": self.secondary_session["current_city"],
                "xp_gained": self.secondary_session["xp_gained"],
                "quests_completed": self.secondary_session["quests_completed"],
                "combat_kills": self.secondary_session["combat_kills"],
                "last_activity": self.secondary_session["last_activity"].isoformat()
            }
        
        return status
    
    def stop_dual_mode(self) -> None:
        """Stop dual mode session."""
        self.is_running = False
        
        # Stop monitoring threads
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        if self.discord_thread:
            self.discord_thread.join(timeout=5)
        
        # Close communication socket
        if self.communication_socket:
            self.communication_socket.close()
        
        # Save session logs
        self._save_session_logs()
        
        logger.info("[DUAL_MODE] Dual mode stopped")
    
    def _save_session_logs(self) -> None:
        """Save session logs for both characters."""
        if not self.shared_session_id:
            return
        
        try:
            log_dir = Path("logs/dual_mode_sessions")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Save shared session data
            shared_data = {
                "session_id": self.shared_session_id,
                "dual_mode_type": self.config.dual_mode_type.value,
                "start_time": datetime.now().isoformat(),
                "primary_session": self.primary_session,
                "secondary_session": self.secondary_session
            }
            
            shared_log_path = log_dir / f"dual_mode_{self.shared_session_id}.json"
            with open(shared_log_path, 'w') as f:
                json.dump(shared_data, f, indent=2)
            
            logger.info(f"[DUAL_MODE] Session logs saved to {log_dir}")
            
        except Exception as e:
            logger.error(f"[DUAL_MODE] Failed to save session logs: {e}")


# Global instance for easy access
dual_mode_support = DualModeSupport()


@requires_license
def run(config=None, session=None, max_loops: int = None) -> Dict[str, Any]:
    """Main entry point for dual mode support.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    session : object, optional
        Session object
    max_loops : int, optional
        Maximum number of loops to run
        
    Returns
    -------
    dict
        Status of the dual mode operation
    """
    
    assert_profile_ready(getattr(session, "profile", None))
    
    try:
        # Load configuration
        dual_config = DualModeConfig()
        
        # Get character names from config or use defaults
        primary_char = dual_config.primary_character
        secondary_char = dual_config.secondary_character
        
        # Start dual mode
        success = dual_mode_support.start_dual_mode(primary_char, secondary_char)
        
        if success:
            logger.info(f"[DUAL_MODE] Started dual mode: {primary_char} + {secondary_char}")
            
            # Run the dual mode loop
            loops = 0
            while dual_mode_support.is_running:
                # Check if we should stop
                if max_loops and loops >= max_loops:
                    break
                
                # Get current status
                status = dual_mode_support.get_session_status()
                
                # Log status periodically
                if loops % 10 == 0:
                    logger.info(f"[DUAL_MODE] Status: {status}")
                
                loops += 1
                time.sleep(5)  # Check every 5 seconds
            
            # Stop dual mode
            dual_mode_support.stop_dual_mode()
            
            return {
                "status": "success",
                "session_id": dual_mode_support.shared_session_id,
                "loops_completed": loops,
                "message": "Dual mode completed successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to start dual mode"
            }
            
    except Exception as e:
        logger.error(f"[DUAL_MODE] Error in dual mode: {e}")
        return {
            "status": "error",
            "message": f"Exception in dual mode: {e}"
        }


def get_dual_mode_status() -> Dict[str, Any]:
    """Get current dual mode status."""
    return dual_mode_support.get_session_status()


def stop_dual_mode() -> None:
    """Stop the current dual mode."""
    dual_mode_support.stop_dual_mode() 