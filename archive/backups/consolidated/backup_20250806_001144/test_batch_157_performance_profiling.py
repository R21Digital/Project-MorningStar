#!/usr/bin/env python3
"""
Test suite for Batch 157 - Session Weight & Performance Lightness Audit

This test suite validates the performance profiling functionality including:
- Performance profiler initialization and configuration
- Session weight analysis and optimization recommendations
- Memory leak detection and CPU bottleneck identification
- CLI integration and report generation
- Edge case handling and error scenarios
"""

import unittest
import time
import random
import json
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Import the modules we're testing
try:
    from core.performance_profiler import (
        PerformanceProfiler, PerformanceMetrics, SessionProfile,
        start_profiling, stop_profiling, reset_profiling,
        get_performance_report, get_lightweight_report,
        profile_module, track_ocr_call, track_event_listener
    )
    from core.session_weight_analyzer import (
        SessionWeightAnalyzer, ProcessWeight, SessionWeightReport,
        analyze_session_weight, get_lightweight_analysis
    )
    from core.performance_cli import (
        PerformanceCLI, setup_performance_parser, handle_performance_profiling
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import performance profiling modules: {e}")
    MODULES_AVAILABLE = False


class TestPerformanceProfiler(unittest.TestCase):
    """Test the PerformanceProfiler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Performance profiling modules not available")
        
        self.profiler = PerformanceProfiler(enabled=True)
    
    def test_profiler_initialization(self):
        """Test PerformanceProfiler initialization."""
        self.assertIsNotNone(self.profiler)
        self.assertTrue(self.profiler.enabled)
        self.assertIsNotNone(self.profiler.session_profile)
        self.assertIsNotNone(self.profiler.process)
    
    def test_profiler_disabled(self):
        """Test profiler with disabled state."""
        disabled_profiler = PerformanceProfiler(enabled=False)
        self.assertFalse(disabled_profiler.enabled)
        
        # Test that disabled profiler returns appropriate responses
        report = disabled_profiler.get_performance_report()
        self.assertEqual(report.get("status"), "profiling_disabled")
    
    @patch('time.sleep')
    def test_monitoring_start_stop(self, mock_sleep):
        """Test monitoring start and stop functionality."""
        # Start monitoring
        self.profiler.start_monitoring()
        self.assertTrue(self.profiler.monitoring_active)
        
        # Stop monitoring
        self.profiler.stop_monitoring()
        self.assertFalse(self.profiler.monitoring_active)
    
    def test_performance_metrics(self):
        """Test PerformanceMetrics class."""
        metrics = PerformanceMetrics("test_module")
        
        # Test initial state
        self.assertEqual(metrics.module_name, "test_module")
        self.assertEqual(metrics.cpu_usage, 0.0)
        self.assertEqual(metrics.memory_usage, 0.0)
        self.assertEqual(metrics.call_count, 0)
        
        # Test update method
        metrics.update(50.0, 100.0, 1.5)
        self.assertEqual(metrics.cpu_usage, 50.0)
        self.assertEqual(metrics.memory_usage, 100.0)
        self.assertEqual(metrics.execution_time, 1.5)
        self.assertEqual(metrics.call_count, 1)
    
    def test_session_profile(self):
        """Test SessionProfile class."""
        profile = SessionProfile()
        
        # Test initial state
        self.assertIsNotNone(profile.session_start)
        self.assertEqual(profile.ocr_frequency, 0)
        self.assertEqual(profile.event_listener_load, 0)
        self.assertEqual(len(profile.alerts), 0)
    
    def test_profile_module_decorator(self):
        """Test the profile_module decorator."""
        @profile_module("test_module")
        def test_function():
            time.sleep(0.1)
            return "test_result"
        
        # Call the decorated function
        result = test_function()
        self.assertEqual(result, "test_result")
        
        # Check that module was tracked
        self.assertIn("test_module", self.profiler.session_profile.active_modules)
    
    def test_track_ocr_call(self):
        """Test OCR call tracking."""
        initial_count = self.profiler.session_profile.ocr_frequency
        track_ocr_call()
        self.assertEqual(self.profiler.session_profile.ocr_frequency, initial_count + 1)
    
    def test_track_event_listener(self):
        """Test event listener tracking."""
        initial_count = self.profiler.session_profile.event_listener_load
        track_event_listener()
        self.assertEqual(self.profiler.session_profile.event_listener_load, initial_count + 1)
    
    def test_get_performance_report(self):
        """Test performance report generation."""
        report = get_performance_report()
        
        # Check report structure
        self.assertIn("session_duration", report)
        self.assertIn("total_memory_usage_mb", report)
        self.assertIn("total_cpu_usage_percent", report)
        self.assertIn("active_modules", report)
        self.assertIn("module_metrics", report)
    
    def test_get_lightweight_report(self):
        """Test lightweight report generation."""
        report = get_lightweight_report()
        
        # Check report structure
        self.assertIn("memory_mb", report)
        self.assertIn("cpu_percent", report)
        self.assertIn("active_modules", report)
        self.assertIn("alerts", report)


class TestSessionWeightAnalyzer(unittest.TestCase):
    """Test the SessionWeightAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Session weight analyzer not available")
        
        self.analyzer = SessionWeightAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test SessionWeightAnalyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.weight_thresholds)
        self.assertIsNotNone(self.analyzer.heavy_process_patterns)
    
    def test_process_weight_calculation(self):
        """Test ProcessWeight calculation."""
        weight = ProcessWeight("test_module")
        
        # Set weights
        weight.cpu_weight = 60.0
        weight.memory_weight = 40.0
        weight.frequency_weight = 20.0
        
        # Calculate total weight
        weight.calculate_total_weight()
        
        expected_weight = (60.0 * 0.4 + 40.0 * 0.4 + 20.0 * 0.2)
        self.assertEqual(weight.total_weight, expected_weight)
        self.assertEqual(weight.optimization_priority, "high")
    
    def test_process_weight_priorities(self):
        """Test ProcessWeight priority determination."""
        # Test critical priority
        weight = ProcessWeight("test_module")
        weight.cpu_weight = 90.0
        weight.memory_weight = 90.0
        weight.frequency_weight = 90.0
        weight.calculate_total_weight()
        self.assertEqual(weight.optimization_priority, "critical")
        
        # Test low priority
        weight = ProcessWeight("test_module")
        weight.cpu_weight = 10.0
        weight.memory_weight = 10.0
        weight.frequency_weight = 10.0
        weight.calculate_total_weight()
        self.assertEqual(weight.optimization_priority, "low")
    
    def test_session_weight_report(self):
        """Test SessionWeightReport class."""
        report = SessionWeightReport(session_start=time.time())
        
        # Test initial state
        self.assertIsNotNone(report.session_start)
        self.assertEqual(report.total_weight_score, 0.0)
        self.assertEqual(len(report.heaviest_modules), 0)
        self.assertEqual(len(report.optimization_recommendations), 0)
        self.assertFalse(report.memory_leaks_detected)
        self.assertEqual(len(report.cpu_bottlenecks), 0)
        self.assertEqual(report.resource_usage_trend, "stable")
    
    @patch('core.session_weight_analyzer.get_performance_report')
    def test_analyze_session_weight(self, mock_get_report):
        """Test session weight analysis."""
        # Mock performance report
        mock_get_report.return_value = {
            "module_metrics": {
                "test_module": {
                    "cpu_usage_percent": 50.0,
                    "memory_usage_mb": 100.0,
                    "call_count": 10
                }
            }
        }
        
        report = analyze_session_weight()
        
        # Check report structure
        self.assertIsNotNone(report)
        self.assertIsInstance(report, SessionWeightReport)
        self.assertIsNotNone(report.session_start)
    
    def test_get_lightweight_analysis(self):
        """Test lightweight analysis."""
        analysis = get_lightweight_analysis()
        
        # Check analysis structure
        self.assertIn("status", analysis)
        if analysis["status"] != "profiling_disabled":
            self.assertIn("weight_score", analysis)
            self.assertIn("memory_mb", analysis)
            self.assertIn("cpu_percent", analysis)
            self.assertIn("active_modules", analysis)
            self.assertIn("alerts", analysis)


