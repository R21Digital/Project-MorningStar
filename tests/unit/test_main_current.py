#!/usr/bin/env python3
"""
Modern test suite for src/main.py - current implementation
Tests the actual MS11 main module with fallback implementations
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import main


class TestArgumentParsing:
    """Test command line argument parsing."""
    
    def test_parse_args_defaults(self):
        """Test default argument values."""
        args = main.parse_args([])
        assert args.mode is None
        assert args.profile is None
        assert args.smart is False
        assert args.loop is False
        assert args.repeat is False
        assert args.rest == 10
        assert args.max_loops is None
        assert args.train is False
        
    def test_parse_args_mode(self):
        """Test mode argument."""
        args = main.parse_args(['--mode', 'medic'])
        assert args.mode == 'medic'
        
    def test_parse_args_profile(self):
        """Test profile argument.""" 
        args = main.parse_args(['--profile', 'test_profile'])
        assert args.profile == 'test_profile'
        
    def test_parse_args_smart(self):
        """Test smart mode flag."""
        args = main.parse_args(['--smart'])
        assert args.smart is True
        
    def test_parse_args_loop(self):
        """Test loop mode flag."""
        args = main.parse_args(['--loop'])
        assert args.loop is True
        
    def test_parse_args_repeat(self):
        """Test repeat mode flag."""
        args = main.parse_args(['--repeat'])
        assert args.repeat is True
        
    def test_parse_args_rest(self):
        """Test rest time parameter."""
        args = main.parse_args(['--rest', '30'])
        assert args.rest == 30
        
    def test_parse_args_max_loops(self):
        """Test max loops parameter."""
        args = main.parse_args(['--max_loops', '5'])
        assert args.max_loops == 5
        
    def test_parse_args_train(self):
        """Test training flag."""
        args = main.parse_args(['--train'])
        assert args.train is True
        
    def test_parse_args_farming_target_json(self):
        """Test farming target JSON parsing."""
        target = '{"planet": "tatooine", "city": "mos_eisley"}'
        args = main.parse_args(['--farming_target', target])
        expected = {"planet": "tatooine", "city": "mos_eisley"}
        assert args.farming_target == expected
        
    def test_parse_args_farming_target_invalid_json(self):
        """Test invalid farming target JSON."""
        with pytest.raises(SystemExit):
            main.parse_args(['--farming_target', 'invalid-json'])


class TestConfigurationLoading:
    """Test configuration file loading."""
    
    def test_load_json_valid_file(self):
        """Test loading valid JSON file."""
        test_data = {"key": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
            
        try:
            result = main.load_json(temp_path)
            assert result == test_data
        finally:
            os.unlink(temp_path)
            
    def test_load_json_missing_file(self):
        """Test loading non-existent JSON file."""
        result = main.load_json('/nonexistent/path.json')
        assert result == {}
        
    def test_load_json_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name
            
        try:
            result = main.load_json(temp_path)
            assert result == {}
        finally:
            os.unlink(temp_path)
            
    def test_load_config_defaults(self):
        """Test loading config with defaults when file missing."""
        config = main.load_config('/nonexistent/config.json')
        assert config["character_name"] == "Default"
        assert config["default_mode"] == "medic"
        assert config["enable_discord_relay"] is False
        
    def test_load_runtime_profile_missing(self):
        """Test loading missing runtime profile."""
        result = main.load_runtime_profile('nonexistent')
        assert result == {}
        
    def test_load_runtime_profile_valid(self):
        """Test loading valid runtime profile."""
        test_profile = {
            "character_name": "TestChar",
            "mode": "medic",
            "character_skills": {"healing": 100}
        }
        
        # Create temporary profile directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_path = Path(temp_dir) / "test.json"
            with open(profile_path, 'w') as f:
                json.dump(test_profile, f)
                
            result = main.load_runtime_profile('test', str(temp_dir))
            assert result == test_profile


class TestModeHandling:
    """Test mode handler functionality."""
    
    def test_mode_handlers_dict_exists(self):
        """Test that MODE_HANDLERS dictionary exists."""
        assert hasattr(main, 'MODE_HANDLERS')
        assert isinstance(main.MODE_HANDLERS, dict)
        
    def test_mode_handlers_contains_expected_modes(self):
        """Test that expected modes are in handlers."""
        expected_modes = [
            "quest", "profession", "combat", "dancer", "medic",
            "crafting", "whisper", "support", "follow", "bounty",
            "entertainer", "rls", "special-goals"
        ]
        
        for mode in expected_modes:
            assert mode in main.MODE_HANDLERS
            
    def test_run_mode_unknown_mode(self):
        """Test running unknown mode returns empty dict."""
        session_mock = Mock()
        profile_mock = {"character_name": "test"}  # Valid profile to pass assert_profile_ready
        config_mock = {}
        
        result = main.run_mode(
            "unknown_mode", 
            session_mock, 
            profile_mock, 
            config_mock
        )
        assert result == {}
        
    def test_run_mode_with_handler(self):
        """Test running mode with valid handler."""
        # Mock handler function
        handler_mock = Mock(return_value={"status": "success"})
        
        # Temporarily add test handler
        main.MODE_HANDLERS["test_mode"] = handler_mock
        
        session_mock = Mock()
        profile_mock = {"character_name": "test"}
        config_mock = {}
        
        try:
            result = main.run_mode(
                "test_mode", 
                session_mock, 
                profile_mock, 
                config_mock
            )
            assert result == {"status": "success"}
            handler_mock.assert_called_once()
        finally:
            # Clean up test handler
            if "test_mode" in main.MODE_HANDLERS:
                del main.MODE_HANDLERS["test_mode"]


class TestMainFunction:
    """Test main function behavior."""
    
    @patch('main.load_config')
    @patch('main.load_required_profile')  
    @patch('main.SessionManager')
    @patch('main.WindowManager')
    def test_main_requires_profile(self, mock_window_mgr, mock_session_mgr, 
                                   mock_load_profile, mock_load_config, capsys):
        """Test main exits when no profile provided."""
        mock_load_config.return_value = {}
        
        # Call main without profile
        main.main(['--mode', 'medic'])
        
        # Check error message was printed
        captured = capsys.readouterr()
        assert "--profile is required" in captured.out
        
    @patch('main.load_config')
    @patch('main.load_required_profile')
    @patch('main.SessionManager')
    @patch('main.WindowManager')
    @patch('main.run_mode')
    @patch('main.state_tracker')
    def test_main_runs_with_profile(self, mock_state_tracker, mock_run_mode, 
                                   mock_window_mgr, mock_session_mgr, 
                                   mock_load_profile, mock_load_config):
        """Test main runs successfully with profile."""
        # Setup mocks
        mock_load_config.return_value = {"default_mode": "medic"}
        mock_load_profile.return_value = {"character_name": "Test", "mode": "medic"}
        mock_session = Mock()
        mock_session_mgr.return_value = mock_session
        mock_window_mgr_instance = Mock()
        mock_window_mgr.return_value = mock_window_mgr_instance
        mock_run_mode.return_value = {"status": "complete"}
        
        # Mock state_tracker methods
        mock_state_tracker.reset_state.return_value = None
        mock_state_tracker.get_state.return_value = {"mode": "medic", "fatigue_level": 0}
        
        # Call main with profile
        main.main(['--profile', 'test', '--mode', 'medic'])
        
        # Verify session manager was created
        mock_session_mgr.assert_called_once()
        mock_window_mgr.assert_called_once_with(mock_session)
        
        # Verify state_tracker was called
        mock_state_tracker.reset_state.assert_called_once()
        
        # Verify run_mode was called
        mock_run_mode.assert_called()


class TestFallbackImplementations:
    """Test fallback implementation behavior when core modules missing."""
    
    def test_fallback_session_manager_creation(self):
        """Test fallback SessionManager can be created."""
        # This tests the fallback class defined when core modules unavailable
        session_mgr = main.SessionManager()
        assert session_mgr is not None
        
    def test_fallback_window_manager_creation(self):
        """Test fallback WindowManager can be created.""" 
        session_mock = Mock()
        window_mgr = main.WindowManager(session_mock)
        assert window_mgr is not None
        
    def test_fallback_functions_exist(self):
        """Test fallback functions are available."""
        # Test fallback functions defined when modules unavailable
        assert callable(main.monitor_session)
        assert callable(main.log_event)
        
        # Test they can be called without error
        result = main.monitor_session({})
        assert isinstance(result, dict)
        
        main.log_event("test_event")


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_check_and_train_skills(self):
        """Test skill training check function."""
        agent_mock = Mock()
        character_skills = {"healing": 50}
        profession_tree = {"medic": {"healing": 100}}
        
        # Should not raise exception even with missing dependencies
        main.check_and_train_skills(agent_mock, character_skills, profession_tree)


if __name__ == "__main__":
    pytest.main([__file__])