#!/usr/bin/env python3
"""
Configuration Validation System for MS11
Validates all configuration files for errors, inconsistencies, and best practices.
"""

import json
import yaml
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import logging
from datetime import datetime
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConfigurationValidator:
    """Validates MS11 configuration files for errors and best practices."""
    
    def __init__(self, config_root: str = "config"):
        self.config_root = Path(config_root)
        self.errors = []
        self.warnings = []
        self.validated_files = []
        
        # Define validation rules
        self.validation_rules = {
            'required_fields': {
                'combat_profiles': ['profile_name', 'description', 'version'],
                'travel_config': ['config_name', 'description', 'version'],
                'general': ['name', 'description', 'version']
            },
            'field_types': {
                'version': str,
                'enabled': bool,
                'timeout': (int, float),
                'coordinates': dict,
                'bounds': dict
            },
            'value_ranges': {
                'timeout': (0, 3600),
                'coordinates_x': (-10000, 10000),
                'coordinates_y': (-10000, 10000),
                'health_thresholds': (0.0, 1.0)
            }
        }
    
    def validate_all_configurations(self) -> Tuple[List[str], List[str]]:
        """Validate all configuration files in the config directory."""
        logger.info("Starting configuration validation...")
        
        if not self.config_root.exists():
            self.errors.append(f"Configuration root directory {self.config_root} does not exist")
            return self.errors, self.warnings
        
        # Validate each configuration file
        for config_file in self.config_root.rglob("*.yaml"):
            self._validate_yaml_file(config_file)
        
        for config_file in self.config_root.rglob("*.yml"):
            self._validate_yaml_file(config_file)
            
        for config_file in self.config_root.rglob("*.json"):
            self._validate_json_file(config_file)
        
        # Validate templates
        templates_dir = self.config_root / "templates"
        if templates_dir.exists():
            for template_file in templates_dir.rglob("*.yaml"):
                self._validate_template_file(template_file)
        
        logger.info(f"Validation complete. Found {len(self.errors)} errors and {len(self.warnings)} warnings")
        return self.errors, self.warnings
    
    def _validate_yaml_file(self, file_path: Path) -> None:
        """Validate a YAML configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if content is None:
                self.warnings.append(f"Empty YAML file: {file_path}")
                return
            
            self._validate_content(content, file_path, "YAML")
            self.validated_files.append(str(file_path))
            
        except yaml.YAMLError as e:
            self.errors.append(f"YAML syntax error in {file_path}: {e}")
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
    
    def _validate_json_file(self, file_path: Path) -> None:
        """Validate a JSON configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            self._validate_content(content, file_path, "JSON")
            self.validated_files.append(str(file_path))
            
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON syntax error in {file_path}: {e}")
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
    
    def _validate_template_file(self, file_path: Path) -> None:
        """Validate a template configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if content is None:
                self.warnings.append(f"Empty template file: {file_path}")
                return
            
            # Additional template-specific validation
            self._validate_template_structure(content, file_path)
            self._validate_content(content, file_path, "Template")
            self.validated_files.append(str(file_path))
            
        except yaml.YAMLError as e:
            self.errors.append(f"Template YAML syntax error in {file_path}: {e}")
        except Exception as e:
            self.errors.append(f"Error reading template {file_path}: {e}")
    
    def _validate_content(self, content: Any, file_path: Path, file_type: str) -> None:
        """Validate the content of a configuration file."""
        if isinstance(content, dict):
            self._validate_dict_content(content, file_path, file_type)
        elif isinstance(content, list):
            self._validate_list_content(content, file_path, file_type)
        else:
            self.warnings.append(f"Unexpected content type in {file_path}: {type(content)}")
    
    def _validate_dict_content(self, content: Dict, file_path: Path, file_type: str) -> None:
        """Validate dictionary content."""
        # Check for required fields based on file type
        self._check_required_fields(content, file_path, file_type)
        
        # Validate field types and values
        for key, value in content.items():
            self._validate_field(key, value, file_path)
            
            # Recursively validate nested structures
            if isinstance(value, dict):
                self._validate_dict_content(value, file_path, file_type)
            elif isinstance(value, list):
                self._validate_list_content(value, file_path, file_type)
    
    def _validate_list_content(self, content: List, file_path: Path, file_type: str) -> None:
        """Validate list content."""
        for i, item in enumerate(content):
            if isinstance(item, dict):
                self._validate_dict_content(item, file_path, file_type)
            elif isinstance(item, list):
                self._validate_list_content(item, file_path, file_type)
            else:
                # Validate primitive values in lists
                self._validate_primitive_value(item, file_path, f"[{i}]")
    
    def _check_required_fields(self, content: Dict, file_path: Path, file_type: str) -> None:
        """Check if required fields are present."""
        # Determine which required fields to check based on file content
        if 'combat_profiles' in str(file_path) or 'combat' in str(file_path):
            required_fields = self.validation_rules['required_fields']['combat_profiles']
        elif 'travel' in str(file_path):
            required_fields = self.validation_rules['required_fields']['travel_config']
        else:
            required_fields = self.validation_rules['required_fields']['general']
        
        missing_fields = [field for field in required_fields if field not in content]
        if missing_fields:
            self.errors.append(f"Missing required fields in {file_path}: {missing_fields}")
    
    def _validate_field(self, key: str, value: Any, file_path: Path) -> None:
        """Validate a specific field."""
        # Check field type
        expected_type = self.validation_rules['field_types'].get(key)
        if expected_type and not isinstance(value, expected_type):
            self.errors.append(f"Invalid type for field '{key}' in {file_path}: expected {expected_type}, got {type(value)}")
        
        # Check value ranges
        if key in self.validation_rules['value_ranges']:
            min_val, max_val = self.validation_rules['value_ranges'][key]
            if isinstance(value, (int, float)) and (value < min_val or value > max_val):
                self.errors.append(f"Value for field '{key}' in {file_path} is out of range [{min_val}, {max_val}]: {value}")
        
        # Special validation for coordinates
        if key in ['x', 'y'] and isinstance(value, (int, float)):
            if value < -10000 or value > 10000:
                self.warnings.append(f"Coordinate value for '{key}' in {file_path} seems extreme: {value}")
        
        # Validate health thresholds
        if key in ['auto_heal', 'retreat', 'emergency_heal'] and isinstance(value, (int, float)):
            if value < 0.0 or value > 1.0:
                self.errors.append(f"Health threshold '{key}' in {file_path} must be between 0.0 and 1.0: {value}")
    
    def _validate_primitive_value(self, value: Any, file_path: Path, field_path: str) -> None:
        """Validate primitive values."""
        if isinstance(value, str):
            # Check for empty strings
            if not value.strip():
                self.warnings.append(f"Empty string value in {file_path} at {field_path}")
            
            # Check for suspicious patterns
            if re.search(r'password|secret|key|token', value.lower()):
                self.warnings.append(f"Potential sensitive information in {file_path} at {field_path}")
        
        elif isinstance(value, (int, float)):
            # Check for extreme values
            if abs(value) > 1000000:
                self.warnings.append(f"Extreme numeric value in {file_path} at {field_path}: {value}")
    
    def _validate_template_structure(self, content: Dict, file_path: Path) -> None:
        """Validate template-specific structure."""
        # Check for template metadata
        if 'template_name' not in content and 'config_name' not in content:
            self.warnings.append(f"Template file {file_path} missing template identification")
        
        # Check for version information
        if 'version' not in content:
            self.warnings.append(f"Template file {file_path} missing version information")
        
        # Check for description
        if 'description' not in content:
            self.warnings.append(f"Template file {file_path} missing description")
    
    def generate_validation_report(self, output_file: Optional[str] = None) -> str:
        """Generate a comprehensive validation report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
