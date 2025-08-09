#!/usr/bin/env python3
"""
Setup Tesseract PATH for Windows
This script adds Tesseract OCR to the system PATH permanently.
"""

import os
import sys
import subprocess
from pathlib import Path

def add_tesseract_to_path():
    """Add Tesseract OCR to system PATH permanently."""
    tesseract_path = r"D:\Program Files\Tesseract-OCR"
    
    if not Path(tesseract_path).exists():
        print(f"❌ Tesseract not found at: {tesseract_path}")
        print("Please install Tesseract OCR first: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    try:
        # Use PowerShell to add to PATH permanently
        ps_command = f'''
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*{tesseract_path}*") {{
            $newPath = $currentPath + ";{tesseract_path}"
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            Write-Host "Added Tesseract to PATH permanently"
        }} else {{
            Write-Host "Tesseract already in PATH"
        }}
        '''
        
        result = subprocess.run([
            "powershell", "-Command", ps_command
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tesseract added to PATH permanently")
            print("Note: You may need to restart your terminal for changes to take effect")
            return True
        else:
            print(f"❌ Failed to add Tesseract to PATH: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding Tesseract to PATH: {e}")
        return False

def main():
    """Main setup function."""
    print("🔧 Setting up Tesseract PATH...")
    
    if add_tesseract_to_path():
        print("\n✅ Tesseract PATH setup completed!")
        print("\n📋 Next steps:")
        print("1. Restart your terminal or command prompt")
        print("2. Run: python scripts/quick_start.py")
        print("3. Then run: python src/main.py --profile your_character --mode medic --max_loops 1")
    else:
        print("\n❌ Tesseract PATH setup failed!")
        print("Please run this script as Administrator or manually add Tesseract to PATH")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
