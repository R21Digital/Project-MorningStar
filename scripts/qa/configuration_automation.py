#!/usr/bin/env python3
"""
Configuration Automation System for MS11
Manages all configuration files, validates them, and provides automated setup.
"""

import json
import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import yaml

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConfigurationAutomation:
    """Comprehensive configuration management system for MS11."""
    
    def __init__(self, config_root: str = "config"):
        self.config_root = Path(config_root)
        self.backup_dir = Path("config/backups")
        self.templates_dir = Path("config/templates")
        self.validation_schema = self._load_validation_schema()
        
        # Ensure directories exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_validation_schema(self) -> Dict[str, Any]:
        """Load configuration validation schema."""
        return {
            "main_config": {
                "required_fields": ["character_name", "default_mode"],
                "optional_fields": ["enable_discord_relay", "auto_backup", "log_level"],
                "field_types": {
                    "character_name": str,
                    "default_mode": str,
                    "enable_discord_relay": bool,
                    "auto_backup": bool,
                    "log_level": str
                },
                "valid_modes": ["medic", "combat", "vendor", "questing", "training"]
            },
            "session_config": {
                "required_fields": ["enable_logging"],
                "optional_fields": ["auto_train", "log_level", "session_timeout"],
                "field_types": {
                    "enable_logging": bool,
                    "auto_train": bool,
                    "log_level": str,
                    "session_timeout": int
                }
            },
            "travel_config": {
                "required_fields": ["shuttles", "trainers"],
                "optional_fields": ["quests", "unlocks", "settings"],
                "field_types": {
                    "shuttles": dict,
                    "trainers": dict,
                    "quests": dict,
                    "unlocks": dict,
                    "settings": dict
                }
            }
        }
    
    def create_backup(self, config_file: Path) -> Path:
        """Create backup of configuration file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{config_file.stem}_{timestamp}.json"
        backup_path = self.backup_dir / backup_name
        
        if config_file.exists():
            shutil.copy2(config_file, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        return None
    
    def validate_configuration(self, config_data: Dict[str, Any], config_type: str) -> Tuple[bool, List[str]]:
        """Validate configuration against schema."""
        if config_type not in self.validation_schema:
            return False, [f"Unknown configuration type: {config_type}"]
        
        schema = self.validation_schema[config_type]
        errors = []
        
        # Check required fields
        for field in schema["required_fields"]:
            if field not in config_data:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        for field, expected_type in schema["field_types"].items():
            if field in config_data:
                if not isinstance(config_data[field], expected_type):
                    errors.append(f"Field {field} should be {expected_type.__name__}, got {type(config_data[field]).__name__}")
        
        # Check specific validations
        if config_type == "main_config" and "default_mode" in config_data:
            mode = config_data["default_mode"]
            if mode not in schema["valid_modes"]:
                errors.append(f"Invalid mode '{mode}'. Valid modes: {', '.join(schema['valid_modes'])}")
        
        return len(errors) == 0, errors
    
    def load_configuration(self, config_path: Path) -> Optional[Dict[str, Any]]:
        """Load and validate configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix == '.json':
                    config_data = json.load(f)
                elif config_path.suffix in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                else:
                    logger.error(f"Unsupported file format: {config_path.suffix}")
                    return None
            
            # Determine config type from filename
            config_type = self._determine_config_type(config_path.name)
            
            # Validate configuration
            is_valid, errors = self.validate_configuration(config_data, config_type)
            if not is_valid:
                logger.error(f"Configuration validation failed for {config_path}:")
                for error in errors:
                    logger.error(f"  - {error}")
                return None
            
            logger.info(f"Successfully loaded and validated: {config_path}")
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to load configuration {config_path}: {e}")
            return None
    
    def _determine_config_type(self, filename: str) -> str:
        """Determine configuration type from filename."""
        if "travel" in filename:
            return "travel_config"
        elif "session" in filename:
            return "session_config"
        elif "main" in filename or "config" in filename:
            return "main_config"
        else:
            return "main_config"  # Default
    
    def create_default_configurations(self) -> Dict[str, Path]:
        """Create all default configuration files."""
        created_files = {}
        
        # Main configuration
        main_config = {
            "character_name": "Default",
            "default_mode": "medic",
            "enable_discord_relay": False,
            "auto_backup": True,
            "log_level": "INFO"
        }
        main_path = self.config_root / "config.json"
        self._write_config(main_config, main_path)
        created_files["main"] = main_path
        
        # Session configuration
        session_config = {
            "enable_logging": True,
            "auto_train": False,
            "log_level": "INFO",
            "session_timeout": 3600
        }
        session_path = self.config_root / "session_config.json"
        self._write_config(session_config, session_path)
        created_files["session"] = session_path
        
        # Travel configuration
        travel_config = {
            "shuttles": {
                "tatooine": [
                    {
                        "city": "mos_eisley",
                        "npc": "Shuttle Conductor",
                        "x": 3520,
                        "y": -4800,
                        "destinations": [
                            {"planet": "corellia", "city": "coronet"},
                            {"planet": "naboo", "city": "theed"}
                        ]
                    }
                ]
            },
            "trainers": {
                "artisan": {
                    "name": "Artisan Trainer",
                    "planet": "tatooine",
                    "city": "mos_eisley",
                    "x": 3432,
                    "y": -4795,
                    "expected_skill": "Novice Artisan"
                }
            },
            "settings": {
                "default_start_planet": "tatooine",
                "default_start_city": "mos_eisley",
                "max_travel_attempts": 3,
                "travel_timeout_seconds": 60.0
            }
        }
        travel_path = self.config_root / "travel_config.json"
        self._write_config(travel_config, travel_path)
        created_files["travel"] = travel_path
        
        # Combat profiles configuration
        combat_config = {
            "profiles": {
                "medic": {
                    "name": "Medic Support",
                    "description": "Healing-focused combat profile",
                    "priority_targets": ["healers", "support"],
                    "defensive_mode": True
                },
                "combat": {
                    "name": "Combat Focused",
                    "description": "Damage-dealing combat profile",
                    "priority_targets": ["damage_dealers", "tanks"],
                    "defensive_mode": False
                }
            },
            "settings": {
                "auto_heal_threshold": 0.7,
                "retreat_health": 0.3,
                "max_combat_time": 300
            }
        }
        combat_path = self.config_root / "combat_config.json"
        self._write_config(combat_config, combat_path)
        created_files["combat"] = combat_path
        
        logger.info("Created default configuration files")
        return created_files
    
    def _write_config(self, config_data: Dict[str, Any], file_path: Path) -> None:
        """Write configuration to file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created: {file_path}")
    
    def migrate_configurations(self, source_dir: str = "config/legacy") -> Dict[str, Path]:
        """Migrate configurations from legacy format."""
        source_path = Path(source_dir)
        migrated_files = {}
        
        if not source_path.exists():
            logger.info(f"Legacy directory not found: {source_path}")
            return migrated_files
        
        # Find legacy config files
        legacy_files = list(source_path.glob("*.json")) + list(source_path.glob("*.yaml"))
        
        for legacy_file in legacy_files:
            try:
                # Load legacy config
                with open(legacy_file, 'r', encoding='utf-8') as f:
                    if legacy_file.suffix == '.json':
                        legacy_data = json.load(f)
                    else:
                        legacy_data = yaml.safe_load(f)
                
                # Create backup
                self.create_backup(legacy_file)
                
                # Migrate to new format
                migrated_data = self._migrate_legacy_config(legacy_data, legacy_file.name)
                
                # Save to new location
                new_path = self.config_root / legacy_file.name
                self._write_config(migrated_data, new_path)
                
                migrated_files[legacy_file.name] = new_path
                logger.info(f"Migrated: {legacy_file} -> {new_path}")
                
            except Exception as e:
                logger.error(f"Failed to migrate {legacy_file}: {e}")
        
        return migrated_files
    
    def _migrate_legacy_config(self, legacy_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Migrate legacy configuration to new format."""
        # Basic migration - preserve all data but ensure structure
        if isinstance(legacy_data, dict):
            return legacy_data
        else:
            # If it's not a dict, wrap it
            return {"legacy_data": legacy_data, "migrated_at": datetime.now().isoformat()}
    
    def validate_all_configurations(self) -> Dict[str, Tuple[bool, List[str]]]:
        """Validate all configuration files in the config directory."""
        results = {}
        
        config_files = list(self.config_root.glob("*.json")) + list(self.config_root.glob("*.yaml"))
        
        for config_file in config_files:
            config_data = self.load_configuration(config_file)
            if config_data is not None:
                config_type = self._determine_config_type(config_file.name)
                is_valid, errors = self.validate_configuration(config_data, config_type)
                results[config_file.name] = (is_valid, errors)
            else:
                results[config_file.name] = (False, ["Failed to load file"])
        
        return results
    
    def generate_configuration_report(self, output_file: str = "config_validation_report.json") -> None:
        """Generate comprehensive configuration validation report."""
        validation_results = self.validate_all_configurations()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(validation_results),
            "valid_files": sum(1 for is_valid, _ in validation_results.values() if is_valid),
            "invalid_files": sum(1 for is_valid, _ in validation_results.values() if not is_valid),
            "details": validation_results,
            "recommendations": self._generate_recommendations(validation_results)
        }
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuration report generated: {output_file}")
        
        # Print summary
        print(f"\n📊 Configuration Validation Report")
        print(f"   Total files: {report['total_files']}")
        print(f"   Valid: {report['valid_files']}")
        print(f"   Invalid: {report['invalid_files']}")
        
        if report['invalid_files'] > 0:
            print(f"\n❌ Issues found:")
            for filename, (is_valid, errors) in validation_results.items():
                if not is_valid:
                    print(f"   • {filename}:")
                    for error in errors:
                        print(f"     - {error}")
    
    def _generate_recommendations(self, validation_results: Dict[str, Tuple[bool, List[str]]]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        invalid_count = sum(1 for is_valid, _ in validation_results.values() if not is_valid)
        
        if invalid_count > 0:
            recommendations.append(f"Fix {invalid_count} invalid configuration file(s)")
        
        if not any("travel" in name for name in validation_results.keys()):
            recommendations.append("Create travel configuration for automated navigation")
        
        if not any("combat" in name for name in validation_results.keys()):
            recommendations.append("Create combat configuration for automated combat")
        
        return recommendations
    
    def setup_environment(self, force: bool = False) -> bool:
        """Complete environment setup with all configurations."""
        try:
            logger.info("Starting MS11 configuration environment setup...")
            
            # Create backup of existing configs
            if not force:
                for config_file in self.config_root.glob("*.json"):
                    self.create_backup(config_file)
            
            # Create default configurations
            created_files = self.create_default_configurations()
            
            # Validate all configurations
            validation_results = self.validate_all_configurations()
            
            # Check if setup was successful
            all_valid = all(is_valid for is_valid, _ in validation_results.values())
            
            if all_valid:
                logger.info("✅ Environment setup completed successfully!")
                return True
            else:
                logger.error("❌ Environment setup completed with validation errors")
                return False
                
        except Exception as e:
            logger.error(f"Environment setup failed: {e}")
            return False


def main():
    """Main entry point for configuration automation."""
    parser = argparse.ArgumentParser(description="MS11 Configuration Automation System")
    parser.add_argument("--action", choices=["setup", "validate", "migrate", "backup", "report"], 
                       default="setup", help="Action to perform")
    parser.add_argument("--config-root", default="config", help="Configuration root directory")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing configurations")
    parser.add_argument("--output", help="Output file for reports")
    
    args = parser.parse_args()
    
    # Initialize automation system
    automation = ConfigurationAutomation(args.config_root)
    
    try:
        if args.action == "setup":
            success = automation.setup_environment(force=args.force)
            sys.exit(0 if success else 1)
            
        elif args.action == "validate":
            validation_results = automation.validate_all_configurations()
            all_valid = all(is_valid for is_valid, _ in validation_results.values())
            
            if all_valid:
                print("✅ All configurations are valid")
                sys.exit(0)
            else:
                print("❌ Some configurations have validation errors")
                for filename, (is_valid, errors) in validation_results.items():
                    if not is_valid:
                        print(f"  {filename}: {', '.join(errors)}")
                sys.exit(1)
                
        elif args.action == "migrate":
            migrated_files = automation.migrate_configurations()
            print(f"Migrated {len(migrated_files)} configuration files")
            
        elif args.action == "backup":
            # Backup all existing configs
            for config_file in automation.config_root.glob("*.json"):
                automation.create_backup(config_file)
            print("Backup completed")
            
        elif args.action == "report":
            output_file = args.output or "config_validation_report.json"
            automation.generate_configuration_report(output_file)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
