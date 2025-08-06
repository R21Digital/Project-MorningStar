"""
Profiler Package

This package provides build-aware combat profiles and spec detection functionality.
"""

from .spec_detector import SpecDetector, BuildMatch, DetectionResult
from .build_manager import BuildManager, BuildInfo, TrainingPlan

__all__ = [
    "SpecDetector",
    "BuildMatch", 
    "DetectionResult",
    "BuildManager",
    "BuildInfo",
    "TrainingPlan"
] 