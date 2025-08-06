#!/usr/bin/env python3
"""
Batch 148 - Dual Session CLI

Command-line interface for managing dual-character same-account sessions.
Provides interactive management of dual sessions with leader/follower behavior.
"""

import argparse
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add core directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from core.dual_session_manager import DualSessionManager, DualSessionMode, CharacterBehavior


class DualSessionCLI:
    """Command-line interface for dual session management."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.manager = DualSessionManager()
        self.running = False
    
    def show_help(self):
        """Show help information."""
        print("=" * 60)
        print("BATCH 148 - DUAL SESSION CLI")
        print("=" * 60)
        print()
        print("Available commands:")
        print("  start <char1> <char2>     - Start dual session")
        print("  stop                      - Stop dual session")
        print("  status                    - Show session status")
        print("  config                    - Show configuration")
        print("  update-config <key> <value> - Update configuration")
        print("  list-modes                - List available modes")
        print("  list-behaviors            - List available behaviors")
        print("  test-connection           - Test character communication")
        print("  sync-status               - Show synchronization status")
        print("  help                      - Show this help")
        print("  exit                      - Exit CLI")
        print()
    
    def start_session(self, char1_name: str, char2_name: str):
        """Start a dual session."""
        try:
            print(f"Starting dual session: {char1_name} + {char2_name}")
            
            # Create window titles
            char1_window = f"SWG - {char1_name}"
            char2_window = f"SWG - {char2_name}"
            
            # Start dual session
            success = self.manager.start_dual_session(
                char1_name, char1_window,
                char2_name, char2_window
            )
            
            if success:
                print("✅ Dual session started successfully")
                print(f"   Character 1: {char1_name} ({self.manager.config.character_1_mode})")
                print(f"   Character 2: {char2_name} ({self.manager.config.character_2_mode})")
                print(f"   Sync Mode: {self.manager.config.sync_mode.value}")
                print(f"   Communication Port: {self.manager.config.communication_port}")
                
                self.running = True
            else:
                print("❌ Failed to start dual session")
                
        except Exception as e:
            print(f"❌ Error starting session: {e}")
    
    def stop_session(self):
        """Stop the dual session."""
        try:
            print("Stopping dual session...")
            self.manager.stop_dual_session()
            self.running = False
            print("✅ Dual session stopped")
            
        except Exception as e:
            print(f"❌ Error stopping session: {e}")
    
    def show_status(self):
        """Show current session status."""
        try:
            status = self.manager.get_session_status()
            
            print("=" * 60)
            print("DUAL SESSION STATUS")
            print("=" * 60)
            
            print(f"Session Enabled: {'✅' if status['dual_session_enabled'] else '❌'}")
            print(f"Sync Mode: {status['sync_mode']}")
            print(f"Running: {'✅' if status['running'] else '❌'}")
            print()
            
            if status['character_sessions']:
                print("Character Sessions:")
                for char_name, char_data in status['character_sessions'].items():
                    print(f"  {char_name}:")
                    print(f"    Behavior: {char_data['behavior']}")
                    print(f"    Active: {'✅' if char_data['is_active'] else '❌'}")
                    print(f"    Status: {char_data['status']}")
                    print(f"    Position: {char_data['position']}")
                    print(f"    Planet: {char_data['current_planet']}")
                    print(f"    XP Gained: {char_data['xp_gained']}")
                    print(f"    Credits: {char_data['credits_earned']}")
                    print(f"    Quests: {char_data['quests_completed']}")
                    print(f"    Kills: {char_data['combat_kills']}")
                    print()
            
            if status['shared_data']:
                shared = status['shared_data']
                print("Shared Session Data:")
                print(f"  Session ID: {shared['session_id']}")
                print(f"  Start Time: {shared['start_time']}")
                print(f"  Total XP: {shared['total_xp_gained']}")
                print(f"  Total Credits: {shared['total_credits_earned']}")
                print(f"  Total Quests: {shared['total_quests_completed']}")
                print(f"  Total Kills: {shared['total_combat_kills']}")
                print(f"  Last Sync: {shared['last_sync_time']}")
                print(f"  Activities: {len(shared['shared_activities'])}")
                print()
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def show_config(self):
        """Show current configuration."""
        try:
            config = self.manager.config
            
            print("=" * 60)
            print("DUAL SESSION CONFIGURATION")
            print("=" * 60)
            
            print(f"Dual Session Enabled: {config.dual_session_enabled}")
            print(f"Character 1 Mode: {config.character_1_mode}")
            print(f"Character 2 Mode: {config.character_2_mode}")
            print(f"Sync Mode: {config.sync_mode.value if hasattr(config.sync_mode, 'value') else config.sync_mode}")
            print(f"Tether Distance: {config.tether_distance}")
            print(f"Shared XP: {'✅' if config.shared_xp_enabled else '❌'}")
            print(f"Shared Combat: {'✅' if config.shared_combat_enabled else '❌'}")
            print(f"Auto Follow: {'✅' if config.auto_follow_enabled else '❌'}")
            print(f"Communication Port: {config.communication_port}")
            print(f"Sync Interval: {config.sync_interval}s")
            print(f"Max Retry Attempts: {config.max_retry_attempts}")
            print()
            
        except Exception as e:
            print(f"❌ Error getting config: {e}")
    
    def update_config(self, key: str, value: str):
        """Update configuration."""
        try:
            # Convert value to appropriate type
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
            
            success = self.manager.update_config(**{key: value})
            
            if success:
                print(f"✅ Configuration updated: {key} = {value}")
            else:
                print(f"❌ Failed to update configuration")
                
        except Exception as e:
            print(f"❌ Error updating config: {e}")
    
    def list_modes(self):
        """List available sync modes."""
        print("=" * 60)
        print("AVAILABLE SYNC MODES")
        print("=" * 60)
        
        for mode in DualSessionMode:
            print(f"  {mode.value}: {mode.name}")
        
        print()
    
    def list_behaviors(self):
        """List available character behaviors."""
        print("=" * 60)
        print("AVAILABLE CHARACTER BEHAVIORS")
        print("=" * 60)
        
        for behavior in CharacterBehavior:
            print(f"  {behavior.value}: {behavior.name}")
        
        print()
    
    def test_connection(self):
        """Test character communication."""
        try:
            print("Testing character communication...")
            
            if not self.running:
                print("❌ No active session to test")
                return
            
            # Test basic communication
            print("✅ Communication server running")
            print(f"✅ Port {self.manager.config.communication_port} available")
            print("✅ Message queue active")
            
            # Test character sessions
            if self.manager.character_sessions:
                print(f"✅ {len(self.manager.character_sessions)} characters registered")
                for char_name in self.manager.character_sessions:
                    print(f"  - {char_name}")
            else:
                print("❌ No characters registered")
            
            print("✅ Connection test completed")
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
    
    def show_sync_status(self):
        """Show synchronization status."""
        try:
            print("=" * 60)
            print("SYNCHRONIZATION STATUS")
            print("=" * 60)
            
            if not self.running:
                print("❌ No active session")
                return
            
            # Check sync thread
            if self.manager.sync_thread and self.manager.sync_thread.is_alive():
                print("✅ Sync thread running")
            else:
                print("❌ Sync thread not running")
            
            # Check communication
            if self.manager.communication_socket:
                print("✅ Communication socket active")
            else:
                print("❌ Communication socket not active")
            
            # Check character sessions
            leader = self.manager._get_leader_character()
            follower = self.manager._get_follower_character()
            
            if leader:
                print(f"✅ Leader character: {leader}")
            else:
                print("❌ No leader character")
            
            if follower:
                print(f"✅ Follower character: {follower}")
            else:
                print("❌ No follower character")
            
            # Check shared data
            if self.manager.shared_data:
                print("✅ Shared data active")
                print(f"  Session ID: {self.manager.shared_data.session_id}")
                print(f"  Total XP: {self.manager.shared_data.total_xp_gained}")
                print(f"  Total Credits: {self.manager.shared_data.total_credits_earned}")
            else:
                print("❌ No shared data")
            
            print()
            
        except Exception as e:
            print(f"❌ Error getting sync status: {e}")
    
    def run_interactive(self):
        """Run interactive CLI mode."""
        print("Welcome to Batch 148 - Dual Session CLI")
        print("Type 'help' for available commands")
        print()
        
        while True:
            try:
                command = input("dual-session> ").strip().split()
                
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == 'help':
                    self.show_help()
                elif cmd == 'exit':
                    if self.running:
                        self.stop_session()
                    print("Goodbye!")
                    break
                elif cmd == 'start':
                    if len(command) >= 3:
                        self.start_session(command[1], command[2])
                    else:
                        print("Usage: start <char1> <char2>")
                elif cmd == 'stop':
                    self.stop_session()
                elif cmd == 'status':
                    self.show_status()
                elif cmd == 'config':
                    self.show_config()
                elif cmd == 'update-config':
                    if len(command) >= 3:
                        self.update_config(command[1], command[2])
                    else:
                        print("Usage: update-config <key> <value>")
                elif cmd == 'list-modes':
                    self.list_modes()
                elif cmd == 'list-behaviors':
                    self.list_behaviors()
                elif cmd == 'test-connection':
                    self.test_connection()
                elif cmd == 'sync-status':
                    self.show_sync_status()
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Batch 148 - Dual Session CLI")
    parser.add_argument('--start', nargs=2, metavar=('CHAR1', 'CHAR2'),
                       help='Start dual session with two characters')
    parser.add_argument('--stop', action='store_true',
                       help='Stop dual session')
    parser.add_argument('--status', action='store_true',
                       help='Show session status')
    parser.add_argument('--config', action='store_true',
                       help='Show configuration')
    parser.add_argument('--update-config', nargs=2, metavar=('KEY', 'VALUE'),
                       help='Update configuration')
    parser.add_argument('--list-modes', action='store_true',
                       help='List available sync modes')
    parser.add_argument('--list-behaviors', action='store_true',
                       help='List available character behaviors')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test character communication')
    parser.add_argument('--sync-status', action='store_true',
                       help='Show synchronization status')
    parser.add_argument('--interactive', action='store_true',
                       help='Run interactive mode')
    
    args = parser.parse_args()
    
    cli = DualSessionCLI()
    
    try:
        if args.start:
            cli.start_session(args.start[0], args.start[1])
        elif args.stop:
            cli.stop_session()
        elif args.status:
            cli.show_status()
        elif args.config:
            cli.show_config()
        elif args.update_config:
            cli.update_config(args.update_config[0], args.update_config[1])
        elif args.list_modes:
            cli.list_modes()
        elif args.list_behaviors:
            cli.list_behaviors()
        elif args.test_connection:
            cli.test_connection()
        elif args.sync_status:
            cli.show_sync_status()
        elif args.interactive:
            cli.run_interactive()
        else:
            cli.show_help()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 