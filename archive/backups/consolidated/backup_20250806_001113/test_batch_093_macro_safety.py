#!/usr/bin/env python3
"""
MS11 Batch 093 - Macro Safety + Auto-Cancellation System Tests

This test suite validates the macro safety system's functionality including:
- Performance monitoring
- Macro safety profiles
- Auto-cancellation logic
- Discord notifications
- Per-profile overrides
- Logging and reporting
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the macro safety system
from core.macro_safety import (
    MacroSafetyManager,
    PerformanceMonitor,
    MacroSafetyProfile,
    SafetyLevel,
    PerformanceThresholds,
    PerformanceSnapshot,
    MacroCancellationEvent
)


class TestPerformanceMonitor:
    """Test the PerformanceMonitor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor(history_size=10)
    
    def teardown_method(self):
        """Clean up after tests."""
        if self.monitor.monitoring:
            self.monitor.stop_monitoring()
    
    def test_initialization(self):
        """Test PerformanceMonitor initialization."""
        assert self.monitor.history_size == 10
        assert len(self.monitor.performance_history) == 0
        assert not self.monitor.monitoring
        assert self.monitor.monitor_thread is None
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring."""
        # Start monitoring
        self.monitor.start_monitoring(interval=0.1)
        assert self.monitor.monitoring
        assert self.monitor.monitor_thread is not None
        assert self.monitor.monitor_thread.is_alive()
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        assert not self.monitor.monitoring
    
    def test_take_performance_snapshot(self):
        """Test taking performance snapshots."""
        snapshot = self.monitor._take_performance_snapshot()
        
        assert isinstance(snapshot, PerformanceSnapshot)
        assert isinstance(snapshot.timestamp, datetime)
        assert isinstance(snapshot.cpu_usage, float)
        assert isinstance(snapshot.memory_usage, float)
        assert 0 <= snapshot.cpu_usage <= 100
        assert 0 <= snapshot.memory_usage <= 100
    
    def test_get_current_metrics(self):
        """Test getting current metrics."""
        metrics = self.monitor.get_current_metrics()
        assert isinstance(metrics, PerformanceSnapshot)
    
    def test_get_average_metrics_empty_history(self):
        """Test getting average metrics with empty history."""
        avg_metrics = self.monitor.get_average_metrics(30)
        assert isinstance(avg_metrics, PerformanceSnapshot)
    
    def test_get_average_metrics_with_history(self):
        """Test getting average metrics with history."""
        # Add some test snapshots
        for i in range(5):
            snapshot = PerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_usage=50.0 + i,
                memory_usage=60.0 + i
            )
            self.monitor.performance_history.append(snapshot)
        
        avg_metrics = self.monitor.get_average_metrics(30)
        assert isinstance(avg_metrics, PerformanceSnapshot)
        assert 50.0 <= avg_metrics.cpu_usage <= 54.0
        assert 60.0 <= avg_metrics.memory_usage <= 64.0
    
    def test_monitor_loop_error_handling(self):
        """Test error handling in monitor loop."""
        with patch.object(self.monitor, '_take_performance_snapshot', side_effect=Exception("Test error")):
            self.monitor.start_monitoring(interval=0.1)
            time.sleep(0.2)  # Let it run for a bit
            self.monitor.stop_monitoring()
            # Should not crash despite errors


class TestMacroSafetyProfile:
    """Test the MacroSafetyProfile class."""
    
    def test_initialization(self):
        """Test MacroSafetyProfile initialization."""
        profile = MacroSafetyProfile(
            macro_id="test",
            name="Test Macro",
            category="test",
            safety_level=SafetyLevel.SAFE
        )
        
        assert profile.macro_id == "test"
        assert profile.name == "Test Macro"
        assert profile.category == "test"
        assert profile.safety_level == SafetyLevel.SAFE
        assert profile.max_duration == 300
        assert profile.auto_cancel_enabled is True
        assert profile.discord_notify is True
        assert profile.description == ""
        assert isinstance(profile.performance_thresholds, PerformanceThresholds)
    
    def test_initialization_with_custom_thresholds(self):
        """Test initialization with custom performance thresholds."""
        custom_thresholds = PerformanceThresholds(
            cpu_usage_max=70.0,
            memory_usage_max=75.0,
            fps_min=20.0,
            latency_max=300.0,
            response_time_max=800.0
        )
        
        profile = MacroSafetyProfile(
            macro_id="test",
            name="Test Macro",
            category="test",
            safety_level=SafetyLevel.RISKY,
            max_duration=600,
            performance_thresholds=custom_thresholds,
            auto_cancel_enabled=False,
            discord_notify=False,
            description="Test description"
        )
        
        assert profile.performance_thresholds == custom_thresholds
        assert profile.max_duration == 600
        assert profile.auto_cancel_enabled is False
        assert profile.discord_notify is False
        assert profile.description == "Test description"


class TestPerformanceThresholds:
    """Test the PerformanceThresholds class."""
    
    def test_default_values(self):
        """Test default threshold values."""
        thresholds = PerformanceThresholds()
        
        assert thresholds.cpu_usage_max == 80.0
        assert thresholds.memory_usage_max == 85.0
        assert thresholds.fps_min == 15.0
        assert thresholds.latency_max == 500.0
        assert thresholds.response_time_max == 1000.0
    
    def test_custom_values(self):
        """Test custom threshold values."""
        thresholds = PerformanceThresholds(
            cpu_usage_max=70.0,
            memory_usage_max=75.0,
            fps_min=25.0,
            latency_max=300.0,
            response_time_max=800.0
        )
        
        assert thresholds.cpu_usage_max == 70.0
        assert thresholds.memory_usage_max == 75.0
        assert thresholds.fps_min == 25.0
        assert thresholds.latency_max == 300.0
        assert thresholds.response_time_max == 800.0


class TestMacroSafetyManager:
    """Test the MacroSafetyManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for test profiles
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MacroSafetyManager(profiles_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up after tests."""
        self.manager.cleanup()
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test MacroSafetyManager initialization."""
        assert isinstance(self.manager.performance_monitor, PerformanceMonitor)
        assert len(self.manager.active_macros) == 0
        assert len(self.manager.safety_profiles) > 0  # Should have default profiles
        assert len(self.manager.cancellation_events) == 0
        assert self.manager.performance_monitor.monitoring
    
    def test_load_default_profiles(self):
        """Test loading default safety profiles."""
        # Check that default profiles are loaded
        expected_profiles = ["heal", "buff", "attack", "craft", "travel", "dance"]
        for profile_id in expected_profiles:
            assert profile_id in self.manager.safety_profiles
        
        # Check a specific profile
        heal_profile = self.manager.safety_profiles["heal"]
        assert heal_profile.name == "Heal Macro"
        assert heal_profile.category == "combat"
        assert heal_profile.safety_level == SafetyLevel.SAFE
    
    def test_start_macro(self):
        """Test starting a macro."""
        # Start a macro
        success = self.manager.start_macro("test_macro", "Test Macro")
        assert success is True
        assert "test_macro" in self.manager.active_macros
        
        # Check macro info
        macro_info = self.manager.active_macros["test_macro"]
        assert macro_info["name"] == "Test Macro"
        assert isinstance(macro_info["start_time"], datetime)
        assert macro_info["profile"].macro_id == "test_macro"
    
    def test_start_macro_already_running(self):
        """Test starting a macro that's already running."""
        # Start macro first time
        success1 = self.manager.start_macro("test_macro", "Test Macro")
        assert success1 is True
        
        # Try to start same macro again
        success2 = self.manager.start_macro("test_macro", "Test Macro")
        assert success2 is False
    
    def test_start_macro_with_unknown_id(self):
        """Test starting a macro with unknown ID."""
        success = self.manager.start_macro("unknown_macro", "Unknown Macro")
        assert success is True
        
        # Should create default profile
        assert "unknown_macro" in self.manager.safety_profiles
        profile = self.manager.safety_profiles["unknown_macro"]
        assert profile.safety_level == SafetyLevel.RISKY
        assert profile.max_duration == 300
    
    def test_stop_macro(self):
        """Test stopping a macro."""
        # Start a macro
        self.manager.start_macro("test_macro", "Test Macro")
        assert "test_macro" in self.manager.active_macros
        
        # Stop the macro
        success = self.manager.stop_macro("test_macro")
        assert success is True
        assert "test_macro" not in self.manager.active_macros
    
    def test_stop_macro_not_running(self):
        """Test stopping a macro that's not running."""
        success = self.manager.stop_macro("nonexistent_macro")
        assert success is False
    
    def test_check_macro_safety_no_cancellations(self):
        """Test safety check with no cancellations."""
        # Start a safe macro
        self.manager.start_macro("heal", "Heal Macro")
        
        # Check safety
        cancellations = self.manager.check_macro_safety()
        assert len(cancellations) == 0
    
    def test_check_macro_safety_duration_exceeded(self):
        """Test safety check with duration exceeded."""
        # Create a profile with very short duration
        profile = MacroSafetyProfile(
            macro_id="short_duration",
            name="Short Duration Macro",
            category="test",
            safety_level=SafetyLevel.SAFE,
            max_duration=1  # 1 second
        )
        self.manager.safety_profiles["short_duration"] = profile
        
        # Start the macro
        self.manager.start_macro("short_duration", "Short Duration Macro")
        
        # Wait for duration to exceed
        import time
        time.sleep(1.1)
        
        # Check safety
        cancellations = self.manager.check_macro_safety()
        assert len(cancellations) == 1
        assert cancellations[0].macro_id == "short_duration"
        assert "Duration exceeded" in cancellations[0].cancellation_reason
    
    def test_check_macro_safety_performance_threshold(self):
        """Test safety check with performance threshold exceeded."""
        # Create a profile with strict thresholds
        profile = MacroSafetyProfile(
            macro_id="strict_threshold",
            name="Strict Threshold Macro",
            category="test",
            safety_level=SafetyLevel.DANGEROUS,
            max_duration=300,
            performance_thresholds=PerformanceThresholds(
                cpu_usage_max=10.0,  # Very low threshold
                memory_usage_max=20.0,  # Very low threshold
                fps_min=60.0,  # Very high threshold
                latency_max=50.0,  # Very low threshold
                response_time_max=100.0  # Very low threshold
            )
        )
        self.manager.safety_profiles["strict_threshold"] = profile
        
        # Start the macro
        self.manager.start_macro("strict_threshold", "Strict Threshold Macro")
        
        # Mock high CPU usage
        with patch.object(self.manager.performance_monitor, 'get_current_metrics') as mock_metrics:
            mock_metrics.return_value = PerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_usage=85.0,  # Above threshold
                memory_usage=30.0,
                fps=None,
                latency=None,
                response_time=None
            )
            
            # Check safety
            cancellations = self.manager.check_macro_safety()
            assert len(cancellations) == 1
            assert cancellations[0].macro_id == "strict_threshold"
            assert "Performance threshold exceeded" in cancellations[0].cancellation_reason
    
    def test_should_cancel_for_performance(self):
        """Test performance threshold checking logic."""
        profile = MacroSafetyProfile(
            macro_id="test",
            name="Test Macro",
            category="test",
            safety_level=SafetyLevel.SAFE,
            performance_thresholds=PerformanceThresholds(
                cpu_usage_max=80.0,
                memory_usage_max=85.0,
                fps_min=15.0,
                latency_max=500.0,
                response_time_max=1000.0
            )
        )
        
        # Test normal metrics (should not cancel)
        normal_metrics = PerformanceSnapshot(
            timestamp=datetime.now(),
            cpu_usage=50.0,
            memory_usage=60.0,
            fps=30.0,
            latency=200.0,
            response_time=500.0
        )
        assert not self.manager._should_cancel_for_performance(profile, normal_metrics)
        
        # Test high CPU usage (should cancel)
        high_cpu_metrics = PerformanceSnapshot(
            timestamp=datetime.now(),
            cpu_usage=85.0,
            memory_usage=60.0,
            fps=30.0,
            latency=200.0,
            response_time=500.0
        )
        assert self.manager._should_cancel_for_performance(profile, high_cpu_metrics)
        
        # Test high memory usage (should cancel)
        high_memory_metrics = PerformanceSnapshot(
            timestamp=datetime.now(),
            cpu_usage=50.0,
            memory_usage=90.0,
            fps=30.0,
            latency=200.0,
            response_time=500.0
        )
        assert self.manager._should_cancel_for_performance(profile, high_memory_metrics)
    
    def test_load_profile_overrides(self):
        """Test loading profile overrides."""
        # Create override file
        override_data = {
            "dance": {
                "name": "Dance Macro (Override)",
                "safety_level": "safe",
                "max_duration": 1800,
                "auto_cancel_enabled": False,
                "discord_notify": False
            }
        }
        
        override_file = Path(self.temp_dir) / "test_profile.safe.json"
        with open(override_file, 'w', encoding='utf-8') as f:
            json.dump(override_data, f, indent=2)
        
        # Load override
        self.manager.load_profile_overrides("test_profile")
        
        # Check that override was applied
        dance_profile = self.manager.safety_profiles["dance"]
        assert dance_profile.safety_level == SafetyLevel.SAFE
        assert dance_profile.max_duration == 1800
        assert dance_profile.auto_cancel_enabled is False
        assert dance_profile.discord_notify is False
    
    def test_get_safety_report(self):
        """Test getting safety report."""
        # Start some macros
        self.manager.start_macro("heal", "Heal Macro")
        self.manager.start_macro("attack", "Attack Macro")
        
        # Get report
        report = self.manager.get_safety_report()
        
        assert "timestamp" in report
        assert report["active_macros"] == 2
        assert "performance_metrics" in report
        assert "active_macro_details" in report
        assert "recent_cancellations" in report
        
        # Check active macro details
        macro_details = report["active_macro_details"]
        assert len(macro_details) == 2
        macro_ids = [m["macro_id"] for m in macro_details]
        assert "heal" in macro_ids
        assert "attack" in macro_ids
    
    def test_save_cancellation_log(self):
        """Test saving cancellation log."""
        # Create a cancellation event
        metrics = PerformanceSnapshot(
            timestamp=datetime.now(),
            cpu_usage=85.0,
            memory_usage=80.0
        )
        
        cancellation = MacroCancellationEvent(
            macro_id="test_macro",
            macro_name="Test Macro",
            cancellation_reason="Performance threshold exceeded",
            performance_metrics=metrics,
            timestamp=datetime.now()
        )
        
        self.manager.cancellation_events.append(cancellation)
        
        # Save log
        log_path = self.manager.save_cancellation_log()
        
        # Check that file was created
        assert os.path.exists(log_path)
        
        # Check log contents
        with open(log_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        assert log_data["total_cancellations"] == 1
        assert len(log_data["cancellations"]) == 1
        assert log_data["cancellations"][0]["macro_id"] == "test_macro"
    
    def test_send_discord_notification(self):
        """Test Discord notification sending."""
        # Create a test cancellation
        metrics = PerformanceSnapshot(
            timestamp=datetime.now(),
            cpu_usage=85.0,
            memory_usage=80.0
        )
        
        cancellation = MacroCancellationEvent(
            macro_id="test_macro",
            macro_name="Test Macro",
            cancellation_reason="Performance threshold exceeded",
            performance_metrics=metrics,
            timestamp=datetime.now()
        )
        
        # Test notification (should not crash)
        self.manager._send_discord_notification(cancellation)
        # No assertion needed - just checking it doesn't crash


class TestMacroCancellationEvent:
    """Test the MacroCancellationEvent class."""
    
    def test_initialization(self):
        """Test MacroCancellationEvent initialization."""
        metrics = PerformanceSnapshot(
            timestamp=datetime.now(),
            cpu_usage=85.0,
            memory_usage=80.0
        )
        
        event = MacroCancellationEvent(
            macro_id="test_macro",
            macro_name="Test Macro",
            cancellation_reason="Performance threshold exceeded",
            performance_metrics=metrics,
            timestamp=datetime.now(),
            session_id="test_session"
        )
        
        assert event.macro_id == "test_macro"
        assert event.macro_name == "Test Macro"
        assert event.cancellation_reason == "Performance threshold exceeded"
        assert event.performance_metrics == metrics
        assert event.session_id == "test_session"


class TestPerformanceSnapshot:
    """Test the PerformanceSnapshot class."""
    
    def test_initialization(self):
        """Test PerformanceSnapshot initialization."""
        timestamp = datetime.now()
        snapshot = PerformanceSnapshot(
            timestamp=timestamp,
            cpu_usage=50.0,
            memory_usage=60.0,
            fps=30.0,
            latency=200.0,
            response_time=500.0
        )
        
        assert snapshot.timestamp == timestamp
        assert snapshot.cpu_usage == 50.0
        assert snapshot.memory_usage == 60.0
        assert snapshot.fps == 30.0
        assert snapshot.latency == 200.0
        assert snapshot.response_time == 500.0
    
    def test_initialization_with_none_values(self):
        """Test initialization with None values."""
        timestamp = datetime.now()
        snapshot = PerformanceSnapshot(
            timestamp=timestamp,
            cpu_usage=50.0,
            memory_usage=60.0
        )
        
        assert snapshot.fps is None
        assert snapshot.latency is None
        assert snapshot.response_time is None


def test_integration():
    """Integration test for the complete macro safety system."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize manager
        manager = MacroSafetyManager(profiles_dir=temp_dir)
        
        # Start a macro
        success = manager.start_macro("test_integration", "Integration Test Macro")
        assert success is True
        
        # Check that macro is active
        assert "test_integration" in manager.active_macros
        
        # Get safety report
        report = manager.get_safety_report()
        assert report["active_macros"] == 1
        
        # Stop the macro
        success = manager.stop_macro("test_integration")
        assert success is True
        
        # Check that macro is no longer active
        assert "test_integration" not in manager.active_macros
        
        # Clean up
        manager.cleanup()
        
    finally:
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 