class TestPerformanceCLI(unittest.TestCase):
    """Test the PerformanceCLI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Performance CLI not available")
        
        self.cli = PerformanceCLI()
    
    def test_cli_initialization(self):
        """Test PerformanceCLI initialization."""
        self.assertIsNotNone(self.cli)
        self.assertIsNotNone(self.cli.logger)
    
    def test_setup_parser(self):
        """Test CLI parser setup."""
        import argparse
        parser = argparse.ArgumentParser()
        self.cli.setup_parser(parser)
        
        # Check that arguments were added
        actions = [action.dest for action in parser._actions]
        self.assertIn("profile_session", actions)
        self.assertIn("performance_report", actions)
        self.assertIn("performance_interval", actions)
        self.assertIn("performance_output", actions)
    
    def test_handle_profiling_disabled(self):
        """Test profiling when disabled."""
        import argparse
        args = argparse.Namespace()
        args.profile_session = False
        
        result = self.cli.handle_profiling(args)
        self.assertEqual(result.get("status"), "profiling_disabled")
    
    @patch('core.performance_cli.start_profiling')
    @patch('core.performance_cli.stop_profiling')
    @patch('core.performance_cli.get_lightweight_report')
    def test_handle_profiling_lightweight(self, mock_get_report, mock_stop, mock_start):
        """Test profiling with lightweight report."""
        import argparse
        args = argparse.Namespace()
        args.profile_session = True
        args.performance_report = "lightweight"
        args.performance_interval = 1
        args.performance_output = None
        
        # Mock lightweight report
        mock_get_report.return_value = {
            "memory_mb": 100.0,
            "cpu_percent": 50.0,
            "active_modules": 5,
            "alerts": 2
        }
        
        result = self.cli.handle_profiling(args)
        
        # Check that profiling was started and stopped
        mock_start.assert_called_once()
        mock_stop.assert_called_once()
        
        # Check result structure
        self.assertIn("timestamp", result)
        self.assertIn("performance_summary", result)
        self.assertIn("weight_summary", result)


class TestPerformanceProfilingIntegration(unittest.TestCase):
    """Test performance profiling integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Performance profiling modules not available")
    
    def test_full_integration_workflow(self):
        """Test complete integration workflow."""
        # Start profiling
        start_profiling()
        
        # Simulate some activity
        @profile_module("integration_test")
        def test_function():
            time.sleep(0.1)
            track_ocr_call()
            track_event_listener()
            return "test_result"
        
        result = test_function()
        self.assertEqual(result, "test_result")
        
        # Get reports
        perf_report = get_performance_report()
        weight_analysis = get_lightweight_analysis()
        
        # Check reports
        self.assertIsNotNone(perf_report)
        self.assertIsNotNone(weight_analysis)
        
        # Stop profiling
        stop_profiling()
    
    def test_performance_thresholds(self):
        """Test performance threshold detection."""
        # Test memory threshold
        profiler = PerformanceProfiler()
        profiler.session_profile.total_memory_usage = 600  # Above 500MB threshold
        
        # Check that alert is generated
        profiler._check_thresholds()
        self.assertGreater(len(profiler.session_profile.alerts), 0)
        
        # Test CPU threshold
        profiler.session_profile.total_cpu_usage = 90  # Above 80% threshold
        profiler._check_thresholds()
        
        # Should have multiple alerts
        self.assertGreater(len(profiler.session_profile.alerts), 1)
    
    def test_memory_leak_detection(self):
        """Test memory leak detection."""
        analyzer = SessionWeightAnalyzer()
        
        # Simulate memory history with increasing trend
        profiler = PerformanceProfiler()
        for i in range(15):
            profiler.session_profile.memory_history.append(100 + i * 10)
        
        # Test memory leak detection
        perf_report = {"module_metrics": {}}
        memory_leaks = analyzer._detect_memory_leaks(perf_report)
        
        # Should detect memory leak with increasing trend
        self.assertTrue(memory_leaks)
    
    def test_cpu_bottleneck_identification(self):
        """Test CPU bottleneck identification."""
        analyzer = SessionWeightAnalyzer()
        
        # Create module weights with CPU bottlenecks
        module_weights = [
            ProcessWeight("high_cpu_module"),
            ProcessWeight("normal_module"),
            ProcessWeight("critical_cpu_module")
        ]
        
        # Set CPU weights
        module_weights[0].cpu_weight = 75.0  # High CPU
        module_weights[1].cpu_weight = 30.0  # Normal CPU
        module_weights[2].cpu_weight = 95.0  # Critical CPU
        
        bottlenecks = analyzer._identify_cpu_bottlenecks(module_weights)
        
        # Should identify high CPU modules
        self.assertGreater(len(bottlenecks), 0)
        self.assertIn("high_cpu_module", bottlenecks[0])
        self.assertIn("critical_cpu_module", bottlenecks[1])


