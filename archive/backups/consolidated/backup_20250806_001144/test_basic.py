#!/usr/bin/env python3
"""Basic functionality test for Android MS11."""

import json
import os
from pathlib import Path

def test_core_imports():
    """Test that core modules can be imported."""
    print("🧪 Testing core imports...")
    
    try:
        from core.session_manager import SessionManager
        print("   ✅ SessionManager imported")
        
        from src.credit_tracker import CreditTracker
        print("   ✅ CreditTracker imported")
        
        from core import profile_loader
        print("   ✅ Profile loader imported")
        
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_profile_loading():
    """Test profile loading functionality."""
    print("📋 Testing profile loading...")
    
    try:
        profile_path = "profiles/runtime/default.json"
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
            print(f"   ✅ Profile loaded: {profile.get('character_name', 'Unknown')}")
            return True
        else:
            print("   ❌ Profile file not found")
            return False
    except Exception as e:
        print(f"   ❌ Profile loading failed: {e}")
        return False

def test_session_creation():
    """Test session manager creation."""
    print("🔄 Testing session creation...")
    
    try:
        from core.session_manager import SessionManager
        session = SessionManager(mode="test")
        print(f"   ✅ Session created: {session.session_id}")
        print(f"   ✅ Session mode: {session.mode}")
        return True
    except Exception as e:
        print(f"   ❌ Session creation failed: {e}")
        return False

def test_credit_tracker():
    """Test credit tracker functionality."""
    print("💰 Testing credit tracker...")
    
    try:
        from src.credit_tracker import CreditTracker
        tracker = CreditTracker("test_session")
        tracker.set_start_credits(1000)
        print(f"   ✅ Credit tracker initialized")
        print(f"   ✅ Start credits: {tracker.start_credits}")
        return True
    except Exception as e:
        print(f"   ❌ Credit tracker failed: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist."""
    print("📁 Testing directory structure...")
    
    required_dirs = [
        "logs",
        "profiles/runtime",
        "config",
        "data",
        "screenshots"
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/ exists")
        else:
            print(f"   ❌ {directory}/ missing")
            all_exist = False
    
    return all_exist

def test_config_files():
    """Test configuration files."""
    print("⚙️  Testing configuration files...")
    
    config_files = [
        "config/config.json",
        "config/discord_config.json"
    ]
    
    all_exist = True
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   ✅ {config_file} exists")
        else:
            print(f"   ❌ {config_file} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("🚀 Android MS11 Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_core_imports,
        test_profile_loading,
        test_session_creation,
        test_credit_tracker,
        test_directory_structure,
        test_config_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The system is ready to use.")
        print("\n📋 Next steps:")
        print("   1. Install Tesseract OCR for full OCR functionality")
        print("   2. Configure your character profile in profiles/runtime/")
        print("   3. Set up Discord bot (optional) in config/discord_config.json")
        print("   4. Run: python src/main.py --profile your_profile_name")
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 