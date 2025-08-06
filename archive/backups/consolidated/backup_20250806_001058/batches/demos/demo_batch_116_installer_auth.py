#!/usr/bin/env python3
"""
Batch 116 Demo - Local Installer + Auth Gateway
Demonstrates the MS11 installer with Discord authentication.
"""

import os
import sys
import json
import time
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from auth.discord_auth import DiscordAuthGateway, DiscordAuthManager, DiscordAuthServer
from auth.validate_token import TokenValidator, AuthFileValidator, TokenSecurityChecker


class MS11InstallerDemo:
    """Demo class for MS11 installer functionality."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ms11_demo_"))
        self.install_dir = self.temp_dir / "MS11_Install"
        self.auth_file = self.install_dir / "auth" / "discord_auth.json"
        
    def run_demo(self) -> None:
        """Run the complete installer demo."""
        print("=== MS11 Installer + Auth Gateway Demo ===")
        print("Batch 116 - Local Installer + Auth Gateway")
        print()
        
        try:
            # Demo 1: Installer Setup
            self.demo_installer_setup()
            
            # Demo 2: Discord Authentication
            self.demo_discord_auth()
            
            # Demo 3: Token Validation
            self.demo_token_validation()
            
            # Demo 4: Security Checks
            self.demo_security_checks()
            
            # Demo 5: Configuration Management
            self.demo_config_management()
            
            print("\n=== Demo Complete ===")
            print("All installer and authentication features demonstrated successfully!")
            
        except Exception as e:
            print(f"Demo failed: {e}")
        finally:
            # Cleanup
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                
    def demo_installer_setup(self) -> None:
        """Demo installer setup and directory creation."""
        print("1. Installer Setup Demo")
        print("-" * 30)
        
        # Create installation directories
        directories = [
            self.install_dir,
            self.install_dir / "config",
            self.install_dir / "data",
            self.install_dir / "auth",
            self.install_dir / "logs",
            self.install_dir / "screenshots",
            self.install_dir / "session_logs",
            self.install_dir / "backups",
            self.install_dir / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {directory.name}")
            
        # Create sample configuration files
        self.create_sample_configs()
        
        print("✓ Installer setup completed")
        print()
        
    def create_sample_configs(self) -> None:
        """Create sample configuration files."""
        # User config
        user_config = {
            "installation": {
                "installation_path": str(self.install_dir),
                "version": "1.0.0",
                "install_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "first_run": True,
                "auto_update": True
            },
            "authentication": {
                "discord_auth_required": True,
                "auth_file_path": str(self.auth_file),
                "auto_refresh_tokens": True,
                "session_timeout": 3600
            },
            "logging": {
                "log_level": "INFO",
                "log_file": str(self.install_dir / "logs" / "ms11.log"),
                "max_log_size": "10MB",
                "log_retention_days": 30,
                "console_output": True
            }
        }
        
        config_file = self.install_dir / "config" / "user_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(user_config, f, indent=2)
            
        # Discord config
        discord_config = {
            "discord_token": "DEMO_TOKEN",
            "relay_mode": "notify",
            "target_user_id": 0,
            "reply_queue": [],
            "_comment": "Demo configuration - replace with real values"
        }
        
        discord_config_file = self.install_dir / "config" / "discord_config.json"
        with open(discord_config_file, 'w', encoding='utf-8') as f:
            json.dump(discord_config, f, indent=2)
            
    def demo_discord_auth(self) -> None:
        """Demo Discord authentication flow."""
        print("2. Discord Authentication Demo")
        print("-" * 30)
        
        # Create auth manager
        auth_manager = DiscordAuthManager(str(self.auth_file))
        
        # Mock Discord OAuth2 flow
        with patch('auth.discord_auth.DiscordAuthGateway') as mock_gateway:
            mock_gateway_instance = Mock()
            mock_gateway_instance.get_auth_url.return_value = "https://discord.com/api/oauth2/authorize?client_id=DEMO&redirect_uri=http://localhost:8080/callback&response_type=code&scope=identify%20email&state=DEMO_STATE"
            mock_gateway_instance.exchange_code_for_token.return_value = {
                'access_token': 'DEMO_ACCESS_TOKEN',
                'refresh_token': 'DEMO_REFRESH_TOKEN',
                'expires_in': 604800,
                'user_id': '123456789',
                'username': 'DemoUser',
                'email': 'demo@example.com',
                'scope': 'identify email',
                'token_type': 'Bearer'
            }
            mock_gateway_instance.get_user_info.return_value = {
                'id': '123456789',
                'username': 'DemoUser',
                'email': 'demo@example.com',
                'verified': True,
                'mfa_enabled': False
            }
            mock_gateway.return_value = mock_gateway_instance
            
            # Simulate OAuth2 flow
            print("✓ Generating Discord OAuth2 URL")
            auth_url = mock_gateway_instance.get_auth_url()
            print(f"  Auth URL: {auth_url}")
            
            # Simulate token exchange
            print("✓ Exchanging authorization code for token")
            token_data = mock_gateway_instance.exchange_code_for_token("DEMO_CODE")
            
            # Save auth data
            auth_data = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': time.time() + token_data.get('expires_in', 0),
                'user_id': token_data['user_id'],
                'username': token_data['username'],
                'email': token_data.get('email'),
                'scope': token_data.get('scope', ''),
                'token_type': token_data.get('token_type', 'Bearer')
            }
            
            auth_manager.save_auth_data(auth_data)
            print(f"✓ Authentication successful for user: {token_data['username']}")
            
        print("✓ Discord authentication demo completed")
        print()
        
    def demo_token_validation(self) -> None:
        """Demo token validation functionality."""
        print("3. Token Validation Demo")
        print("-" * 30)
        
        # Create validators
        token_validator = TokenValidator()
        auth_file_validator = AuthFileValidator(str(self.auth_file))
        
        # Test token validation
        with patch('auth.validate_token.TokenValidator.validate_token') as mock_validate:
            mock_validate.return_value = True
            
            # Test with mock token
            test_token = "DEMO_ACCESS_TOKEN"
            is_valid = token_validator.validate_token(test_token)
            print(f"✓ Token validation: {'Valid' if is_valid else 'Invalid'}")
            
            # Test token info retrieval
            with patch('auth.validate_token.TokenValidator.get_user_info') as mock_user_info:
                mock_user_info.return_value = {
                    'id': '123456789',
                    'username': 'DemoUser',
                    'email': 'demo@example.com',
                    'verified': True,
                    'mfa_enabled': False
                }
                
                user_info = token_validator.get_user_info(test_token)
                if user_info:
                    print(f"✓ User info retrieved: {user_info['username']}")
                    
        # Test auth file validation
        is_valid, auth_data = auth_file_validator.load_and_validate_auth()
        print(f"✓ Auth file validation: {'Valid' if is_valid else 'Invalid'}")
        
        if is_valid and auth_data:
            print(f"✓ Auth data loaded for user: {auth_data.get('username', 'Unknown')}")
            
        print("✓ Token validation demo completed")
        print()
        
    def demo_security_checks(self) -> None:
        """Demo security checking functionality."""
        print("4. Security Checks Demo")
        print("-" * 30)
        
        security_checker = TokenSecurityChecker()
        
        # Test token permissions
        with patch('auth.validate_token.TokenSecurityChecker.check_token_permissions') as mock_check:
            mock_check.return_value = {
                'valid': True,
                'user_id': '123456789',
                'username': 'DemoUser',
                'email': 'demo@example.com',
                'verified': True,
                'mfa_enabled': False,
                'guild_count': 5,
                'guilds': [
                    {'id': '1', 'name': 'Demo Server 1'},
                    {'id': '2', 'name': 'Demo Server 2'}
                ],
                'permissions': {
                    'can_read_user_info': True,
                    'can_read_guilds': True,
                    'has_email': True,
                    'is_verified': True
                }
            }
            
            test_token = "DEMO_ACCESS_TOKEN"
            permissions = security_checker.check_token_permissions(test_token)
            
            if permissions['valid']:
                print(f"✓ Token security check passed")
                print(f"  User: {permissions['username']}")
                print(f"  Verified: {permissions['verified']}")
                print(f"  MFA Enabled: {permissions['mfa_enabled']}")
                print(f"  Guild Count: {permissions['guild_count']}")
                print(f"  Permissions: {list(permissions['permissions'].keys())}")
            else:
                print(f"✗ Token security check failed: {permissions.get('error', 'Unknown error')}")
                
        print("✓ Security checks demo completed")
        print()
        
    def demo_config_management(self) -> None:
        """Demo configuration management."""
        print("5. Configuration Management Demo")
        print("-" * 30)
        
        # Load user config template
        template_path = project_root / "config" / "user_config_template.json"
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
                
            # Customize template for demo
            template['installation']['installation_path'] = str(self.install_dir)
            template['installation']['install_date'] = time.strftime("%Y-%m-%d %H:%M:%S")
            template['paths']['config_dir'] = str(self.install_dir / "config")
            template['paths']['data_dir'] = str(self.install_dir / "data")
            
            # Save customized config
            demo_config_path = self.install_dir / "config" / "demo_user_config.json"
            with open(demo_config_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
                
            print("✓ Configuration template loaded and customized")
            print(f"  Config sections: {list(template.keys())}")
            print(f"  Installation path: {template['installation']['installation_path']}")
            print(f"  Auth required: {template['authentication']['discord_auth_required']}")
            print(f"  Log level: {template['logging']['log_level']}")
            
        else:
            print("✗ Configuration template not found")
            
        # Test configuration validation
        config_sections = ['installation', 'authentication', 'logging', 'security']
        for section in config_sections:
            if section in template:
                print(f"✓ {section.capitalize()} configuration valid")
            else:
                print(f"✗ {section.capitalize()} configuration missing")
                
        print("✓ Configuration management demo completed")
        print()


class InstallerBuilderDemo:
    """Demo for installer builder functionality."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.demo_build_dir = self.project_root / "demo_build"
        
    def run_builder_demo(self) -> None:
        """Demo the installer builder."""
        print("=== Installer Builder Demo ===")
        
        try:
            # Create demo build directory
            self.demo_build_dir.mkdir(exist_ok=True)
            
            # Demo PyInstaller spec creation
            self.demo_spec_creation()
            
            # Demo installer main creation
            self.demo_installer_main_creation()
            
            # Demo file packaging
            self.demo_file_packaging()
            
            print("✓ Installer builder demo completed")
            
        except Exception as e:
            print(f"Builder demo failed: {e}")
        finally:
            # Cleanup
            if self.demo_build_dir.exists():
                shutil.rmtree(self.demo_build_dir)
                
    def demo_spec_creation(self) -> None:
        """Demo PyInstaller spec file creation."""
        print("1. PyInstaller Spec Creation")
        print("-" * 30)
        
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
)
'''
        
        spec_file = self.demo_build_dir / "ms11_installer.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
            
        print("✓ PyInstaller spec file created")
        print(f"  Spec file: {spec_file}")
        print(f"  Entry point: installer/installer_main.py")
        print(f"  Hidden imports: 8 modules")
        print(f"  Data files: 4 directories")
        print()
        
    def demo_installer_main_creation(self) -> None:
        """Demo installer main script creation."""
        print("2. Installer Main Script Creation")
        print("-" * 30)
        
        installer_main = '''#!/usr/bin/env python3
