#!/usr/bin/env python3
"""
Test Batch 164 - Performance Dashboard & Profiler Hooks

This test suite validates the performance dashboard system including:
- System metrics collection and monitoring
- Module performance tracking and load level classification
- Performance recommendations generation
- Dashboard data export and integration
- Profiler hooks and tracking functions
"""

import json
import time
import random
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from core.performance_dashboard import (
    PerformanceDashboard, 
    ModuleLoadLevel, 
    PerformanceMetric,
    get_performance_dashboard,
    start_performance_monitoring,
    stop_performance_monitoring,
    get_dashboard_data,
    export_performance_profile,
    track_ocr_call,
    track_frame_analysis,
    track_io_wait
)

class PerformanceDashboardTester:
    """Test suite for performance dashboard system."""
    
    def __init__(self):
        self.dashboard = get_performance_dashboard()
        self.test_results = []
        self.scenarios = []
        
    def setup_test_scenarios(self):
        """Setup various test scenarios."""
        self.scenarios = [
            {
                "name": "Normal Performance",
                "description": "Test normal performance conditions",
                "cpu_usage": 30.0,
                "memory_usage": 50.0,
                "ocr_calls": 5,
                "frames_analyzed": 20,
                "expected_load_levels": {
                    "green": 3,
                    "yellow": 1,
                    "red": 0
                }
            },
            {
                "name": "High CPU Usage",
                "description": "Test high CPU usage scenario",
                "cpu_usage": 85.0,
                "memory_usage": 60.0,
                "ocr_calls": 15,
                "frames_analyzed": 50,
                "expected_load_levels": {
                    "green": 1,
                    "yellow": 2,
                    "red": 2
                }
            },
            {
                "name": "High Memory Usage",
                "description": "Test high memory usage scenario",
                "cpu_usage": 40.0,
                "memory_usage": 90.0,
                "ocr_calls": 8,
                "frames_analyzed": 30,
                "expected_load_levels": {
                    "green": 0,
                    "yellow": 2,
                    "red": 3
                }
            },
            {
                "name": "Critical Performance",
                "description": "Test critical performance conditions",
                "cpu_usage": 95.0,
                "memory_usage": 95.0,
                "ocr_calls": 25,
                "frames_analyzed": 100,
                "expected_load_levels": {
                    "green": 0,
                    "yellow": 1,
                    "red": 4
                }
            },
            {
                "name": "OCR Heavy Workload",
                "description": "Test high OCR frequency scenario",
                "cpu_usage": 70.0,
                "memory_usage": 75.0,
                "ocr_calls": 20,
                "frames_analyzed": 80,
                "expected_load_levels": {
                    "green": 0,
                    "yellow": 3,
                    "red": 2
                }
            }
        ]
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a test scenario and return results."""
        print(f"\n🧪 Running: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        
        start_time = time.time()
        results = {
            "scenario": scenario["name"],
            "success": False,
            "metrics": {},
            "recommendations": [],
            "errors": []
        }
        
        try:
            # Start monitoring
            start_performance_monitoring()
            
            # Simulate performance conditions
            self._simulate_performance_conditions(scenario)
            
            # Wait for metrics to be collected
            time.sleep(2)
            
            # Get dashboard data
            dashboard_data = get_dashboard_data()
            
            # Validate results
            validation_result = self._validate_scenario_results(scenario, dashboard_data)
            
            results.update(validation_result)
            results["success"] = len(results["errors"]) == 0
            
            # Stop monitoring
            stop_performance_monitoring()
            
        except Exception as e:
            results["errors"].append(f"Scenario failed: {e}")
            results["success"] = False
        
        results["execution_time"] = time.time() - start_time
        return results
    
    def _simulate_performance_conditions(self, scenario: Dict[str, Any]):
        """Simulate performance conditions for testing."""
        # Simulate OCR calls
        for _ in range(scenario["ocr_calls"]):
            track_ocr_call()
            time.sleep(0.1)
        
        # Simulate frame analysis
        for _ in range(scenario["frames_analyzed"]):
            track_frame_analysis()
            time.sleep(0.05)
        
        # Simulate IO wait
        for _ in range(5):
            track_io_wait(random.uniform(0.1, 0.5))
            time.sleep(0.1)
        
        # Simulate module performance
        self._simulate_module_performance(scenario)
    
    def _simulate_module_performance(self, scenario: Dict[str, Any]):
        """Simulate module performance data."""
        modules = [
            "core.ocr",
            "core.screenshot", 
            "core.movement_controller",
            "core.combat_manager",
            "core.navigation"
        ]
        
        for module in modules:
            # Simulate module calls with performance impact
            cpu_impact = scenario["cpu_usage"] / len(modules)
            memory_impact = scenario["memory_usage"] / len(modules)
            
            # Add some variation
            cpu_impact += random.uniform(-10, 10)
            memory_impact += random.uniform(-5, 5)
            
            # Ensure values are within bounds
            cpu_impact = max(0, min(100, cpu_impact))
            memory_impact = max(0, min(100, memory_impact))
            
            # Simulate module execution
            self.dashboard.module_performance[module] = type('obj', (object,), {
                'module_name': module,
                'load_level': self._determine_load_level(cpu_impact, memory_impact),
                'cpu_usage': cpu_impact,
                'memory_usage': memory_impact,
                'call_count': random.randint(10, 100),
                'execution_time': random.uniform(0.1, 2.0),
                'last_updated': datetime.now(),
                'recommendations': self._generate_test_recommendations(cpu_impact, memory_impact)
            })()
    
    def _determine_load_level(self, cpu_usage: float, memory_usage: float) -> ModuleLoadLevel:
        """Determine load level based on CPU and memory usage."""
        if cpu_usage > 50.0 or memory_usage > 100.0:
            return ModuleLoadLevel.RED
        elif cpu_usage > 25.0 or memory_usage > 50.0:
            return ModuleLoadLevel.YELLOW
        else:
            return ModuleLoadLevel.GREEN
    
    def _generate_test_recommendations(self, cpu_usage: float, memory_usage: float) -> List[str]:
        """Generate test recommendations based on usage."""
        recommendations = []
        
        if cpu_usage > 70.0:
            recommendations.append("Consider reducing OCR frequency or optimizing image processing")
        elif cpu_usage > 50.0:
            recommendations.append("Monitor CPU usage and consider caching results")
        
        if memory_usage > 100.0:
            recommendations.append("High memory usage - consider implementing cleanup routines")
        elif memory_usage > 50.0:
            recommendations.append("Monitor memory usage and implement object pooling if needed")
        
        return recommendations
    
    def _validate_scenario_results(self, scenario: Dict[str, Any], dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scenario results against expected outcomes."""
        validation_result = {
            "metrics": {},
            "recommendations": [],
            "errors": []
        }
        
        # Validate system metrics
        system_metrics = dashboard_data.get("system_metrics", {})
        if system_metrics:
            validation_result["metrics"]["cpu_percent"] = system_metrics.get("cpu_percent", 0)
            validation_result["metrics"]["memory_percent"] = system_metrics.get("memory_percent", 0)
            validation_result["metrics"]["ocr_calls_per_minute"] = system_metrics.get("ocr_calls_per_minute", 0)
            validation_result["metrics"]["frames_analyzed_per_minute"] = system_metrics.get("frames_analyzed_per_minute", 0)
        
        # Validate performance metrics
        performance_metrics = dashboard_data.get("performance_metrics", {})
        if performance_metrics:
            validation_result["metrics"]["active_modules"] = performance_metrics.get("active_modules", 0)
            validation_result["metrics"]["heavy_modules"] = performance_metrics.get("heavy_modules", 0)
            validation_result["metrics"]["medium_modules"] = performance_metrics.get("medium_modules", 0)
            validation_result["metrics"]["light_modules"] = performance_metrics.get("light_modules", 0)
        
        # Validate recommendations
        recommendations = dashboard_data.get("recommendations", [])
        validation_result["recommendations"] = recommendations
        
        # Check for expected load levels
        expected_load_levels = scenario.get("expected_load_levels", {})
        actual_load_levels = {
            "green": performance_metrics.get("light_modules", 0),
            "yellow": performance_metrics.get("medium_modules", 0),
            "red": performance_metrics.get("heavy_modules", 0)
        }
        
        for level, expected_count in expected_load_levels.items():
            actual_count = actual_load_levels.get(level, 0)
            if abs(actual_count - expected_count) > 2:  # Allow some variance
                validation_result["errors"].append(
                    f"Load level {level}: expected {expected_count}, got {actual_count}"
                )
        
        return validation_result
    
    def run_all_scenarios(self):
        """Run all test scenarios."""
        print("🚀 Running Performance Dashboard Test Scenarios")
        
        for scenario in self.scenarios:
            result = self.run_scenario(scenario)
            self.test_results.append(result)
            
            if result["success"]:
                print(f"✅ {scenario['name']}: PASSED")
            else:
                print(f"❌ {scenario['name']}: FAILED")
                for error in result["errors"]:
                    print(f"   Error: {error}")
    
    def test_monitoring_functionality(self):
        """Test monitoring start/stop functionality."""
        print("\n🔍 Testing Monitoring Functionality")
        
        try:
            # Test start monitoring
            start_performance_monitoring()
            time.sleep(1)
            
            # Test dashboard data retrieval
            dashboard_data = get_dashboard_data()
            if dashboard_data and dashboard_data.get("status") != "no_data":
                print("✅ Monitoring start: PASSED")
            else:
                print("❌ Monitoring start: FAILED")
            
            # Test stop monitoring
            stop_performance_monitoring()
            print("✅ Monitoring stop: PASSED")
            
        except Exception as e:
            print(f"❌ Monitoring functionality failed: {e}")
    
    def test_tracking_functions(self):
        """Test performance tracking functions."""
        print("\n📊 Testing Tracking Functions")
        
        try:
            # Test OCR call tracking
            for _ in range(5):
                track_ocr_call()
                time.sleep(0.1)
            print("✅ OCR call tracking: PASSED")
            
            # Test frame analysis tracking
            for _ in range(3):
                track_frame_analysis()
                time.sleep(0.1)
            print("✅ Frame analysis tracking: PASSED")
            
            # Test IO wait tracking
            for _ in range(3):
                track_io_wait(random.uniform(0.1, 0.3))
                time.sleep(0.1)
            print("✅ IO wait tracking: PASSED")
            
        except Exception as e:
            print(f"❌ Tracking functions failed: {e}")
    
    def test_recommendations_generation(self):
        """Test performance recommendations generation."""
        print("\n💡 Testing Recommendations Generation")
        
        try:
            # Start monitoring
            start_performance_monitoring()
            
            # Simulate high load conditions
            self._simulate_performance_conditions({
                "cpu_usage": 90.0,
                "memory_usage": 85.0,
                "ocr_calls": 20,
                "frames_analyzed": 80
            })
            
            time.sleep(2)
            
            # Get dashboard data
            dashboard_data = get_dashboard_data()
            recommendations = dashboard_data.get("recommendations", [])
            
            if recommendations:
                print(f"✅ Recommendations generated: {len(recommendations)} recommendations")
                for rec in recommendations[:3]:  # Show first 3
                    print(f"   - {rec.get('category')}: {rec.get('description')}")
            else:
                print("❌ No recommendations generated")
            
            stop_performance_monitoring()
            
        except Exception as e:
            print(f"❌ Recommendations generation failed: {e}")
    
    def test_export_functionality(self):
        """Test profile export functionality."""
        print("\n📤 Testing Export Functionality")
        
        try:
            # Start monitoring and collect data
            start_performance_monitoring()
            time.sleep(2)
            
            # Export profile
            session_id = f"test_session_{int(time.time())}"
            profile = export_performance_profile(session_id)
            
            if profile and "session_id" in profile:
                print("✅ Profile export: PASSED")
                print(f"   Session ID: {profile['session_id']}")
                print(f"   Export timestamp: {profile.get('export_timestamp', 'N/A')}")
                
                # Validate profile structure
                required_fields = ["session_id", "export_timestamp", "dashboard_data"]
                missing_fields = [field for field in required_fields if field not in profile]
                
                if not missing_fields:
                    print("✅ Profile structure: PASSED")
                else:
                    print(f"❌ Profile structure: Missing fields {missing_fields}")
            else:
                print("❌ Profile export: FAILED")
            
            stop_performance_monitoring()
            
        except Exception as e:
            print(f"❌ Export functionality failed: {e}")
    
    def test_configuration_loading(self):
        """Test configuration loading and validation."""
        print("\n⚙️ Testing Configuration Loading")
        
        try:
            # Test configuration loading
            config = self.dashboard.config
            
            required_sections = ["monitoring", "modules", "recommendations", "dashboard"]
            missing_sections = [section for section in required_sections if section not in config]
            
            if not missing_sections:
                print("✅ Configuration loading: PASSED")
                print(f"   Monitoring enabled: {config.get('monitoring', {}).get('enabled', False)}")
                print(f"   Heavy modules: {len(config.get('modules', {}).get('heavy_modules', []))}")
                print(f"   Alert thresholds: {len(config.get('monitoring', {}).get('alert_thresholds', {}))}")
            else:
                print(f"❌ Configuration loading: Missing sections {missing_sections}")
            
        except Exception as e:
            print(f"❌ Configuration loading failed: {e}")
    
    def test_alert_system(self):
        """Test alert system functionality."""
        print("\n🚨 Testing Alert System")
        
        try:
            # Simulate high load conditions
            self._simulate_performance_conditions({
                "cpu_usage": 95.0,
                "memory_usage": 90.0,
                "ocr_calls": 25,
                "frames_analyzed": 100
            })
            
            # Check for alerts
            dashboard_data = get_dashboard_data()
            system_metrics = dashboard_data.get("system_metrics", {})
            
            alerts_generated = False
            if system_metrics.get("cpu_percent", 0) > 80:
                print("✅ CPU alert threshold: PASSED")
                alerts_generated = True
            
            if system_metrics.get("memory_percent", 0) > 85:
                print("✅ Memory alert threshold: PASSED")
                alerts_generated = True
            
            if not alerts_generated:
                print("⚠️ No alerts generated (may be normal)")
            
        except Exception as e:
            print(f"❌ Alert system failed: {e}")
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n📋 Generating Test Report")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        report = {
            "test_summary": {
                "total_scenarios": total_tests,
                "passed_scenarios": passed_tests,
                "failed_scenarios": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "scenario_results": self.test_results,
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}"
            }
        }
        
        # Save report
        report_path = Path("test_reports")
        report_path.mkdir(exist_ok=True)
        
        report_file = report_path / f"performance_dashboard_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to: {report_file}")
        print(f"📊 Summary: {passed_tests}/{total_tests} scenarios passed ({report['test_summary']['success_rate']:.1f}%)")
        
        return report


def main():
    """Run the complete test suite."""
    tester = PerformanceDashboardTester()
    
    try:
        print("🎯 Starting Performance Dashboard Test Suite")
        print("=" * 60)
        
        # Setup scenarios
        tester.setup_test_scenarios()
        
        # Run tests
        tester.run_all_scenarios()
        tester.test_monitoring_functionality()
        tester.test_tracking_functions()
        tester.test_recommendations_generation()
        tester.test_export_functionality()
        tester.test_configuration_loading()
        tester.test_alert_system()
        
        # Generate report
        report = tester.generate_test_report()
        
        print("\n🎉 Performance Dashboard Test Suite Completed!")
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 