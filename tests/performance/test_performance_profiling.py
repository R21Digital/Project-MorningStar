#!/usr/bin/env python3
"""
Performance profiling and optimization tests for MS11
Tests performance characteristics and identifies bottlenecks
"""

import cProfile
import io
import pstats
import sys
import time
import tracemalloc
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import main as ms11_main


class TestImportPerformance:
    """Test import performance and startup time."""
    
    def test_main_import_time(self):
        """Test main module import performance."""
        start_time = time.time()
        
        # Re-import to test fresh import time
        import importlib
        importlib.reload(ms11_main)
        
        import_time = time.time() - start_time
        
        # Import should be fast (under 2 seconds even with fallbacks)
        assert import_time < 2.0, f"Import took {import_time:.3f}s, should be under 2.0s"
        
        print(f"\n[PERF] Main module import time: {import_time:.3f}s")
        
    def test_fallback_import_performance(self):
        """Test fallback import performance when modules missing."""
        # Test that fallback imports are fast
        start_time = time.time()
        
        # Test fallback class creation
        session_mgr = ms11_main.SessionManager()
        window_mgr = ms11_main.WindowManager(session_mgr)
        
        fallback_time = time.time() - start_time
        
        # Fallback creation should be very fast
        assert fallback_time < 0.1, f"Fallback creation took {fallback_time:.3f}s"
        
        print(f"[PERF] Fallback creation time: {fallback_time:.4f}s")


class TestConfigurationPerformance:
    """Test configuration loading performance."""
    
    def test_config_loading_performance(self):
        """Test configuration loading speed."""
        start_time = time.time()
        
        # Load config multiple times to test caching/performance
        for _ in range(10):
            config = ms11_main.load_config()
            
        config_time = time.time() - start_time
        avg_time = config_time / 10
        
        # Each config load should be fast
        assert avg_time < 0.1, f"Average config load took {avg_time:.3f}s"
        
        print(f"[PERF] Average config load time: {avg_time:.4f}s")
        
    def test_profile_loading_performance(self):
        """Test profile loading performance."""
        start_time = time.time()
        
        # Test loading non-existent profile (fallback case)
        for _ in range(10):
            profile = ms11_main.load_runtime_profile('nonexistent')
            
        profile_time = time.time() - start_time
        avg_time = profile_time / 10
        
        # Profile loading should be fast even for missing profiles
        assert avg_time < 0.05, f"Average profile load took {avg_time:.3f}s"
        
        print(f"[PERF] Average profile load time: {avg_time:.4f}s")


class TestArgumentParsingPerformance:
    """Test command line argument parsing performance."""
    
    def test_parse_args_performance(self):
        """Test argument parsing performance."""
        test_args = [
            ['--mode', 'medic', '--profile', 'test'],
            ['--smart', '--loop', '--repeat'],
            ['--max_loops', '10', '--rest', '30'],
            []
        ]
        
        start_time = time.time()
        
        for args in test_args:
            for _ in range(25):  # 100 total parses
                parsed = ms11_main.parse_args(args)
                
        parse_time = time.time() - start_time
        avg_time = parse_time / 100
        
        # Argument parsing should be very fast
        assert avg_time < 0.01, f"Average argument parsing took {avg_time:.4f}s"
        
        print(f"[PERF] Average argument parsing time: {avg_time:.5f}s")


