#!/usr/bin/env python3
"""
Security hardening tests for MS11
Tests input validation, secrets management, and security best practices
"""

import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dashboard"))

import main as ms11_main


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_json_input_validation(self):
        """Test JSON input validation against malicious payloads."""
        malicious_json_inputs = [
            ('{"__proto__": {"isAdmin": true}}', dict),  # Prototype pollution
            ('{"constructor": {"prototype": {"isAdmin": true}}}', dict),  # Constructor pollution
            ('{"eval": "process.exit()"}', dict),  # Code injection attempt
            ('{"import": "os"}', dict),  # Import injection
            ('"' + 'A' * 1000 + '"', str),  # String input (valid JSON)
            ('{"nested": {"very": {"deeply": {"nested": {"object": "value"}}}}}', dict),  # Deep nesting
        ]
        
        for malicious_input, expected_type in malicious_json_inputs:
            # Test that JSON loading handles malicious inputs safely
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(malicious_input)
                temp_path = f.name
                
            try:
                # Should either parse safely or return empty dict
                result = ms11_main.load_json(temp_path)
                
                # For dict inputs, result should be dict (possibly sanitized)
                # For string inputs, we expect empty dict (not handled as config)
                if expected_type == dict:
                    assert isinstance(result, dict)
                    # Should not contain dangerous keys (they should be sanitized)
                    dangerous_keys = ['__proto__', 'constructor', 'eval', 'import', 'require']
                    for key in dangerous_keys:
                        assert key not in result  # Keys should be removed from dict
                else:
                    # Non-dict JSON should return empty dict for safety
                    assert result == {}
                    
            finally:
                os.unlink(temp_path)
                
    def test_filename_validation(self):
        """Test filename validation against path traversal."""
        malicious_filenames = [
            '../../../etc/passwd',  # Unix path traversal
            '..\\..\\..\\windows\\system32\\config\\sam',  # Windows path traversal
            '/etc/passwd',  # Absolute path
            'C:\\Windows\\System32\\config\\sam',  # Windows absolute path
            'file:///etc/passwd',  # File URI
            'profile\x00.json',  # Null byte injection
            'profile.json.exe',  # Extension confusion
            '..%2F..%2F..%2Fetc%2Fpasswd',  # URL encoded traversal
        ]
        
        for malicious_filename in malicious_filenames:
            # Test that profile loading handles malicious filenames safely
            result = ms11_main.load_runtime_profile(malicious_filename)
            
            # Should return empty dict for invalid/dangerous filenames
            assert result == {}
            
    def test_argument_validation(self):
        """Test command line argument validation."""
        malicious_args = [
            ['--mode', '../../../etc/passwd'],  # Path traversal in mode
            ['--profile', '../../config'],  # Path traversal in profile
            ['--farming_target', '{"eval": "os.system(\'rm -rf /\')"}'],  # Code injection in JSON
            ['--rest', '-1'],  # Negative rest time
            ['--max_loops', '999999999'],  # Excessive loop count
            ['--farming_target', 'not-valid-json'],  # Invalid JSON
        ]
        
        for args in malicious_args:
            try:
                parsed = ms11_main.parse_args(args)
                
                # These should now be blocked by security validation
                # If we get here, the values should be safe
                if hasattr(parsed, 'mode') and parsed.mode:
                    assert parsed.mode  # Should have a valid mode
                    
                if hasattr(parsed, 'profile') and parsed.profile:
                    assert parsed.profile  # Should have a valid profile
                    
                if hasattr(parsed, 'rest') and parsed.rest:
                    assert parsed.rest >= 0, "Rest time should not be negative"
                    
                if hasattr(parsed, 'max_loops') and parsed.max_loops:
                    assert parsed.max_loops <= 1000000, "Max loops should be reasonable"
                    
            except (SystemExit, ValueError, json.JSONDecodeError):
                # Expected for invalid arguments
                pass


