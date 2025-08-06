"""Demo Batch 078 - Support System + Ticket Generator.

This demo showcases the support system functionality including ticket submission,
validation, notifications, and admin dashboard features.
"""

import json
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import time

from api.tickets.post_ticket import (
    TicketManager,
    SupportTicket,
    TicketResponse,
    handle_ticket_submission
)
from discord_alerts.support_notifications import (
    SupportDiscordNotifier,
    SupportNotification,
    create_support_notifier
)


class SupportSystemDemo:
    """Demo class for the support system."""
    
    def __init__(self):
        """Initialize the demo."""
        self.temp_dir = tempfile.mkdtemp()
        self.tickets_file = Path(self.temp_dir) / "support_tickets.json"
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create demo configurations
        self._create_demo_configs()
        
        # Initialize components
        self.ticket_manager = TicketManager(str(self.tickets_file))
        self.discord_notifier = create_support_notifier()
        
        print("🎫 MS11 Support System Demo Initialized")
        print("=" * 50)

    def _create_demo_configs(self):
        """Create demo configuration files."""
        # Email config
        email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "demo@ms11.com",
            "password": "demo_password",
            "from_email": "noreply@ms11.com",
            "admin_email": "admin@ms11.com",
            "use_tls": True
        }
        
        with open(self.config_dir / "email_config.json", 'w') as f:
            json.dump(email_config, f)
        
        # Discord config
        discord_config = {
            "support_webhook_url": "https://discord.com/api/webhooks/demo",
            "discord_token": "demo_token",
            "support_channel_id": 123456789
        }
        
        with open(self.config_dir / "discord_config.json", 'w') as f:
            json.dump(discord_config, f)

    def cleanup(self):
        """Clean up demo resources."""
        shutil.rmtree(self.temp_dir)
        print("\n🧹 Demo cleanup completed")

    def demo_ticket_validation(self):
        """Demo ticket validation functionality."""
        print("\n📋 Demo: Ticket Validation")
        print("-" * 30)
        
        # Valid ticket data
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Software Installation Issue',
            'message': 'I am having trouble installing the software on Windows 10. The installation process stops at 50% and shows an error message.'
        }
        
        print("✅ Valid ticket data:")
        print(f"   Name: {valid_data['name']}")
        print(f"   Email: {valid_data['email']}")
        print(f"   Category: {valid_data['category']}")
        print(f"   Priority: {valid_data['priority']}")
        print(f"   Subject: {valid_data['subject']}")
        print(f"   Message: {valid_data['message'][:50]}...")
        
        errors = self.ticket_manager.validate_ticket_data(valid_data)
        print(f"   Validation result: {'✅ Valid' if not errors else '❌ Invalid'}")
        if errors:
            for error in errors:
                print(f"     - {error}")
        
        # Invalid ticket data
        invalid_data = {
            'name': '',  # Empty name
            'email': 'invalid-email',
            'category': 'invalid_category',
            'priority': 'invalid_priority',
            'subject': '',  # Empty subject
            'message': 'Short'  # Too short
        }
        
        print("\n❌ Invalid ticket data:")
        print(f"   Name: '{invalid_data['name']}'")
        print(f"   Email: '{invalid_data['email']}'")
        print(f"   Category: '{invalid_data['category']}'")
        print(f"   Priority: '{invalid_data['priority']}'")
        print(f"   Subject: '{invalid_data['subject']}'")
        print(f"   Message: '{invalid_data['message']}'")
        
        errors = self.ticket_manager.validate_ticket_data(invalid_data)
        print(f"   Validation result: {'✅ Valid' if not errors else '❌ Invalid'}")
        if errors:
            for error in errors:
                print(f"     - {error}")

    def demo_ticket_creation(self):
        """Demo ticket creation functionality."""
        print("\n🎫 Demo: Ticket Creation")
        print("-" * 30)
        
        # Create sample tickets
        sample_tickets = [
            {
                'name': 'John Doe',
                'email': 'john@example.com',
                'category': 'software',
                'priority': 'high',
                'subject': 'Critical Software Bug',
                'message': 'The software crashes when I try to open large files. This is affecting my daily workflow and I need this resolved urgently.'
            },
            {
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'category': 'account',
                'priority': 'medium',
                'subject': 'Account Access Issue',
                'message': 'I cannot access my account after the recent password reset. The system says my credentials are invalid.'
            },
            {
                'name': 'Bob Wilson',
                'email': 'bob@example.com',
                'category': 'general',
                'priority': 'low',
                'subject': 'Feature Request',
                'message': 'I would like to request a new feature for batch processing. This would greatly improve my workflow efficiency.'
            }
        ]
        
        created_tickets = []
        
        for i, data in enumerate(sample_tickets, 1):
            print(f"\n📝 Creating ticket {i}:")
            print(f"   Customer: {data['name']}")
            print(f"   Category: {data['category']}")
            print(f"   Priority: {data['priority']}")
            print(f"   Subject: {data['subject']}")
            
            # Create ticket
            ticket = self.ticket_manager.create_ticket(data)
            print(f"   ✅ Ticket ID: {ticket.ticket_id}")
            print(f"   ✅ Status: {ticket.status}")
            print(f"   ✅ Created: {ticket.created_at}")
            
            # Add to system
            success = self.ticket_manager.add_ticket(ticket)
            if success:
                print(f"   ✅ Added to system successfully")
                created_tickets.append(ticket)
            else:
                print(f"   ❌ Failed to add to system")
        
        print(f"\n📊 Summary: Created {len(created_tickets)} tickets")
        return created_tickets

    def demo_ticket_statistics(self):
        """Demo ticket statistics functionality."""
        print("\n📊 Demo: Ticket Statistics")
        print("-" * 30)
        
        stats = self.ticket_manager.get_ticket_stats()
        
        print("📈 Current Statistics:")
        print(f"   Total Tickets: {stats['total_tickets']}")
        print(f"   Open Tickets: {stats['open_tickets']}")
        print(f"   Closed Tickets: {stats['closed_tickets']}")
        
        print("\n📂 Category Breakdown:")
        for category, count in stats['categories'].items():
            print(f"   {category.title()}: {count}")
        
        print("\n⚡ Priority Breakdown:")
        for priority, count in stats['priorities'].items():
            emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
            print(f"   {emoji} {priority.title()}: {count}")

    async def demo_discord_notifications(self):
        """Demo Discord notification functionality."""
        print("\n📢 Demo: Discord Notifications")
        print("-" * 30)
        
        # Sample ticket data for notifications
        ticket_data = {
            'ticket_id': 'TKT-20250101-DEMO123',
            'name': 'Demo User',
            'email': 'demo@example.com',
            'subject': 'Demo Notification Test',
            'category': 'software',
            'priority': 'high',
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'message': 'This is a demo notification test to showcase the Discord integration functionality.'
        }
        
        print("🎫 New Ticket Notification:")
        print(f"   Ticket ID: {ticket_data['ticket_id']}")
        print(f"   Customer: {ticket_data['name']}")
        print(f"   Priority: {ticket_data['priority']}")
        print(f"   Category: {ticket_data['category']}")
        
        # Test new ticket notification
        success = await self.discord_notifier.send_new_ticket_notification(ticket_data)
        print(f"   ✅ Notification sent: {success}")
        
        # Test priority alert
        print("\n🚨 Priority Alert Test:")
        success = await self.discord_notifier.send_priority_alert(ticket_data)
        print(f"   ✅ Priority alert sent: {success}")
        
        # Test status update notification
        print("\n📊 Status Update Notification:")
        success = await self.discord_notifier.send_status_update_notification(
            ticket_data, 'open', 'in_progress'
        )
        print(f"   ✅ Status update sent: {success}")
        
        # Test daily summary
        print("\n📈 Daily Summary Test:")
        tickets_data = [ticket_data]  # Use the same ticket for demo
        success = await self.discord_notifier.send_daily_summary(tickets_data)
        print(f"   ✅ Daily summary sent: {success}")

    def demo_ticket_submission_api(self):
        """Demo ticket submission API functionality."""
        print("\n🌐 Demo: Ticket Submission API")
        print("-" * 30)
        
        # Test successful submission
        valid_data = {
            'name': 'API Test User',
            'email': 'api@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'API Integration Test',
            'message': 'This is a test of the ticket submission API functionality to ensure proper validation and processing.'
        }
        
        print("✅ Testing successful submission:")
        print(f"   Customer: {valid_data['name']}")
        print(f"   Email: {valid_data['email']}")
        print(f"   Category: {valid_data['category']}")
        print(f"   Priority: {valid_data['priority']}")
        
        response = handle_ticket_submission(valid_data)
        
        print(f"   Response: {'✅ Success' if response.success else '❌ Failed'}")
        if response.success:
            print(f"   Ticket ID: {response.ticket_id}")
            print(f"   Category: {response.category}")
            print(f"   Priority: {response.priority}")
        else:
            print(f"   Error: {response.error}")
            print(f"   Message: {response.message}")
        
        # Test failed submission
        invalid_data = {
            'name': '',
            'email': 'invalid-email',
            'category': 'invalid_category',
            'priority': 'invalid_priority',
            'subject': '',
            'message': 'Short'
        }
        
        print("\n❌ Testing failed submission:")
        response = handle_ticket_submission(invalid_data)
        
        print(f"   Response: {'✅ Success' if response.success else '❌ Failed'}")
        if not response.success:
            print(f"   Error: {response.error}")
            print(f"   Message: {response.message}")

    def demo_admin_dashboard_features(self):
        """Demo admin dashboard features."""
        print("\n🖥️ Demo: Admin Dashboard Features")
        print("-" * 30)
        
        # Simulate dashboard data
        dashboard_data = {
            'total_tickets': 15,
            'open_tickets': 8,
            'in_progress_tickets': 4,
            'resolved_tickets': 3,
            'high_priority_tickets': 2,
            'recent_activity': [
                {
                    'time': '2 minutes ago',
                    'action': 'New ticket created: TKT-20250101-ABC123'
                },
                {
                    'time': '5 minutes ago',
                    'action': 'Ticket TKT-20250101-DEF456 status updated to In Progress'
                },
                {
                    'time': '10 minutes ago',
                    'action': 'Ticket TKT-20250101-GHI789 resolved'
                }
            ]
        }
        
        print("📊 Dashboard Statistics:")
        print(f"   Total Tickets: {dashboard_data['total_tickets']}")
        print(f"   Open Tickets: {dashboard_data['open_tickets']}")
        print(f"   In Progress: {dashboard_data['in_progress_tickets']}")
        print(f"   Resolved: {dashboard_data['resolved_tickets']}")
        print(f"   High Priority: {dashboard_data['high_priority_tickets']}")
        
        print("\n📝 Recent Activity:")
        for activity in dashboard_data['recent_activity']:
            print(f"   {activity['time']}: {activity['action']}")
        
        print("\n🔧 Available Actions:")
        print("   ✅ View ticket details")
        print("   ✅ Update ticket status")
        print("   ✅ Create new tickets")
        print("   ✅ Export ticket data")
        print("   ✅ Filter by status/priority/category")
        print("   ✅ Generate reports")

    def demo_error_handling(self):
        """Demo error handling functionality."""
        print("\n⚠️ Demo: Error Handling")
        print("-" * 30)
        
        # Test various error scenarios
        error_scenarios = [
            {
                'name': 'Empty Data',
                'data': {},
                'expected_error': 'Missing required field'
            },
            {
                'name': 'Invalid Email',
                'data': {
                    'name': 'Test User',
                    'email': 'not-an-email',
                    'category': 'software',
                    'priority': 'medium',
                    'subject': 'Test',
                    'message': 'This is a test message with sufficient length.'
                },
                'expected_error': 'Invalid email format'
            },
            {
                'name': 'Short Message',
                'data': {
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'category': 'software',
                    'priority': 'medium',
                    'subject': 'Test',
                    'message': 'Short'
                },
                'expected_error': 'at least 10 characters'
            }
        ]
        
        for scenario in error_scenarios:
            print(f"\n🔍 Testing: {scenario['name']}")
            response = handle_ticket_submission(scenario['data'])
            
            if not response.success:
                print(f"   ✅ Error caught: {response.error}")
                if scenario['expected_error'] in response.message:
                    print(f"   ✅ Expected error found: {scenario['expected_error']}")
                else:
                    print(f"   ⚠️ Unexpected error: {response.message}")
            else:
                print(f"   ❌ Error not caught (unexpected success)")

    def demo_performance_testing(self):
        """Demo performance testing functionality."""
        print("\n⚡ Demo: Performance Testing")
        print("-" * 30)
        
        # Test multiple ticket submissions
        print("🚀 Testing multiple ticket submissions...")
        
        start_time = time.time()
        successful_submissions = 0
        failed_submissions = 0
        
        for i in range(10):
            ticket_data = {
                'name': f'Performance Test User {i}',
                'email': f'perf{i}@example.com',
                'category': 'software',
                'priority': 'medium',
                'subject': f'Performance Test {i}',
                'message': f'This is performance test ticket number {i} to measure system response times and throughput.'
            }
            
            response = handle_ticket_submission(ticket_data)
            if response.success:
                successful_submissions += 1
            else:
                failed_submissions += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"📊 Performance Results:")
        print(f"   Total submissions: 10")
        print(f"   Successful: {successful_submissions}")
        print(f"   Failed: {failed_submissions}")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Average time per submission: {total_time/10:.3f} seconds")
        print(f"   Submissions per second: {10/total_time:.2f}")

    async def run_full_demo(self):
        """Run the complete support system demo."""
        print("🚀 Starting MS11 Support System Demo")
        print("=" * 50)
        
        try:
            # Run all demo components
            self.demo_ticket_validation()
            self.demo_ticket_creation()
            self.demo_ticket_statistics()
            await self.demo_discord_notifications()
            self.demo_ticket_submission_api()
            self.demo_admin_dashboard_features()
            self.demo_error_handling()
            self.demo_performance_testing()
            
            print("\n🎉 Demo completed successfully!")
            print("=" * 50)
            
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
        finally:
            self.cleanup()


def main():
    """Main demo function."""
    demo = SupportSystemDemo()
    
    # Run the demo
    asyncio.run(demo.run_full_demo())


if __name__ == "__main__":
    main() 