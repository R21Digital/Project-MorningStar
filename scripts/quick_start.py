#!/usr/bin/env python3
"""
Quick Start Script for MS11
This script helps you get MS11 running quickly with proper configuration.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'pytesseract', 'cv2', 'pyautogui', 'numpy', 'PIL'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    print("\n🔍 Checking Tesseract OCR...")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract {version} found")
        return True
    except Exception as e:
        print(f"❌ Tesseract not found: {e}")
        print("Please install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    directories = ['logs', 'data', 'profiles/runtime', 'config']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")

def create_default_config():
    """Create default configuration if it doesn't exist."""
    config_path = Path("config/config.json")
    if not config_path.exists():
        print("\n⚙️ Creating default config...")
        config = {
            "character_name": "YourCharacterName",
            "default_mode": "medic",
            "enable_discord_relay": False,
            "session": {
                "idle_timeout": 300,
                "max_duration": 14400,
                "auto_resume": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/ms11.log"
            },
            "safety": {
                "fatigue_threshold": 75,
                "health_threshold": 50,
                "action_threshold": 25
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print("✅ Default config created")

def create_character_profile():
    """Create character profile if it doesn't exist."""
    profile_path = Path("profiles/runtime/your_character.json")
    if not profile_path.exists():
        print("\n👤 Creating character profile...")
        profile = {
            "name": "YourCharacterName",
            "character_name": "YourCharacterName",
            "default_mode": "medic",
            "skip_modes": [],
            "farming_targets": ["auto"],
            "skill_build": "marksman_rifleman",
            "support_target": "auto",
            "preferred_trainers": {
                "combat": "auto",
                "crafting": "auto",
                "entertainer": "auto"
            },
            "description": "Your character profile for MS11",
            "version": "1.0.0",
            "settings": {
                "scan_interval": 60,
                "idle_scan_interval": 300,
                "travel_scan_interval": 30,
                "ocr_confidence_threshold": 50.0,
                "privacy_enabled": True
            },
            "modes": {
                "quest": {
                    "enabled": True,
                    "priority": 1,
                    "settings": {
                        "auto_accept": True,
                        "auto_complete": True,
                        "quest_types": ["story", "daily", "repeatable"]
                    }
                },
                "combat": {
                    "enabled": True,
                    "priority": 2,
                    "settings": {
                        "combat_style": "defensive",
                        "health_threshold": 50,
                        "action_threshold": 25
                    }
                },
                "medic": {
                    "enabled": True,
                    "priority": 3,
                    "settings": {
                        "heal_threshold": 75,
                        "buff_interval": 300
                    }
                }
            },
            "paths": {
                "logs": "logs/ms11.log",
                "data": "data/ms11.db",
                "cache": "data/cache"
            }
        }
        
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=4)
        print("✅ Character profile created")

def main():
    """Main quick start function."""
    print("🚀 MS11 Quick Start")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check Tesseract
    if not check_tesseract():
        return False
    
    # Create directories
    create_directories()
    
    # Create default config
    create_default_config()
    
    # Create character profile
    create_character_profile()
    
    print("\n✅ Quick start completed!")
    print("\n📋 Next steps:")
    print("1. Edit config/config.json with your character name")
    print("2. Edit profiles/runtime/your_character.json with your character details")
    print("3. Start SWG and position your character")
    print("4. Run: python src/main.py --profile your_character --mode medic --max_loops 1")
    print("5. Monitor logs/ms11.log for any issues")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
