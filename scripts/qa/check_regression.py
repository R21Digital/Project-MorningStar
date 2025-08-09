#!/usr/bin/env python3
"""
Performance regression checker for CI/CD pipeline.
Fails the build if significant performance regressions are detected.
"""

import sys
import argparse
from pathlib import Path

# Import the performance comparer
from compare_performance import PerformanceComparer


def main():
    """Main entry point for regression checking."""
    parser = argparse.ArgumentParser(description="Check for performance regressions")
    parser.add_argument("baseline", help="Baseline benchmark JSON file")
    parser.add_argument("current", help="Current benchmark JSON file")
    parser.add_argument("--threshold", type=float, default=20.0,
                       help="Regression threshold percentage (default: 20)")
    parser.add_argument("--critical-threshold", type=float, default=50.0,
                       help="Critical regression threshold percentage (default: 50)")
    parser.add_argument("--max-regressions", type=int, default=3,
                       help="Maximum allowed regressions (default: 3)")
    
    args = parser.parse_args()
    
    comparer = PerformanceComparer(regression_threshold=args.threshold)
    
    # Load and compare data
    baseline_data = comparer.load_benchmark_data(args.baseline)
    current_data = comparer.load_benchmark_data(args.current)
    
    if not current_data:
        print("❌ ERROR: Could not load current benchmark data")
        sys.exit(1)
        
    if not baseline_data:
        print("⚠️  WARNING: No baseline data - skipping regression check")
        sys.exit(0)
        
    # Extract and compare statistics
    baseline_stats = comparer.extract_benchmark_stats(baseline_data)
    current_stats = comparer.extract_benchmark_stats(current_data)
    comparison = comparer.compare_benchmarks(baseline_stats, current_stats)
    
    # Check for critical failures
    critical_regressions = [
        r for r in comparison['regressions']
        if r['percent_change'] > args.critical_threshold
    ]
    
    if critical_regressions:
        print(f"❌ CRITICAL PERFORMANCE REGRESSIONS DETECTED!")
        print(f"   Threshold: {args.critical_threshold}%")
        for reg in critical_regressions:
            print(f"   • {reg['name']}: +{reg['percent_change']:.1f}% slower")
        sys.exit(1)
        
    # Check for too many regressions
    if len(comparison['regressions']) > args.max_regressions:
        print(f"❌ TOO MANY PERFORMANCE REGRESSIONS!")
        print(f"   Found: {len(comparison['regressions'])}, Max allowed: {args.max_regressions}")
        for reg in comparison['regressions']:
            print(f"   • {reg['name']}: +{reg['percent_change']:.1f}% slower")
        sys.exit(1)
        
    # Summary
    if comparison['regressions']:
        print(f"⚠️  {len(comparison['regressions'])} performance regression(s) detected but within limits")
        for reg in comparison['regressions']:
            print(f"   • {reg['name']}: +{reg['percent_change']:.1f}% slower")
    else:
        print("✅ No significant performance regressions detected")
        
    if comparison['improvements']:
        print(f"🚀 {len(comparison['improvements'])} performance improvement(s) detected!")
        for imp in comparison['improvements'][:3]:  # Show top 3
            print(f"   • {imp['name']}: {abs(imp['percent_change']):.1f}% faster")
            
    print("✅ Performance regression check PASSED")


if __name__ == "__main__":
    main()