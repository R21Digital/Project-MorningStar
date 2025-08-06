#!/usr/bin/env python3
"""
Batch 137 - Multi-Character CLI Tool

Command-line interface for managing multi-character sessions.
Allows starting, stopping, and monitoring multiple character instances.
"""

import argparse
import json
import sys
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from core.multi_character_manager import (
    multi_character_manager,
    CharacterMode,
    CharacterRole
)
from android_ms11.modes.enhanced_support_mode import EnhancedSupportMode
from utils.license_hooks import requires_license
from profession_logic.utils.logger import logger


class MultiCharacterCLI:
    """CLI tool for managing multi-character sessions."""
    
    def __init__(self):
        """Initialize the CLI tool."""
        self.config = self._load_config()
        self.support_instances: Dict[str, EnhancedSupportMode] = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration."""
        try:
            with open("config/multi_character_config.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Multi-character config not found")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid config format: {e}")
            return {}
    
    def start_session(self, main_char: str, support_char: str, 
                     support_type: str = "medic") -> bool:
        """Start a multi-character session.
        
        Parameters
        ----------
        main_char : str
            Name of the main character
        support_char : str
            Name of the support character
        support_type : str
            Type of support (medic, dancer, entertainer)
            
        Returns
        -------
        bool
            True if session started successfully
        """
        try:
            # Start communication server
            if not multi_character_manager.start_communication_server():
                logger.error("Failed to start communication server")
                return False
            
            # Register main character
            main_window = f"SWG - {main_char}"
            if not multi_character_manager.register_character(
                character_name=main_char,
                window_title=main_window,
                mode=CharacterMode.MAIN,
                role=CharacterRole.LEADER
            ):
                logger.error(f"Failed to register main character: {main_char}")
                return False
            
            # Register support character
            support_window = f"SWG - {support_char}"
            if not multi_character_manager.register_character(
                character_name=support_char,
                window_title=support_window,
                mode=CharacterMode.SUPPORT,
                role=CharacterRole.FOLLOWER
            ):
                logger.error(f"Failed to register support character: {support_char}")
                return False
            
            # Arrange windows
            window_titles = [main_window, support_window]
            multi_character_manager.window_manager.arrange_windows(window_titles)
            
            # Start enhanced support mode
            support = EnhancedSupportMode(support_char, support_type)
            if support.start_support():
                self.support_instances[support_char] = support
                logger.info(f"Started {support_type} support for {support_char}")
            else:
                logger.error(f"Failed to start support for {support_char}")
                return False
            
            # Activate main character
            if not multi_character_manager.activate_character(main_char):
                logger.error(f"Failed to activate main character: {main_char}")
                return False
            
            logger.info(f"Multi-character session started: {main_char} (main) + {support_char} ({support_type})")
            return True
            
        except Exception as e:
            logger.error(f"Error starting multi-character session: {e}")
            return False
    
    def stop_session(self) -> bool:
        """Stop the multi-character session."""
        try:
            # Stop support instances
            for char_name, support in self.support_instances.items():
                support.stop_support()
                logger.info(f"Stopped support for {char_name}")
            
            self.support_instances.clear()
            
            # Cleanup multi-character manager
            multi_character_manager.cleanup()
            
            logger.info("Multi-character session stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping multi-character session: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all characters."""
        status = {
            "characters": multi_character_manager.get_all_status(),
            "support_instances": {}
        }
        
        for char_name, support in self.support_instances.items():
            status["support_instances"][char_name] = support.get_support_stats()
        
        return status
    
    def print_status(self) -> None:
        """Print status of all characters."""
        status = self.get_status()
        
        print("\n" + "="*60)
        print("MULTI-CHARACTER SESSION STATUS")
        print("="*60)
        
        # Character status
        print("\n📋 CHARACTER STATUS:")
        for char_name, char_status in status["characters"].items():
            if char_status:
                mode_icon = "🎮" if char_status["mode"] == "main" else "🛡️"
                role_icon = "👑" if char_status["role"] == "leader" else "👥"
                active_icon = "✅" if char_status["is_active"] else "❌"
                
                print(f"  {mode_icon} {char_name} ({char_status['mode']}) {role_icon} {active_icon}")
                print(f"    Location: {char_status['planet']} - {char_status['city']}")
                print(f"    Status: {char_status['status']}")
                print(f"    Last Activity: {char_status['last_activity']}")
        
        # Support instances
        if status["support_instances"]:
            print("\n🛡️ SUPPORT INSTANCES:")
            for char_name, support_stats in status["support_instances"].items():
                running_icon = "✅" if support_stats["is_running"] else "❌"
                print(f"  {running_icon} {char_name} ({support_stats['support_type']})")
                print(f"    Buffs Applied: {support_stats['buffs_applied']}")
                print(f"    Heals Applied: {support_stats['heals_applied']}")
        
        # Communication status
        print(f"\n📡 COMMUNICATION:")
        comm_enabled = multi_character_manager.communication_socket is not None
        comm_icon = "✅" if comm_enabled else "❌"
        print(f"  {comm_icon} Server: {'Running' if comm_enabled else 'Stopped'}")
        print(f"  📨 Messages in queue: {len(multi_character_manager.message_queue)}")
        
        print("\n" + "="*60)
    
    def send_command(self, target_char: str, command: str, data: Dict[str, Any] = None) -> bool:
        """Send a command to a character.
        
        Parameters
        ----------
        target_char : str
            Target character name
        command : str
            Command to send
        data : Dict[str, Any]
            Additional command data
            
        Returns
        -------
        bool
            True if command sent successfully
        """
        if data is None:
            data = {}
        
        data["command"] = command
        multi_character_manager.send_message(
            sender="cli",
            message_type="command",
            data=data,
            priority="high"
        )
        
        logger.info(f"Sent command '{command}' to {target_char}")
        return True
    
    def switch_mode(self, character_name: str, new_mode: str) -> bool:
        """Switch a character's mode.
        
        Parameters
        ----------
        character_name : str
            Character name
        new_mode : str
            New mode (main/support)
            
        Returns
        -------
        bool
            True if mode switched successfully
        """
        try:
            if new_mode.lower() == "main":
                mode = CharacterMode.MAIN
            elif new_mode.lower() == "support":
                mode = CharacterMode.SUPPORT
            else:
                logger.error(f"Invalid mode: {new_mode}")
                return False
            
            if multi_character_manager.switch_character_mode(character_name, mode):
                logger.info(f"Switched {character_name} to {new_mode} mode")
                return True
            else:
                logger.error(f"Failed to switch {character_name} to {new_mode} mode")
                return False
                
        except Exception as e:
            logger.error(f"Error switching mode: {e}")
            return False
    
    def monitor_session(self, duration: int = 3600) -> None:
        """Monitor the session for a specified duration.
        
        Parameters
        ----------
        duration : int
            Duration to monitor in seconds
        """
        print(f"Monitoring session for {duration} seconds...")
        print("Press Ctrl+C to stop monitoring")
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                self.print_status()
                time.sleep(30)  # Update every 30 seconds
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
    
    def run_interactive(self) -> None:
        """Run interactive CLI mode."""
        print("Multi-Character CLI - Interactive Mode")
        print("Type 'help' for available commands")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "help":
                    self._print_help()
                elif command == "status":
                    self.print_status()
                elif command == "quit" or command == "exit":
                    break
                elif command.startswith("start"):
                    self._handle_start_command(command)
                elif command.startswith("stop"):
                    self.stop_session()
                elif command.startswith("switch"):
                    self._handle_switch_command(command)
                elif command.startswith("command"):
                    self._handle_command_command(command)
                elif command.startswith("monitor"):
                    self._handle_monitor_command(command)
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
    
    def _print_help(self) -> None:
        """Print help information."""
        print("\nAvailable Commands:")
        print("  start <main_char> <support_char> [support_type] - Start session")
        print("  stop - Stop session")
        print("  status - Show status")
        print("  switch <char> <mode> - Switch character mode")
        print("  command <target> <cmd> - Send command to character")
        print("  monitor [duration] - Monitor session")
        print("  quit/exit - Exit")
    
    def _handle_start_command(self, command: str) -> None:
        """Handle start command."""
        parts = command.split()
        if len(parts) < 3:
            print("Usage: start <main_char> <support_char> [support_type]")
            return
        
        main_char = parts[1]
        support_char = parts[2]
        support_type = parts[3] if len(parts) > 3 else "medic"
        
        if self.start_session(main_char, support_char, support_type):
            print(f"Session started: {main_char} + {support_char} ({support_type})")
        else:
            print("Failed to start session")
    
    def _handle_switch_command(self, command: str) -> None:
        """Handle switch command."""
        parts = command.split()
        if len(parts) != 3:
            print("Usage: switch <char> <mode>")
            return
        
        char_name = parts[1]
        new_mode = parts[2]
        
        if self.switch_mode(char_name, new_mode):
            print(f"Switched {char_name} to {new_mode} mode")
        else:
            print(f"Failed to switch {char_name} to {new_mode} mode")
    
    def _handle_command_command(self, command: str) -> None:
        """Handle command command."""
        parts = command.split()
        if len(parts) < 3:
            print("Usage: command <target> <cmd>")
            return
        
        target = parts[1]
        cmd = parts[2]
        
        if self.send_command(target, cmd):
            print(f"Command '{cmd}' sent to {target}")
        else:
            print(f"Failed to send command to {target}")
    
    def _handle_monitor_command(self, command: str) -> None:
        """Handle monitor command."""
        parts = command.split()
        duration = int(parts[1]) if len(parts) > 1 else 3600
        
        self.monitor_session(duration)


