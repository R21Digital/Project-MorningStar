#!/usr/bin/env python3
"""
Auto-Updater & Channeling System for MS11

This module provides seamless update functionality with support for:
- Stable and canary update channels
- Version checking and comparison
- Secure download with hash verification
- Staged application on next launch
- Automatic rollback on failure
- Dashboard integration for update status
"""

import json
import os
import sys
import hashlib
import shutil
import zipfile
import tempfile
import logging
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UpdateChannel(Enum):
    """Update channel types."""
    STABLE = "stable"
    CANARY = "canary"


class UpdateStatus(Enum):
    """Update status enumeration."""
    IDLE = "idle"
    CHECKING = "checking"
    DOWNLOADING = "downloading"
    VERIFYING = "verifying"
    STAGING = "staging"
    READY = "ready"
    APPLYING = "applying"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"


@dataclass
class VersionInfo:
    """Version information structure."""
    version: str
    build_number: int
    release_date: str
    channel: UpdateChannel
    download_url: str
    file_size: int
    checksum: str
    changelog: List[str]
    is_mandatory: bool
    min_compatible_version: str


@dataclass
class UpdateProgress:
    """Update progress tracking."""
    status: UpdateStatus
    current_step: str
    progress_percent: float
    downloaded_bytes: int
    total_bytes: int
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    estimated_time_remaining: Optional[float] = None


