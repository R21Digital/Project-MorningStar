#!/usr/bin/env python3
"""Simplified main entry point for Android MS11."""

import argparse
import json
import os
import sys
from typing import Dict, Any

def load_profile(profile_name: str) -> Dict[str, Any]:
    """Load a character profile."""
    profile_path = f"profiles/runtime/{profile_name}.json"
    if not os.path.exists(profile_path):
        print(f"[ERROR] Profile not found: {profile_path}")
        sys.exit(1)
    
    with open(profile_path, 'r') as f:
        return json.load(f)

def load_config() -> Dict[str, Any]:
    """Load main configuration."""
    config_path = "config/config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {"default_mode": "medic", "enable_discord_relay": False}

def run_session(profile: Dict[str, Any], mode: str, max_loops: int = 1):
    """Run a simple session."""
    print(f"🚀 Starting Android MS11 Session")
    print(f"📋 Character: {profile.get('character_name', 'Unknown')}")
    print(f"🎮 Mode: {mode}")
    print(f"🔄 Max Loops: {max_loops}")
    
    # Import core components
    try:
        from core.session_manager import SessionManager
        from src.credit_tracker import CreditTracker
        
        # Create session
        session = SessionManager(mode=mode)
        print(f"✅ Session created: {session.session_id}")
        
        # Initialize credit tracker
        tracker = CreditTracker(session.session_id)
        tracker.set_start_credits(1000)
        print(f"💰 Credit tracker initialized")
        
        # Simulate some activity
        for i in range(max_loops):
            print(f"\n🔄 Loop {i+1}/{max_loops}")
            
            # Simulate mode execution
            if mode == "medic":
                print("🏥 Running medic mode...")
                session.add_action("Healing nearby players")
            elif mode == "quest":
                print("📜 Running quest mode...")
                session.add_action("Completing quest objectives")
            elif mode == "farming":
                print("🌾 Running farming mode...")
                session.add_action("Farming resources")
            else:
                print(f"⚙️ Running {mode} mode...")
                session.add_action(f"Executing {mode} actions")
            
            # Update credits
            current_credits = 1000 + (i * 50)
            tracker.current_credits = current_credits
            print(f"💰 Credits: {current_credits:,}")
        
        # End session
        session.set_end_credits(current_credits)
        session.end_session()
        
        print(f"\n✅ Session completed successfully!")
        print(f"📊 Credits earned: {current_credits - 1000:,}")
        print(f"⏱️ Duration: {session.duration:.2f} minutes")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: python setup.py")
        return False
    except Exception as e:
        print(f"❌ Error during session: {e}")
        return False
    
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Android MS11 Simplified Demo")
    parser.add_argument("--profile", type=str, default="default", help="Profile name")
    parser.add_argument("--mode", type=str, help="Override mode")
    parser.add_argument("--max_loops", type=int, default=1, help="Number of loops")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    profile = load_profile(args.profile)
    
    # Determine mode
    mode = args.mode or profile.get("mode") or config.get("default_mode", "medic")
    
    print("🎯 Android MS11 - Simplified Demo")
    print("=" * 40)
    
    success = run_session(profile, mode, args.max_loops)
    
    if success:
        print("\n🎉 Demo completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Install Tesseract OCR for full OCR functionality")
        print("   2. Configure your character profile in profiles/runtime/")
        print("   3. Set up Discord bot (optional) in config/discord_config.json")
        print("   4. Run: python src/main.py --profile your_profile_name")
    else:
        print("\n❌ Demo failed. Check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 