#!/usr/bin/env python3
"""Setup script for Android MS11 project."""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def check_system_dependencies():
    """Check for system-level dependencies."""
    print("🔍 Checking system dependencies...")
    
    # Check for Tesseract OCR
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is available")
    except Exception as e:
        print("⚠️  Tesseract OCR not found or not working properly")
        print("   Please install Tesseract OCR:")
        print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Linux: sudo apt-get install tesseract-ocr")
        print("   macOS: brew install tesseract")
    
    # Check for OpenCV
    try:
        import cv2
        print("✅ OpenCV is available")
    except ImportError:
        print("❌ OpenCV not installed")
    
    # Check for PyAutoGUI
    try:
        import pyautogui
        print("✅ PyAutoGUI is available")
    except ImportError:
        print("❌ PyAutoGUI not installed")


def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = [
        "logs",
        "profiles/runtime",
        "config",
        "data",
        "screenshots"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created {directory}/")


def create_default_configs():
    """Create default configuration files if they don't exist."""
    print("⚙️  Setting up configuration files...")
    
    # Default config.json
    config_path = Path("config/config.json")
    if not config_path.exists():
        default_config = {
            "character_name": "Default",
            "default_mode": "medic",
            "enable_discord_relay": False
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        print("   ✅ Created config/config.json")
    
    # Default session config
    session_config_path = Path("config/session_config.json")
    if not session_config_path.exists():
        default_session = {
            "auto_train": False,
            "enable_logging": True,
            "log_level": "INFO"
        }
        with open(session_config_path, "w") as f:
            json.dump(default_session, f, indent=2)
        print("   ✅ Created config/session_config.json")


def run_tests():
    """Run basic tests to verify installation."""
    print("🧪 Running basic tests...")
    try:
        # Test core imports
        import core.session_manager
        print("   ✅ Core modules import successfully")
        
        # Test vision modules
        import src.vision.ocr
        print("   ✅ Vision modules import successfully")
        
        # Test basic functionality
        from src.credit_tracker import CreditTracker
        tracker = CreditTracker()
        print("   ✅ Credit tracker initializes successfully")
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 Android MS11 Setup")
    print("=" * 40)
    
    check_python_version()
    install_dependencies()
    check_system_dependencies()
    create_directories()
    create_default_configs()
    
    if run_tests():
        print("\n✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Configure your character profile in profiles/runtime/")
        print("   2. Set up Discord bot (optional) in config/discord_config.json")
        print("   3. Run: python src/main.py --profile your_profile_name")
    else:
        print("\n❌ Setup completed with errors. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 