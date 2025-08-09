#!/usr/bin/env python3
"""
Auto Session Detector for MS11
Automatically detects SWG sessions and configures MS11 accordingly.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.window_finder import find_game_window
from core.screenshot import capture_screen
from core.ocr import extract_text_from_screen


class AutoSessionDetector:
    """Automatically detects SWG sessions and configures MS11."""
    
    def __init__(self):
        """Initialize the auto session detector."""
        self.swg_window = None
        self.session_config = {}
        self.detected_modes = []
        
        # SWG window title patterns
        self.swg_patterns = [
            "Star Wars Galaxies",
            "SWG",
            "Galaxies",
            "SWGEmu",
            "SWG Legends",
            "SWG Restoration"
        ]
        
        # Game state detection patterns
        self.state_patterns = {
            "combat": ["Combat", "Attack", "Defend", "Health", "Damage"],
            "quest": ["Quest", "Mission", "Objective", "Task"],
            "crafting": ["Craft", "Resource", "Component", "Assembly"],
            "medic": ["Heal", "Medical", "Treatment", "Buff"],
            "social": ["Entertain", "Dance", "Music", "Performance"],
            "travel": ["Travel", "Transport", "Shuttle", "Waypoint"]
        }
        
    def detect_swg_window(self) -> Optional[gw.Window]:
        """Detect SWG game window."""
        print("🔍 Detecting SWG window...")
        
        # Try to find SWG window by title patterns
        for pattern in self.swg_patterns:
            window = find_game_window(pattern)
            if window:
                print(f"✅ Found SWG window: {window.title}")
                return window
        
        # Try to find by active window
        try:
            active_window = gw.getActiveWindow()
            if active_window and any(pattern.lower() in active_window.title.lower() 
                                   for pattern in self.swg_patterns):
                print(f"✅ Found active SWG window: {active_window.title}")
                return active_window
        except Exception as e:
            print(f"⚠️ Error detecting active window: {e}")
        
        print("❌ No SWG window detected")
        return None
    
    def detect_game_state(self, window: gw.Window) -> Dict[str, Any]:
        """Detect current game state from screen."""
        print("🔍 Analyzing game state...")
        
        try:
            # Capture screen
            screenshot = capture_screen()
            
            # Extract text from screen
            screen_text = extract_text_from_screen(screenshot)
            
            # Analyze text for game state
            detected_states = {}
            
            for state, keywords in self.state_patterns.items():
                matches = sum(1 for keyword in keywords 
                            if keyword.lower() in screen_text.lower())
                if matches > 0:
                    detected_states[state] = matches
            
            # Determine primary state
            if detected_states:
                primary_state = max(detected_states.items(), key=lambda x: x[1])[0]
                print(f"✅ Detected game state: {primary_state}")
                return {
                    "primary_state": primary_state,
                    "detected_states": detected_states,
                    "confidence": len(detected_states) / len(self.state_patterns)
                }
            else:
                print("⚠️ No specific game state detected")
                return {"primary_state": "unknown", "detected_states": {}, "confidence": 0.0}
                
        except Exception as e:
            print(f"❌ Error detecting game state: {e}")
            return {"primary_state": "error", "detected_states": {}, "confidence": 0.0}
    
    def auto_configure_profile(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-configure profile based on detected game state."""
        print("🔧 Auto-configuring profile...")
        
        primary_state = game_state.get("primary_state", "unknown")
        
        # Map game states to MS11 modes
        mode_mapping = {
            "combat": "combat",
            "quest": "quest", 
            "crafting": "crafting",
            "medic": "medic",
            "social": "entertainer",
            "travel": "quest"  # Default to quest for travel
        }
        
        recommended_mode = mode_mapping.get(primary_state, "quest")
        
        # Create auto-configured profile
        auto_profile = {
            "character_name": "Auto-Detected",
            "mode": recommended_mode,
            "auto_train": True,
            "enable_logging": True,
            "log_level": "INFO",
            "support_target": "self",
            "detected_state": primary_state,
            "confidence": game_state.get("confidence", 0.0),
            "auto_configured": True
        }
        
        print(f"✅ Auto-configured profile for {primary_state} mode")
        return auto_profile
    
    def save_auto_profile(self, profile: Dict[str, Any]) -> str:
        """Save auto-configured profile."""
        profiles_dir = Path("profiles/runtime")
        profiles_dir.mkdir(parents=True, exist_ok=True)
        
        profile_name = f"auto_{int(time.time())}"
        profile_path = profiles_dir / f"{profile_name}.json"
        
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2)
        
        print(f"Saved auto-profile: {profile_name}")
        return profile_name
    
    def start_auto_session(self, profile_name: str) -> bool:
        """Start MS11 with auto-detected configuration."""
        print("Starting auto-detected session...")
        
        try:
            # Set Python path
            env = os.environ.copy()
            env['PYTHONPATH'] = f".;{env.get('PYTHONPATH', '')}"
            
            # Start MS11 with auto-profile
            cmd = [
                sys.executable, "src/main.py",
                "--mode", "auto",
                "--profile", profile_name
            ]
            
            print(f"Running: {' '.join(cmd)}")
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("Auto session started successfully!")
            return True
            
        except Exception as e:
            print(f"Error starting auto session: {e}")
            return False
    
    def run_auto_detection(self) -> Optional[str]:
        """Run complete auto-detection process."""
        print("MS11 Auto Session Detector")
        print("=" * 40)
        
        # Step 1: Detect SWG window
        swg_window = self.detect_swg_window()
        if not swg_window:
            print("Please start SWG and try again")
            return None
        
        # Step 2: Detect game state
        game_state = self.detect_game_state(swg_window)
        if game_state.get("primary_state") == "error":
            print("Error detecting game state")
            return None
        
        # Step 3: Auto-configure profile
        auto_profile = self.auto_configure_profile(game_state)
        
        # Step 4: Save profile
        profile_name = self.save_auto_profile(auto_profile)
        
        # Step 5: Start session
        if self.start_auto_session(profile_name):
            return profile_name
        else:
            return None


def main():
    """Main entry point for auto session detection."""
    detector = AutoSessionDetector()
    
    print("Auto Session Detection")
    print("This will automatically detect your SWG session and configure MS11.")
    print("Make sure SWG is running and visible on screen.")
    print()
    
    input("Press Enter to start auto-detection...")
    
    profile_name = detector.run_auto_detection()
    
    if profile_name:
        print(f"\nAuto session started with profile: {profile_name}")
        print("MS11 is now running with auto-detected settings!")
    else:
        print("\nAuto session detection failed")
        print("Please check that SWG is running and try again.")


if __name__ == "__main__":
    main()
