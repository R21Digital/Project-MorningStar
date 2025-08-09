#!/usr/bin/env python3
"""
Performance comparison tool for MS11 regression testing.
Compares benchmark results between baseline and current performance.
"""

import json
import sys
import argparse
from typing import Dict, List, Any, Optional
from pathlib import Path
import statistics


class PerformanceComparer:
    """Compare performance benchmarks and detect regressions."""
    
    def __init__(self, regression_threshold: float = 20.0):
        self.regression_threshold = regression_threshold  # Percent threshold for regression
        self.improvement_threshold = 10.0  # Percent threshold for improvement
        
    def load_benchmark_data(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load benchmark JSON data."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Benchmark file not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing benchmark file {file_path}: {e}")
            return None
            
    def extract_benchmark_stats(self, data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Extract benchmark statistics from pytest-benchmark data."""
        stats = {}
        
        if 'benchmarks' not in data:
            return stats
            
        for benchmark in data['benchmarks']:
            name = benchmark.get('name', 'unknown')
            stats_data = benchmark.get('stats', {})
            
            stats[name] = {
                'mean': stats_data.get('mean', 0.0),
                'min': stats_data.get('min', 0.0),
                'max': stats_data.get('max', 0.0),
                'stddev': stats_data.get('stddev', 0.0),
                'rounds': stats_data.get('rounds', 0),
                'iterations': stats_data.get('iterations', 0)
            }
            
        return stats
        
    def compare_benchmarks(self, baseline_stats: Dict[str, Dict[str, float]], 
                          current_stats: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Compare benchmark statistics and identify regressions/improvements."""
        comparison = {
            'regressions': [],
            'improvements': [],
            'stable': [],
            'missing_baselines': [],
            'new_benchmarks': [],
            'summary': {
                'total_benchmarks': len(current_stats),
                'regressions_count': 0,
                'improvements_count': 0,
                'stable_count': 0
            }
        }
        
        # Compare existing benchmarks
        for name, current in current_stats.items():
            if name not in baseline_stats:
                comparison['new_benchmarks'].append({
                    'name': name,
                    'mean_time': current['mean'],
                    'rounds': current['rounds']
                })
                continue
                
            baseline = baseline_stats[name]
            
            # Calculate percentage change
            if baseline['mean'] > 0:
                percent_change = ((current['mean'] - baseline['mean']) / baseline['mean']) * 100
            else:
                percent_change = 0.0
                
            benchmark_comparison = {
                'name': name,
                'baseline_mean': baseline['mean'],
                'current_mean': current['mean'],
                'percent_change': percent_change,
                'baseline_stddev': baseline['stddev'],
                'current_stddev': current['stddev'],
                'baseline_rounds': baseline['rounds'],
                'current_rounds': current['rounds']
            }
            
            # Classify the change
            if percent_change > self.regression_threshold:
                comparison['regressions'].append(benchmark_comparison)
                comparison['summary']['regressions_count'] += 1
            elif percent_change < -self.improvement_threshold:
                comparison['improvements'].append(benchmark_comparison)
                comparison['summary']['improvements_count'] += 1
            else:
                comparison['stable'].append(benchmark_comparison)
                comparison['summary']['stable_count'] += 1
                
        # Check for missing benchmarks
        for name in baseline_stats:
            if name not in current_stats:
                comparison['missing_baselines'].append({
                    'name': name,
                    'baseline_mean': baseline_stats[name]['mean']
                })
                
        return comparison
        
    def format_time(self, seconds: float) -> str:
        """Format time in human-readable format."""
        if seconds < 0.001:
            return f"{seconds * 1000000:.1f}μs"
        elif seconds < 1.0:
            return f"{seconds * 1000:.1f}ms"
        else:
            return f"{seconds:.3f}s"
            
    def print_comparison_report(self, comparison: Dict[str, Any]):
        """Print detailed comparison report."""
        print("=" * 80)
        print("MS11 PERFORMANCE COMPARISON REPORT")
        print("=" * 80)
        
        summary = comparison['summary']
        print(f"\nSUMMARY:")
        print(f"  Total benchmarks: {summary['total_benchmarks']}")
        print(f"  Regressions: {summary['regressions_count']}")
        print(f"  Improvements: {summary['improvements_count']}")
        print(f"  Stable: {summary['stable_count']}")
        print(f"  New benchmarks: {len(comparison['new_benchmarks'])}")
        print(f"  Missing baselines: {len(comparison['missing_baselines'])}")
        
        # Print regressions (most important)
        if comparison['regressions']:
            print(f"\n🔴 PERFORMANCE REGRESSIONS (>{self.regression_threshold}% slower):")
            print("-" * 80)
            for reg in sorted(comparison['regressions'], key=lambda x: x['percent_change'], reverse=True):
                print(f"  {reg['name']}")
                print(f"    Baseline: {self.format_time(reg['baseline_mean'])}")
                print(f"    Current:  {self.format_time(reg['current_mean'])}")
                print(f"    Change:   +{reg['percent_change']:.1f}% SLOWER")
                print()
        
        # Print improvements
        if comparison['improvements']:
            print(f"\n🟢 PERFORMANCE IMPROVEMENTS (>{self.improvement_threshold}% faster):")
            print("-" * 80)
            for imp in sorted(comparison['improvements'], key=lambda x: x['percent_change']):
                print(f"  {imp['name']}")
                print(f"    Baseline: {self.format_time(imp['baseline_mean'])}")
                print(f"    Current:  {self.format_time(imp['current_mean'])}")
                print(f"    Change:   {abs(imp['percent_change']):.1f}% FASTER")
                print()
        
        # Print new benchmarks
        if comparison['new_benchmarks']:
            print(f"\n🆕 NEW BENCHMARKS:")
            print("-" * 80)
            for new in comparison['new_benchmarks']:
                print(f"  {new['name']}: {self.format_time(new['mean_time'])}")
                
        # Print missing benchmarks
        if comparison['missing_baselines']:
            print(f"\n⚠️  MISSING BENCHMARKS (present in baseline but not current):")
            print("-" * 80)
            for missing in comparison['missing_baselines']:
                print(f"  {missing['name']}: {self.format_time(missing['baseline_mean'])}")
                
        # Print stable benchmarks summary
        if comparison['stable']:
            print(f"\n✅ STABLE BENCHMARKS ({len(comparison['stable'])} total)")
            print("-" * 80)
            
            # Show summary statistics for stable benchmarks
            stable_changes = [abs(s['percent_change']) for s in comparison['stable']]
            if stable_changes:
                avg_change = statistics.mean(stable_changes)
                max_change = max(stable_changes)
                print(f"  Average change: {avg_change:.1f}%")
                print(f"  Maximum change: {max_change:.1f}%")
                
                # Show a few examples
                print(f"  Examples:")
                for stable in comparison['stable'][:3]:
                    change_str = f"{stable['percent_change']:+.1f}%"
                    print(f"    {stable['name']}: {self.format_time(stable['current_mean'])} ({change_str})")
                    
        print("\n" + "=" * 80)
        
    def check_regression_threshold(self, comparison: Dict[str, Any]) -> bool:
        """Check if any regressions exceed the acceptable threshold."""
        if not comparison['regressions']:
            return True  # No regressions
            
        # Check if any regression is above critical threshold (2x the normal threshold)
        critical_threshold = self.regression_threshold * 2
        critical_regressions = [
            r for r in comparison['regressions'] 
            if r['percent_change'] > critical_threshold
        ]
        
        if critical_regressions:
            print(f"\n❌ CRITICAL REGRESSIONS DETECTED (>{critical_threshold}% slower):")
            for reg in critical_regressions:
                print(f"  {reg['name']}: +{reg['percent_change']:.1f}%")
            return False
            
        # Check if too many regressions overall
        if len(comparison['regressions']) > 5:
            print(f"\n❌ TOO MANY REGRESSIONS: {len(comparison['regressions'])} > 5")
            return False
            
        print(f"\n✅ Regressions within acceptable limits")
        return True
        
    def generate_html_report(self, comparison: Dict[str, Any], output_file: str):
        """Generate HTML report for CI/CD integration."""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>MS11 Performance Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; }
        .regression { color: #d32f2f; }
        .improvement { color: #388e3c; }
        .stable { color: #1976d2; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>MS11 Performance Comparison Report</h1>
"""
        
        # Add summary
        summary = comparison['summary']
        html_content += f"""
    <div class="summary">
        <h2>Summary</h2>
        <p>Total benchmarks: {summary['total_benchmarks']}</p>
        <p class="regression">Regressions: {summary['regressions_count']}</p>
        <p class="improvement">Improvements: {summary['improvements_count']}</p>
        <p class="stable">Stable: {summary['stable_count']}</p>
    </div>
"""
        
        # Add regressions table
        if comparison['regressions']:
            html_content += """
    <h2 class="regression">Performance Regressions</h2>
    <table>
        <tr><th>Benchmark</th><th>Baseline</th><th>Current</th><th>Change</th></tr>
"""
            for reg in comparison['regressions']:
                html_content += f"""
        <tr>
            <td>{reg['name']}</td>
            <td>{self.format_time(reg['baseline_mean'])}</td>
            <td>{self.format_time(reg['current_mean'])}</td>
            <td class="regression">+{reg['percent_change']:.1f}%</td>
        </tr>
"""
            html_content += "</table>"
            
        # Add improvements table
        if comparison['improvements']:
            html_content += """
    <h2 class="improvement">Performance Improvements</h2>
    <table>
        <tr><th>Benchmark</th><th>Baseline</th><th>Current</th><th>Change</th></tr>
"""
            for imp in comparison['improvements']:
                html_content += f"""
        <tr>
            <td>{imp['name']}</td>
            <td>{self.format_time(imp['baseline_mean'])}</td>
            <td>{self.format_time(imp['current_mean'])}</td>
            <td class="improvement">{imp['percent_change']:.1f}%</td>
        </tr>
"""
            html_content += "</table>"
            
        html_content += """
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html_content)
            
        print(f"HTML report generated: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Compare MS11 performance benchmarks")
    parser.add_argument("baseline", help="Baseline benchmark JSON file")
    parser.add_argument("current", help="Current benchmark JSON file")
    parser.add_argument("--threshold", type=float, default=20.0, 
                       help="Regression threshold percentage (default: 20)")
    parser.add_argument("--html", help="Generate HTML report file")
    parser.add_argument("--fail-on-regression", action="store_true",
                       help="Exit with error code if regressions detected")
    
    args = parser.parse_args()
    
    comparer = PerformanceComparer(regression_threshold=args.threshold)
    
    # Load benchmark data
    baseline_data = comparer.load_benchmark_data(args.baseline)
    current_data = comparer.load_benchmark_data(args.current)
    
    if not current_data:
        print("Error: Could not load current benchmark data")
        sys.exit(1)
        
    if not baseline_data:
        print("Warning: No baseline data available - showing current results only")
        current_stats = comparer.extract_benchmark_stats(current_data)
        
        print(f"\nCURRENT BENCHMARK RESULTS ({len(current_stats)} benchmarks):")
        print("-" * 80)
        for name, stats in current_stats.items():
            print(f"  {name}: {comparer.format_time(stats['mean'])}")
            
        sys.exit(0)
        
    # Extract statistics
    baseline_stats = comparer.extract_benchmark_stats(baseline_data)
    current_stats = comparer.extract_benchmark_stats(current_data)
    
    # Compare benchmarks
    comparison = comparer.compare_benchmarks(baseline_stats, current_stats)
    
    # Print report
    comparer.print_comparison_report(comparison)
    
    # Generate HTML report if requested
    if args.html:
        comparer.generate_html_report(comparison, args.html)
        
    # Check if we should fail on regressions
    if args.fail_on_regression:
        if not comparer.check_regression_threshold(comparison):
            print("\n❌ Performance regression check FAILED")
            sys.exit(1)
        else:
            print("\n✅ Performance regression check PASSED")
            
    print("\nPerformance comparison completed successfully!")


if __name__ == "__main__":
    main()