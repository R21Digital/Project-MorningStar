#!/usr/bin/env python3
"""
Configuration Deployment System for MS11
Automatically deploys and syncs configuration files across different environments.
"""

import json
import yaml
import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import hashlib
import subprocess
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConfigurationDeployer:
    """Deploys MS11 configurations across different environments."""
    
    def __init__(self, config_root: str = "config"):
        self.config_root = Path(config_root)
        self.deployment_history = []
        self.backup_dir = Path("backups/config_deployments")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Environment configurations
        self.environments = {
            'development': {
                'path': 'config/development',
                'backup': True,
                'validate': True,
                'notify': False
            },
            'testing': {
                'path': 'config/testing',
                'backup': True,
                'validate': True,
                'notify': True
            },
            'staging': {
                'path': 'config/staging',
                'backup': True,
                'validate': True,
                'notify': True
            },
            'production': {
                'path': 'config/production',
                'backup': True,
                'validate': True,
                'notify': True,
                'require_approval': True
            }
        }
    
    def deploy_to_environment(self, environment: str, source_configs: List[str] = None, 
                            force: bool = False, dry_run: bool = False) -> bool:
        """Deploy configurations to a specific environment."""
        if environment not in self.environments:
            logger.error(f"Unknown environment: {environment}")
            return False
        
        env_config = self.environments[environment]
        target_path = Path(env_config['path'])
        
        logger.info(f"Deploying to {environment} environment...")
        
        # Check if target directory exists
        if not target_path.exists():
            logger.info(f"Creating target directory: {target_path}")
            if not dry_run:
                target_path.mkdir(parents=True, exist_ok=True)
        
        # Determine which configurations to deploy
        if source_configs is None:
            source_configs = self._get_all_configurations()
        
        # Create backup if required
        if env_config['backup'] and not dry_run:
            self._create_backup(environment, target_path)
        
        # Deploy each configuration
        deployed_count = 0
        for config in source_configs:
            if self._deploy_single_config(config, target_path, environment, dry_run):
                deployed_count += 1
        
        # Validate deployment if required
        if env_config['validate'] and not dry_run:
            self._validate_deployment(target_path, environment)
        
        # Send notifications if required
        if env_config['notify'] and not dry_run:
            self._send_deployment_notification(environment, deployed_count)
        
        logger.info(f"Deployment to {environment} complete. {deployed_count} configurations deployed.")
        return True
    
    def _get_all_configurations(self) -> List[Path]:
        """Get all configuration files to deploy."""
        configs = []
        
        # Get main configuration files
        for config_file in self.config_root.rglob("*.yaml"):
            if "templates" not in str(config_file):
                configs.append(config_file)
        
        for config_file in self.config_root.rglob("*.yml"):
            if "templates" not in str(config_file):
                configs.append(config_file)
        
        for config_file in self.config_root.rglob("*.json"):
            if "templates" not in str(config_file):
                configs.append(config_file)
        
        return configs
    
    def _deploy_single_config(self, source_config: Path, target_path: Path, 
                             environment: str, dry_run: bool) -> bool:
        """Deploy a single configuration file."""
        try:
            # Determine target path
            relative_path = source_config.relative_to(self.config_root)
            target_file = target_path / relative_path
            
            # Create target directory if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file has changed
            if target_file.exists():
                if not self._has_changes(source_config, target_file):
                    logger.debug(f"No changes detected for {source_config.name}")
                    return True
            
            # Copy file
            if not dry_run:
                shutil.copy2(source_config, target_file)
                logger.info(f"Deployed {source_config.name} to {environment}")
            else:
                logger.info(f"[DRY RUN] Would deploy {source_config.name} to {environment}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy {source_config}: {e}")
            return False
    
    def _has_changes(self, source: Path, target: Path) -> bool:
        """Check if source file has changes compared to target."""
        try:
            if not target.exists():
                return True
            
            # Compare file hashes
            source_hash = self._get_file_hash(source)
            target_hash = self._get_file_hash(target)
            
            return source_hash != target_hash
            
        except Exception as e:
            logger.warning(f"Could not determine changes for {source}: {e}")
            return True
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _create_backup(self, environment: str, target_path: Path) -> None:
        """Create a backup of the current environment configuration."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{environment}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            if target_path.exists():
                shutil.copytree(target_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
                
                # Record backup in deployment history
                self.deployment_history.append({
                    'timestamp': timestamp,
                    'environment': environment,
                    'backup_path': str(backup_path),
                    'action': 'backup'
                })
            
        except Exception as e:
            logger.error(f"Failed to create backup for {environment}: {e}")
    
    def _validate_deployment(self, target_path: Path, environment: str) -> None:
        """Validate the deployed configuration."""
        try:
            # Run configuration validation
            from validate_configurations import ConfigurationValidator
            
            validator = ConfigurationValidator(str(target_path))
            errors, warnings = validator.validate_all_configurations()
            
            if errors:
                logger.error(f"Deployment validation failed for {environment}: {len(errors)} errors")
                for error in errors:
                    logger.error(f"  - {error}")
            elif warnings:
                logger.warning(f"Deployment validation completed with {len(warnings)} warnings for {environment}")
                for warning in warnings:
                    logger.warning(f"  - {warning}")
            else:
                logger.info(f"Deployment validation successful for {environment}")
                
        except ImportError:
            logger.warning("Configuration validator not available, skipping validation")
        except Exception as e:
            logger.error(f"Deployment validation failed: {e}")
    
    def _send_deployment_notification(self, environment: str, deployed_count: int) -> None:
        """Send deployment notification."""
        try:
            # This would integrate with your notification system
            # For now, just log the notification
            logger.info(f"Deployment notification sent for {environment}: {deployed_count} configurations deployed")
            
        except Exception as e:
            logger.error(f"Failed to send deployment notification: {e}")
    
    def rollback_environment(self, environment: str, backup_timestamp: str = None) -> bool:
        """Rollback an environment to a previous backup."""
        if environment not in self.environments:
            logger.error(f"Unknown environment: {environment}")
            return False
        
        env_config = self.environments[environment]
        target_path = Path(env_config['path'])
        
        # Find backup to restore
        if backup_timestamp is None:
            # Use most recent backup
            backups = [b for b in self.deployment_history if b['environment'] == environment and b['action'] == 'backup']
            if not backups:
                logger.error(f"No backups found for {environment}")
                return False
            
            backup = max(backups, key=lambda x: x['timestamp'])
            backup_path = Path(backup['backup_path'])
        else:
            backup_name = f"{environment}_{backup_timestamp}"
            backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_path}")
            return False
        
        try:
            # Create current state backup before rollback
            current_backup = f"{environment}_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            current_backup_path = self.backup_dir / current_backup
            
            if target_path.exists():
                shutil.copytree(target_path, current_backup_path)
                logger.info(f"Created current state backup: {current_backup_path}")
            
            # Remove current configuration
            if target_path.exists():
                shutil.rmtree(target_path)
            
            # Restore from backup
            shutil.copytree(backup_path, target_path)
            logger.info(f"Successfully rolled back {environment} to {backup_timestamp}")
            
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def sync_environments(self, source_env: str, target_envs: List[str], 
                         force: bool = False, dry_run: bool = False) -> Dict[str, bool]:
        """Sync configurations from one environment to others."""
        if source_env not in self.environments:
            logger.error(f"Unknown source environment: {source_env}")
            return {}
        
        source_path = Path(self.environments[source_env]['path'])
        if not source_path.exists():
            logger.error(f"Source environment {source_env} does not exist")
            return {}
        
        results = {}
        for target_env in target_envs:
            if target_env not in self.environments:
                logger.error(f"Unknown target environment: {target_env}")
                results[target_env] = False
                continue
            
            logger.info(f"Syncing from {source_env} to {target_env}...")
            
            # Get source configurations
            source_configs = []
            for config_file in source_path.rglob("*.yaml"):
                source_configs.append(config_file)
            for config_file in source_path.rglob("*.yml"):
                source_configs.append(config_file)
            for config_file in source_path.rglob("*.json"):
                source_configs.append(config_file)
            
            # Deploy to target environment
            success = self.deploy_to_environment(target_env, source_configs, force, dry_run)
            results[target_env] = success
        
        return results
    
    def generate_deployment_report(self, output_file: Optional[str] = None) -> str:
        """Generate a deployment report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
