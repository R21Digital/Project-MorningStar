#!/usr/bin/env python3
"""
User Configuration Template Loader

This module provides functions to load and customize the user configuration template
for the MS11 onboarding wizard.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any


def load_user_config_template() -> Dict[str, Any]:
    """
    Load the user configuration template and return a customized version.
    
    Returns:
        Dict containing the user configuration template with placeholders replaced.
    """
    template_path = Path(__file__).parent / "user_config_template.json"
    
    try:
        with open(template_path, 'r') as f:
            template = json.load(f)
        
        # Replace placeholders with actual values
        install_date = time.strftime("%Y-%m-%d")
        template["installation"]["install_date"] = install_date
        template["_metadata"]["last_modified"] = install_date
        
        return template
        
    except FileNotFoundError:
        # Return a minimal template if the file doesn't exist
        return _get_minimal_template()
    except Exception as e:
        print(f"Error loading user config template: {e}")
        return _get_minimal_template()


def _get_minimal_template() -> Dict[str, Any]:
    """Get a minimal user configuration template."""
    return {
        "installation": {
            "installation_path": "",
            "version": "1.0.0",
            "install_date": time.strftime("%Y-%m-%d"),
            "first_run": True,
            "auto_update": True
        },
        "authentication": {
            "discord_auth_required": False,
            "auth_file_path": "",
            "auto_refresh_tokens": True,
            "session_timeout": 3600
        },
        "security": {
            "encrypt_auth_data": False,
            "backup_auth_data": True,
            "log_auth_events": True,
            "require_mfa": False
        },
        "logging": {
            "log_level": "INFO",
            "log_file": "logs/ms11.log",
            "max_log_size": "10MB",
            "log_retention_days": 30,
            "console_output": True
        },
        "performance": {
            "max_memory_usage": "2GB",
            "cpu_priority": "normal",
            "auto_restart_on_crash": True,
            "performance_monitoring": True
        },
        "backup": {
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "backup_location": "backups",
            "max_backup_count": 10,
            "backup_config_files": True,
            "backup_session_data": True
        },
        "notifications": {
            "discord_notifications": True,
            "email_notifications": False,
            "desktop_notifications": True,
            "notification_level": "INFO"
        },
        "updates": {
            "check_for_updates": True,
            "update_check_interval_hours": 24,
            "auto_download_updates": False,
            "update_channel": "stable"
        },
        "privacy": {
            "collect_usage_data": False,
            "share_error_reports": False,
            "telemetry_enabled": False,
            "anonymize_logs": True
        },
        "accessibility": {
            "high_contrast_mode": False,
            "large_text_mode": False,
            "screen_reader_support": False,
            "keyboard_navigation": True
        },
        "advanced": {
            "debug_mode": False,
            "developer_mode": False,
            "experimental_features": False,
            "custom_scripts_enabled": False
        },
        "paths": {
            "config_dir": "config",
            "data_dir": "data",
            "logs_dir": "logs",
            "screenshots_dir": "screenshots",
            "session_logs_dir": "session_logs",
            "backups_dir": "backups",
            "temp_dir": "temp"
        },
        "compatibility": {
            "windows_version": "10",
            "python_version": "3.8+",
            "required_dependencies": [
                "discord.py",
                "requests",
                "PIL",
                "opencv-python",
                "pyautogui",
                "pytesseract",
                "rich",
                "PyYAML"
            ]
        },
        "licensing": {
            "license_key": "",
            "license_type": "trial",
            "expiration_date": "",
            "features_enabled": [
                "basic_bot_functionality",
                "discord_integration",
                "session_logging"
            ]
        },
        "_metadata": {
            "template_version": "1.0",
            "created_by": "MS11 Onboarding Wizard",
            "last_modified": time.strftime("%Y-%m-%d"),
            "description": "Minimal user configuration template for MS11"
        }
    }


def create_user_config(user_hash: str, installation_path: str) -> Dict[str, Any]:
    """
    Create a personalized user configuration.
    
    Args:
        user_hash: Unique identifier for the user
        installation_path: Path where MS11 is installed
        
    Returns:
        Dict containing the personalized user configuration
    """
    template = load_user_config_template()
    
    # Personalize the configuration
    template["installation"]["installation_path"] = installation_path
    template["installation"]["install_date"] = time.strftime("%Y-%m-%d")
    template["installation"]["first_run"] = True
    
    # Update paths to use installation path
    for path_key, path_value in template["paths"].items():
        if not path_value.startswith("/") and not path_value.startswith("\\"):
            template["paths"][path_key] = f"{installation_path}/{path_value}"
    
    # Update auth file path
    template["authentication"]["auth_file_path"] = f"{installation_path}/auth/discord_auth.json"
    
    # Update log file path
    template["logging"]["log_file"] = f"{installation_path}/logs/ms11.log"
    
    # Update backup location
    template["backup"]["backup_location"] = f"{installation_path}/backups"
    
    # Add user-specific metadata
    template["_metadata"]["user_hash"] = user_hash
    template["_metadata"]["created_by"] = "MS11 Onboarding Wizard"
    template["_metadata"]["last_modified"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    return template


def save_user_config(config: Dict[str, Any], file_path: str) -> bool:
    """
    Save user configuration to file.
    
    Args:
        config: User configuration dictionary
        file_path: Path where to save the configuration
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving user config: {e}")
        return False


if __name__ == "__main__":
    # Test the template loading
    template = load_user_config_template()
    print("✅ User config template loaded successfully")
    print(f"📅 Install date: {template['installation']['install_date']}")
    print(f"🔧 Version: {template['installation']['version']}") 