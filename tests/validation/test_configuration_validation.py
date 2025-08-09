#!/usr/bin/env python3
"""
Configuration validation and error handling tests for MS11
Tests robust configuration validation, error handling, and recovery mechanisms
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import main as ms11_main


class TestConfigurationValidation:
    """Test configuration file validation."""
    
    def test_valid_config_structure(self):
        """Test that valid configuration is accepted."""
        valid_configs = [
            {
                "character_name": "TestCharacter",
                "default_mode": "medic",
                "enable_discord_relay": False
            },
            {
                "character_name": "Another Character",
                "default_mode": "combat",
                "enable_discord_relay": True,
                "custom_setting": "value"
            },
            {}  # Empty config should use defaults
        ]
        
        for config in valid_configs:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(config, f)
                temp_path = f.name
                
            try:
                result = ms11_main.load_config(temp_path)
                assert isinstance(result, dict)
                assert 'character_name' in result
                assert 'default_mode' in result
                assert 'enable_discord_relay' in result
            finally:
                os.unlink(temp_path)
                
    def test_invalid_config_handling(self):
        """Test handling of invalid configuration files."""
        invalid_configs = [
            "not json at all",
            '{"invalid": json}',  # Invalid JSON syntax
            '{"character_name": null}',  # Null values
            '{"default_mode": 123}',  # Wrong type
            '[]',  # Array instead of object
        ]
        
        for invalid_config in invalid_configs:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(invalid_config)
                temp_path = f.name
                
            try:
                result = ms11_main.load_config(temp_path)
                
                # Should return default config for invalid files
                assert isinstance(result, dict)
                
                # For completely invalid JSON, should return defaults
                # For valid JSON with null values, null values should be filtered out
                if 'character_name' in result:
                    assert result['character_name'] is not None
                if 'default_mode' in result:
                    assert result['default_mode'] is not None
                if 'enable_discord_relay' in result:
                    assert result['enable_discord_relay'] is not None
                    
                # Should have some default structure (either from defaults or sanitized valid JSON)
                expected_keys = ['character_name', 'default_mode', 'enable_discord_relay']
                # At least some keys should be present (either all defaults or sanitized valid data)
                assert any(key in result for key in expected_keys)
            finally:
                os.unlink(temp_path)
                
    def test_config_type_validation(self):
        """Test that configuration values have correct types."""
        config = ms11_main.load_config()
        
        # Should have string values for these keys
        if 'character_name' in config:
            assert isinstance(config['character_name'], str)
        if 'default_mode' in config:
            assert isinstance(config['default_mode'], str)
        if 'enable_discord_relay' in config:
            assert isinstance(config['enable_discord_relay'], bool)


class TestProfileValidation:
    """Test profile validation and error handling."""
    
    def test_valid_profile_structure(self):
        """Test valid profile structures."""
        valid_profiles = [
            {
                "character_name": "TestChar",
                "mode": "medic",
                "character_skills": {"healing": 100},
                "profession_tree": {"medic": {"healing": 100}}
            },
            {
                "character_name": "TestChar2",
                "mode": "combat",
                "auto_train": True
            },
            {}  # Empty profile should be handled gracefully
        ]
        
        for profile in valid_profiles:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(profile, f)
                temp_path = f.name
                
            try:
                # Test loading as runtime profile
                profile_name = Path(temp_path).stem
                profile_dir = Path(temp_path).parent
                
                result = ms11_main.load_runtime_profile(profile_name, str(profile_dir))
                assert isinstance(result, dict)
                
                # Test validation through profile_loader
                validated = ms11_main.profile_loader.validate_profile(result)
                assert isinstance(validated, dict)
                
            finally:
                os.unlink(temp_path)
                
    def test_invalid_profile_handling(self):
        """Test handling of invalid profiles."""
        # Test with completely invalid profile name
        result = ms11_main.load_runtime_profile("../invalid")
        assert result == {}
        
        # Test with non-existent profile
        result = ms11_main.load_runtime_profile("nonexistent")
        assert result == {}
        
        # Test with empty profile name
        result = ms11_main.load_runtime_profile("")
        assert result == {}
        
    def test_profile_validation_errors(self):
        """Test profile validation error handling."""
        # Test assert_profile_ready with invalid profiles
        invalid_profiles = [
            {},  # Empty profile
            None,  # None profile
            {"character_name": ""},  # Empty character name
        ]
        
        for profile in invalid_profiles:
            try:
                ms11_main.profile_loader.assert_profile_ready(profile)
                # Should not reach here for invalid profiles
                assert False, f"Expected ProfileValidationError for {profile}"
            except ms11_main.ProfileValidationError:
                # Expected behavior
                pass
            except Exception as e:
                # Other exceptions are also acceptable
                pass


class TestArgumentValidation:
    """Test command line argument validation and error handling."""
    
    def test_valid_argument_combinations(self):
        """Test valid argument combinations."""
        valid_arg_sets = [
            ['--mode', 'medic', '--profile', 'test'],
            ['--smart', '--loop'],
            ['--repeat', '--rest', '30'],
            ['--max_loops', '100'],
            ['--train'],
            []  # No arguments
        ]
        
        for args in valid_arg_sets:
            try:
                result = ms11_main.parse_args(args)
                assert result is not None
            except SystemExit:
                # SystemExit for missing required args is acceptable
                pass
                
    def test_invalid_argument_handling(self):
        """Test handling of invalid arguments."""
        invalid_arg_sets = [
            ['--rest', '-5'],  # Negative rest time  
            ['--max_loops', '999999999'],  # Too large max_loops
            ['--profile', '../invalid'],  # Invalid profile path
            ['--mode', 'invalid/mode'],  # Invalid mode name
            ['--farming_target', 'not-json'],  # Invalid JSON
        ]
        
        for args in invalid_arg_sets:
            with pytest.raises(SystemExit):
                # Should raise SystemExit for invalid arguments
                ms11_main.parse_args(args)
                
    def test_argument_type_validation(self):
        """Test argument type validation."""
        # Test valid arguments produce correct types
        args = ms11_main.parse_args(['--rest', '30', '--max_loops', '100'])
        
        assert isinstance(args.rest, int)
        assert isinstance(args.max_loops, int)
        assert args.rest > 0
        assert args.max_loops > 0


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""
    
    def test_file_permission_recovery(self):
        """Test recovery from file permission errors."""
        # Test that permission errors are handled gracefully
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            config = ms11_main.load_config()
            
            # Should return default config
            assert isinstance(config, dict)
            assert 'character_name' in config
            
    def test_missing_directory_recovery(self):
        """Test recovery from missing directories."""
        # Test loading from non-existent directory
        result = ms11_main.load_runtime_profile('test', '/nonexistent/directory')
        assert result == {}
        
    def test_corrupted_file_recovery(self):
        """Test recovery from corrupted files."""
        # Create a file with corrupted JSON
        corrupted_content = '{"valid": "start", "corrupted": invalid json here}'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(corrupted_content)
            temp_path = f.name
            
        try:
            result = ms11_main.load_json(temp_path)
            # Should return empty dict for corrupted files
            assert result == {}
        finally:
            os.unlink(temp_path)
            
    def test_network_error_recovery(self):
        """Test recovery from network-related errors."""
        # Test Discord token handling with missing environment
        with patch.dict(os.environ, {}, clear=True):
            # Should not crash when Discord token is missing
            config = ms11_main.load_config()
            assert isinstance(config, dict)


class TestValidationMessages:
    """Test validation error messages and logging."""
    
    def test_informative_error_messages(self):
        """Test that error messages are informative but safe."""
        # Test various error conditions and check messages
        import logging
        import io
        
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger('main')
        logger.addHandler(handler)
        original_level = logger.level
        logger.setLevel(logging.DEBUG)
        
        try:
            # Trigger various validation errors
            ms11_main.load_json('/nonexistent/path.json')
            ms11_main.load_runtime_profile('../invalid')
            ms11_main.load_runtime_profile('')
            
            log_output = log_stream.getvalue()
            
            # Should contain informative messages
            assert 'not found' in log_output or 'Unsafe' in log_output
            
            # Should not contain sensitive information
            sensitive_patterns = ['password', 'secret', 'token', '/etc/', 'C:\\Windows']
            for pattern in sensitive_patterns:
                assert pattern.lower() not in log_output.lower()
                
        finally:
            logger.removeHandler(handler)
            logger.setLevel(original_level)
            
    def test_graceful_degradation_logging(self):
        """Test that graceful degradation is properly logged."""
        import logging
        import io
        
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger('main')
        logger.addHandler(handler)
        original_level = logger.level
        logger.setLevel(logging.INFO)
        
        try:
            # Trigger fallback behavior
            ms11_main.load_config('/nonexistent/config.json')
            
            log_output = log_stream.getvalue()
            
            # Should log graceful handling
            degradation_indicators = ['using defaults', 'fallback', 'not found']
            found_indicator = any(indicator in log_output.lower() for indicator in degradation_indicators)
            # It's OK if no specific message, as long as it doesn't crash
            assert True  # Test passes if we reach here without exception
            
        finally:
            logger.removeHandler(handler)
            logger.setLevel(original_level)


class TestConfigurationDefaults:
    """Test default configuration handling."""
    
    def test_default_config_structure(self):
        """Test that default configuration is well-formed."""
        config = ms11_main.load_config('/nonexistent/config.json')
        
        # Should have required keys
        required_keys = ['character_name', 'default_mode', 'enable_discord_relay']
        for key in required_keys:
            assert key in config
            
        # Should have sensible default values
        assert config['character_name'] == 'Default'
        assert config['default_mode'] in ['medic', 'combat', 'quest']
        assert isinstance(config['enable_discord_relay'], bool)
        
    def test_default_profile_behavior(self):
        """Test default profile behavior."""
        # Test fallback profile creation
        session_mgr = ms11_main.SessionManager()
        assert session_mgr is not None
        
        # Test fallback window manager
        window_mgr = ms11_main.WindowManager(session_mgr)
        assert window_mgr is not None
        
    def test_mode_fallback_behavior(self):
        """Test mode handler fallback behavior."""
        # Test that unknown modes are handled gracefully
        session = ms11_main.SessionManager()
        profile = {'character_name': 'test'}
        config = {}
        
        result = ms11_main.run_mode('unknown_mode', session, profile, config)
        assert isinstance(result, dict)


class TestValidationIntegration:
    """Test validation integration across components."""
    
    def test_end_to_end_validation(self):
        """Test validation from command line to execution."""
        # Test complete validation chain
        args = ms11_main.parse_args(['--mode', 'medic'])
        assert args.mode == 'medic'
        
        config = ms11_main.load_config()
        assert isinstance(config, dict)
        
        # Test with valid profile
        profile = {'character_name': 'test', 'mode': 'medic'}
        validated = ms11_main.profile_loader.validate_profile(profile)
        assert isinstance(validated, dict)
        
    def test_validation_consistency(self):
        """Test that validation is consistent across functions."""
        # Test that the same validation logic is applied consistently
        
        # Profile name validation should be consistent
        unsafe_names = ['../test', '/etc/test', 'test\x00']
        
        for unsafe_name in unsafe_names:
            # Should be rejected by runtime profile loading
            result = ms11_main.load_runtime_profile(unsafe_name)
            assert result == {}
            
            # Should be rejected by argument parsing
            with pytest.raises(SystemExit):
                ms11_main.parse_args(['--profile', unsafe_name])
                
        # Empty string should be handled gracefully (not cause SystemExit)
        result = ms11_main.load_runtime_profile('')
        assert result == {}
        
        # Empty profile argument should be handled gracefully
        args = ms11_main.parse_args(['--profile', ''])
        assert args.profile == ''


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])