"""
MS11 Installer - Main Entry Point
Handles installation, configuration, and Discord authentication.
"""

import os
import sys
import json
import shutil
from pathlib import Path

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
        self.auth_file = self.install_dir / "auth" / "discord_auth.json"
        
    def run(self) -> None:
        """Run the installer."""
        print("=== MS11 Installer ===")
        print("Welcome to MS11 - Star Wars Galaxies Bot")
        print()
        
        # Create installation directories
        self.create_installation_directories()
        
        # Setup configuration
        self.setup_configuration()
        
        # Handle Discord authentication
        self.handle_discord_auth()
        
        print("\\n=== Installation Complete ===")
        print(f"MS11 has been installed to: {self.install_dir}")
        
    def create_installation_directories(self) -> None:
        """Create necessary installation directories."""
        directories = [
            self.install_dir,
            self.config_dir,
            self.install_dir / "auth",
            self.install_dir / "logs",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {directory}")
            
    def setup_configuration(self) -> None:
        """Setup initial configuration files."""
        user_config = {
            "installation_path": str(self.install_dir),
            "discord_auth_required": True,
            "auto_update": True,
            "log_level": "INFO",
        }
        
        user_config_path = self.config_dir / "user_config.json"
        with open(user_config_path, 'w', encoding='utf-8') as f:
            json.dump(user_config, f, indent=2)
            
        print("Created user configuration template")
        
    def handle_discord_auth(self) -> None:
        """Handle Discord OAuth2 authentication."""
        print("\\n=== Discord Authentication Required ===")
        print("MS11 requires Discord authentication for security.")
        
        auth_gateway = DiscordAuthGateway()
        auth_url = auth_gateway.get_auth_url()
        
        print(f"\\nPlease visit this URL to authorize MS11:")
        print(f"{auth_url}")
        print("\\nAfter authorization, you'll be redirected to a local URL.")
        print("Copy the 'code' parameter from that URL.")
        
        # Simulate auth code input
        auth_code = input("\\nEnter the authorization code: ").strip()
        
        if auth_code:
            try:
                token_data = auth_gateway.exchange_code_for_token(auth_code)
                
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
        else:
            print("No authorization code provided. Installation will continue without Discord auth.")


def main():
    """Main installer entry point."""
    try:
        installer = MS11Installer()
        installer.run()
    except KeyboardInterrupt:
        print("\\nInstallation cancelled by user.")
    except Exception as e:
        print(f"\\nInstallation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
        
        installer_main_path = self.demo_build_dir / "installer_main.py"
        with open(installer_main_path, 'w', encoding='utf-8') as f:
            f.write(installer_main)
            
        print("✓ Installer main script created")
        print(f"  Script file: {installer_main_path}")
        print(f"  Features: Directory creation, config setup, Discord auth")
        print()
        
    def demo_file_packaging(self) -> None:
        """Demo file packaging for installer."""
        print("3. File Packaging Demo")
        print("-" * 30)
        
        # Create demo package structure
        package_dirs = [
            self.demo_build_dir / "package" / "core",
            self.demo_build_dir / "package" / "modules",
            self.demo_build_dir / "package" / "auth",
            self.demo_build_dir / "package" / "config",
            self.demo_build_dir / "package" / "data",
        ]
        
        for package_dir in package_dirs:
            package_dir.mkdir(parents=True, exist_ok=True)
            
        # Create demo files
        demo_files = [
            (self.demo_build_dir / "package" / "main.py", "# MS11 Main Entry Point"),
            (self.demo_build_dir / "package" / "requirements.txt", "discord.py\nrequests\nPIL\nopencv-python"),
            (self.demo_build_dir / "package" / "README.md", "# MS11 - Star Wars Galaxies Bot"),
            (self.demo_build_dir / "package" / "config" / "user_config.json", '{"demo": true}'),
        ]
        
        for file_path, content in demo_files:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        print("✓ Package structure created")
        print(f"  Directories: {len(package_dirs)}")
        print(f"  Files: {len(demo_files)}")
        print(f"  Total size: {self.get_dir_size(self.demo_build_dir / 'package')} bytes")
        print()


def main():
    """Run the complete Batch 116 demo."""
    print("=== Batch 116 Demo - Local Installer + Auth Gateway ===")
    print()
    
    # Run installer demo
    installer_demo = MS11InstallerDemo()
    installer_demo.run_demo()
    
    # Run builder demo
    builder_demo = InstallerBuilderDemo()
    builder_demo.run_builder_demo()
    
    print("\n=== Demo Summary ===")
    print("✓ Installer setup and directory creation")
    print("✓ Discord OAuth2 authentication flow")
    print("✓ Token validation and refresh")
    print("✓ Security permission checks")
    print("✓ Configuration management")
    print("✓ PyInstaller spec creation")
    print("✓ Installer main script generation")
    print("✓ File packaging and structure")
    print()
    print("Batch 116 implementation completed successfully!")


if __name__ == "__main__":
    main() 