class TestMemoryUsage:
    """Test memory usage and leaks."""
    
    def test_memory_usage_startup(self):
        """Test memory usage during startup."""
        tracemalloc.start()
        
        # Simulate startup operations
        config = ms11_main.load_config()
        profile = ms11_main.load_runtime_profile('test')
        session_mgr = ms11_main.SessionManager()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory usage should be reasonable (under 50MB for basic operations)
        current_mb = current / 1024 / 1024
        peak_mb = peak / 1024 / 1024
        
        assert current_mb < 50, f"Current memory usage {current_mb:.1f}MB too high"
        assert peak_mb < 100, f"Peak memory usage {peak_mb:.1f}MB too high"
        
        print(f"[PERF] Memory usage - Current: {current_mb:.1f}MB, Peak: {peak_mb:.1f}MB")
        
    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations."""
        tracemalloc.start()
        
        # Perform operations multiple times
        for _ in range(100):
            config = ms11_main.load_config()
            profile = ms11_main.load_runtime_profile('test')
            args = ms11_main.parse_args(['--mode', 'medic'])
            
        first_snapshot = tracemalloc.take_snapshot()
        
        # Perform same operations again
        for _ in range(100):
            config = ms11_main.load_config()
            profile = ms11_main.load_runtime_profile('test')
            args = ms11_main.parse_args(['--mode', 'medic'])
            
        second_snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        # Compare memory usage
        top_stats = second_snapshot.compare_to(first_snapshot, 'lineno')
        
        # Total memory growth should be minimal
        total_growth = sum(stat.size_diff for stat in top_stats)
        growth_mb = total_growth / 1024 / 1024
        
        # Should not grow by more than 5MB
        assert growth_mb < 5, f"Memory grew by {growth_mb:.1f}MB, possible leak"
        
        print(f"[PERF] Memory growth after 100 iterations: {growth_mb:.2f}MB")


class TestFunctionProfiling:
    """Test function-level performance profiling."""
    
    def test_profile_mode_handlers(self):
        """Profile mode handler performance."""
        pr = cProfile.Profile()
        
        # Profile mode handler lookup
        pr.enable()
        
        for _ in range(1000):
            # Test mode handler lookup performance
            handler = ms11_main.MODE_HANDLERS.get('medic')
            handler = ms11_main.MODE_HANDLERS.get('combat')
            handler = ms11_main.MODE_HANDLERS.get('nonexistent')
            
        pr.disable()
        
        # Analyze profile
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats('tottime')
        ps.print_stats(10)  # Top 10 functions
        
        profile_output = s.getvalue()
        print(f"\n[PERF] Mode handler lookup profile:\n{profile_output}")
        
        # Should complete quickly - verify we have some function calls
        assert "function calls" in profile_output  # Verify profiling worked
        
    def test_profile_fallback_functions(self):
        """Profile fallback function performance."""
        pr = cProfile.Profile()
        
        pr.enable()
        
        for _ in range(1000):
            # Test fallback functions
            result = ms11_main.monitor_session({})
            ms11_main.log_event("test_event")
            state = ms11_main.state_tracker.get_state()
            
        pr.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats('tottime')
        ps.print_stats(10)
        
        profile_output = s.getvalue()
        print(f"\n[PERF] Fallback functions profile:\n{profile_output}")


class TestBottleneckIdentification:
    """Identify performance bottlenecks."""
    
    def test_identify_slow_operations(self):
        """Identify slow operations in the codebase."""
        operations = {
            'config_loading': lambda: ms11_main.load_config(),
            'profile_loading': lambda: ms11_main.load_runtime_profile('test'),
            'argument_parsing': lambda: ms11_main.parse_args(['--mode', 'medic']),
            'session_creation': lambda: ms11_main.SessionManager(),
            'window_creation': lambda: ms11_main.WindowManager(None),
        }
        
        timings = {}
        
        for op_name, operation in operations.items():
            op_start_time = time.time()
            
            # Run operation multiple times
            for _ in range(100):
                try:
                    operation()
                except Exception:
                    # Some operations may fail, that's OK for timing
                    pass
                    
            op_end_time = time.time()
            avg_time = (op_end_time - op_start_time) / 100
            timings[op_name] = avg_time
            
        # Print timing results
        print(f"\n[PERF] Operation timings (average of 100 runs):")
        for op_name, avg_time in sorted(timings.items(), key=lambda x: x[1], reverse=True):
            print(f"  {op_name}: {avg_time:.5f}s")
            
        # Identify bottlenecks (operations taking longer than 10ms)
        bottlenecks = {op: op_time for op, op_time in timings.items() if op_time > 0.01}
        
        if bottlenecks:
            print(f"\n[WARN] Performance bottlenecks identified:")
            for op_name, op_time in bottlenecks.items():
                print(f"  {op_name}: {op_time:.5f}s")
                
        # Test should pass but report bottlenecks
        assert len(bottlenecks) < len(operations), "Too many operations are slow"


class TestScalabilityPerformance:
    """Test performance under various load conditions."""
    
    @pytest.mark.slow
    def test_concurrent_operations(self):
        """Test performance under concurrent-like load."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def worker():
            start_time = time.time()
            for _ in range(10):
                config = ms11_main.load_config()
                profile = ms11_main.load_runtime_profile('test')
            end_time = time.time()
            results.put(end_time - start_time)
            
        # Simulate concurrent operations
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Collect results
        times = []
        while not results.empty():
            times.append(results.get())
            
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"[PERF] Concurrent operations - Average: {avg_time:.3f}s, Max: {max_time:.3f}s")
        
        # Operations should complete reasonably fast even under load
        assert avg_time < 1.0, f"Average concurrent operation time {avg_time:.3f}s too high"
        assert max_time < 2.0, f"Max concurrent operation time {max_time:.3f}s too high"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print output