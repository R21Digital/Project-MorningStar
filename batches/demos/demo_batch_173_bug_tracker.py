#!/usr/bin/env python3
"""
Demo Batch 173 - SWGDB.com Bug Tracker System

This demo showcases the bug tracking system functionality including:
- Bug data management and storage
- Admin bug management interface
- User bug reporter form
- Discord webhook integration
- Bug statistics and reporting
- Filtering and sorting capabilities
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class BugReport:
    """Bug report data structure."""
    id: str
    title: str
    description: str
    severity: str
    status: str
    module: str
    reported_by: str
    reported_at: str
    assigned_to: Optional[str] = None
    priority: str = "normal"
    category: str = "general"
    steps_to_reproduce: List[str] = None
    expected_behavior: str = ""
    actual_behavior: str = ""
    browser: str = "N/A"
    os: str = "N/A"
    discord_link: Optional[str] = None
    tags: List[str] = None
    comments: List[Dict[str, Any]] = None
    updated_at: str = ""
    resolved_at: Optional[str] = None

    def __post_init__(self):
        if self.steps_to_reproduce is None:
            self.steps_to_reproduce = []
        if self.tags is None:
            self.tags = []
        if self.comments is None:
            self.comments = []
        if not self.updated_at:
            self.updated_at = self.reported_at


class BugTracker:
    """Manages bug tracking operations."""
    
    def __init__(self, bugs_file: str = "swgdb_site/data/bugs/bugs.json"):
        """Initialize the bug tracker.
        
        Parameters
        ----------
        bugs_file : str
            Path to the bugs JSON file
        """
        self.bugs_file = Path(bugs_file)
        self.bugs_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing bugs
        self.bugs_data = self._load_bugs_data()
        
        logger.info("[BUG_TRACKER] Bug tracker initialized")

    def _load_bugs_data(self) -> Dict[str, Any]:
        """Load existing bugs data from JSON file."""
        try:
            if self.bugs_file.exists():
                with open(self.bugs_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"[BUG_TRACKER] Loaded {len(data.get('bugs', []))} existing bugs")
                return data
            else:
                logger.info("[BUG_TRACKER] No existing bugs file found, creating new one")
                return self._create_default_bugs_data()
        except Exception as e:
            logger.error(f"[BUG_TRACKER] Error loading bugs: {e}")
            return self._create_default_bugs_data()

    def _create_default_bugs_data(self) -> Dict[str, Any]:
        """Create default bugs data structure."""
        return {
            "bugs": [],
            "config": {
                "severity_levels": ["low", "medium", "high", "critical"],
                "status_options": ["open", "in_progress", "resolved", "closed", "duplicate"],
                "priority_levels": ["low", "normal", "high", "urgent"],
                "categories": ["ui", "functionality", "api", "performance", "security", "mobile", "desktop"],
                "modules": ["heroics", "rls", "api", "dashboard", "admin", "user-management", "builds", "loot", "general"],
                "discord_webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL",
                "auto_assign_enabled": True,
                "default_assignee": "admin@swgdb.com",
                "notification_settings": {
                    "new_bug_notifications": True,
                    "status_change_notifications": True,
                    "high_priority_alerts": True,
                    "daily_summary": True
                }
            },
            "stats": {
                "total_bugs": 0,
                "open_bugs": 0,
                "in_progress_bugs": 0,
                "resolved_bugs": 0,
                "critical_bugs": 0,
                "high_priority_bugs": 0,
                "bugs_by_module": {},
                "bugs_by_severity": {}
            }
        }

    def _save_bugs_data(self) -> bool:
        """Save bugs data to JSON file."""
        try:
            with open(self.bugs_file, 'w') as f:
                json.dump(self.bugs_data, f, indent=2, default=str)
            logger.info(f"[BUG_TRACKER] Saved {len(self.bugs_data.get('bugs', []))} bugs")
            return True
        except Exception as e:
            logger.error(f"[BUG_TRACKER] Error saving bugs: {e}")
            return False

    def generate_bug_id(self) -> str:
        """Generate a unique bug ID."""
        return f"BUG-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"

    def create_bug_report(self, data: Dict[str, Any]) -> BugReport:
        """Create a new bug report.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Bug report data
            
        Returns
        -------
        BugReport
            Created bug report
        """
        bug_id = self.generate_bug_id()
        reported_at = datetime.now().isoformat() + "Z"
        
        bug = BugReport(
            id=bug_id,
            title=data.get('title', ''),
            description=data.get('description', ''),
            severity=data.get('severity', 'medium'),
            status='open',
            module=data.get('module', 'general'),
            reported_by=data.get('email', 'anonymous@swgdb.com'),
            reported_at=reported_at,
            priority=data.get('priority', 'normal'),
            category=data.get('category', 'general'),
            steps_to_reproduce=data.get('steps_to_reproduce', []),
            expected_behavior=data.get('expected_behavior', ''),
            actual_behavior=data.get('actual_behavior', ''),
            browser=data.get('browser', 'N/A'),
            os=data.get('os', 'N/A'),
            discord_link=data.get('discord_link'),
            tags=data.get('tags', []),
            updated_at=reported_at
        )
        
        return bug

    def add_bug_report(self, bug: BugReport) -> bool:
        """Add a bug report to the system.
        
        Parameters
        ----------
        bug : BugReport
            Bug report to add
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            # Add to bugs list
            self.bugs_data['bugs'].append(asdict(bug))
            
            # Update statistics
            self._update_statistics()
            
            # Save to file
            success = self._save_bugs_data()
            
            if success:
                logger.info(f"[BUG_TRACKER] Added bug report: {bug.id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"[BUG_TRACKER] Error adding bug report: {e}")
            return False

    def _update_statistics(self):
        """Update bug statistics."""
        bugs = self.bugs_data.get('bugs', [])
        
        stats = {
            "total_bugs": len(bugs),
            "open_bugs": len([b for b in bugs if b.get('status') == 'open']),
            "in_progress_bugs": len([b for b in bugs if b.get('status') == 'in_progress']),
            "resolved_bugs": len([b for b in bugs if b.get('status') == 'resolved']),
            "critical_bugs": len([b for b in bugs if b.get('severity') == 'critical']),
            "high_priority_bugs": len([b for b in bugs if b.get('priority') in ['high', 'urgent']]),
            "bugs_by_module": {},
            "bugs_by_severity": {}
        }
        
        # Count bugs by module
        for bug in bugs:
            module = bug.get('module', 'general')
            stats["bugs_by_module"][module] = stats["bugs_by_module"].get(module, 0) + 1
            
            severity = bug.get('severity', 'medium')
            stats["bugs_by_severity"][severity] = stats["bugs_by_severity"].get(severity, 0) + 1
        
        self.bugs_data['stats'] = stats

    def get_bugs(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get bugs with optional filtering.
        
        Parameters
        ----------
        filters : Optional[Dict[str, Any]]
            Filter criteria
            
        Returns
        -------
        List[Dict[str, Any]]
            Filtered bugs
        """
        bugs = self.bugs_data.get('bugs', [])
        
        if not filters:
            return bugs
        
        filtered_bugs = []
        for bug in bugs:
            include = True
            
            for key, value in filters.items():
                if key in bug and bug[key] != value:
                    include = False
                    break
            
            if include:
                filtered_bugs.append(bug)
        
        return filtered_bugs

    def update_bug_status(self, bug_id: str, status: str, assigned_to: Optional[str] = None) -> bool:
        """Update bug status.
        
        Parameters
        ----------
        bug_id : str
            Bug ID to update
        status : str
            New status
        assigned_to : Optional[str]
            Assignee
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            for bug in self.bugs_data['bugs']:
                if bug['id'] == bug_id:
                    bug['status'] = status
                    bug['updated_at'] = datetime.now().isoformat() + "Z"
                    
                    if assigned_to:
                        bug['assigned_to'] = assigned_to
                    
                    if status == 'resolved':
                        bug['resolved_at'] = datetime.now().isoformat() + "Z"
                    
                    self._update_statistics()
                    self._save_bugs_data()
                    
                    logger.info(f"[BUG_TRACKER] Updated bug {bug_id} status to {status}")
                    return True
            
            logger.warning(f"[BUG_TRACKER] Bug {bug_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"[BUG_TRACKER] Error updating bug status: {e}")
            return False

    def add_comment(self, bug_id: str, author: str, content: str) -> bool:
        """Add a comment to a bug.
        
        Parameters
        ----------
        bug_id : str
            Bug ID
        author : str
            Comment author
        content : str
            Comment content
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            for bug in self.bugs_data['bugs']:
                if bug['id'] == bug_id:
                    comment = {
                        "id": f"COM-{str(uuid.uuid4())[:8].upper()}",
                        "author": author,
                        "content": content,
                        "timestamp": datetime.now().isoformat() + "Z"
                    }
                    
                    bug['comments'].append(comment)
                    bug['updated_at'] = datetime.now().isoformat() + "Z"
                    
                    self._save_bugs_data()
                    
                    logger.info(f"[BUG_TRACKER] Added comment to bug {bug_id}")
                    return True
            
            logger.warning(f"[BUG_TRACKER] Bug {bug_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"[BUG_TRACKER] Error adding comment: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get bug statistics.
        
        Returns
        -------
        Dict[str, Any]
            Bug statistics
        """
        return self.bugs_data.get('stats', {})

    def send_discord_notification(self, bug: BugReport, notification_type: str = "new_bug") -> bool:
        """Send Discord notification for bug.
        
        Parameters
        ----------
        bug : BugReport
            Bug report
        notification_type : str
            Type of notification
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            webhook_url = self.bugs_data['config']['discord_webhook_url']
            
            if webhook_url == "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL":
                logger.info("[BUG_TRACKER] Discord webhook not configured, skipping notification")
                return True
            
            # In a real implementation, this would send to Discord
            # For demo purposes, we'll just log the notification
            logger.info(f"[BUG_TRACKER] Discord notification ({notification_type}): {bug.id}")
            return True
            
        except Exception as e:
            logger.error(f"[BUG_TRACKER] Error sending Discord notification: {e}")
            return False


class BugTrackerDemo:
    """Demo class for showcasing bug tracker functionality."""
    
    def __init__(self):
        """Initialize the demo."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.bugs_file = self.temp_dir / "demo_bugs.json"
        
        # Initialize bug tracker
        self.bug_tracker = BugTracker(str(self.bugs_file))
        
        logger.info("[DEMO] Bug tracker demo initialized")

    def __del__(self):
        """Cleanup temporary files."""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def demo_bug_creation(self):
        """Demo bug creation functionality."""
        print("\n🐛 Demo: Bug Creation")
        print("=" * 50)
        
        # Sample bug reports
        sample_bugs = [
            {
                "title": "Heroics loot table not displaying correctly on mobile",
                "description": "The heroics loot table component is not responsive on mobile devices. Items are overlapping and the filter dropdown is cut off on smaller screens.",
                "severity": "medium",
                "module": "heroics",
                "email": "user@example.com",
                "priority": "normal",
                "category": "ui",
                "steps_to_reproduce": [
                    "Navigate to /heroics/ on mobile device",
                    "Try to use the loot type filter",
                    "Observe overlapping elements"
                ],
                "expected_behavior": "Loot table should be fully responsive and usable on mobile",
                "actual_behavior": "Elements overlap and filters are unusable",
                "browser": "Chrome Mobile",
                "os": "Android 13",
                "discord_link": "https://discord.com/channels/123456789/987654321",
                "tags": ["mobile", "responsive", "heroics"]
            },
            {
                "title": "RLS mode not detecting rare loot properly",
                "description": "The Rare Loot Scan mode is not properly detecting rare loot items in certain areas. False negatives are occurring.",
                "severity": "high",
                "module": "rls",
                "email": "admin@swgdb.com",
                "priority": "high",
                "category": "functionality",
                "steps_to_reproduce": [
                    "Enable RLS mode in MS11",
                    "Navigate to Krayt Dragon spawn area",
                    "Wait for spawn and engage",
                    "Check if rare loot is detected"
                ],
                "expected_behavior": "RLS mode should detect all rare loot items",
                "actual_behavior": "Some rare items are not being detected",
                "browser": "N/A",
                "os": "Windows 11",
                "tags": ["rls", "loot-detection", "ms11"]
            },
            {
                "title": "Build showcase API returning 500 errors",
                "description": "The build showcase API endpoint is intermittently returning 500 internal server errors when fetching build data.",
                "severity": "critical",
                "module": "api",
                "email": "user@example.com",
                "priority": "urgent",
                "category": "api",
                "steps_to_reproduce": [
                    "Make GET request to /api/builds/showcase",
                    "Observe intermittent 500 errors"
                ],
                "expected_behavior": "API should return build data consistently",
                "actual_behavior": "Intermittent 500 errors",
                "browser": "N/A",
                "os": "N/A",
                "tags": ["api", "builds", "server-error"]
            }
        ]
        
        created_bugs = []
        
        for i, data in enumerate(sample_bugs, 1):
            print(f"\n📝 Creating bug report {i}:")
            print(f"   Title: {data['title']}")
            print(f"   Severity: {data['severity']}")
            print(f"   Module: {data['module']}")
            
            # Create bug report
            bug = self.bug_tracker.create_bug_report(data)
            print(f"   ✅ Bug ID: {bug.id}")
            print(f"   ✅ Status: {bug.status}")
            print(f"   ✅ Created: {bug.reported_at}")
            
            # Add to system
            success = self.bug_tracker.add_bug_report(bug)
            if success:
                print(f"   ✅ Added to system")
                created_bugs.append(bug)
                
                # Send Discord notification
                self.bug_tracker.send_discord_notification(bug, "new_bug")
            else:
                print(f"   ❌ Failed to add to system")
        
        print(f"\n📊 Summary: Created {len(created_bugs)} bug reports")
        return created_bugs

    def demo_bug_management(self):
        """Demo bug management functionality."""
        print("\n🔧 Demo: Bug Management")
        print("=" * 50)
        
        # Get all bugs
        bugs = self.bug_tracker.get_bugs()
        print(f"📋 Total bugs: {len(bugs)}")
        
        # Filter bugs by status
        open_bugs = self.bug_tracker.get_bugs({"status": "open"})
        print(f"📋 Open bugs: {len(open_bugs)}")
        
        # Filter bugs by severity
        critical_bugs = self.bug_tracker.get_bugs({"severity": "critical"})
        print(f"📋 Critical bugs: {len(critical_bugs)}")
        
        # Update bug status
        if bugs:
            first_bug = bugs[0]
            print(f"\n🔄 Updating bug {first_bug['id']} status to 'in_progress'")
            
            success = self.bug_tracker.update_bug_status(
                first_bug['id'], 
                'in_progress', 
                'dev@swgdb.com'
            )
            
            if success:
                print(f"   ✅ Status updated successfully")
            else:
                print(f"   ❌ Failed to update status")
        
        # Add comment
        if bugs:
            print(f"\n💬 Adding comment to bug {bugs[0]['id']}")
            
            success = self.bug_tracker.add_comment(
                bugs[0]['id'],
                "admin@swgdb.com",
                "Investigating this issue. Will provide updates soon."
            )
            
            if success:
                print(f"   ✅ Comment added successfully")
            else:
                print(f"   ❌ Failed to add comment")

    def demo_statistics(self):
        """Demo bug statistics functionality."""
        print("\n📊 Demo: Bug Statistics")
        print("=" * 50)
        
        stats = self.bug_tracker.get_statistics()
        
        print(f"📈 Total Bugs: {stats.get('total_bugs', 0)}")
        print(f"📈 Open Bugs: {stats.get('open_bugs', 0)}")
        print(f"📈 In Progress: {stats.get('in_progress_bugs', 0)}")
        print(f"📈 Resolved: {stats.get('resolved_bugs', 0)}")
        print(f"📈 Critical: {stats.get('critical_bugs', 0)}")
        print(f"📈 High Priority: {stats.get('high_priority_bugs', 0)}")
        
        print(f"\n📊 Bugs by Module:")
        for module, count in stats.get('bugs_by_module', {}).items():
            print(f"   {module}: {count}")
        
        print(f"\n📊 Bugs by Severity:")
        for severity, count in stats.get('bugs_by_severity', {}).items():
            print(f"   {severity}: {count}")

    def demo_discord_integration(self):
        """Demo Discord integration functionality."""
        print("\n🔗 Demo: Discord Integration")
        print("=" * 50)
        
        # Sample bug for notification
        sample_bug_data = {
            "title": "Test Discord notification",
            "description": "Testing Discord webhook integration",
            "severity": "medium",
            "module": "general",
            "email": "test@swgdb.com"
        }
        
        bug = self.bug_tracker.create_bug_report(sample_bug_data)
        
        print(f"🐛 Created test bug: {bug.id}")
        print(f"📧 Sending Discord notification...")
        
        success = self.bug_tracker.send_discord_notification(bug, "new_bug")
        
        if success:
            print(f"   ✅ Discord notification sent successfully")
        else:
            print(f"   ❌ Failed to send Discord notification")

    def demo_admin_features(self):
        """Demo admin-specific features."""
        print("\n👨‍💼 Demo: Admin Features")
        print("=" * 50)
        
        # Get bugs for admin view
        bugs = self.bug_tracker.get_bugs()
        
        print(f"📋 Admin Bug Dashboard:")
        print(f"   Total bugs: {len(bugs)}")
        
        # Show bugs by priority
        high_priority_bugs = [b for b in bugs if b.get('priority') in ['high', 'urgent']]
        print(f"   High priority bugs: {len(high_priority_bugs)}")
        
        # Show bugs by module
        module_counts = {}
        for bug in bugs:
            module = bug.get('module', 'general')
            module_counts[module] = module_counts.get(module, 0) + 1
        
        print(f"\n📊 Bugs by Module:")
        for module, count in module_counts.items():
            print(f"   {module}: {count}")
        
        # Resolve a bug
        if bugs:
            bug_to_resolve = bugs[0]
            print(f"\n✅ Resolving bug {bug_to_resolve['id']}")
            
            success = self.bug_tracker.update_bug_status(
                bug_to_resolve['id'], 
                'resolved'
            )
            
            if success:
                print(f"   ✅ Bug resolved successfully")
            else:
                print(f"   ❌ Failed to resolve bug")

    def run_full_demo(self):
        """Run the complete bug tracker demo."""
        print("🚀 SWGDB Bug Tracker System Demo")
        print("=" * 60)
        
        try:
            # Demo bug creation
            created_bugs = self.demo_bug_creation()
            
            # Demo bug management
            self.demo_bug_management()
            
            # Demo statistics
            self.demo_statistics()
            
            # Demo Discord integration
            self.demo_discord_integration()
            
            # Demo admin features
            self.demo_admin_features()
            
            print(f"\n✅ Demo completed successfully!")
            print(f"📁 Demo data saved to: {self.bugs_file}")
            
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            logger.error(f"[DEMO] Demo failed: {e}")


def main():
    """Main demo function."""
    demo = BugTrackerDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main() 