#!/usr/bin/env python3
"""
MS11 Session Recovery CLI Tool

This module provides the CLI interface for the session recovery system,
including session state management, crash recovery, and auto-save functionality.
"""

import argparse
import sys
import time
from pathlib import Path

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from session_recovery import SessionRecoveryEngine


def main():
    """Main CLI function for session recovery."""
    parser = argparse.ArgumentParser(
        description="MS11 Session Recovery & Continuation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ms11 session-recovery --recover                    # Attempt session recovery
  ms11 session-recovery --save                       # Save current session state
  ms11 session-recovery --stats                      # Show session statistics
  ms11 session-recovery --auto-save                  # Start auto-save mode
  ms11 session-recovery --config config.yaml         # Use custom configuration
  ms11 session-recovery --cleanup                    # Clean up old session states
  ms11 session-recovery --detect-crashes             # Detect and handle crashes
        """
    )
    
    # Main command group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--recover", action="store_true",
                       help="Attempt session recovery")
    group.add_argument("--save", action="store_true",
                       help="Save current session state")
    group.add_argument("--stats", action="store_true",
                       help="Show session statistics")
    group.add_argument("--auto-save", action="store_true",
                       help="Start auto-save mode")
    group.add_argument("--cleanup", action="store_true",
                       help="Clean up old session states")
    group.add_argument("--detect-crashes", action="store_true",
                       help="Detect and handle crashes")
    group.add_argument("--restart", action="store_true",
                       help="Attempt game restart")
    group.add_argument("--relog", action="store_true",
                       help="Attempt game relog")
    
    # Optional arguments
    parser.add_argument("--config", type=str,
                       help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--force", action="store_true",
                       help="Force operation even if recovery is disabled")
    parser.add_argument("--max-age", type=int, default=24,
                       help="Maximum age in hours for cleanup (default: 24)")
    parser.add_argument("--output", type=str,
                       help="Output file for results (JSON format)")
    
    args = parser.parse_args()
    
    # Initialize session recovery engine
    try:
        engine = SessionRecoveryEngine(args.config)
        
        if args.verbose:
            import logging
            engine.logger.setLevel(logging.DEBUG)
        
        # Handle different commands
        if args.recover:
            print("🔄 Session Recovery")
            print("=" * 40)
            
            if not engine.current_state:
                print("❌ No previous session found")
                sys.exit(1)
            
            print(f"📅 Last Session: {engine.current_state.timestamp}")
            print(f"🌍 Location: {engine.current_state.planet}, {engine.current_state.zone}")
            print(f"🎯 Quest: {engine.current_state.current_quest.get('name', 'None') if engine.current_state.current_quest else 'None'}")
            print(f"📊 Level: {engine.current_state.xp_level}")
            print(f"⏱️  Duration: {engine.current_state.session_duration:.1f} seconds")
            print()
            
            if engine.prompt_recovery():
                success = engine.recover_session()
                if success:
                    print("✅ Session recovery completed successfully")
                else:
                    print("❌ Session recovery failed")
                    sys.exit(1)
            else:
                print("⏹️  Recovery cancelled by user")
                sys.exit(1)
        
        elif args.save:
            print("💾 Session State Saving")
            print("=" * 40)
            
            success = engine.save_session_state(force=args.force)
            if success:
                print("✅ Session state saved successfully")
                print(f"📁 File: {engine.state_file}")
                
                if args.output:
                    import json
                    stats = engine.get_session_statistics()
                    with open(args.output, 'w') as f:
                        json.dump(stats, f, indent=2)
                    print(f"📄 Statistics saved to {args.output}")
            else:
                print("❌ Failed to save session state")
                sys.exit(1)
        
        elif args.stats:
            print("📊 Session Statistics")
            print("=" * 40)
            
            stats = engine.get_session_statistics()
            if stats:
                print(f"⏱️  Session Duration: {stats.get('session_duration', 0):.1f} seconds")
                print(f"💥 Crash Count: {stats.get('crash_count', 0)}")
                print(f"💾 Last Save: {stats.get('last_save', 'Unknown')}")
                print(f"🔄 Recovery Enabled: {stats.get('recovery_enabled', False)}")
                print(f"🔄 Auto Restart: {stats.get('auto_restart', False)}")
                print(f"🔄 Auto Relog: {stats.get('auto_relog', False)}")
                print(f"⏰ Save Interval: {stats.get('save_interval', 0)} seconds")
                print(f"📁 State File: {stats.get('state_file', 'Unknown')}")
                
                if args.output:
                    import json
                    with open(args.output, 'w') as f:
                        json.dump(stats, f, indent=2)
                    print(f"\n📄 Statistics saved to {args.output}")
            else:
                print("❌ No session statistics available")
                sys.exit(1)
        
        elif args.auto_save:
            print("⏰ Auto-Save Mode")
            print("=" * 40)
            print(f"💾 Save Interval: {engine.save_interval} seconds")
            print(f"📁 State File: {engine.state_file}")
            print("🔄 Starting auto-save thread...")
            print("⏹️  Press Ctrl+C to stop")
            print()
            
            try:
                engine.start_auto_save()
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️  Stopping auto-save...")
                engine.stop_auto_save()
                print("✅ Auto-save stopped")
        
        elif args.cleanup:
            print("🧹 Session State Cleanup")
            print("=" * 40)
            
            print(f"🗑️  Cleaning up session states older than {args.max_age} hours...")
            engine.cleanup_old_states(max_age_hours=args.max_age)
            print("✅ Cleanup completed")
        
        elif args.detect_crashes:
            print("💥 Crash Detection")
            print("=" * 40)
            
            crashes = engine.detect_crashes()
            if crashes:
                print(f"⚠️  Detected {len(crashes)} crash(es):")
                for i, crash in enumerate(crashes, 1):
                    print(f"   {i}. {crash.error_type}")
                    print(f"      Message: {crash.error_message}")
                    print(f"      Time: {crash.timestamp}")
                
                print("\n🔄 Attempting crash recovery...")
                recovery_success = engine.handle_crash_recovery()
                if recovery_success:
                    print("✅ Crash recovery successful")
                else:
                    print("❌ Crash recovery failed")
                    sys.exit(1)
            else:
                print("✅ No crashes detected")
        
        elif args.restart:
            print("🔄 Game Restart")
            print("=" * 40)
            
            print("🔄 Attempting game restart...")
            success = engine.attempt_restart()
            if success:
                print("✅ Game restart completed")
            else:
                print("❌ Game restart failed")
                sys.exit(1)
        
        elif args.relog:
            print("🔄 Game Relog")
            print("=" * 40)
            
            print("🔄 Attempting game relog...")
            success = engine.attempt_relog()
            if success:
                print("✅ Game relog completed")
            else:
                print("❌ Game relog failed")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 