Configuration Validation Report
Generated: {timestamp}
=====================================

Summary:
- Files Validated: {len(self.validated_files)}
- Errors Found: {len(self.errors)}
- Warnings Found: {len(self.warnings)}

Validated Files:
{chr(10).join(f"- {file}" for file in sorted(self.validated_files))}

"""
        
        if self.errors:
            report += f"""
Errors ({len(self.errors)}):
{chr(10).join(f"{i+1}. {error}" for i, error in enumerate(self.errors))}

"""
        
        if self.warnings:
            report += f"""
Warnings ({len(self.warnings)}):
{chr(10).join(f"{i+1}. {warning}" for i, warning in enumerate(self.warnings))}

"""
        
        if not self.errors and not self.warnings:
            report += "✅ All configurations are valid!\n"
        elif not self.errors:
            report += "⚠️  Configurations have warnings but no errors.\n"
        else:
            report += "❌ Configurations have errors that need to be fixed.\n"
        
        # Write report to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                logger.info(f"Validation report written to {output_file}")
            except Exception as e:
                logger.error(f"Failed to write validation report to {output_file}: {e}")
        
        return report
    
    def fix_common_issues(self) -> List[str]:
        """Attempt to fix common configuration issues automatically."""
        fixed_issues = []
        
        for file_path in self.validated_files:
            try:
                path = Path(file_path)
                if path.suffix == '.yaml' or path.suffix == '.yml':
                    fixed = self._fix_yaml_issues(path)
                elif path.suffix == '.json':
                    fixed = self._fix_json_issues(path)
                
                if fixed:
                    fixed_issues.append(file_path)
                    
            except Exception as e:
                logger.error(f"Failed to fix issues in {file_path}: {e}")
        
        return fixed_issues
    
    def _fix_yaml_issues(self, file_path: Path) -> bool:
        """Fix common issues in YAML files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            original_content = content.copy()
            fixed = False
            
            # Fix missing required fields
            if isinstance(content, dict):
                if 'version' not in content:
                    content['version'] = '1.0.0'
                    fixed = True
                
                if 'description' not in content:
                    content['description'] = f"Configuration for {file_path.stem}"
                    fixed = True
                
                if 'last_updated' not in content:
                    content['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                    fixed = True
            
            # Write back if changes were made
            if fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(content, f, default_flow_style=False, indent=2)
                logger.info(f"Fixed issues in {file_path}")
            
            return fixed
            
        except Exception as e:
            logger.error(f"Failed to fix YAML issues in {file_path}: {e}")
            return False
    
    def _fix_json_issues(self, file_path: Path) -> bool:
        """Fix common issues in JSON files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            original_content = content.copy()
            fixed = False
            
            # Fix missing required fields
            if isinstance(content, dict):
                if 'version' not in content:
                    content['version'] = '1.0.0'
                    fixed = True
                
                if 'description' not in content:
                    content['description'] = f"Configuration for {file_path.stem}"
                    fixed = True
                
                if 'last_updated' not in content:
                    content['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                    fixed = True
            
            # Write back if changes were made
            if fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
                logger.info(f"Fixed issues in {file_path}")
            
            return fixed
            
        except Exception as e:
            logger.error(f"Failed to fix JSON issues in {file_path}: {e}")
            return False


def main():
    """Main entry point for configuration validation."""
    parser = argparse.ArgumentParser(description="Validate MS11 configuration files")
    parser.add_argument("--config-dir", default="config", help="Configuration directory to validate")
    parser.add_argument("--output", help="Output file for validation report")
    parser.add_argument("--fix", action="store_true", help="Automatically fix common issues")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize validator
    validator = ConfigurationValidator(args.config_dir)
    
    # Run validation
    errors, warnings = validator.validate_all_configurations()
    
    # Generate report
    report = validator.generate_validation_report(args.output)
    print(report)
    
    # Auto-fix if requested
    if args.fix:
        logger.info("Attempting to fix common issues...")
        fixed_files = validator.fix_common_issues()
        if fixed_files:
            logger.info(f"Fixed issues in {len(fixed_files)} files")
            # Re-validate after fixes
            errors, warnings = validator.validate_all_configurations()
            report = validator.generate_validation_report(args.output)
            print("\n" + "="*50 + "\n")
            print("Re-validation after fixes:")
            print(report)
        else:
            logger.info("No issues were automatically fixed")
    
    # Exit with error code if there are errors
    if errors:
        sys.exit(1)
    elif warnings:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
