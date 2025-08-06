#!/usr/bin/env python3
"""
Performance Profiler for MS11

This module provides low-level performance profiling hooks to track:
- CPU and RAM usage
- OCR call frequency
- Frame analysis rate
- IO wait times
- Module performance impact

The profiler integrates with the performance dashboard to provide
real-time monitoring and recommendations for optimization.
"""

import json
import time
import psutil
import threading
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from collections import defaultdict, deque
import statistics
import functools
import gc
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProfilerState(Enum):
    """Profiler state enumeration."""
    IDLE = "idle"
    SAMPLING = "sampling"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class PerformanceSample:
    """Single performance measurement sample."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: float
    io_wait_percent: float
    network_io_bytes: int
    disk_io_bytes: int
    ocr_calls: int
    frames_analyzed: int
    active_modules: List[str]
    gc_stats: Dict[str, Any]


@dataclass
class ModuleProfile:
    """Performance profile for a specific module."""
    module_name: str
    call_count: int
    total_execution_time: float
    avg_execution_time: float
    max_execution_time: float
    min_execution_time: float
    cpu_impact: float
    memory_impact: float
    last_called: datetime
    recommendations: List[str]


class PerformanceProfiler:
    """Enhanced performance profiler with sampling and analysis capabilities."""
    
    def __init__(self, 
                 sample_interval: float = 1.0,
                 max_samples: int = 3600,  # 1 hour at 1s intervals
                 log_file: str = "logs/profiler_samples.jsonl"):
        self.sample_interval = sample_interval
        self.max_samples = max_samples
        self.log_file = log_file
        
        # Profiler state
        self.state = ProfilerState.IDLE
        self.start_time = None
        self.samples: deque = deque(maxlen=max_samples)
        
        # Performance tracking
        self.module_profiles: Dict[str, ModuleProfile] = {}
        self.ocr_call_count = 0
        self.frame_analysis_count = 0
        self.io_wait_time = 0.0
        
        # Sampling thread
        self.sampling_thread = None
        self.sampling_active = False
        
        # Hooks and callbacks
        self.pre_sample_hooks: List[Callable] = []
        self.post_sample_hooks: List[Callable] = []
        self.alert_callbacks: List[Callable] = []
        
        # Thresholds and alerts
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.io_wait_threshold = 10.0
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup profiler logging."""
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
    def start_sampling(self) -> None:
        """Start performance sampling."""
        if self.state != ProfilerState.IDLE:
            logger.warning("Profiler is already active")
            return
            
        self.state = ProfilerState.SAMPLING
        self.start_time = datetime.now()
        self.sampling_active = True
        
        # Start sampling thread
        self.sampling_thread = threading.Thread(
            target=self._sampling_loop,
            daemon=True,
            name="PerformanceSampler"
        )
        self.sampling_thread.start()
        
        logger.info("Performance sampling started")
        
    def stop_sampling(self) -> None:
        """Stop performance sampling."""
        if self.state == ProfilerState.IDLE:
            logger.warning("Profiler is not active")
            return
            
        self.sampling_active = False
        self.state = ProfilerState.IDLE
        
        if self.sampling_thread and self.sampling_thread.is_alive():
            self.sampling_thread.join(timeout=5.0)
            
        logger.info("Performance sampling stopped")
        
    def _sampling_loop(self) -> None:
        """Main sampling loop."""
        while self.sampling_active:
            try:
                # Execute pre-sample hooks
                for hook in self.pre_sample_hooks:
                    try:
                        hook()
                    except Exception as e:
                        logger.error(f"Pre-sample hook error: {e}")
                
                # Collect performance sample
                sample = self._collect_sample()
                self.samples.append(sample)
                
                # Execute post-sample hooks
                for hook in self.post_sample_hooks:
                    try:
                        hook(sample)
                    except Exception as e:
                        logger.error(f"Post-sample hook error: {e}")
                
                # Check for alerts
                self._check_alerts(sample)
                
                # Log sample if configured
                self._log_sample(sample)
                
                # Sleep until next sample
                time.sleep(self.sample_interval)
                
            except Exception as e:
                logger.error(f"Sampling loop error: {e}")
                self.state = ProfilerState.ERROR
                break
                
    def _collect_sample(self) -> PerformanceSample:
        """Collect a single performance sample."""
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()
        
        # Get IO wait (if available)
        try:
            io_wait = psutil.cpu_times_percent().iowait
        except AttributeError:
            io_wait = 0.0
            
        # Get GC stats
        gc_stats = {
            'collections': gc.get_stats(),
            'counts': gc.get_count(),
            'thresholds': gc.get_threshold()
        }
        
        # Get active modules (simplified)
        active_modules = self._get_active_modules()
        
        return PerformanceSample(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available=memory.available,
            io_wait_percent=io_wait,
            network_io_bytes=network_io.bytes_sent + network_io.bytes_recv,
            disk_io_bytes=(disk_io.read_bytes + disk_io.write_bytes) if disk_io else 0,
            ocr_calls=self.ocr_call_count,
            frames_analyzed=self.frame_analysis_count,
            active_modules=active_modules,
            gc_stats=gc_stats
        )
        
    def _get_active_modules(self) -> List[str]:
        """Get list of currently active modules."""
        # This is a simplified implementation
        # In a real system, you'd track which modules are actually running
        active_modules = []
        
        # Check for common MS11 modules
        module_patterns = [
            'core.ai_companion',
            'core.combat',
            'core.navigation',
            'core.ocr',
            'modules.combat_feedback',
            'modules.buff_advisor'
        ]
        
        for pattern in module_patterns:
            if self._is_module_active(pattern):
                active_modules.append(pattern)
                
        return active_modules
        
    def _is_module_active(self, module_name: str) -> bool:
        """Check if a module is currently active."""
        # Simplified implementation - in reality you'd check actual module state
        return True  # Placeholder
        
    def _check_alerts(self, sample: PerformanceSample) -> None:
        """Check for performance alerts."""
        alerts = []
        
        if sample.cpu_percent > self.cpu_threshold:
            alerts.append({
                'type': 'cpu_high',
                'value': sample.cpu_percent,
                'threshold': self.cpu_threshold,
                'message': f"CPU usage is high: {sample.cpu_percent:.1f}%"
            })
            
        if sample.memory_percent > self.memory_threshold:
            alerts.append({
                'type': 'memory_high',
                'value': sample.memory_percent,
                'threshold': self.memory_threshold,
                'message': f"Memory usage is high: {sample.memory_percent:.1f}%"
            })
            
        if sample.io_wait_percent > self.io_wait_threshold:
            alerts.append({
                'type': 'io_wait_high',
                'value': sample.io_wait_percent,
                'threshold': self.io_wait_threshold,
                'message': f"IO wait is high: {sample.io_wait_percent:.1f}%"
            })
            
        # Trigger alert callbacks
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback error: {e}")
                    
    def _log_sample(self, sample: PerformanceSample) -> None:
        """Log performance sample to file."""
        try:
            with open(self.log_file, 'a') as f:
                json.dump(asdict(sample), f, default=str)
                f.write('\n')
        except Exception as e:
            logger.error(f"Failed to log sample: {e}")
            
    def track_ocr_call(self) -> None:
        """Track an OCR call."""
        self.ocr_call_count += 1
        
    def track_frame_analysis(self) -> None:
        """Track a frame analysis."""
        self.frame_analysis_count += 1
        
    def track_io_wait(self, wait_time: float) -> None:
        """Track IO wait time."""
        self.io_wait_time += wait_time
        
    def profile_module(self, module_name: str):
        """Decorator to profile module performance."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_cpu = psutil.cpu_percent()
                start_memory = psutil.virtual_memory().percent
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    end_cpu = psutil.cpu_percent()
                    end_memory = psutil.virtual_memory().percent
                    
                    execution_time = end_time - start_time
                    cpu_impact = end_cpu - start_cpu
                    memory_impact = end_memory - start_memory
                    
                    self._update_module_profile(
                        module_name, execution_time, cpu_impact, memory_impact
                    )
                    
            return wrapper
        return decorator
        
    def _update_module_profile(self, 
                              module_name: str, 
                              execution_time: float,
                              cpu_impact: float,
                              memory_impact: float) -> None:
        """Update module performance profile."""
        if module_name not in self.module_profiles:
            self.module_profiles[module_name] = ModuleProfile(
                module_name=module_name,
                call_count=0,
                total_execution_time=0.0,
                avg_execution_time=0.0,
                max_execution_time=0.0,
                min_execution_time=float('inf'),
                cpu_impact=0.0,
                memory_impact=0.0,
                last_called=datetime.now(),
                recommendations=[]
            )
            
        profile = self.module_profiles[module_name]
        profile.call_count += 1
        profile.total_execution_time += execution_time
        profile.avg_execution_time = profile.total_execution_time / profile.call_count
        profile.max_execution_time = max(profile.max_execution_time, execution_time)
        profile.min_execution_time = min(profile.min_execution_time, execution_time)
        profile.cpu_impact = (profile.cpu_impact + cpu_impact) / 2
        profile.memory_impact = (profile.memory_impact + memory_impact) / 2
        profile.last_called = datetime.now()
        
    def get_recent_samples(self, count: int = 100) -> List[PerformanceSample]:
        """Get recent performance samples."""
        return list(self.samples)[-count:]
        
    def get_statistics(self, window_minutes: int = 5) -> Dict[str, Any]:
        """Get performance statistics for the specified time window."""
        if not self.samples:
            return {}
            
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_samples = [
            s for s in self.samples 
            if s.timestamp >= cutoff_time
        ]
        
        if not recent_samples:
            return {}
            
        return {
            'cpu_avg': statistics.mean(s.cpu_percent for s in recent_samples),
            'cpu_max': max(s.cpu_percent for s in recent_samples),
            'memory_avg': statistics.mean(s.memory_percent for s in recent_samples),
            'memory_max': max(s.memory_percent for s in recent_samples),
            'io_wait_avg': statistics.mean(s.io_wait_percent for s in recent_samples),
            'io_wait_max': max(s.io_wait_percent for s in recent_samples),
            'ocr_calls_per_minute': self._calculate_rate(
                [s.ocr_calls for s in recent_samples], window_minutes
            ),
            'frames_per_minute': self._calculate_rate(
                [s.frames_analyzed for s in recent_samples], window_minutes
            ),
            'sample_count': len(recent_samples)
        }
        
    def _calculate_rate(self, values: List[int], window_minutes: int) -> float:
        """Calculate rate per minute from cumulative values."""
        if len(values) < 2:
            return 0.0
            
        total_change = values[-1] - values[0]
        return total_change / window_minutes
        
    def export_profile(self, session_id: str) -> Dict[str, Any]:
        """Export performance profile for a session."""
        profile_data = {
            'session_id': session_id,
            'export_timestamp': datetime.now().isoformat(),
            'profiler_state': self.state.value,
            'total_samples': len(self.samples),
            'sampling_duration': None,
            'statistics': self.get_statistics(),
            'module_profiles': {
                name: asdict(profile) 
                for name, profile in self.module_profiles.items()
            },
            'recent_samples': [
                asdict(sample) for sample in self.get_recent_samples(50)
            ]
        }
        
        if self.start_time:
            profile_data['sampling_duration'] = (
                datetime.now() - self.start_time
            ).total_seconds()
            
        return profile_data
        
    def save_session_profile(self, session_id: str) -> str:
        """Save session profile to file."""
        profile_data = self.export_profile(session_id)
        
        # Create samples directory if it doesn't exist
        samples_dir = Path("perf/samples")
        samples_dir.mkdir(parents=True, exist_ok=True)
        
        # Save profile
        profile_file = samples_dir / f"{session_id}.json"
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=2, default=str)
            
        return str(profile_file)


# Global profiler instance
profiler = PerformanceProfiler()


# Convenience functions for external use
def start_profiling() -> None:
    """Start performance profiling."""
    profiler.start_sampling()


def stop_profiling() -> None:
    """Stop performance profiling."""
    profiler.stop_sampling()


def track_ocr_call() -> None:
    """Track an OCR call."""
    profiler.track_ocr_call()


def track_frame_analysis() -> None:
    """Track a frame analysis."""
    profiler.track_frame_analysis()


def track_io_wait(wait_time: float) -> None:
    """Track IO wait time."""
    profiler.track_io_wait(wait_time)


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance."""
    return profiler


def profile_module(module_name: str):
    """Decorator to profile module performance."""
    return profiler.profile_module(module_name) 