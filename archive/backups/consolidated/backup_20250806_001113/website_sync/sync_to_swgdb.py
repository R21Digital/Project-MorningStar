"""SWGDB Website Sync for MS11.

This module provides functionality to sync exported MS11 data to the SWGDB public website,
including file transfer, validation, and status reporting.
"""

import json
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from android_ms11.utils.logging_utils import log_event


@dataclass
class SyncStatus:
    """Sync status information."""
    sync_id: str
    timestamp: str
    files_synced: List[str]
    files_failed: List[str]
    total_files: int
    success_count: int
    failure_count: int
    sync_duration: float
    status: str  # "success", "partial", "failed"
    error_messages: List[str]


@dataclass
class WebsiteConfig:
    """Website configuration for sync."""
    target_directory: str
    backup_directory: str
    allowed_file_types: List[str]
    max_file_size: int  # in bytes
    sync_interval: int  # in seconds
    enable_backup: bool
    enable_validation: bool


class SWGDBSync:
    """Main sync handler for SWGDB website integration."""

    def __init__(self, config: WebsiteConfig = None):
        """Initialize the SWGDB sync handler.

        Parameters
        ----------
        config : WebsiteConfig, optional
            Website configuration settings
        """
        if config is None:
            config = WebsiteConfig(
                target_directory="website_data",
                backup_directory="website_backups",
                allowed_file_types=[".json", ".md", ".yml", ".yaml"],
                max_file_size=10 * 1024 * 1024,  # 10MB
                sync_interval=3600,  # 1 hour
                enable_backup=True,
                enable_validation=True
            )
        
        self.config = config
        self.target_dir = Path(config.target_directory)
        self.backup_dir = Path(config.backup_directory)
        self.export_dir = Path("data/exported")
        
        # Create directories
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Track sync history
        self.sync_history = []
        
        log_event("[SWGDB_SYNC] SWGDB sync handler initialized")

    def sync_exported_data(self, force_sync: bool = False) -> SyncStatus:
        """Sync exported data to the website directory.
        
        Parameters
        ----------
        force_sync : bool
            Force sync even if files haven't changed
            
        Returns
        -------
        SyncStatus
            Status of the sync operation
        """
        try:
            sync_start = datetime.now()
            sync_id = f"sync_{int(sync_start.timestamp())}"
            
            log_event(f"[SWGDB_SYNC] Starting sync operation: {sync_id}")
            
            # Check if export directory exists
            if not self.export_dir.exists():
                log_event("[SWGDB_SYNC] Export directory not found")
                return self._create_failed_sync_status(sync_id, ["Export directory not found"])
            
            # Get list of files to sync
            files_to_sync = self._get_files_to_sync()
            if not files_to_sync:
                log_event("[SWGDB_SYNC] No files to sync")
                return self._create_success_sync_status(sync_id, [], sync_start)
            
            # Validate files before sync
            if self.config.enable_validation:
                validation_errors = self._validate_files(files_to_sync)
                if validation_errors:
                    log_event(f"[SWGDB_SYNC] Validation errors: {validation_errors}")
                    return self._create_failed_sync_status(sync_id, validation_errors)
            
            # Create backup if enabled
            if self.config.enable_backup:
                self._create_backup()
            
            # Sync files
            synced_files = []
            failed_files = []
            error_messages = []
            
            for file_path in files_to_sync:
                try:
                    if self._should_sync_file(file_path, force_sync):
                        success = self._sync_single_file(file_path)
                        if success:
                            synced_files.append(file_path.name)
                            log_event(f"[SWGDB_SYNC] Synced: {file_path.name}")
                        else:
                            failed_files.append(file_path.name)
                            error_messages.append(f"Failed to sync {file_path.name}")
                    else:
                        log_event(f"[SWGDB_SYNC] Skipped (no changes): {file_path.name}")
                        
                except Exception as e:
                    failed_files.append(file_path.name)
                    error_messages.append(f"Error syncing {file_path.name}: {str(e)}")
                    log_event(f"[SWGDB_SYNC] Error syncing {file_path.name}: {e}")
            
            # Calculate sync duration
            sync_duration = (datetime.now() - sync_start).total_seconds()
            
            # Determine sync status
            total_files = len(files_to_sync)
            success_count = len(synced_files)
            failure_count = len(failed_files)
            
            if failure_count == 0:
                status = "success"
            elif success_count > 0:
                status = "partial"
            else:
                status = "failed"
            
            # Create sync status
            sync_status = SyncStatus(
                sync_id=sync_id,
                timestamp=sync_start.isoformat(),
                files_synced=synced_files,
                files_failed=failed_files,
                total_files=total_files,
                success_count=success_count,
                failure_count=failure_count,
                sync_duration=sync_duration,
                status=status,
                error_messages=error_messages
            )
            
            # Store sync history
            self.sync_history.append(asdict(sync_status))
            
            # Log sync results
            log_event(f"[SWGDB_SYNC] Sync completed: {success_count}/{total_files} files synced")
            if failed_files:
                log_event(f"[SWGDB_SYNC] Failed files: {failed_files}")
            
            return sync_status
            
        except Exception as e:
            log_event(f"[SWGDB_SYNC] Error during sync: {e}")
            return self._create_failed_sync_status(sync_id, [str(e)])

    def _get_files_to_sync(self) -> List[Path]:
        """Get list of files to sync."""
        files = []
        for file_path in self.export_dir.iterdir():
            if file_path.is_file() and file_path.suffix in self.config.allowed_file_types:
                files.append(file_path)
        return files

    def _validate_files(self, files: List[Path]) -> List[str]:
        """Validate files before syncing."""
        errors = []
        
        for file_path in files:
            # Check file size
            if file_path.stat().st_size > self.config.max_file_size:
                errors.append(f"File too large: {file_path.name}")
                continue
            
            # Check file format
            if file_path.suffix == ".json":
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                except Exception as e:
                    errors.append(f"Invalid JSON in {file_path.name}: {e}")
            
            elif file_path.suffix in [".yml", ".yaml"]:
                try:
                    import yaml
                    with open(file_path, 'r') as f:
                        yaml.safe_load(f)
                except Exception as e:
                    errors.append(f"Invalid YAML in {file_path.name}: {e}")
        
        return errors

    def _should_sync_file(self, file_path: Path, force_sync: bool) -> bool:
        """Determine if a file should be synced."""
        if force_sync:
            return True
        
        target_file = self.target_dir / file_path.name
        
        # If target doesn't exist, sync
        if not target_file.exists():
            return True
        
        # Compare file hashes
        source_hash = self._get_file_hash(file_path)
        target_hash = self._get_file_hash(target_file)
        
        return source_hash != target_hash

    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _sync_single_file(self, file_path: Path) -> bool:
        """Sync a single file to the target directory."""
        try:
            target_file = self.target_dir / file_path.name
            
            # Copy file
            shutil.copy2(file_path, target_file)
            
            # Verify copy
            if target_file.exists() and target_file.stat().st_size == file_path.stat().st_size:
                return True
            else:
                return False
                
        except Exception as e:
            log_event(f"[SWGDB_SYNC] Error copying {file_path.name}: {e}")
            return False

    def _create_backup(self) -> None:
        """Create backup of current website data."""
        try:
            if not self.target_dir.exists():
                return
            
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.backup_dir / backup_name
            
            # Copy target directory to backup
            shutil.copytree(self.target_dir, backup_path)
            
            # Clean old backups (keep last 5)
            self._cleanup_old_backups()
            
            log_event(f"[SWGDB_SYNC] Created backup: {backup_name}")
            
        except Exception as e:
            log_event(f"[SWGDB_SYNC] Error creating backup: {e}")

    def _cleanup_old_backups(self) -> None:
        """Clean up old backup directories."""
        try:
            backups = sorted(self.backup_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the last 5 backups
            for backup in backups[5:]:
                shutil.rmtree(backup)
                log_event(f"[SWGDB_SYNC] Removed old backup: {backup.name}")
                
        except Exception as e:
            log_event(f"[SWGDB_SYNC] Error cleaning up backups: {e}")

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        try:
            # Get file counts
            export_files = len(list(self.export_dir.glob("*"))) if self.export_dir.exists() else 0
            target_files = len(list(self.target_dir.glob("*"))) if self.target_dir.exists() else 0
            
            # Get last sync
            last_sync = None
            if self.sync_history:
                last_sync = self.sync_history[-1]
            
            # Calculate sync statistics
            total_syncs = len(self.sync_history)
            successful_syncs = len([s for s in self.sync_history if s["status"] == "success"])
            partial_syncs = len([s for s in self.sync_history if s["status"] == "partial"])
            failed_syncs = len([s for s in self.sync_history if s["status"] == "failed"])
            
            return {
                "export_files_count": export_files,
                "target_files_count": target_files,
                "total_syncs": total_syncs,
                "successful_syncs": successful_syncs,
                "partial_syncs": partial_syncs,
                "failed_syncs": failed_syncs,
                "last_sync": last_sync,
                "config": asdict(self.config)
            }
            
        except Exception as e:
            log_event(f"[SWGDB_SYNC] Error getting sync status: {e}")
            return {"error": str(e)}

    def validate_website_data(self) -> Dict[str, Any]:
        """Validate the current website data."""
        try:
            validation_results = {
                "timestamp": datetime.now().isoformat(),
                "files_validated": 0,
                "files_valid": 0,
                "files_invalid": 0,
                "errors": []
            }
            
            if not self.target_dir.exists():
                validation_results["errors"].append("Target directory does not exist")
                return validation_results
            
            for file_path in self.target_dir.iterdir():
                if file_path.is_file():
                    validation_results["files_validated"] += 1
                    
                    try:
                        if file_path.suffix == ".json":
                            with open(file_path, 'r') as f:
                                json.load(f)
                        elif file_path.suffix in [".yml", ".yaml"]:
                            import yaml
                            with open(file_path, 'r') as f:
                                yaml.safe_load(f)
                        
                        validation_results["files_valid"] += 1
                        
                    except Exception as e:
                        validation_results["files_invalid"] += 1
                        validation_results["errors"].append(f"Invalid {file_path.name}: {e}")
            
            return validation_results
            
        except Exception as e:
            log_event(f"[SWGDB_SYNC] Error validating website data: {e}")
            return {"error": str(e)}

    def _create_success_sync_status(self, sync_id: str, synced_files: List[str], start_time: datetime) -> SyncStatus:
        """Create a successful sync status."""
        duration = (datetime.now() - start_time).total_seconds()
        return SyncStatus(
            sync_id=sync_id,
            timestamp=start_time.isoformat(),
            files_synced=synced_files,
            files_failed=[],
            total_files=len(synced_files),
            success_count=len(synced_files),
            failure_count=0,
            sync_duration=duration,
            status="success",
            error_messages=[]
        )

    def _create_failed_sync_status(self, sync_id: str, error_messages: List[str]) -> SyncStatus:
        """Create a failed sync status."""
        return SyncStatus(
            sync_id=sync_id,
            timestamp=datetime.now().isoformat(),
            files_synced=[],
            files_failed=[],
            total_files=0,
            success_count=0,
            failure_count=0,
            sync_duration=0.0,
            status="failed",
            error_messages=error_messages
        )


def create_swgdb_sync(config: WebsiteConfig = None) -> SWGDBSync:
    """Create and return an SWGDBSync instance."""
    return SWGDBSync(config)


__all__ = [
    "SWGDBSync",
    "create_swgdb_sync",
    "SyncStatus",
    "WebsiteConfig"
] 