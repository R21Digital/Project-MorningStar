#!/usr/bin/env python3
"""
Test script for MS11 Configuration Automation System
Verifies that all components work correctly.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_configuration_validation():
    """Test the configuration validation system."""
    logger.info("Testing configuration validation...")
    
    try:
        from validate_configurations import ConfigurationValidator
        
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test configuration files
            test_yaml = temp_path / "test_config.yaml"
            test_yaml.write_text("""
name: "Test Configuration"
description: "Test configuration for validation"
version: "1.0.0"
enabled: true
timeout: 30
coordinates:
  x: 100
  y: 200
""")
            
            test_json = temp_path / "test_config.json"
            test_json.write_text('''{
    "name": "Test JSON Config",
    "description": "Test JSON configuration",
    "version": "1.0.0",
    "enabled": true,
    "timeout": 60
}''')
            
            # Test validation
            validator = ConfigurationValidator(temp_dir)
            errors, warnings = validator.validate_all_configurations()
            
            if errors:
                logger.error(f"Validation test failed with {len(errors)} errors:")
                for error in errors:
                    logger.error(f"  - {error}")
                return False
            
            if warnings:
                logger.warning(f"Validation test completed with {len(warnings)} warnings:")
                for warning in warnings:
                    logger.warning(f"  - {warning}")
            
            logger.info("✅ Configuration validation test passed")
            return True
            
    except Exception as e:
        logger.error(f"Configuration validation test failed: {e}")
        return False


def test_configuration_deployment():
    """Test the configuration deployment system."""
    logger.info("Testing configuration deployment...")
    
    try:
        from deploy_configurations import ConfigurationDeployer
        
        # Create temporary test directories
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create source and target directories
            source_dir = temp_path / "source"
            target_dir = temp_path / "target"
            source_dir.mkdir()
            target_dir.mkdir()
            
            # Create test configuration
            test_config = source_dir / "test.yaml"
            test_config.write_text("""
name: "Test Deploy Config"
description: "Test configuration for deployment"
version: "1.0.0"
""")
            
            # Test deployment
            deployer = ConfigurationDeployer(str(source_dir))
            
            # Override environment paths for testing
            deployer.environments['test'] = {
                'path': str(target_dir),
                'backup': False,
                'validate': False,
                'notify': False
            }
            
            success = deployer.deploy_to_environment('test', dry_run=True)
            
            if success:
                logger.info("✅ Configuration deployment test passed")
                return True
            else:
                logger.error("Configuration deployment test failed")
                return False
                
    except Exception as e:
        logger.error(f"Configuration deployment test failed: {e}")
        return False


def test_template_loading():
    """Test that configuration templates can be loaded."""
    logger.info("Testing template loading...")
    
    try:
        import yaml
        
        # Test combat profile template
        combat_template_path = Path("config/templates/combat_profile_template.yaml")
        if combat_template_path.exists():
            with open(combat_template_path, 'r') as f:
                combat_data = yaml.safe_load(f)
            
            if combat_data and 'profile_name' in combat_data:
                logger.info("✅ Combat profile template loaded successfully")
            else:
                logger.error("Combat profile template is invalid")
                return False
        else:
            logger.warning("Combat profile template not found, skipping test")
        
        # Test travel configuration template
        travel_template_path = Path("config/templates/travel_config_template.yaml")
        if travel_template_path.exists():
            with open(travel_template_path, 'r') as f:
                travel_data = yaml.safe_load(f)
            
            if travel_data and 'config_name' in travel_data:
                logger.info("✅ Travel configuration template loaded successfully")
            else:
                logger.error("Travel configuration template is invalid")
                return False
        else:
            logger.warning("Travel configuration template not found, skipping test")
        
        logger.info("✅ Template loading test passed")
        return True
        
    except Exception as e:
        logger.error(f"Template loading test failed: {e}")
        return False


def test_file_structure():
    """Test that the required file structure exists."""
    logger.info("Testing file structure...")
    
    required_files = [
        "scripts/qa/configuration_automation.py",
        "scripts/qa/validate_configurations.py",
        "scripts/qa/deploy_configurations.py",
        "config/templates/combat_profile_template.yaml",
        "config/templates/travel_config_template.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing required files: {missing_files}")
        return False
    
    logger.info("✅ File structure test passed")
    return True


def run_all_tests():
    """Run all configuration automation tests."""
    logger.info("Starting MS11 Configuration Automation System tests...")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Template Loading", test_template_loading),
        ("Configuration Validation", test_configuration_validation),
        ("Configuration Deployment", test_configuration_deployment)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info(f"\nTotal: {passed + failed} tests")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    
    if failed == 0:
        logger.info("\n🎉 All tests passed! Configuration automation system is working correctly.")
        return True
    else:
        logger.error(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        return False


def main():
    """Main entry point for testing."""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Testing failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