class TestPerformanceProfilingEdgeCases(unittest.TestCase):
    """Test performance profiling edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Performance profiling modules not available")
    
    def test_profiler_with_no_modules(self):
        """Test profiler with no active modules."""
        profiler = PerformanceProfiler()
        
        # Ensure no modules are active
        profiler.active_modules.clear()
        
        # Get lightweight report
        report = profiler.get_lightweight_report()
        
        # Should still return valid report
        self.assertIn("active_modules", report)
        self.assertEqual(report["active_modules"], 0)
    
    def test_profiler_with_extreme_values(self):
        """Test profiler with extreme performance values."""
        profiler = PerformanceProfiler()
        
        # Set extreme values
        profiler.session_profile.total_memory_usage = 999999  # Very high memory
        profiler.session_profile.total_cpu_usage = 999  # Very high CPU
        
        # Check thresholds
        profiler._check_thresholds()
        
        # Should generate alerts
        self.assertGreater(len(profiler.session_profile.alerts), 0)
    
    def test_profiler_with_disabled_state(self):
        """Test profiler with disabled state."""
        profiler = PerformanceProfiler(enabled=False)
        
        # All operations should return disabled status
        report = profiler.get_performance_report()
        self.assertEqual(report.get("status"), "profiling_disabled")
        
        lightweight = profiler.get_lightweight_report()
        self.assertEqual(lightweight.get("status"), "profiling_disabled")
    
    def test_analyzer_with_empty_data(self):
        """Test analyzer with empty performance data."""
        analyzer = SessionWeightAnalyzer()
        
        # Mock empty performance report
        with patch('core.session_weight_analyzer.get_performance_report') as mock_get:
            mock_get.return_value = {"module_metrics": {}}
            
            report = analyzer.analyze_session_weight()
            
            # Should still return valid report
            self.assertIsNotNone(report)
            self.assertEqual(len(report.heaviest_modules), 0)
    
    def test_cli_with_invalid_arguments(self):
        """Test CLI with invalid arguments."""
        cli = PerformanceCLI()
        
        # Test with None arguments
        import argparse
        args = argparse.Namespace()
        args.profile_session = True
        args.performance_report = "invalid_report_type"
        args.performance_interval = -1
        args.performance_output = "/invalid/path/report.json"
        
        # Should handle gracefully
        result = cli.handle_profiling(args)
        self.assertIsNotNone(result)


def run_performance_benchmark():
    """Run performance benchmark tests."""
    print("\n🚀 Running Performance Benchmark Tests")
    print("-" * 50)
    
    if not MODULES_AVAILABLE:
        print("❌ Performance profiling modules not available")
        return
    
    # Benchmark profiler initialization
    start_time = time.time()
    profiler = PerformanceProfiler()
    init_time = time.time() - start_time
    print(f"✅ Profiler initialization: {init_time:.3f}s")
    
    # Benchmark report generation
    start_time = time.time()
    report = profiler.get_performance_report()
    report_time = time.time() - start_time
    print(f"✅ Report generation: {report_time:.3f}s")
    
    # Benchmark weight analysis
    start_time = time.time()
    analyzer = SessionWeightAnalyzer()
    analysis = analyzer.analyze_session_weight()
    analysis_time = time.time() - start_time
    print(f"✅ Weight analysis: {analysis_time:.3f}s")
    
    # Benchmark CLI operations
    start_time = time.time()
    cli = PerformanceCLI()
    cli_time = time.time() - start_time
    print(f"✅ CLI initialization: {cli_time:.3f}s")
    
    total_time = init_time + report_time + analysis_time + cli_time
    print(f"\n📊 Total benchmark time: {total_time:.3f}s")
    print(f"📊 Average operation time: {total_time / 4:.3f}s")


def main():
    """Run the test suite."""
    print("🧪 BATCH 157 - PERFORMANCE PROFILING TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPerformanceProfiler,
        TestSessionWeightAnalyzer,
        TestPerformanceCLI,
        TestPerformanceProfilingIntegration,
        TestPerformanceProfilingEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run benchmark
    run_performance_benchmark()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\n⚠️  ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE PROFILING TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main() 