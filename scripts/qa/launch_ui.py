#!/usr/bin/env python3
"""
MS11 UI Launcher
Launches both the configuration automation UI and bot attachment monitor.
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    
    # Install UI requirements
    ui_req = Path(__file__).parent / "requirements_ui.txt"
    if ui_req.exists():
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(ui_req)], 
                         check=True, capture_output=True)
            print("✅ UI requirements installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install UI requirements: {e}")
            return False
    
    # Install monitor requirements
    monitor_req = Path(__file__).parent / "requirements_monitor.txt"
    if monitor_req.exists():
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(monitor_req)], 
                         check=True, capture_output=True)
            print("✅ Monitor requirements installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install monitor requirements: {e}")
            return False
    
    return True

def start_configuration_ui():
    """Start the configuration automation UI."""
    try:
        ui_script = Path(__file__).parent / "config_ui.py"
        if ui_script.exists():
            print("🚀 Starting Configuration Automation UI...")
            subprocess.Popen([sys.executable, str(ui_script)], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a bit then open browser
            time.sleep(3)
            webbrowser.open('http://localhost:5000')
            return True
        else:
            print("❌ Configuration UI script not found")
            return False
    except Exception as e:
        print(f"❌ Failed to start configuration UI: {e}")
        return False

def start_bot_monitor():
    """Start the bot attachment monitor."""
    try:
        monitor_script = Path(__file__).parent / "bot_attachment_monitor.py"
        if monitor_script.exists():
            print("🔍 Starting Bot Attachment Monitor...")
            subprocess.Popen([sys.executable, str(monitor_script)], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        else:
            print("❌ Bot monitor script not found")
            return False
    except Exception as e:
        print(f"❌ Failed to start bot monitor: {e}")
        return False

def main():
    """Main launcher function."""
    print("🎮 MS11 UI Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path(__file__).parent.exists():
        print("❌ Launcher script not in expected location")
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Please install manually:")
        print("   pip install -r scripts/qa/requirements_ui.txt")
        print("   pip install -r scripts/qa/requirements_monitor.txt")
        return
    
    print("\n🚀 Launching MS11 UIs...")
    
    # Start configuration UI
    ui_started = start_configuration_ui()
    
    # Start bot monitor
    monitor_started = start_bot_monitor()
    
    if ui_started and monitor_started:
        print("\n✅ Both UIs launched successfully!")
        print("\n📱 Configuration UI: http://localhost:5000")
        print("🔍 Bot Monitor: Check for the Tkinter window")
        print("\n💡 Press Ctrl+C to stop the launcher")
        
        try:
            # Keep launcher running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping launcher...")
    else:
        print("\n❌ Some UIs failed to start")
        if not ui_started:
            print("   - Configuration UI failed")
        if not monitor_started:
            print("   - Bot Monitor failed")

if __name__ == '__main__':
    main()
