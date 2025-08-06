#!/usr/bin/env python3
"""
MS11 Installer Builder
Creates a standalone executable installer for MS11 with Discord authentication.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class MS11InstallerBuilder:
    """Builds MS11 installer with PyInstaller."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.spec_file = self.project_root / "ms11_installer.spec"
        
    def create_installer_spec(self) -> None:
        """Create PyInstaller spec file for MS11 installer."""
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['installer/installer_main.py'],
    pathex=[r'{self.project_root}'],
    binaries=[],
    datas=[
        (r'{self.project_root}/config', 'config'),
        (r'{self.project_root}/data', 'data'),
        (r'{self.project_root}/assets', 'assets'),
        (r'{self.project_root}/docs', 'docs'),
        (r'{self.project_root}/requirements.txt', '.'),
        (r'{self.project_root}/README.md', '.'),
    ],
    hiddenimports=[
        'discord',
        'discord.ext.commands',
        'requests',
        'PIL',
        'cv2',
        'pyautogui',
        'pytesseract',
        'rich',
        'yaml',
        'pymongo',
        'numpy',
        'pygetwindow',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MS11_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{self.project_root}/assets/ms11_icon.ico' if os.path.exists(r'{self.project_root}/assets/ms11_icon.ico') else None,
)
'''
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
            
    def create_installer_main(self) -> None:
        """Create the main installer entry point."""
        
        installer_main = '''#!/usr/bin/env python3
"""
MS11 Installer - Main Entry Point
Handles installation, configuration, and Discord authentication.
"""

import os
import sys
import json
import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from auth.discord_auth import DiscordAuthGateway
from auth.validate_token import TokenValidator