class UpdateClient:
    """Auto-updater client with channel support."""
    
    def __init__(self, 
                 config_path: str = "config/update_channel.json",
                 update_dir: str = "updates",
                 backup_dir: str = "backups"):
        self.config_path = config_path
        self.update_dir = Path(update_dir)
        self.backup_dir = Path(backup_dir)
        self.config = {}
        
        # Update state
        self.current_version = self._get_current_version()
        self.available_version = None
        self.update_progress = UpdateProgress(
            status=UpdateStatus.IDLE,
            current_step="Idle",
            progress_percent=0.0,
            downloaded_bytes=0,
            total_bytes=0
        )
        
        # Threading
        self.update_thread = None
        self.update_active = False
        
        # Create directories
        self.update_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._load_config()
        
        logger.info(f"Update client initialized - Current version: {self.current_version}")
        
    def _load_config(self) -> None:
        """Load update configuration."""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self._create_default_config()
        except Exception as e:
            logger.error(f"Failed to load update config: {e}")
            self._create_default_config()
            
    def _create_default_config(self) -> None:
        """Create default update configuration."""
        self.config = {
            "channel": "stable",
            "auto_check_enabled": True,
            "check_interval_hours": 24,
            "download_timeout_seconds": 300,
            "max_retry_attempts": 3,
            "keep_backups_count": 2,
            "update_servers": {
                "stable": {
                    "base_url": "https://updates.ms11.com/stable",
                    "version_endpoint": "/version.json",
                    "download_endpoint": "/download"
                },
                "canary": {
                    "base_url": "https://updates.ms11.com/canary",
                    "version_endpoint": "/version.json",
                    "download_endpoint": "/download"
                }
            },
            "notification_settings": {
                "notify_on_available": True,
                "notify_on_download": True,
                "notify_on_ready": True,
                "notify_on_failure": True
            }
        }
        self._save_config()
        
    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save update config: {e}")
            
    def _get_current_version(self) -> str:
        """Get current application version."""
        try:
            # Try to read from version file
            version_file = Path("version.txt")
            if version_file.exists():
                return version_file.read_text().strip()
            
            # Fallback to git describe
            try:
                result = subprocess.run(
                    ["git", "describe", "--tags", "--always"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Default version
            return "1.0.0-dev"
            
        except Exception as e:
            logger.error(f"Failed to get current version: {e}")
            return "1.0.0-dev"
            
    def get_channel(self) -> UpdateChannel:
        """Get current update channel."""
        channel_name = self.config.get("channel", "stable")
        return UpdateChannel.STABLE if channel_name == "stable" else UpdateChannel.CANARY
        
    def set_channel(self, channel: UpdateChannel) -> None:
        """Set update channel."""
        self.config["channel"] = channel.value
        self._save_config()
        logger.info(f"Update channel set to: {channel.value}")
        
    def check_for_updates(self, force: bool = False) -> Optional[VersionInfo]:
        """Check for available updates."""
        if not force and not self._should_check_for_updates():
            return None
            
        try:
            self.update_progress.status = UpdateStatus.CHECKING
            self.update_progress.current_step = "Checking for updates"
            self.update_progress.progress_percent = 0.0
            
            channel = self.get_channel()
            server_config = self.config["update_servers"][channel.value]
            
            # Get version information
            version_url = f"{server_config['base_url']}{server_config['version_endpoint']}"
            response = requests.get(version_url, timeout=30)
            response.raise_for_status()
            
            version_data = response.json()
            available_version = VersionInfo(
                version=version_data["version"],
                build_number=version_data["build_number"],
                release_date=version_data["release_date"],
                channel=channel,
                download_url=f"{server_config['base_url']}{server_config['download_endpoint']}/{version_data['version']}",
                file_size=version_data["file_size"],
                checksum=version_data["checksum"],
                changelog=version_data["changelog"],
                is_mandatory=version_data.get("is_mandatory", False),
                min_compatible_version=version_data.get("min_compatible_version", "1.0.0")
            )
            
            # Check if update is needed
            if self._is_newer_version(available_version.version):
                self.available_version = available_version
                logger.info(f"Update available: {available_version.version}")
                return available_version
            else:
                logger.info("No updates available")
                return None
                
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            self.update_progress.status = UpdateStatus.FAILED
            self.update_progress.error_message = str(e)
            return None
        finally:
            self.update_progress.status = UpdateStatus.IDLE
            self.update_progress.current_step = "Idle"
            
    def _should_check_for_updates(self) -> bool:
        """Check if we should check for updates based on interval."""
        if not self.config.get("auto_check_enabled", True):
            return False
            
        last_check_file = Path("last_update_check.txt")
        if not last_check_file.exists():
            return True
            
        try:
            last_check = datetime.fromisoformat(last_check_file.read_text().strip())
            interval_hours = self.config.get("check_interval_hours", 24)
            return datetime.now() - last_check > timedelta(hours=interval_hours)
        except Exception:
            return True
            
    def _is_newer_version(self, version: str) -> bool:
        """Check if version is newer than current."""
        try:
            from packaging import version as pkg_version
            
            # Clean version strings for comparison
            current_clean = self._clean_version_string(self.current_version)
            new_clean = self._clean_version_string(version)
            
            return pkg_version.parse(new_clean) > pkg_version.parse(current_clean)
        except ImportError:
            # Fallback to simple string comparison
            return version > self.current_version
        except Exception:
            # If version parsing fails, use simple string comparison
            return version > self.current_version
            
    def _clean_version_string(self, version: str) -> str:
        """Clean version string for comparison."""
        # Remove git-specific prefixes and suffixes
        cleaned = version
        
        # Remove 'v' prefix if present
        if cleaned.startswith('v'):
            cleaned = cleaned[1:]
            
        # Remove git hash suffix (e.g., -gbe1136b)
        if '-g' in cleaned:
            cleaned = cleaned.split('-g')[0]
            
        # Remove build number suffix (e.g., -1027)
        if '-' in cleaned and cleaned.split('-')[-1].isdigit():
            cleaned = cleaned.rsplit('-', 1)[0]
            
        return cleaned
            
    def download_update(self, version_info: VersionInfo) -> bool:
        """Download update package."""
        try:
            self.update_progress.status = UpdateStatus.DOWNLOADING
            self.update_progress.current_step = "Downloading update"
            self.update_progress.start_time = datetime.now()
            self.update_progress.downloaded_bytes = 0
            self.update_progress.total_bytes = version_info.file_size
            
            # Create temporary file
            temp_file = self.update_dir / f"update_{version_info.version}.zip"
            
            # Download with progress tracking
            response = requests.get(
                version_info.download_url,
                stream=True,
                timeout=self.config.get("download_timeout_seconds", 300)
            )
            response.raise_for_status()
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        self.update_progress.downloaded_bytes += len(chunk)
                        self.update_progress.progress_percent = (
                            self.update_progress.downloaded_bytes / version_info.file_size * 100
                        )
                        
                        # Calculate estimated time remaining
                        if self.update_progress.start_time:
                            elapsed = (datetime.now() - self.update_progress.start_time).total_seconds()
                            if elapsed > 0:
                                rate = self.update_progress.downloaded_bytes / elapsed
                                remaining_bytes = version_info.file_size - self.update_progress.downloaded_bytes
                                self.update_progress.estimated_time_remaining = remaining_bytes / rate
                            
            # Verify checksum
            if not self._verify_checksum(temp_file, version_info.checksum):
                raise Exception("Checksum verification failed")
                
            # Move to final location
            final_file = self.update_dir / f"update_{version_info.version}_ready.zip"
            shutil.move(temp_file, final_file)
            
            logger.info(f"Update downloaded successfully: {version_info.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            self.update_progress.status = UpdateStatus.FAILED
            self.update_progress.error_message = str(e)
            return False
            
    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum."""
        try:
            self.update_progress.status = UpdateStatus.VERIFYING
            self.update_progress.current_step = "Verifying download"
            
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
                    
            actual_checksum = sha256_hash.hexdigest()
            return actual_checksum == expected_checksum
            
        except Exception as e:
            logger.error(f"Checksum verification failed: {e}")
            return False
            
    def stage_update(self, version_info: VersionInfo) -> bool:
        """Stage update for next launch."""
        try:
            self.update_progress.status = UpdateStatus.STAGING
            self.update_progress.current_step = "Staging update"
            
            # Create backup of current installation
            backup_name = f"backup_{self.current_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.backup_dir / backup_name
            
            # Backup current files (excluding update-related directories)
            self._create_backup(backup_path)
            
            # Extract update package
            update_file = self.update_dir / f"update_{version_info.version}_ready.zip"
            if not update_file.exists():
                raise Exception("Update file not found")
                
            # Extract to staging directory
            staging_dir = self.update_dir / "staging"
            staging_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(staging_dir)
                
            # Create update manifest
            manifest = {
                "version": version_info.version,
                "backup_path": str(backup_path),
                "staging_path": str(staging_dir),
                "timestamp": datetime.now().isoformat(),
                "channel": version_info.channel.value
            }
            
            manifest_file = self.update_dir / "update_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
                
            # Clean up old backups
            self._cleanup_old_backups()
            
            self.update_progress.status = UpdateStatus.READY
            self.update_progress.current_step = "Update ready to apply"
            logger.info(f"Update staged successfully: {version_info.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stage update: {e}")
            self.update_progress.status = UpdateStatus.FAILED
            self.update_progress.error_message = str(e)
            return False
            
    def _create_backup(self, backup_path: Path) -> None:
        """Create backup of current installation."""
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy current files to backup
        current_dir = Path(".")
        exclude_dirs = {".git", "updates", "backups", "__pycache__", "node_modules"}
        
        for item in current_dir.iterdir():
            if item.name not in exclude_dirs and item.is_file():
                shutil.copy2(item, backup_path / item.name)
            elif item.name not in exclude_dirs and item.is_dir():
                shutil.copytree(item, backup_path / item.name, ignore=shutil.ignore_patterns("__pycache__"))
                
    def _cleanup_old_backups(self) -> None:
        """Clean up old backup directories."""
        keep_count = self.config.get("keep_backups_count", 2)
        
        backups = sorted(
            [d for d in self.backup_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Remove old backups
        for backup in backups[keep_count:]:
            shutil.rmtree(backup)
            logger.info(f"Removed old backup: {backup.name}")
            
    def apply_update(self) -> bool:
        """Apply staged update."""
        try:
            self.update_progress.status = UpdateStatus.APPLYING
            self.update_progress.current_step = "Applying update"
            
            # Load update manifest
            manifest_file = self.update_dir / "update_manifest.json"
            if not manifest_file.exists():
                raise Exception("No update manifest found")
                
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
                
            staging_dir = Path(manifest["staging_path"])
            if not staging_dir.exists():
                raise Exception("Staging directory not found")
                
            # Apply update files
            self._apply_update_files(staging_dir)
            
            # Update version file
            version_file = Path("version.txt")
            version_file.write_text(manifest["version"])
            
            # Clean up staging
            shutil.rmtree(staging_dir)
            manifest_file.unlink()
            
            # Update current version
            self.current_version = manifest["version"]
            
            self.update_progress.status = UpdateStatus.IDLE
            self.update_progress.current_step = "Update applied successfully"
            logger.info(f"Update applied successfully: {manifest['version']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply update: {e}")
            self._rollback_update()
            return False
            
    def _apply_update_files(self, staging_dir: Path) -> None:
        """Apply update files from staging directory."""
        current_dir = Path(".")
        
        for item in staging_dir.rglob("*"):
            if item.is_file():
                # Calculate relative path
                relative_path = item.relative_to(staging_dir)
                target_path = current_dir / relative_path
                
                # Create parent directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(item, target_path)
                
    def _rollback_update(self) -> None:
        """Rollback to previous version."""
        try:
            self.update_progress.status = UpdateStatus.ROLLING_BACK
            self.update_progress.current_step = "Rolling back update"
            
            # Load update manifest
            manifest_file = self.update_dir / "update_manifest.json"
            if not manifest_file.exists():
                return
                
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
                
            backup_path = Path(manifest["backup_path"])
            if not backup_path.exists():
                raise Exception("Backup not found for rollback")
                
            # Restore from backup
            self._restore_from_backup(backup_path)
            
            # Clean up
            manifest_file.unlink()
            
            self.update_progress.status = UpdateStatus.IDLE
            self.update_progress.current_step = "Rollback completed"
            logger.info("Update rollback completed")
            
        except Exception as e:
            logger.error(f"Failed to rollback update: {e}")
            self.update_progress.status = UpdateStatus.FAILED
            self.update_progress.error_message = f"Rollback failed: {e}"
            
    def _restore_from_backup(self, backup_path: Path) -> None:
        """Restore files from backup."""
        current_dir = Path(".")
        
        # Remove current files (excluding update-related directories)
        exclude_dirs = {".git", "updates", "backups", "__pycache__", "node_modules"}
        
        for item in current_dir.iterdir():
            if item.name not in exclude_dirs:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                    
        # Restore from backup
        for item in backup_path.iterdir():
            if item.is_file():
                shutil.copy2(item, current_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, current_dir / item.name)
                
    def get_update_status(self) -> Dict[str, Any]:
        """Get current update status for dashboard."""
        return {
            "current_version": self.current_version,
            "available_version": asdict(self.available_version) if self.available_version else None,
            "channel": self.get_channel().value,
            "progress": asdict(self.update_progress),
            "has_pending_update": self._has_pending_update(),
            "last_check": self._get_last_check_time()
        }
        
    def _has_pending_update(self) -> bool:
        """Check if there's a pending update ready to apply."""
        manifest_file = self.update_dir / "update_manifest.json"
        return manifest_file.exists()
        
    def _get_last_check_time(self) -> Optional[str]:
        """Get last update check time."""
        last_check_file = Path("last_update_check.txt")
        if last_check_file.exists():
            return last_check_file.read_text().strip()
        return None
        
    def start_auto_update_check(self) -> None:
        """Start automatic update checking."""
        if self.update_active:
            return
            
        self.update_active = True
        self.update_thread = threading.Thread(
            target=self._auto_update_loop,
            daemon=True,
            name="AutoUpdateChecker"
        )
        self.update_thread.start()
        logger.info("Auto-update checking started")
        
    def stop_auto_update_check(self) -> None:
        """Stop automatic update checking."""
        self.update_active = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5.0)
        logger.info("Auto-update checking stopped")
        
    def _auto_update_loop(self) -> None:
        """Automatic update checking loop."""
        while self.update_active:
            try:
                # Check for updates
                available_update = self.check_for_updates()
                
                if available_update:
                    # Download and stage update
                    if self.download_update(available_update):
                        self.stage_update(available_update)
                        
                # Update last check time
                last_check_file = Path("last_update_check.txt")
                last_check_file.write_text(datetime.now().isoformat())
                
                # Wait for next check
                interval_hours = self.config.get("check_interval_hours", 24)
                time.sleep(interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error in auto-update loop: {e}")
                time.sleep(3600)  # Wait 1 hour on error


# Global update client instance
update_client = UpdateClient()


def get_update_client() -> UpdateClient:
    """Get singleton instance of UpdateClient."""
    return update_client


def check_for_updates(force: bool = False) -> Optional[VersionInfo]:
    """Check for available updates."""
    return update_client.check_for_updates(force)


def download_update(version_info: VersionInfo) -> bool:
    """Download update package."""
    return update_client.download_update(version_info)


def stage_update(version_info: VersionInfo) -> bool:
    """Stage update for next launch."""
    return update_client.stage_update(version_info)


def apply_update() -> bool:
    """Apply staged update."""
    return update_client.apply_update()


def get_update_status() -> Dict[str, Any]:
    """Get current update status."""
    return update_client.get_update_status()


def set_update_channel(channel: UpdateChannel) -> None:
    """Set update channel."""
    update_client.set_channel(channel)


def start_auto_update_check() -> None:
    """Start automatic update checking."""
    update_client.start_auto_update_check()


def stop_auto_update_check() -> None:
    """Stop automatic update checking."""
    update_client.stop_auto_update_check() 