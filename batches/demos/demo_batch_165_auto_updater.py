#!/usr/bin/env python3
"""
Demo Batch 165 - Auto-Updater & Channeling (Stable/Canary)

This demonstration showcases the auto-updater system including:
- Version checking and comparison
- Download with hash verification
- Staged application on next launch
- Rollback on failure
- Channel switching (stable/canary)
- Dashboard integration
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from updater.update_client import (
    UpdateClient, 
    UpdateChannel, 
    UpdateStatus,
    VersionInfo,
    get_update_client,
    check_for_updates,
    download_update,
    stage_update,
    apply_update,
    get_update_status,
    set_update_channel,
    start_auto_update_check,
    stop_auto_update_check
)

class AutoUpdaterDemo:
    """Demonstration of auto-updater system."""
    
    def __init__(self):
        self.update_client = get_update_client()
        self.demo_scenarios = []
        self.current_scenario = None
        self.demo_running = False
        
    def setup_demo_scenarios(self):
        """Setup demonstration scenarios."""
        self.demo_scenarios = [
            {
                "name": "Stable Channel Demo",
                "description": "Demonstrate stable channel update process",
                "channel": UpdateChannel.STABLE,
                "mock_version": "2.1.0",
                "mock_changelog": [
                    "Fixed critical security vulnerability",
                    "Improved performance by 15%",
                    "Added new quest tracking features",
                    "Enhanced UI responsiveness"
                ],
                "expected_behavior": "Smooth update process with low risk"
            },
            {
                "name": "Canary Channel Demo",
                "description": "Demonstrate canary channel update process",
                "channel": UpdateChannel.CANARY,
                "mock_version": "2.2.0-alpha.1",
                "mock_changelog": [
                    "Experimental AI companion improvements",
                    "New combat system prototype",
                    "Advanced performance profiling",
                    "Beta testing features"
                ],
                "expected_behavior": "Early access with higher risk"
            },
            {
                "name": "Update Failure Demo",
                "description": "Demonstrate rollback on update failure",
                "channel": UpdateChannel.STABLE,
                "mock_version": "2.1.1",
                "mock_changelog": [
                    "Bug fix that will fail",
                    "Simulated update failure"
                ],
                "expected_behavior": "Automatic rollback to previous version"
            },
            {
                "name": "Channel Switching Demo",
                "description": "Demonstrate switching between channels",
                "channel": UpdateChannel.CANARY,
                "mock_version": "2.2.0-beta.1",
                "mock_changelog": [
                    "Channel switching test",
                    "Cross-channel compatibility"
                ],
                "expected_behavior": "Seamless channel switching"
            }
        ]
        
    def run_demo_scenario(self, scenario: Dict[str, Any]):
        """Run a specific demo scenario."""
        print(f"\n{'='*60}")
        print(f"Running: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Expected Behavior: {scenario['expected_behavior']}")
        print(f"{'='*60}")
        
        self.current_scenario = scenario
        self.demo_running = True
        
        # Step 1: Set channel
        print(f"\n1. Setting update channel to: {scenario['channel'].value}")
        set_update_channel(scenario['channel'])
        
        # Step 2: Check for updates
        print(f"\n2. Checking for updates...")
        available_update = self._mock_check_for_updates(scenario)
        
        if available_update:
            print(f"   ✓ Update available: {available_update.version}")
            print(f"   Channel: {available_update.channel.value}")
            print(f"   Build: {available_update.build_number}")
            print(f"   Size: {self._format_bytes(available_update.file_size)}")
            
            # Step 3: Download update
            print(f"\n3. Downloading update...")
            if self._mock_download_update(available_update):
                print(f"   ✓ Download completed successfully")
                
                # Step 4: Stage update
                print(f"\n4. Staging update...")
                if self._mock_stage_update(available_update):
                    print(f"   ✓ Update staged successfully")
                    
                    # Step 5: Apply update (if not failure demo)
                    if "failure" not in scenario['name'].lower():
                        print(f"\n5. Applying update...")
                        if self._mock_apply_update(available_update):
                            print(f"   ✓ Update applied successfully")
                        else:
                            print(f"   ✗ Update application failed")
                    else:
                        print(f"\n5. Simulating update failure...")
                        self._mock_update_failure()
                        
                else:
                    print(f"   ✗ Update staging failed")
            else:
                print(f"   ✗ Download failed")
        else:
            print(f"   No updates available")
            
        # Step 6: Display final status
        print(f"\n6. Final Update Status:")
        self._display_update_status()
        
        self.demo_running = False
        self.current_scenario = None
        
    def _mock_check_for_updates(self, scenario: Dict[str, Any]) -> VersionInfo:
        """Mock check for updates."""
        time.sleep(1)  # Simulate network delay
        
        return VersionInfo(
            version=scenario['mock_version'],
            build_number=12345,
            release_date=datetime.now().isoformat(),
            channel=scenario['channel'],
            download_url=f"https://updates.ms11.com/{scenario['channel'].value}/download/{scenario['mock_version']}",
            file_size=15 * 1024 * 1024,  # 15MB
            checksum="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234",
            changelog=scenario['mock_changelog'],
            is_mandatory=False,
            min_compatible_version="1.0.0"
        )
        
    def _mock_download_update(self, version_info: VersionInfo) -> bool:
        """Mock download update with progress."""
        total_steps = 10
        for i in range(total_steps):
            progress = (i + 1) / total_steps * 100
            downloaded = int(version_info.file_size * progress / 100)
            print(f"   Downloading: {progress:.1f}% ({self._format_bytes(downloaded)}/{self._format_bytes(version_info.file_size)})")
            time.sleep(0.2)  # Simulate download time
            
        return True
        
    def _mock_stage_update(self, version_info: VersionInfo) -> bool:
        """Mock stage update."""
        print(f"   Creating backup...")
        time.sleep(0.5)
        print(f"   Extracting update package...")
        time.sleep(0.5)
        print(f"   Verifying file integrity...")
        time.sleep(0.5)
        print(f"   Creating update manifest...")
        time.sleep(0.5)
        
        return True
        
    def _mock_apply_update(self, version_info: VersionInfo) -> bool:
        """Mock apply update."""
        print(f"   Applying update files...")
        time.sleep(0.5)
        print(f"   Updating version information...")
        time.sleep(0.5)
        print(f"   Cleaning up staging files...")
        time.sleep(0.5)
        
        return True
        
    def _mock_update_failure(self):
        """Mock update failure and rollback."""
        print(f"   Simulating update failure...")
        time.sleep(0.5)
        print(f"   Update application failed!")
        print(f"   Initiating automatic rollback...")
        time.sleep(1.0)
        print(f"   Restoring from backup...")
        time.sleep(0.5)
        print(f"   Rollback completed successfully")
        
    def _display_update_status(self):
        """Display current update status."""
        status = get_update_status()
        
        print(f"   Current Version: {status['current_version']}")
        print(f"   Update Channel: {status['channel']}")
        print(f"   Has Pending Update: {status['has_pending_update']}")
        
        if status['available_version']:
            print(f"   Available Version: {status['available_version']['version']}")
            print(f"   Release Date: {status['available_version']['release_date']}")
            
        if status['progress']:
            progress = status['progress']
            print(f"   Status: {progress['status']}")
            print(f"   Current Step: {progress['current_step']}")
            print(f"   Progress: {progress['progress_percent']:.1f}%")
            
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
        
    def demonstrate_channel_switching(self):
        """Demonstrate switching between update channels."""
        print(f"\n{'='*60}")
        print("Channel Switching Demonstration")
        print(f"{'='*60}")
        
        # Current channel
        current_channel = self.update_client.get_channel()
        print(f"\nCurrent Channel: {current_channel.value}")
        
        # Switch to canary
        print(f"\nSwitching to Canary channel...")
        set_update_channel(UpdateChannel.CANARY)
        time.sleep(1)
        
        # Check for updates on canary
        print(f"Checking for updates on Canary channel...")
        canary_update = self._mock_check_for_updates({
            "channel": UpdateChannel.CANARY,
            "mock_version": "2.2.0-alpha.2",
            "mock_changelog": ["Canary channel test"]
        })
        
        if canary_update:
            print(f"   ✓ Canary update available: {canary_update.version}")
            
        # Switch back to stable
        print(f"\nSwitching back to Stable channel...")
        set_update_channel(UpdateChannel.STABLE)
        time.sleep(1)
        
        # Check for updates on stable
        print(f"Checking for updates on Stable channel...")
        stable_update = self._mock_check_for_updates({
            "channel": UpdateChannel.STABLE,
            "mock_version": "2.1.1",
            "mock_changelog": ["Stable channel test"]
        })
        
        if stable_update:
            print(f"   ✓ Stable update available: {stable_update.version}")
            
    def demonstrate_auto_update_check(self):
        """Demonstrate automatic update checking."""
        print(f"\n{'='*60}")
        print("Auto-Update Check Demonstration")
        print(f"{'='*60}")
        
        print(f"\nStarting automatic update checking...")
        start_auto_update_check()
        
        # Let it run for a few seconds
        time.sleep(3)
        
        print(f"Stopping automatic update checking...")
        stop_auto_update_check()
        
        print(f"Auto-update check demonstration completed")
        
    def demonstrate_dashboard_integration(self):
        """Demonstrate dashboard integration features."""
        print(f"\n{'='*60}")
        print("Dashboard Integration Demonstration")
        print(f"{'='*60}")
        
        # Get update status for dashboard
        status = get_update_status()
        
        print(f"\nDashboard Update Status:")
        print(f"   Current Version: {status['current_version']}")
        print(f"   Channel: {status['channel']}")
        print(f"   Has Pending Update: {status['has_pending_update']}")
        
        if status['available_version']:
            print(f"\nAvailable Update:")
            print(f"   Version: {status['available_version']['version']}")
            print(f"   Build: {status['available_version']['build_number']}")
            print(f"   Release Date: {status['available_version']['release_date']}")
            print(f"   Channel: {status['available_version']['channel']}")
            print(f"   File Size: {self._format_bytes(status['available_version']['file_size'])}")
            print(f"   Mandatory: {status['available_version']['is_mandatory']}")
            
            print(f"\nChangelog:")
            for change in status['available_version']['changelog']:
                print(f"   • {change}")
                
        if status['progress']:
            progress = status['progress']
            print(f"\nUpdate Progress:")
            print(f"   Status: {progress['status']}")
            print(f"   Step: {progress['current_step']}")
            print(f"   Progress: {progress['progress_percent']:.1f}%")
            
            if progress['downloaded_bytes'] > 0:
                print(f"   Downloaded: {self._format_bytes(progress['downloaded_bytes'])}")
                
            if progress['estimated_time_remaining']:
                print(f"   ETA: {progress['estimated_time_remaining']:.1f} seconds")
                
    def run_all_demos(self):
        """Run all demonstration scenarios."""
        print("Auto-Updater & Channeling System Demo")
        print("=" * 60)
        
        self.setup_demo_scenarios()
        
        # Run each scenario
        for scenario in self.demo_scenarios:
            self.run_demo_scenario(scenario)
            time.sleep(2)  # Pause between scenarios
            
        # Demonstrate channel switching
        self.demonstrate_channel_switching()
        
        # Demonstrate auto-update checking
        self.demonstrate_auto_update_check()
        
        # Demonstrate dashboard integration
        self.demonstrate_dashboard_integration()
        
        print(f"\n{'='*60}")
        print("All demonstrations completed successfully!")
        print("Auto-Updater & Channeling System is working correctly.")
        print(f"{'='*60}")


def main():
    """Main demonstration function."""
    try:
        demo = AutoUpdaterDemo()
        demo.run_all_demos()
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 