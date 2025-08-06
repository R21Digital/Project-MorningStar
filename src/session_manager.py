#!/usr/bin/env python3
"""
Batch 179 - Dual-Character Support for Same Account

This module provides enhanced dual-character support for MS11 with:
- Support for running two MS11-controlled characters from the same SWG account
- Primary character can lead (questing), second can follow (medic/dancer)
- Shared Discord channel for both (with tag)
- Session monitor to detect dropped client
- Simultaneous quest + support operation
- Session logs per character stored under shared session ID
"""

import os
import json
import time
import threading
import socket
import pickle
import subprocess
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging

import pygetwindow
import pyautogui

from core.session_manager import SessionManager
from core.dual_session_manager import DualSessionManager, DualSessionMode, CharacterBehavior
from utils.license_hooks import requires_license
from profession_logic.utils.logger import logger


class DualModeConfig:
    """Configuration for dual mode support."""
    
    def __init__(self, config_path: str = "config/session_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load dual mode configuration."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = self._get_default_config()
            self._save_config(config)
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default dual mode configuration."""
        return {
            "dual_mode": False,
            "primary_character": {
                "name": "PrimaryChar",
                "mode": "quest",
                "role": "leader",
                "window_title": "SWG - Primary"
            },
            "secondary_character": {
                "name": "SecondaryChar", 
                "mode": "medic",
                "role": "follower",
                "window_title": "SWG - Secondary"
            },
            "shared_discord_channel": {
                "enabled": False,
                "channel_id": "",
                "tag_format": "[{character}] {message}"
            },
            "session_monitor": {
                "enabled": True,
                "check_interval": 30,
                "drop_threshold": 60,
                "auto_reconnect": True
            },
            "sync_settings": {
                "shared_session_id": True,
                "sync_positions": True,
                "sync_combat": True,
                "sync_quests": True
            }
        }
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def update_config(self, **kwargs) -> bool:
        """Update configuration with new values."""
        try:
            for key, value in kwargs.items():
                keys = key.split('.')
                current = self.config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
            
            self._save_config(self.config)
            return True
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return False


@dataclass
class CharacterSession:
    """Individual character session data."""
    character_name: str
    window_title: str
    mode: str
    role: str
    session_id: str
    window_handle: Optional[pygetwindow.Window] = None
    is_active: bool = False
    last_activity: datetime = None
    position: Optional[Tuple[int, int]] = None
    current_planet: str = ""
    current_city: str = ""
    status: str = "idle"
    xp_gained: int = 0
    credits_earned: int = 0
    quests_completed: int = 0
    combat_kills: int = 0
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now()


@dataclass
class SharedSessionData:
    """Shared data between dual sessions."""
    session_id: str
    start_time: datetime
    total_xp_gained: int = 0
    total_credits_earned: int = 0
    total_quests_completed: int = 0
    total_combat_kills: int = 0
    shared_activities: List[str] = None
    leader_position: Optional[Tuple[int, int]] = None
    follower_position: Optional[Tuple[int, int]] = None
    last_sync_time: datetime = None
    discord_messages: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.shared_activities is None:
            self.shared_activities = []
        if self.last_sync_time is None:
            self.last_sync_time = datetime.now()
        if self.discord_messages is None:
            self.discord_messages = []


class DualCharacterSessionManager:
    """Manager for dual character sessions on same account."""
    
    def __init__(self, config_path: str = "config/session_config.json"):
        """Initialize dual character session manager."""
        self.config = DualModeConfig(config_path)
        self.character_sessions: Dict[str, CharacterSession] = {}
        self.shared_data: Optional[SharedSessionData] = None
        self.session_monitor_thread: Optional[threading.Thread] = None
        self.discord_relay_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Communication
        self.communication_socket: Optional[socket.socket] = None
        self.communication_port = 12347
        
        # Monitoring
        self.drop_detection_enabled = True
        self.last_health_check = datetime.now()
        
        logger.info("[DUAL_SESSION] Dual character session manager initialized")
    
    def start_dual_session(self, char1_name: str, char1_window: str, 
                          char2_name: str, char2_window: str) -> bool:
        """Start dual character session."""
        try:
            if not self.config.config.get("dual_mode", False):
                logger.warning("[DUAL_SESSION] Dual mode not enabled in config")
                return False
            
            # Create shared session data
            shared_session_id = f"dual_{int(time.time())}"
            self.shared_data = SharedSessionData(
                session_id=shared_session_id,
                start_time=datetime.now()
            )
            
            # Create character sessions
            primary_config = self.config.config.get("primary_character", {})
            secondary_config = self.config.config.get("secondary_character", {})
            
            char1_session = CharacterSession(
                character_name=char1_name,
                window_title=char1_window,
                mode=primary_config.get("mode", "quest"),
                role=primary_config.get("role", "leader"),
                session_id=shared_session_id
            )
            
            char2_session = CharacterSession(
                character_name=char2_name,
                window_title=char2_window,
                mode=secondary_config.get("mode", "medic"),
                role=secondary_config.get("role", "follower"),
                session_id=shared_session_id
            )
            
            self.character_sessions[char1_name] = char1_session
            self.character_sessions[char2_name] = char2_session
            
            # Start monitoring threads
            self._start_session_monitor()
            self._start_discord_relay()
            self._start_communication()
            
            self.is_running = True
            logger.info(f"[DUAL_SESSION] Started dual session: {shared_session_id}")
            return True
            
        except Exception as e:
            logger.error(f"[DUAL_SESSION] Failed to start dual session: {e}")
            return False
    
    def _start_session_monitor(self) -> None:
        """Start session monitoring thread."""
        if not self.config.config.get("session_monitor", {}).get("enabled", True):
            return
        
        self.session_monitor_thread = threading.Thread(
            target=self._session_monitor_loop,
            daemon=True
        )
        self.session_monitor_thread.start()
        logger.info("[DUAL_SESSION] Session monitor started")
    
    def _session_monitor_loop(self) -> None:
        """Monitor session health and detect dropped clients."""
        check_interval = self.config.config.get("session_monitor", {}).get("check_interval", 30)
        drop_threshold = self.config.config.get("session_monitor", {}).get("drop_threshold", 60)
        
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for char_name, session in self.character_sessions.items():
                    # Check if window is still active
                    if session.window_handle:
                        try:
                            # Check if window still exists and is visible
                            if not session.window_handle.isActive:
                                time_since_activity = (current_time - session.last_activity).total_seconds()
                                if time_since_activity > drop_threshold:
                                    logger.warning(f"[DUAL_SESSION] Character {char_name} appears to be dropped")
                                    self._handle_character_drop(char_name)
                        except Exception as e:
                            logger.error(f"[DUAL_SESSION] Error checking window for {char_name}: {e}")
                            self._handle_character_drop(char_name)
                
                self.last_health_check = current_time
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"[DUAL_SESSION] Error in session monitor: {e}")
                time.sleep(check_interval)
    
    def _handle_character_drop(self, char_name: str) -> None:
        """Handle dropped character detection."""
        session = self.character_sessions.get(char_name)
        if not session:
            return
        
        logger.warning(f"[DUAL_SESSION] Character {char_name} dropped - attempting recovery")
        
        # Try to reconnect if auto_reconnect is enabled
        if self.config.config.get("session_monitor", {}).get("auto_reconnect", True):
            self._attempt_reconnect(char_name)
        
        # Send Discord alert
        self._send_discord_alert(f"Character {char_name} dropped from session")
    
    def _attempt_reconnect(self, char_name: str) -> None:
        """Attempt to reconnect dropped character."""
        try:
            session = self.character_sessions.get(char_name)
            if not session:
                return
            
            # Try to find the window again
            windows = pygetwindow.getWindowsWithTitle(session.window_title)
            if windows:
                session.window_handle = windows[0]
                session.is_active = True
                session.last_activity = datetime.now()
                logger.info(f"[DUAL_SESSION] Successfully reconnected {char_name}")
            else:
                logger.error(f"[DUAL_SESSION] Could not find window for {char_name}")
                
        except Exception as e:
            logger.error(f"[DUAL_SESSION] Failed to reconnect {char_name}: {e}")
    
    def _start_discord_relay(self) -> None:
        """Start Discord relay thread."""
        discord_config = self.config.config.get("shared_discord_channel", {})
        if not discord_config.get("enabled", False):
            return
        
        self.discord_relay_thread = threading.Thread(
            target=self._discord_relay_loop,
            daemon=True
        )
        self.discord_relay_thread.start()
        logger.info("[DUAL_SESSION] Discord relay started")
    
    def _discord_relay_loop(self) -> None:
        """Handle Discord relay for dual characters."""
        discord_config = self.config.config.get("shared_discord_channel", {})
        tag_format = discord_config.get("tag_format", "[{character}] {message}")
        
        while self.is_running:
            try:
                # Process any pending Discord messages
                if self.shared_data and self.shared_data.discord_messages:
                    for message in self.shared_data.discord_messages:
                        formatted_message = tag_format.format(
                            character=message.get("character", "Unknown"),
                            message=message.get("message", "")
                        )
                        # Here you would send to Discord - placeholder for now
                        logger.info(f"[DISCORD] {formatted_message}")
                    
                    self.shared_data.discord_messages.clear()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"[DUAL_SESSION] Error in Discord relay: {e}")
                time.sleep(5)
    
    def _send_discord_alert(self, message: str) -> None:
        """Send alert to Discord channel."""
        if not self.shared_data:
            return
        
        alert_message = {
            "character": "System",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.shared_data.discord_messages.append(alert_message)
    
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
            logger.info(f"[DUAL_SESSION] Communication started on port {self.communication_port}")
            
        except Exception as e:
            logger.error(f"[DUAL_SESSION] Failed to start communication: {e}")
    
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
                    logger.error(f"[DUAL_SESSION] Communication error: {e}")
    
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
            logger.error(f"[DUAL_SESSION] Client handling error: {e}")
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
            logger.error(f"[DUAL_SESSION] Message processing error: {e}")
    
    def _update_character_position(self, char_name: str, position_data: Dict[str, Any]) -> None:
        """Update character position."""
        session = self.character_sessions.get(char_name)
        if session:
            session.position = position_data.get("position")
            session.current_planet = position_data.get("planet", "")
            session.current_city = position_data.get("city", "")
            session.last_activity = datetime.now()
            
            # Update shared data
            if self.shared_data:
                if session.role == "leader":
                    self.shared_data.leader_position = session.position
                else:
                    self.shared_data.follower_position = session.position
    
    def _update_character_status(self, char_name: str, status_data: Dict[str, Any]) -> None:
        """Update character status."""
        session = self.character_sessions.get(char_name)
        if session:
            session.status = status_data.get("status", "idle")
            session.last_activity = datetime.now()
    
    def _handle_xp_gain(self, char_name: str, xp_data: Dict[str, Any]) -> None:
        """Handle XP gain from character."""
        session = self.character_sessions.get(char_name)
        if session and self.shared_data:
            xp_amount = xp_data.get("xp", 0)
            session.xp_gained += xp_amount
            self.shared_data.total_xp_gained += xp_amount
            
            # Send Discord alert for significant XP gains
            if xp_amount > 100:
                self._send_discord_alert(f"{char_name} gained {xp_amount} XP")
    
    def _handle_quest_complete(self, char_name: str, quest_data: Dict[str, Any]) -> None:
        """Handle quest completion."""
        session = self.character_sessions.get(char_name)
        if session and self.shared_data:
            session.quests_completed += 1
            self.shared_data.total_quests_completed += 1
            
            quest_name = quest_data.get("quest_name", "Unknown Quest")
            self._send_discord_alert(f"{char_name} completed: {quest_name}")
    
    def _handle_combat_kill(self, char_name: str, combat_data: Dict[str, Any]) -> None:
        """Handle combat kill."""
        session = self.character_sessions.get(char_name)
        if session and self.shared_data:
            session.combat_kills += 1
            self.shared_data.total_combat_kills += 1
            
            target = combat_data.get("target", "Unknown")
            self._send_discord_alert(f"{char_name} defeated: {target}")
    
    def _handle_discord_message(self, char_name: str, message_data: Dict[str, Any]) -> None:
        """Handle Discord message from character."""
        if self.shared_data:
            discord_message = {
                "character": char_name,
                "message": message_data.get("message", ""),
                "timestamp": datetime.now().isoformat()
            }
            self.shared_data.discord_messages.append(discord_message)
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        if not self.shared_data:
            return {"status": "not_started"}
        
        status = {
            "session_id": self.shared_data.session_id,
            "start_time": self.shared_data.start_time.isoformat(),
            "total_xp_gained": self.shared_data.total_xp_gained,
            "total_credits_earned": self.shared_data.total_credits_earned,
            "total_quests_completed": self.shared_data.total_quests_completed,
            "total_combat_kills": self.shared_data.total_combat_kills,
            "characters": {}
        }
        
        for char_name, session in self.character_sessions.items():
            status["characters"][char_name] = {
                "mode": session.mode,
                "role": session.role,
                "is_active": session.is_active,
                "status": session.status,
                "position": session.position,
                "current_planet": session.current_planet,
                "current_city": session.current_city,
                "xp_gained": session.xp_gained,
                "quests_completed": session.quests_completed,
                "combat_kills": session.combat_kills,
                "last_activity": session.last_activity.isoformat() if session.last_activity else None
            }
        
        return status
    
    def stop_dual_session(self) -> None:
        """Stop dual character session."""
        self.is_running = False
        
        # Stop monitoring threads
        if self.session_monitor_thread:
            self.session_monitor_thread.join(timeout=5)
        
        if self.discord_relay_thread:
            self.discord_relay_thread.join(timeout=5)
        
        # Close communication socket
        if self.communication_socket:
            self.communication_socket.close()
        
        # Save session logs
        self._save_session_logs()
        
        logger.info("[DUAL_SESSION] Dual session stopped")
    
    def _save_session_logs(self) -> None:
        """Save session logs for both characters."""
        if not self.shared_data:
            return
        
        try:
            log_dir = Path("logs/dual_sessions")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Save shared session data
            shared_log_path = log_dir / f"shared_{self.shared_data.session_id}.json"
            with open(shared_log_path, 'w') as f:
                json.dump(asdict(self.shared_data), f, indent=2)
            
            # Save individual character logs
            for char_name, session in self.character_sessions.items():
                char_log_path = log_dir / f"{char_name}_{self.shared_data.session_id}.json"
                with open(char_log_path, 'w') as f:
                    json.dump(asdict(session), f, indent=2)
            
            logger.info(f"[DUAL_SESSION] Session logs saved to {log_dir}")
            
        except Exception as e:
            logger.error(f"[DUAL_SESSION] Failed to save session logs: {e}")


# Global instance for easy access
dual_session_manager = DualCharacterSessionManager()


@requires_license
def run_dual_character_mode(
    char1_name: str,
    char1_window: str,
    char2_name: str,
    char2_window: str
) -> Dict[str, Any]:
    """Run dual character mode with the specified characters."""
    try:
        success = dual_session_manager.start_dual_session(
            char1_name, char1_window, char2_name, char2_window
        )
        
        if success:
            return {
                "status": "success",
                "session_id": dual_session_manager.shared_data.session_id if dual_session_manager.shared_data else None,
                "message": "Dual character session started successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to start dual character session"
            }
            
    except Exception as e:
        logger.error(f"[DUAL_SESSION] Error in run_dual_character_mode: {e}")
        return {
            "status": "error",
            "message": f"Exception in dual character mode: {e}"
        }


def get_dual_session_status() -> Dict[str, Any]:
    """Get current dual session status."""
    return dual_session_manager.get_session_status()


def stop_dual_session() -> None:
    """Stop the current dual session."""
    dual_session_manager.stop_dual_session() 