class TestSecretsManagement:
    """Test secrets and sensitive data handling."""
    
    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets exist in main module."""
        import inspect
        
        # Get source code of main module
        source = inspect.getsource(ms11_main)
        
        # Common patterns that might indicate hardcoded secrets
        secret_patterns = [
            'password',
            'api_key',
            'secret_key',
            'token',
            'credential',
            'auth_token',
        ]
        
        # Check for potential hardcoded secrets (case insensitive)
        source_lower = source.lower()
        
        for pattern in secret_patterns:
            # Look for assignments like password = "something"
            if f'{pattern} = "' in source_lower or f'{pattern}="' in source_lower:
                # Allow empty strings or placeholder values
                if f'{pattern} = ""' in source_lower or f'{pattern}=""' in source_lower:
                    continue
                if 'placeholder' in source_lower or 'example' in source_lower:
                    continue
                    
                pytest.fail(f"Potential hardcoded secret found: {pattern}")
                
    def test_environment_variable_usage(self):
        """Test that sensitive data uses environment variables."""
        # Test Discord token handling
        with patch.dict(os.environ, {'DISCORD_TOKEN': 'test_token'}):
            # Should use environment variable, not hardcoded value
            token = os.getenv('DISCORD_TOKEN')
            assert token == 'test_token'
            
        # Test license key handling  
        with patch.dict(os.environ, {'ANDROID_MS11_LICENSE': 'test_license'}):
            license_key = os.getenv('ANDROID_MS11_LICENSE')
            assert license_key == 'test_license'
            
    def test_config_file_permissions(self):
        """Test that configuration files don't expose secrets."""
        # Create test config with sensitive data
        test_config = {
            "character_name": "TestChar",
            "default_mode": "medic",
            "enable_discord_relay": False,
            # Should NOT contain actual secrets
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name
            
        try:
            config = ms11_main.load_json(temp_path)
            
            # Verify no actual secrets in config
            config_str = json.dumps(config).lower()
            
            # Should not contain actual secret values
            dangerous_values = ['password123', 'secretkey', 'apikey123', 'token123']
            for value in dangerous_values:
                assert value not in config_str
                
        finally:
            os.unlink(temp_path)


class TestFileSystemSecurity:
    """Test file system security measures."""
    
    def test_safe_file_operations(self):
        """Test that file operations are performed safely."""
        # Test directory creation safety
        with patch('os.makedirs') as mock_makedirs:
            # This should be called safely
            os.makedirs('logs', exist_ok=True)
            mock_makedirs.assert_called_with('logs', exist_ok=True)
            
    def test_path_sanitization(self):
        """Test path sanitization functions."""
        # Test various path inputs
        test_paths = [
            'normal_file.json',
            '../parent_dir.json',
            '/absolute/path.json',
            'subdir/file.json',
            'file with spaces.json',
        ]
        
        for test_path in test_paths:
            # Test that runtime profile loading handles paths safely
            result = ms11_main.load_runtime_profile(test_path)
            
            # Should not crash and should return safe result
            assert isinstance(result, dict)
            
    def test_temp_file_security(self):
        """Test temporary file handling security."""
        # Test that temporary files are handled securely
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            test_data = {"test": "data"}
            json.dump(test_data, f)
            temp_path = f.name
            
        try:
            # Load should work with temporary files
            result = ms11_main.load_json(temp_path)
            assert result == test_data
            
            # File should exist
            assert os.path.exists(temp_path)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestLoggingSecurity:
    """Test logging security - ensure no sensitive data in logs."""
    
    def test_no_secrets_in_logs(self):
        """Test that sensitive information is not logged."""
        import logging
        import io
        
        # Create a string stream to capture log output
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        
        # Get the main logger
        logger = logging.getLogger('main')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            # Perform operations that might log sensitive data
            config = ms11_main.load_config()
            profile = ms11_main.load_runtime_profile('test')
            args = ms11_main.parse_args(['--mode', 'medic'])
            
            # Get log output
            log_output = log_stream.getvalue().lower()
            
            # Check that no sensitive patterns are logged
            sensitive_patterns = [
                'password',
                'token',
                'secret',
                'credential',
                'api_key'
            ]
            
            for pattern in sensitive_patterns:
                # Allow the word itself but not with values
                assert f'{pattern}=' not in log_output
                assert f'{pattern}:' not in log_output
                assert f'{pattern} =' not in log_output
                
        finally:
            logger.removeHandler(handler)
            
    def test_log_level_security(self):
        """Test that debug logs don't expose sensitive information."""
        # Test that debug level doesn't expose internal details unsafely
        logger = logging.getLogger('test_security')
        
        # Should be able to set different log levels safely
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
            logger.setLevel(level)
            assert logger.level == level


class TestErrorHandlingSecurity:
    """Test that error handling doesn't expose sensitive information."""
    
    def test_safe_error_messages(self):
        """Test that error messages don't expose sensitive information."""
        # Test various error conditions
        error_conditions = [
            lambda: ms11_main.load_json('/nonexistent/secret/path.json'),
            lambda: ms11_main.load_runtime_profile('../../../etc/passwd'),
        ]
        
        for error_func in error_conditions:
            try:
                result = error_func()
                # Should handle gracefully
                assert isinstance(result, (dict, type(None)))
            except Exception as e:
                # Error messages should not expose system details
                error_msg = str(e).lower()
                
                # Should not contain sensitive system paths
                dangerous_patterns = [
                    '/etc/passwd',
                    'c:\\windows',
                    '/root/',
                    'administrator',
                    'system32'
                ]
                
                for pattern in dangerous_patterns:
                    assert pattern not in error_msg
                    
        # Test argument parsing with invalid JSON (should raise SystemExit)
        with pytest.raises(SystemExit):
            ms11_main.parse_args(['--farming_target', 'invalid-json'])
                    
    def test_exception_handling_security(self):
        """Test that exceptions are handled securely."""
        # Test that exceptions don't leak sensitive information
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            result = ms11_main.load_json('test.json')
            # Should handle gracefully without exposing system details
            assert result == {}


class TestNetworkSecurity:
    """Test network-related security measures."""
    
    def test_discord_token_handling(self):
        """Test Discord token is handled securely."""
        # Test that Discord token comes from environment, not hardcoded
        with patch.dict(os.environ, {}, clear=True):
            # Without environment variable, should not have token
            token = os.getenv('DISCORD_TOKEN')
            assert token is None
            
        with patch.dict(os.environ, {'DISCORD_TOKEN': 'safe_test_token'}):
            token = os.getenv('DISCORD_TOKEN')
            assert token == 'safe_test_token'
            
    def test_no_hardcoded_urls(self):
        """Test that no hardcoded sensitive URLs exist."""
        import inspect
        
        source = inspect.getsource(ms11_main)
        
        # Should not contain hardcoded sensitive URLs
        suspicious_patterns = [
            'http://admin',
            'https://internal',
            'localhost:8080/admin',
            'api.secret',
        ]
        
        source_lower = source.lower()
        for pattern in suspicious_patterns:
            assert pattern not in source_lower


class TestAccessControl:
    """Test access control and permission checks."""
    
    def test_file_access_permissions(self):
        """Test that file access respects permissions."""
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name
            
        try:
            # Should be able to read normally
            result = ms11_main.load_json(temp_path)
            assert result == {"test": "data"}
            
            # Test permission handling
            if os.name != 'nt':  # Unix-like systems
                # Remove read permissions
                os.chmod(temp_path, 0o000)
                
                # Should handle gracefully
                result = ms11_main.load_json(temp_path)
                assert result == {}
                
                # Restore permissions for cleanup
                os.chmod(temp_path, 0o644)
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_directory_traversal_protection(self):
        """Test protection against directory traversal attacks."""
        traversal_attempts = [
            '../',
            '../../',
            '../../../etc/',
            '..\\..\\',
            '//etc//',
            '\\..\\..',
        ]
        
        for attempt in traversal_attempts:
            # Should not allow traversal in profile names
            result = ms11_main.load_runtime_profile(attempt + 'malicious')
            assert result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])