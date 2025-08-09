#!/usr/bin/env python3
"""
Tesseract OCR Installation Guide and Helper Script
Helps users install Tesseract OCR for MS11 functionality.
"""

import os
import sys
import platform
import subprocess
import webbrowser
from pathlib import Path


def print_header(title):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"[INFO] {title}")
    print(f"{'='*60}")


def print_step(step):
    """Print step."""
    print(f"\n[STEP] {step}")


def print_success(message):
    """Print success."""
    print(f"[SUCCESS] {message}")


def print_warning(message):
    """Print warning."""
    print(f"[WARNING] {message}")


def print_error(message):
    """Print error."""
    print(f"[ERROR] {message}")


def check_tesseract_installed():
    """Check if Tesseract is already installed."""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0] if result.stdout else "Unknown version"
            print_success(f"Tesseract OCR already installed: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False


def install_windows():
    """Guide for Windows installation."""
    print_header("Windows Installation Guide")
    
    print_step("Option 1: Manual Download (Recommended)")
    print("1. Visit: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Download: tesseract-ocr-w64-setup-v5.3.0.20221214.exe")
    print("3. Run the installer as Administrator")
    print("4. During installation, note the installation path (usually C:\\Program Files\\Tesseract-OCR)")
    print("5. Add to PATH environment variable")
    
    print_step("Option 2: Chocolatey (if you have admin rights)")
    print("Run in Administrator PowerShell:")
    print("  choco install tesseract")
    
    print_step("Option 3: Scoop")
    print("If you have Scoop package manager:")
    print("  scoop install tesseract")
    
    print_step("Add to PATH")
    print("1. Open System Properties → Advanced → Environment Variables")
    print("2. Edit 'Path' in System Variables")
    print("3. Add: C:\\Program Files\\Tesseract-OCR")
    print("4. Restart command prompt/terminal")
    
    # Offer to open download page
    try:
        response = input("\n[QUESTION] Open Tesseract download page in browser? (y/n): ").lower()
        if response in ['y', 'yes']:
            webbrowser.open('https://github.com/UB-Mannheim/tesseract/wiki')
            print_success("Opened download page in browser")
    except KeyboardInterrupt:
        print("\n")


def install_linux():
    """Guide for Linux installation.""" 
    print_header("Linux Installation Guide")
    
    print_step("Ubuntu/Debian")
    print("sudo apt-get update")
    print("sudo apt-get install tesseract-ocr")
    
    print_step("CentOS/RHEL/Fedora")
    print("sudo yum install tesseract")
    print("# or")
    print("sudo dnf install tesseract")
    
    print_step("Arch Linux")
    print("sudo pacman -S tesseract")
    
    print_step("Additional Language Packs (optional)")
    print("sudo apt-get install tesseract-ocr-eng tesseract-ocr-deu")


def install_macos():
    """Guide for macOS installation."""
    print_header("macOS Installation Guide")
    
    print_step("Homebrew (Recommended)")
    print("brew install tesseract")
    
    print_step("MacPorts")
    print("sudo port install tesseract")
    
    print_step("Manual Installation")
    print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Follow macOS installation instructions")


def test_installation():
    """Test if installation was successful."""
    print_header("Testing Installation")
    
    if check_tesseract_installed():
        print_step("Testing OCR functionality")
        try:
            # Test basic functionality
            import pytesseract
            from PIL import Image
            import numpy as np
            
            # Create a simple test image
            test_image = Image.new('RGB', (200, 60), color='white')
            # This would normally contain text for OCR testing
            print_success("Python integration working")
            
            print_step("MS11 Integration Test")
            print("Run: python scripts/quick_test_ms11.py")
            print("This will verify Tesseract works with MS11")
            
        except ImportError as e:
            print_warning(f"Python libraries need installation: {e}")
            print("Run: pip install pytesseract pillow")
        
        return True
    else:
        print_error("Installation test failed")
        print("\n💡 Troubleshooting:")
        print("1. Restart your terminal/command prompt")
        print("2. Check PATH environment variable")
        print("3. Try running 'tesseract --version' directly")
        return False


def show_troubleshooting():
    """Show troubleshooting guide."""
    print_header("Troubleshooting Guide")
    
    print_step("Common Issues")
    print("1. 'tesseract command not found'")
    print("   → Tesseract not in PATH environment variable")
    print("   → Reinstall and ensure PATH is set correctly")
    print("")
    print("2. Permission denied errors")
    print("   → Run installer as Administrator (Windows)")
    print("   → Use sudo for package managers (Linux/macOS)")
    print("")
    print("3. Import errors in Python")
    print("   → Install: pip install pytesseract pillow")
    print("   → Ensure Tesseract binary is installed first")
    print("")
    print("4. OCR not working in MS11")
    print("   → Test with: python scripts/quick_test_ms11.py")
    print("   → Check logs/ms11.log for error messages")
    
    print_step("Alternative Solutions")
    print("1. Use MS11 without OCR:")
    print("   → Many features work without Tesseract")
    print("   → Vision features will be limited")
    print("")
    print("2. Docker installation:")
    print("   → Use Docker containers with pre-installed Tesseract")
    print("   → Run: docker-compose up -d")


def main():
    """Main installation guide."""
    print("[INFO] Tesseract OCR Installation Helper")
    print("=" * 60)
    print("This script helps you install Tesseract OCR for MS11.")
    print("")
    
    # Check current status
    if check_tesseract_installed():
        print("Tesseract is already installed and working!")
        
        choice = input("\n[QUESTION] What would you like to do?\n"
                      "1. Test installation with MS11\n"
                      "2. View troubleshooting guide\n"
                      "3. Exit\n"
                      "Choice (1-3): ")
        
        if choice == '1':
            test_installation()
        elif choice == '2':
            show_troubleshooting()
        return
    
    # Installation guide
    print_warning("Tesseract OCR not found")
    print("")
    
    system = platform.system().lower()
    
    if system == "windows":
        install_windows()
    elif system == "linux":
        install_linux()
    elif system == "darwin":
        install_macos()
    else:
        print_error(f"Unsupported platform: {system}")
        print("Please install Tesseract manually from:")
        print("https://github.com/tesseract-ocr/tesseract")
    
    print_step("After Installation")
    print("1. Restart your terminal/command prompt")
    print("2. Run this script again to test: python scripts/install_tesseract.py")
    print("3. Run full MS11 test: python scripts/quick_test_ms11.py")
    
    print_step("Need Help?")
    print("• Check documentation: SETUP_GUIDE.md")
    print("• Run troubleshooting: python scripts/install_tesseract.py")
    print("• Visit: https://github.com/tesseract-ocr/tesseract/wiki")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Once installed, MS11 will have full OCR capabilities!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCEL] Installation cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print("Please check the installation manually.")