@requires_license
def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Multi-Character CLI Tool")
    parser.add_argument("--start", nargs=2, metavar=("MAIN", "SUPPORT"), 
                       help="Start session with main and support characters")
    parser.add_argument("--support-type", default="medic", 
                       choices=["medic", "dancer", "entertainer", "medic_mobile"],
                       help="Support character type")
    parser.add_argument("--stop", action="store_true", help="Stop session")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--monitor", type=int, metavar="SECONDS", 
                       help="Monitor session for specified seconds")
    parser.add_argument("--interactive", action="store_true", help="Run interactive mode")
    
    args = parser.parse_args()
    
    cli = MultiCharacterCLI()
    
    try:
        if args.start:
            main_char, support_char = args.start
            if cli.start_session(main_char, support_char, args.support_type):
                print(f"Session started: {main_char} + {support_char} ({args.support_type})")
            else:
                print("Failed to start session")
                sys.exit(1)
        
        elif args.stop:
            if cli.stop_session():
                print("Session stopped")
            else:
                print("Failed to stop session")
                sys.exit(1)
        
        elif args.status:
            cli.print_status()
        
        elif args.monitor:
            cli.monitor_session(args.monitor)
        
        elif args.interactive:
            cli.run_interactive()
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        cli.stop_session()
    except Exception as e:
        logger.error(f"CLI error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 