Configuration Deployment Report
Generated: {timestamp}
=====================================

Deployment History:
"""
        
        for entry in self.deployment_history:
            report += f"- {entry['timestamp']}: {entry['action']} to {entry['environment']}\n"
        
        # Environment status
        report += "\nEnvironment Status:\n"
        for env_name, env_config in self.environments.items():
            env_path = Path(env_config['path'])
            if env_path.exists():
                config_count = len(list(env_path.rglob("*.yaml"))) + len(list(env_path.rglob("*.yml"))) + len(list(env_path.rglob("*.json")))
                report += f"- {env_name}: {config_count} configurations\n"
            else:
                report += f"- {env_name}: Not deployed\n"
        
        # Write report to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                logger.info(f"Deployment report written to {output_file}")
            except Exception as e:
                logger.error(f"Failed to write deployment report to {output_file}: {e}")
        
        return report
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Clean up old backup files."""
        try:
            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
            removed_count = 0
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    # Check if backup is old enough to remove
                    try:
                        dir_time = backup_dir.stat().st_mtime
                        if dir_time < cutoff_date:
                            shutil.rmtree(backup_dir)
                            removed_count += 1
                            logger.info(f"Removed old backup: {backup_dir}")
                    except Exception as e:
                        logger.warning(f"Could not check age of backup {backup_dir}: {e}")
            
            logger.info(f"Cleanup complete. Removed {removed_count} old backups.")
            return removed_count
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return 0