class MS11Installer:
    """Main installer class for MS11."""
    
    def __init__(self):
        self.install_dir = Path.home() / "MS11"
        self.config_dir = self.install_dir / "config"
        self.data_dir = self.install_dir / "data"
        self.auth_file = self.install_dir / "auth" / "discord_auth.json"
        
    def run(self) -> None:
        """Run the installer."""
        print("=== MS11 Installer ===")
        print("Welcome to MS11 - Star Wars Galaxies Bot")
        print()
        
        # Check if already installed
        if self.install_dir.exists():
            print(f"MS11 appears to be already installed at: {self.install_dir}")
            response = input("Do you want to reinstall? (y/N): ").lower()
            if response != 'y':
                print("Installation cancelled.")
                return
                
        # Create installation directory
        self.create_installation_directories()
        
        # Copy files
        self.copy_installation_files()
        
        # Setup configuration
        self.setup_configuration()
        
        # Handle Discord authentication
        self.handle_discord_auth()
        
        # Create shortcuts
        self.create_shortcuts()
        
        print("\\n=== Installation Complete ===")
        print(f"MS11 has been installed to: {self.install_dir}")
        print("You can now run MS11 from the Start Menu or desktop shortcut.")
        
    def create_installation_directories(self) -> None:
        """Create necessary installation directories."""
        directories = [
            self.install_dir,
            self.config_dir,
            self.data_dir,
            self.install_dir / "auth",
            self.install_dir / "logs",
            self.install_dir / "screenshots",
            self.install_dir / "session_logs",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {directory}")
            
    def copy_installation_files(self) -> None:
        """Copy installation files to target directory."""
        print("\\nCopying installation files...")
        
        # Copy main application files
        source_root = Path(__file__).parent.parent
        target_root = self.install_dir
        
        # Copy core directories
        core_dirs = ['core', 'modules', 'cli', 'utils', 'auth']
        for dir_name in core_dirs:
            source_dir = source_root / dir_name
            target_dir = target_root / dir_name
            if source_dir.exists():
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(source_dir, target_dir)
                print(f"Copied {dir_name}/")
                
        # Copy individual files
        main_files = [
            'main.py',
            'requirements.txt',
            'README.md',
        ]
        
        for file_name in main_files:
            source_file = source_root / file_name
            target_file = target_root / file_name
            if source_file.exists():
                shutil.copy2(source_file, target_file)
                print(f"Copied {file_name}")
                
    def setup_configuration(self) -> None:
        """Setup initial configuration files."""
        print("\\nSetting up configuration...")
        
        # Create user config template
        user_config = {
            "installation_path": str(self.install_dir),
            "discord_auth_required": True,
            "auto_update": True,
            "log_level": "INFO",
            "backup_enabled": True,
            "first_run": True
        }
        
        user_config_path = self.config_dir / "user_config.json"
        with open(user_config_path, 'w', encoding='utf-8') as f:
            json.dump(user_config, f, indent=2)
            
        print("Created user configuration template")
        
    def handle_discord_auth(self) -> None:
        """Handle Discord OAuth2 authentication."""
        print("\\n=== Discord Authentication Required ===")
        print("MS11 requires Discord authentication for security.")
        print("This ensures only authorized users can access the bot.")
        
        auth_gateway = DiscordAuthGateway()
        
        # Check if auth file exists
        if self.auth_file.exists():
            try:
                with open(self.auth_file, 'r', encoding='utf-8') as f:
                    auth_data = json.load(f)
                    
                validator = TokenValidator()
                if validator.validate_token(auth_data.get('access_token')):
                    print("✓ Existing Discord authentication found and valid")
                    return
            except Exception as e:
                print(f"Warning: Could not validate existing auth: {e}")
                
        # Perform new authentication
        print("\\nInitiating Discord OAuth2 flow...")
        auth_url = auth_gateway.get_auth_url()
        
        print(f"\\nPlease visit this URL to authorize MS11:")
        print(f"{auth_url}")
        print("\\nAfter authorization, you'll be redirected to a local URL.")
        print("Copy the 'code' parameter from that URL.")
        
        # Open browser
        try:
            webbrowser.open(auth_url)
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            
        # Get authorization code
        auth_code = input("\\nEnter the authorization code: ").strip()
        
        if not auth_code:
            print("No authorization code provided. Installation will continue without Discord auth.")
            return
            
        # Exchange code for token
        try:
            token_data = auth_gateway.exchange_code_for_token(auth_code)
            
            # Save token data
            auth_data = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': token_data.get('expires_in'),
                'user_id': token_data.get('user_id'),
                'scope': token_data.get('scope', ''),
                'token_type': token_data.get('token_type', 'Bearer')
            }
            
            with open(self.auth_file, 'w', encoding='utf-8') as f:
                json.dump(auth_data, f, indent=2)
                
            print("✓ Discord authentication completed successfully!")
            
        except Exception as e:
            print(f"✗ Discord authentication failed: {e}")
            print("Installation will continue without Discord auth.")
            
    def create_shortcuts(self) -> None:
        """Create desktop and start menu shortcuts."""
        print("\\nCreating shortcuts...")
        
        # Create batch file for easy launching
        batch_content = f'''@echo off
cd /d "{self.install_dir}"
python main.py %*
pause
'''
        
        batch_file = self.install_dir / "run_ms11.bat"
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
            
        print(f"Created launcher: {batch_file}")
        
        # Create desktop shortcut
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            shortcut_content = f'''[Desktop Entry]
Name=MS11
Comment=Star Wars Galaxies Bot
Exec={self.install_dir}\\run_ms11.bat
Icon={self.install_dir}\\assets\\ms11_icon.ico
Terminal=true
Type=Application
Categories=Game;
'''
            
            shortcut_file = desktop / "MS11.desktop"
            with open(shortcut_file, 'w', encoding='utf-8') as f:
                f.write(shortcut_content)
                
            print(f"Created desktop shortcut: {shortcut_file}")


def main():
    """Main installer entry point."""
    try:
        installer = MS11Installer()
        installer.run()
    except KeyboardInterrupt:
        print("\\nInstallation cancelled by user.")
    except Exception as e:
        print(f"\\nInstallation failed: {e}")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
        
        installer_main_path = self.project_root / "installer" / "installer_main.py"
        installer_main_path.parent.mkdir(exist_ok=True)
        
        with open(installer_main_path, 'w', encoding='utf-8') as f:
            f.write(installer_main)
            
    def build_installer(self) -> None:
        """Build the installer executable."""
        print("Building MS11 installer...")
        
        # Create spec file
        self.create_installer_spec()
        
        # Create installer main
        self.create_installer_main()
        
        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--onefile",
            "--name=MS11_Installer",
            str(self.spec_file)
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=True)
            print("✓ Installer built successfully!")
            print(f"Executable location: {self.dist_dir / 'MS11_Installer.exe'}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Build failed: {e}")
            raise
            
    def clean_build(self) -> None:
        """Clean build artifacts."""
        print("Cleaning build artifacts...")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            
        if self.spec_file.exists():
            self.spec_file.unlink()
            
        print("✓ Build artifacts cleaned")


def main():
    """Main builder entry point."""
    builder = MS11InstallerBuilder()
    
    try:
        builder.build_installer()
    except KeyboardInterrupt:
        print("\\nBuild cancelled by user.")
    except Exception as e:
        print(f"\\nBuild failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 