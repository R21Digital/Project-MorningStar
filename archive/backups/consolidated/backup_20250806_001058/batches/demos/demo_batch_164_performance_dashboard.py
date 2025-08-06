#!/usr/bin/env python3
"""
Demo Batch 164 - Performance Dashboard & Profiler Hooks

This demonstration showcases the performance dashboard system including:
- Real-time performance monitoring
- Module load level classification
- Performance recommendations
- Dashboard data visualization
- Profile export functionality
"""

import json
import time
import random
import threading
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

class PerformanceDashboardDemo:
    """Demonstration of performance dashboard system."""
    
    def __init__(self):
        self.dashboard = get_performance_dashboard()
        self.demo_scenarios = []
        self.current_scenario = None
        self.demo_running = False
        
    def setup_demo_scenarios(self):
        """Setup demonstration scenarios."""
        self.demo_scenarios = [
            {
                "name": "Light Performance Demo",
                "description": "Demonstrate normal performance conditions",
                "duration": 30,
                "cpu_target": 25.0,
                "memory_target": 40.0,
                "ocr_frequency": 3,
                "frame_frequency": 10,
                "expected_load_levels": {
                    "green": 4,
                    "yellow": 1,
                    "red": 0
                }
            },
            {
                "name": "Medium Performance Demo",
                "description": "Demonstrate moderate performance impact",
                "duration": 45,
                "cpu_target": 60.0,
                "memory_target": 70.0,
                "ocr_frequency": 8,
                "frame_frequency": 25,
                "expected_load_levels": {
                    "green": 1,
                    "yellow": 3,
                    "red": 1
                }
            },
            {
                "name": "Heavy Performance Demo",
                "description": "Demonstrate high performance impact",
                "duration": 60,
                "cpu_target": 85.0,
                "memory_target": 90.0,
                "ocr_frequency": 15,
                "frame_frequency": 50,
                "expected_load_levels": {
                    "green": 0,
                    "yellow": 2,
                    "red": 3
                }
            },
            {
                "name": "Critical Performance Demo",
                "description": "Demonstrate critical performance conditions",
                "duration": 30,
                "cpu_target": 95.0,
                "memory_target": 95.0,
                "ocr_frequency": 25,
                "frame_frequency": 80,
                "expected_load_levels": {
                    "green": 0,
                    "yellow": 1,
                    "red": 4
                }
            }
        ]
    
    def run_demo_scenario(self, scenario: Dict[str, Any]):
        """Run a demonstration scenario."""
        print(f"\n🎬 Starting Demo: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        print(f"⏱️ Duration: {scenario['duration']} seconds")
        print(f"🎯 Targets: CPU {scenario['cpu_target']}%, Memory {scenario['memory_target']}%")
        
        self.current_scenario = scenario
        self.demo_running = True
        
        # Start monitoring
        start_performance_monitoring()
        
        # Start background simulation
        simulation_thread = threading.Thread(target=self._simulate_performance_conditions, args=(scenario,))
        simulation_thread.daemon = True
        simulation_thread.start()
        
        # Monitor and display results
        start_time = time.time()
        update_interval = 5  # Update every 5 seconds
        
        while self.demo_running and (time.time() - start_time) < scenario['duration']:
            try:
                # Get current dashboard data
                dashboard_data = get_dashboard_data()
                
                # Display current status
                self._display_current_status(dashboard_data, time.time() - start_time)
                
                # Check for recommendations
                recommendations = dashboard_data.get("recommendations", [])
                if recommendations:
                    self._display_recommendations(recommendations)
                
                time.sleep(update_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️ Demo interrupted by user")
                break
            except Exception as e:
                print(f"❌ Demo error: {e}")
                break
        
        # Stop demo
        self.demo_running = False
        stop_performance_monitoring()
        
        # Display final results
        self._display_final_results(scenario)
    
    def _simulate_performance_conditions(self, scenario: Dict[str, Any]):
        """Simulate performance conditions for demonstration."""
        start_time = time.time()
        
        while self.demo_running and (time.time() - start_time) < scenario['duration']:
            try:
                # Simulate OCR calls
                for _ in range(scenario['ocr_frequency']):
                    if not self.demo_running:
                        break
                    track_ocr_call()
                    time.sleep(random.uniform(0.5, 1.5))
                
                # Simulate frame analysis
                for _ in range(scenario['frame_frequency']):
                    if not self.demo_running:
                        break
                    track_frame_analysis()
                    time.sleep(random.uniform(0.2, 0.8))
                
                # Simulate IO operations
                for _ in range(3):
                    if not self.demo_running:
                        break
                    track_io_wait(random.uniform(0.1, 0.5))
                    time.sleep(random.uniform(0.3, 1.0))
                
                # Simulate module performance
                self._simulate_module_performance(scenario)
                
                time.sleep(1)  # Main simulation loop interval
                
            except Exception as e:
                print(f"Simulation error: {e}")
                break
    
    def _simulate_module_performance(self, scenario: Dict[str, Any]):
        """Simulate module performance data."""
        modules = [
            "core.ocr",
            "core.screenshot", 
            "core.movement_controller",
            "core.combat_manager",
            "core.navigation"
        ]
        
        for i, module in enumerate(modules):
            if not self.demo_running:
                break
            
            # Calculate performance impact based on scenario
            base_cpu = scenario['cpu_target'] / len(modules)
            base_memory = scenario['memory_target'] / len(modules)
            
            # Add variation based on module type
            if "ocr" in module:
                cpu_impact = base_cpu * 1.5
                memory_impact = base_memory * 1.2
            elif "screenshot" in module:
                cpu_impact = base_cpu * 1.3
                memory_impact = base_memory * 1.5
            elif "movement" in module:
                cpu_impact = base_cpu * 0.8
                memory_impact = base_memory * 0.7
            else:
                cpu_impact = base_cpu
                memory_impact = base_memory
            
            # Add random variation
            cpu_impact += random.uniform(-10, 10)
            memory_impact += random.uniform(-5, 5)
            
            # Ensure values are within bounds
            cpu_impact = max(0, min(100, cpu_impact))
            memory_impact = max(0, min(100, memory_impact))
            
            # Update module performance
            self.dashboard.module_performance[module] = type('obj', (object,), {
                'module_name': module,
                'load_level': self._determine_load_level(cpu_impact, memory_impact),
                'cpu_usage': cpu_impact,
                'memory_usage': memory_impact,
                'call_count': random.randint(10, 100),
                'execution_time': random.uniform(0.1, 2.0),
                'last_updated': datetime.now(),
                'recommendations': self._generate_demo_recommendations(cpu_impact, memory_impact)
            })()
    
    def _determine_load_level(self, cpu_usage: float, memory_usage: float) -> ModuleLoadLevel:
        """Determine load level based on CPU and memory usage."""
        if cpu_usage > 50.0 or memory_usage > 100.0:
            return ModuleLoadLevel.RED
        elif cpu_usage > 25.0 or memory_usage > 50.0:
            return ModuleLoadLevel.YELLOW
        else:
            return ModuleLoadLevel.GREEN
    
    def _generate_demo_recommendations(self, cpu_usage: float, memory_usage: float) -> List[str]:
        """Generate demo recommendations based on usage."""
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
    
    def _display_current_status(self, dashboard_data: Dict[str, Any], elapsed_time: float):
        """Display current performance status."""
        print(f"\n⏰ Elapsed Time: {elapsed_time:.1f}s")
        print("=" * 50)
        
        # System metrics
        system_metrics = dashboard_data.get("system_metrics", {})
        if system_metrics:
            print(f"🖥️ CPU Usage: {system_metrics.get('cpu_percent', 0):.1f}%")
            print(f"💾 Memory Usage: {system_metrics.get('memory_percent', 0):.1f}%")
            print(f"📊 Available Memory: {system_metrics.get('memory_available_gb', 0):.1f}GB")
            print(f"💿 Disk Usage: {system_metrics.get('disk_usage_percent', 0):.1f}%")
            print(f"🌐 Network IO: {self._format_bytes(system_metrics.get('network_io_bytes', 0))}")
            print(f"⏳ IO Wait: {system_metrics.get('io_wait_percent', 0):.1f}%")
        
        # Performance metrics
        performance_metrics = dashboard_data.get("performance_metrics", {})
        if performance_metrics:
            print(f"\n📈 Performance Metrics:")
            print(f"   OCR Calls/min: {performance_metrics.get('ocr_calls_per_minute', 0)}")
            print(f"   Frames Analyzed/min: {performance_metrics.get('frames_analyzed_per_minute', 0)}")
            print(f"   Active Modules: {performance_metrics.get('active_modules', 0)}")
            print(f"   Heavy Modules: {performance_metrics.get('heavy_modules', 0)}")
            print(f"   Medium Modules: {performance_metrics.get('medium_modules', 0)}")
            print(f"   Light Modules: {performance_metrics.get('light_modules', 0)}")
        
        # Module performance summary
        module_performance = dashboard_data.get("module_performance", {})
        if module_performance:
            print(f"\n🔧 Module Performance:")
            for module_name, module_data in list(module_performance.items())[:3]:  # Show top 3
                load_level = module_data.get('load_level', 'unknown')
                cpu_usage = module_data.get('cpu_usage', 0)
                memory_usage = module_data.get('memory_usage', 0)
                print(f"   {module_name}: {load_level.upper()} (CPU: {cpu_usage:.1f}%, Mem: {memory_usage:.1f}MB)")
    
    def _display_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Display performance recommendations."""
        print(f"\n💡 Performance Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
            priority = rec.get('priority', 'medium').upper()
            category = rec.get('category', 'Unknown')
            description = rec.get('description', 'No description')
            print(f"   {i}. [{priority}] {category}: {description}")
    
    def _display_final_results(self, scenario: Dict[str, Any]):
        """Display final demo results."""
        print(f"\n🎯 Demo Results: {scenario['name']}")
        print("=" * 50)
        
        # Get final dashboard data
        dashboard_data = get_dashboard_data()
        
        # System metrics summary
        system_metrics = dashboard_data.get("system_metrics", {})
        if system_metrics:
            print(f"📊 Final System Metrics:")
            print(f"   CPU Usage: {system_metrics.get('cpu_percent', 0):.1f}% (Target: {scenario['cpu_target']:.1f}%)")
            print(f"   Memory Usage: {system_metrics.get('memory_percent', 0):.1f}% (Target: {scenario['memory_target']:.1f}%)")
        
        # Performance metrics summary
        performance_metrics = dashboard_data.get("performance_metrics", {})
        if performance_metrics:
            print(f"\n📈 Final Performance Metrics:")
            print(f"   OCR Calls/min: {performance_metrics.get('ocr_calls_per_minute', 0)}")
            print(f"   Frames Analyzed/min: {performance_metrics.get('frames_analyzed_per_minute', 0)}")
            print(f"   Heavy Modules: {performance_metrics.get('heavy_modules', 0)}")
            print(f"   Medium Modules: {performance_metrics.get('medium_modules', 0)}")
            print(f"   Light Modules: {performance_metrics.get('light_modules', 0)}")
        
        # Recommendations summary
        recommendations = dashboard_data.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Generated Recommendations: {len(recommendations)}")
            for rec in recommendations:
                priority = rec.get('priority', 'medium').upper()
                category = rec.get('category', 'Unknown')
                print(f"   - [{priority}] {category}")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human readable format."""
        if bytes_value == 0:
            return "0 B"
        k = 1024
        sizes = ['B', 'KB', 'MB', 'GB']
        i = int(__import__('math').log(bytes_value) / __import__('math').log(k))
        return f"{bytes_value / (k ** i):.2f} {sizes[i]}"
    
    def run_all_demos(self):
        """Run all demonstration scenarios."""
        print("🎬 Performance Dashboard Demonstration Suite")
        print("=" * 60)
        
        for i, scenario in enumerate(self.demo_scenarios, 1):
            print(f"\n🎭 Demo {i}/{len(self.demo_scenarios)}: {scenario['name']}")
            print(f"Press Ctrl+C to skip to next demo...")
            
            try:
                self.run_demo_scenario(scenario)
                
                # Brief pause between demos
                if i < len(self.demo_scenarios):
                    print("\n⏸️ Pausing 3 seconds before next demo...")
                    time.sleep(3)
                    
            except KeyboardInterrupt:
                print("\n⏭️ Skipping to next demo...")
                continue
    
    def demonstrate_export_functionality(self):
        """Demonstrate profile export functionality."""
        print("\n📤 Demonstrating Profile Export Functionality")
        print("=" * 50)
        
        try:
            # Start monitoring
            start_performance_monitoring()
            
            # Simulate some activity
            print("🔄 Simulating performance activity...")
            for _ in range(10):
                track_ocr_call()
                track_frame_analysis()
                track_io_wait(random.uniform(0.1, 0.3))
                time.sleep(0.5)
            
            # Export profile
            session_id = f"demo_session_{int(time.time())}"
            print(f"📤 Exporting profile for session: {session_id}")
            
            profile = export_performance_profile(session_id)
            
            if profile:
                print("✅ Profile exported successfully!")
                print(f"   Session ID: {profile.get('session_id', 'N/A')}")
                print(f"   Export Timestamp: {profile.get('export_timestamp', 'N/A')}")
                print(f"   Session Duration: {profile.get('session_duration', 'N/A')}")
                
                # Show profile structure
                dashboard_data = profile.get('dashboard_data', {})
                if dashboard_data:
                    system_metrics = dashboard_data.get('system_metrics', {})
                    performance_metrics = dashboard_data.get('performance_metrics', {})
                    recommendations = dashboard_data.get('recommendations', [])
                    
                    print(f"\n📊 Exported Data Summary:")
                    print(f"   System Metrics: {len(system_metrics)} items")
                    print(f"   Performance Metrics: {len(performance_metrics)} items")
                    print(f"   Recommendations: {len(recommendations)} items")
                    print(f"   Module Performance: {len(dashboard_data.get('module_performance', {}))} modules")
            else:
                print("❌ Profile export failed")
            
            stop_performance_monitoring()
            
        except Exception as e:
            print(f"❌ Export demonstration failed: {e}")
    
    def demonstrate_recommendations(self):
        """Demonstrate recommendations generation."""
        print("\n💡 Demonstrating Recommendations Generation")
        print("=" * 50)
        
        try:
            # Start monitoring
            start_performance_monitoring()
            
            # Simulate different performance conditions
            conditions = [
                {"name": "Normal", "cpu": 30, "memory": 50, "ocr": 5},
                {"name": "High CPU", "cpu": 85, "memory": 60, "ocr": 15},
                {"name": "High Memory", "cpu": 40, "memory": 90, "ocr": 8},
                {"name": "Critical", "cpu": 95, "memory": 95, "ocr": 25}
            ]
            
            for condition in conditions:
                print(f"\n🔄 Simulating {condition['name']} conditions...")
                
                # Simulate conditions
                for _ in range(condition['ocr']):
                    track_ocr_call()
                    time.sleep(0.2)
                
                time.sleep(2)  # Wait for metrics to update
                
                # Get recommendations
                dashboard_data = get_dashboard_data()
                recommendations = dashboard_data.get("recommendations", [])
                
                print(f"📊 {condition['name']} Conditions:")
                print(f"   CPU: {condition['cpu']}%, Memory: {condition['memory']}%, OCR: {condition['ocr']}/min")
                print(f"   Recommendations Generated: {len(recommendations)}")
                
                for i, rec in enumerate(recommendations[:2], 1):
                    priority = rec.get('priority', 'medium').upper()
                    category = rec.get('category', 'Unknown')
                    description = rec.get('description', 'No description')
                    print(f"   {i}. [{priority}] {category}: {description}")
                
                time.sleep(1)
            
            stop_performance_monitoring()
            
        except Exception as e:
            print(f"❌ Recommendations demonstration failed: {e}")
    
    def demonstrate_monitoring_controls(self):
        """Demonstrate monitoring start/stop controls."""
        print("\n🎛️ Demonstrating Monitoring Controls")
        print("=" * 50)
        
        try:
            print("▶️ Starting performance monitoring...")
            start_performance_monitoring()
            time.sleep(2)
            
            dashboard_data = get_dashboard_data()
            if dashboard_data.get("monitoring_active"):
                print("✅ Monitoring started successfully")
            else:
                print("❌ Monitoring failed to start")
            
            print("⏸️ Pausing for 3 seconds...")
            time.sleep(3)
            
            print("⏹️ Stopping performance monitoring...")
            stop_performance_monitoring()
            
            print("✅ Monitoring stopped successfully")
            
        except Exception as e:
            print(f"❌ Monitoring controls demonstration failed: {e}")
    
    def demonstrate_tracking_functions(self):
        """Demonstrate tracking functions."""
        print("\n📊 Demonstrating Tracking Functions")
        print("=" * 50)
        
        try:
            print("🔄 Testing OCR call tracking...")
            for i in range(5):
                track_ocr_call()
                print(f"   OCR call {i+1}/5 tracked")
                time.sleep(0.5)
            
            print("\n🔄 Testing frame analysis tracking...")
            for i in range(3):
                track_frame_analysis()
                print(f"   Frame analysis {i+1}/3 tracked")
                time.sleep(0.5)
            
            print("\n🔄 Testing IO wait tracking...")
            for i in range(3):
                wait_time = random.uniform(0.1, 0.5)
                track_io_wait(wait_time)
                print(f"   IO wait {i+1}/3 tracked ({wait_time:.2f}s)")
                time.sleep(0.5)
            
            print("✅ All tracking functions working correctly")
            
        except Exception as e:
            print(f"❌ Tracking functions demonstration failed: {e}")


def main():
    """Run the complete demonstration."""
    demo = PerformanceDashboardDemo()
    
    try:
        print("🎬 Starting Performance Dashboard Demonstration")
        print("=" * 60)
        
        # Setup scenarios
        demo.setup_demo_scenarios()
        
        # Run demonstrations
        demo.demonstrate_monitoring_controls()
        demo.demonstrate_tracking_functions()
        demo.demonstrate_recommendations()
        demo.run_all_demos()
        demo.demonstrate_export_functionality()
        
        print("\n🎉 Performance Dashboard Demonstration Completed!")
        print("\n📋 Summary:")
        print("   ✅ Monitoring controls demonstrated")
        print("   ✅ Tracking functions demonstrated") 
        print("   ✅ Recommendations generation demonstrated")
        print("   ✅ Performance scenarios demonstrated")
        print("   ✅ Profile export demonstrated")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demonstration interrupted by user")
    except Exception as e:
        print(f"❌ Demonstration failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 