def main():
    """Main entry point for configuration deployment."""
    parser = argparse.ArgumentParser(description="Deploy MS11 configurations to different environments")
    parser.add_argument("action", choices=["deploy", "rollback", "sync", "report", "cleanup"], 
                       help="Action to perform")
    parser.add_argument("--environment", "-e", help="Target environment")
    parser.add_argument("--source-env", help="Source environment for sync")
    parser.add_argument("--target-envs", nargs="+", help="Target environments for sync")
    parser.add_argument("--configs", nargs="+", help="Specific configurations to deploy")
    parser.add_argument("--force", action="store_true", help="Force deployment without confirmation")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deployed without actually deploying")
    parser.add_argument("--backup-timestamp", help="Backup timestamp for rollback")
    parser.add_argument("--keep-days", type=int, default=30, help="Days to keep backups (for cleanup)")
    parser.add_argument("--output", help="Output file for reports")
    
    args = parser.parse_args()
    
    # Initialize deployer
    deployer = ConfigurationDeployer()
    
    try:
        if args.action == "deploy":
            if not args.environment:
                logger.error("Environment must be specified for deploy action")
                sys.exit(1)
            
            success = deployer.deploy_to_environment(
                args.environment, 
                args.configs, 
                args.force, 
                args.dry_run
            )
            
            if not success:
                sys.exit(1)
        
        elif args.action == "rollback":
            if not args.environment:
                logger.error("Environment must be specified for rollback action")
                sys.exit(1)
            
            success = deployer.rollback_environment(args.environment, args.backup_timestamp)
            if not success:
                sys.exit(1)
        
        elif args.action == "sync":
            if not args.source_env or not args.target_envs:
                logger.error("Source and target environments must be specified for sync action")
                sys.exit(1)
            
            results = deployer.sync_environments(args.source_env, args.target_envs, args.force, args.dry_run)
            if not all(results.values()):
                sys.exit(1)
        
        elif args.action == "report":
            report = deployer.generate_deployment_report(args.output)
            print(report)
        
        elif args.action == "cleanup":
            removed_count = deployer.cleanup_old_backups(args.keep_days)
            print(f"Removed {removed_count} old backups")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
