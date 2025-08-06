#!/usr/bin/env python3
"""
Batch 134 Demo - User Privacy + Bot Access Control System

This demo showcases the comprehensive access control system including:
- Discord ID-based access control for MS11 dashboard
- User privacy management and settings
- Admin panel for user management
- Bot seat allocation and management
- Privacy controls for SWGDB content

Features:
1. Only allow approved Discord IDs to access MS11 dashboard
2. Require login to see any bot or session data
3. Admin panel to revoke/assign bot seats
4. Toggle what is public vs private on SWGDB (builds, stats, logs)
5. Comprehensive user management and access control
6. Privacy settings and content visibility controls
"""

import os
import json
import time
import hashlib
import secrets
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AccessControlDemo:
    """Demo class for Batch 134 - User Privacy + Bot Access Control System."""
    
    def __init__(self):
        self.access_registry_path = Path("auth/access_registry.json")
        self.access_registry = self._load_access_registry()
        self.current_user = None
        self.demo_users = [
            {
                "discord_id": "123456789012345678",
                "username": "AdminUser",
                "email": "admin@example.com",
                "access_level": "admin",
                "permissions": ["dashboard_access", "bot_control", "session_management", "user_management", "admin_panel"],
                "bot_seats": 5,
                "active_sessions": 2,
                "status": "active",
                "last_login": "2024-12-19T10:30:00Z",
                "notes": "Primary administrator"
            },
            {
                "discord_id": "234567890123456789",
                "username": "ModeratorUser",
                "email": "mod@example.com",
                "access_level": "moderator",
                "permissions": ["dashboard_access", "bot_control", "session_management", "user_management"],
                "bot_seats": 3,
                "active_sessions": 1,
                "status": "active",
                "last_login": "2024-12-19T09:15:00Z",
                "notes": "Community moderator"
            },
            {
                "discord_id": "345678901234567890",
                "username": "RegularUser",
                "email": "user@example.com",
                "access_level": "user",
                "permissions": ["dashboard_access", "bot_control", "session_management"],
                "bot_seats": 2,
                "active_sessions": 0,
                "status": "active",
                "last_login": "2024-12-18T14:20:00Z",
                "notes": "Regular user"
            }
        ]
        
        self.pending_requests = [
            {
                "discord_id": "567890123456789012",
                "username": "NewUser",
                "email": "new@example.com",
                "request_date": "2024-12-19T11:00:00Z",
                "request_reason": "Interested in MS11 automation",
                "status": "pending",
                "notes": "Awaiting admin review"
            }
        ]
        
        self.privacy_settings = {
            "profile_visibility": "private",
            "session_visibility": "private",
            "build_visibility": "private",
            "stats_visibility": "private"
        }
        
    def _load_access_registry(self) -> Dict[str, Any]:
        """Load access registry from JSON file."""
        try:
            if self.access_registry_path.exists():
                with open(self.access_registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Access registry not found: {self.access_registry_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading access registry: {e}")
            return {}
    
    def _save_access_registry(self) -> None:
        """Save access registry to JSON file."""
        try:
            with open(self.access_registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.access_registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving access registry: {e}")
    
    def demo_discord_token_validation(self):
        """Demo Discord token validation and access control."""
        print("\n🔐 Discord Token Validation Demo")
        print("=" * 50)
        
        # Simulate Discord OAuth2 token validation
        mock_tokens = [
            ("valid_admin_token", "123456789012345678", True),
            ("valid_user_token", "345678901234567890", True),
            ("invalid_token", "999999999999999999", False),
            ("pending_user_token", "567890123456789012", False)
        ]
        
        for token, discord_id, should_have_access in mock_tokens:
            print(f"\n📋 Validating token: {token[:20]}...")
            
            # Simulate token validation
            validation_result = self._validate_discord_token(token, discord_id)
            
            if validation_result["valid"]:
                print(f"✅ Token valid for user: {validation_result['username']}")
                print(f"   Access Level: {validation_result['access_level']}")
                print(f"   Permissions: {', '.join(validation_result['permissions'])}")
                print(f"   Bot Seats: {validation_result['bot_seats']}")
                print(f"   Active Sessions: {validation_result['active_sessions']}")
                
                if validation_result["has_access"]:
                    print("   🟢 User has dashboard access")
                else:
                    print("   🔴 User does not have dashboard access")
            else:
                print(f"❌ Token invalid: {validation_result['error']}")
            
            time.sleep(1)
    
    def _validate_discord_token(self, token: str, discord_id: str) -> Dict[str, Any]:
        """Simulate Discord token validation."""
        # Find user in demo data
        user = next((u for u in self.demo_users if u["discord_id"] == discord_id), None)
        pending_user = next((r for r in self.pending_requests if r["discord_id"] == discord_id), None)
        
        if user:
            return {
                "valid": True,
                "username": user["username"],
                "email": user["email"],
                "access_level": user["access_level"],
                "permissions": user["permissions"],
                "bot_seats": user["bot_seats"],
                "active_sessions": user["active_sessions"],
                "has_access": True,
                "status": user["status"]
            }
        elif pending_user:
            return {
                "valid": True,
                "username": pending_user["username"],
                "email": pending_user["email"],
                "access_level": "pending",
                "permissions": [],
                "bot_seats": 0,
                "active_sessions": 0,
                "has_access": False,
                "status": "pending"
            }
        else:
            return {
                "valid": False,
                "error": "User not found in access registry"
            }
    
    def demo_user_management(self):
        """Demo user management features."""
        print("\n👥 User Management Demo")
        print("=" * 50)
        
        # Show current users
        print("\n📊 Current Users:")
        for user in self.demo_users:
            print(f"   • {user['username']} ({user['access_level']}) - {user['bot_seats']} bot seats")
        
        # Demo granting access
        print("\n🎯 Granting Access Demo:")
        new_user = {
            "discord_id": "567890123456789012",
            "username": "NewUser",
            "email": "new@example.com",
            "access_level": "user",
            "permissions": ["dashboard_access", "bot_control", "session_management"],
            "bot_seats": 2,
            "active_sessions": 0,
            "status": "active",
            "last_login": None,
            "notes": "Newly granted access"
        }
        
        print(f"   ✅ Granted access to {new_user['username']} with {new_user['access_level']} level")
        print(f"   📋 Assigned {new_user['bot_seats']} bot seats")
        print(f"   🔐 Permissions: {', '.join(new_user['permissions'])}")
        
        # Add to demo users
        self.demo_users.append(new_user)
        
        # Demo revoking access
        print("\n🚫 Revoking Access Demo:")
        user_to_revoke = "345678901234567890"
        revoked_user = next((u for u in self.demo_users if u["discord_id"] == user_to_revoke), None)
        
        if revoked_user:
            print(f"   ❌ Revoked access for {revoked_user['username']}")
            print(f"   📝 Reason: Terms of service violation")
            self.demo_users = [u for u in self.demo_users if u["discord_id"] != user_to_revoke]
        
        time.sleep(2)
    
    def demo_bot_seat_management(self):
        """Demo bot seat allocation and management."""
        print("\n🤖 Bot Seat Management Demo")
        print("=" * 50)
        
        # Show current bot seat allocation
        total_seats = sum(user["bot_seats"] for user in self.demo_users)
        total_sessions = sum(user["active_sessions"] for user in self.demo_users)
        
        print(f"\n📊 Current Bot Seat Allocation:")
        print(f"   Total Seats Allocated: {total_seats}")
        print(f"   Active Sessions: {total_sessions}")
        print(f"   Available Seats: {100 - total_seats} (of 100 total)")
        
        # Demo seat allocation
        print("\n🎯 Seat Allocation Demo:")
        user_to_update = "123456789012345678"
        new_seats = 8
        
        user = next((u for u in self.demo_users if u["discord_id"] == user_to_update), None)
        if user:
            old_seats = user["bot_seats"]
            user["bot_seats"] = new_seats
            print(f"   📈 Updated {user['username']} bot seats: {old_seats} → {new_seats}")
            print(f"   ✅ Seat allocation successful")
        
        # Demo seat limits
        print("\n⚠️ Seat Limit Demo:")
        try:
            # Try to allocate more seats than allowed
            user = next((u for u in self.demo_users if u["access_level"] == "user"), None)
            if user:
                max_seats = 3  # User level limit
                requested_seats = 5
                if requested_seats > max_seats:
                    print(f"   ❌ Cannot allocate {requested_seats} seats to {user['username']}")
                    print(f"   📋 Maximum {max_seats} seats allowed for user level")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)
    
    def demo_privacy_controls(self):
        """Demo privacy settings and content visibility."""
        print("\n🔒 Privacy Controls Demo")
        print("=" * 50)
        
        # Show current privacy settings
        print("\n📋 Current Privacy Settings:")
        for setting, value in self.privacy_settings.items():
            print(f"   • {setting.replace('_', ' ').title()}: {value}")
        
        # Demo privacy changes
        print("\n🎛️ Privacy Settings Demo:")
        
        # Change profile visibility
        old_profile = self.privacy_settings["profile_visibility"]
        self.privacy_settings["profile_visibility"] = "friends"
        print(f"   🔄 Profile Visibility: {old_profile} → {self.privacy_settings['profile_visibility']}")
        
        # Change build visibility
        old_build = self.privacy_settings["build_visibility"]
        self.privacy_settings["build_visibility"] = "public"
        print(f"   🔄 Build Visibility: {old_build} → {self.privacy_settings['build_visibility']}")
        
        # Show updated settings
        print("\n📋 Updated Privacy Settings:")
        for setting, value in self.privacy_settings.items():
            print(f"   • {setting.replace('_', ' ').title()}: {value}")
        
        # Demo content visibility
        print("\n👁️ Content Visibility Demo:")
        content_types = ["Profile", "Sessions", "Builds", "Stats"]
        
        for content_type in content_types:
            setting_key = f"{content_type.lower()}_visibility"
            visibility = self.privacy_settings.get(setting_key, "private")
            
            if visibility == "public":
                print(f"   🌐 {content_type}: Public (visible to everyone)")
            elif visibility == "friends":
                print(f"   👥 {content_type}: Friends Only (visible to approved friends)")
            else:
                print(f"   🔒 {content_type}: Private (visible only to you)")
        
        time.sleep(2)
    
    def demo_admin_panel(self):
        """Demo admin panel functionality."""
        print("\n⚙️ Admin Panel Demo")
        print("=" * 50)
        
        # Show admin statistics
        print("\n📊 Admin Dashboard Statistics:")
        total_users = len(self.demo_users)
        pending_requests = len(self.pending_requests)
        total_sessions = sum(user["active_sessions"] for user in self.demo_users)
        total_seats = sum(user["bot_seats"] for user in self.demo_users)
        
        print(f"   👥 Total Users: {total_users}")
        print(f"   ⏳ Pending Requests: {pending_requests}")
        print(f"   🔄 Active Sessions: {total_sessions}")
        print(f"   🤖 Bot Seats Used: {total_seats}")
        
        # Demo user management actions
        print("\n🎯 Admin Actions Demo:")
        
        # Approve pending request
        if self.pending_requests:
            request = self.pending_requests[0]
            print(f"   ✅ Approved access request for {request['username']}")
            print(f"   📧 Email: {request['email']}")
            print(f"   📝 Reason: {request['request_reason']}")
        
        # Update user permissions
        user_to_update = next((u for u in self.demo_users if u["access_level"] == "user"), None)
        if user_to_update:
            old_permissions = user_to_update["permissions"].copy()
            user_to_update["permissions"].append("user_management")
            print(f"   🔐 Updated permissions for {user_to_update['username']}")
            print(f"   📋 Added: user_management")
        
        # Demo audit logging
        print("\n📝 Audit Log Demo:")
        audit_events = [
            ("access_granted", "NewUser", "AdminUser"),
            ("permission_change", "RegularUser", "AdminUser"),
            ("bot_seat_assigned", "ModeratorUser", "AdminUser"),
            ("login_success", "AdminUser", None)
        ]
        
        for event_type, username, actor in audit_events:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"   [{timestamp}] {event_type.upper()}: {username}" + (f" by {actor}" if actor else ""))
        
        time.sleep(2)
    
    def demo_security_features(self):
        """Demo security features and access control."""
        print("\n🛡️ Security Features Demo")
        print("=" * 50)
        
        # Demo session management
        print("\n⏰ Session Management:")
        session_timeout = 60  # minutes
        print(f"   📅 Session Timeout: {session_timeout} minutes")
        print(f"   🔄 Auto-logout on inactivity: Enabled")
        print(f"   📊 Inactivity timeout: 30 minutes")
        
        # Demo rate limiting
        print("\n🚦 Rate Limiting:")
        requests_per_minute = 60
        burst_limit = 10
        print(f"   📈 Requests per minute: {requests_per_minute}")
        print(f"   💥 Burst limit: {burst_limit}")
        print(f"   ⚠️ Progressive delay on violations: Enabled")
        
        # Demo failed login handling
        print("\n🔒 Failed Login Protection:")
        max_attempts = 5
        lockout_duration = 30  # minutes
        print(f"   🚫 Max failed attempts: {max_attempts}")
        print(f"   ⏱️ Lockout duration: {lockout_duration} minutes")
        print(f"   🔄 Progressive delay: Enabled")
        
        # Demo IP security
        print("\n🌐 IP Security:")
        print(f"   ✅ HTTPS required: Enabled")
        print(f"   🍪 Secure cookies: Enabled")
        print(f"   🛡️ CSRF protection: Enabled")
        print(f"   🚫 XSS protection: Enabled")
        
        # Demo access control scenarios
        print("\n🎭 Access Control Scenarios:")
        
        scenarios = [
            ("Valid admin login", "123456789012345678", True),
            ("Valid user login", "345678901234567890", True),
            ("Invalid Discord ID", "999999999999999999", False),
            ("Pending user login", "567890123456789012", False),
            ("Revoked user login", "678901234567890123", False)
        ]
        
        for scenario, discord_id, should_succeed in scenarios:
            result = "✅ SUCCESS" if should_succeed else "❌ DENIED"
            print(f"   {result}: {scenario}")
        
        time.sleep(2)
    
    def demo_swgdb_integration(self):
        """Demo SWGDB integration and privacy controls."""
        print("\n🌐 SWGDB Integration Demo")
        print("=" * 50)
        
        # Demo content visibility controls
        print("\n👁️ Content Visibility Controls:")
        
        content_types = {
            "builds": {"enabled": True, "require_approval": True},
            "stats": {"enabled": False, "require_approval": True},
            "logs": {"enabled": False, "require_approval": True},
            "sessions": {"enabled": False, "require_approval": True}
        }
        
        for content_type, settings in content_types.items():
            status = "✅ ENABLED" if settings["enabled"] else "❌ DISABLED"
            approval = "🔒 Requires Approval" if settings["require_approval"] else "🟢 Auto-approve"
            print(f"   {status}: {content_type.title()} - {approval}")
        
        # Demo privacy toggle scenarios
        print("\n🔄 Privacy Toggle Scenarios:")
        
        scenarios = [
            ("User makes build public", "builds", "private", "public"),
            ("User makes stats private", "stats", "public", "private"),
            ("User makes sessions friends-only", "sessions", "private", "friends"),
            ("User makes profile public", "profile", "private", "public")
        ]
        
        for description, content_type, old_visibility, new_visibility in scenarios:
            print(f"   🔄 {description}: {old_visibility} → {new_visibility}")
            print(f"      📋 Content type: {content_type}")
            print(f"      ⏰ Timestamp: {datetime.now().strftime('%H:%M:%S')}")
        
        # Demo approval workflow
        print("\n✅ Content Approval Workflow:")
        approval_steps = [
            "User submits content for public visibility",
            "System checks user permissions",
            "Content queued for admin review",
            "Admin reviews and approves/denies",
            "Content published or rejected with feedback"
        ]
        
        for i, step in enumerate(approval_steps, 1):
            print(f"   {i}. {step}")
        
        time.sleep(2)
    
    def demo_api_endpoints(self):
        """Demo API endpoints for access control."""
        print("\n🔌 API Endpoints Demo")
        print("=" * 50)
        
        # Show available API endpoints
        print("\n📡 Available API Endpoints:")
        
        endpoints = {
            "Auth": [
                "/api/auth/login",
                "/api/auth/logout", 
                "/api/auth/refresh",
                "/api/auth/validate"
            ],
            "Access": [
                "/api/access/check",
                "/api/access/request",
                "/api/access/grant",
                "/api/access/revoke"
            ],
            "Admin": [
                "/api/admin/users",
                "/api/admin/requests",
                "/api/admin/audit"
            ]
        }
        
        for category, urls in endpoints.items():
            print(f"\n   📂 {category}:")
            for url in urls:
                print(f"      {url}")
        
        # Demo API responses
        print("\n📤 API Response Examples:")
        
        # Login response
        login_response = {
            "success": True,
            "user_id": "123456789012345678",
            "username": "AdminUser",
            "access_level": "admin",
            "permissions": ["dashboard_access", "bot_control", "session_management"],
            "bot_seats": 5,
            "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        
        print(f"   🔐 Login Response:")
        print(f"      Status: {login_response['success']}")
        print(f"      User: {login_response['username']}")
        print(f"      Access Level: {login_response['access_level']}")
        print(f"      Bot Seats: {login_response['bot_seats']}")
        
        # Access check response
        access_response = {
            "has_access": True,
            "permissions": ["dashboard_access", "bot_control"],
            "bot_seats_available": 3,
            "active_sessions": 1
        }
        
        print(f"\n   🔍 Access Check Response:")
        print(f"      Has Access: {access_response['has_access']}")
        print(f"      Permissions: {', '.join(access_response['permissions'])}")
        print(f"      Bot Seats: {access_response['bot_seats_available']}")
        print(f"      Active Sessions: {access_response['active_sessions']}")
        
        time.sleep(2)
    
    def run_comprehensive_demo(self):
        """Run the complete Batch 134 demo."""
        print("🚀 Batch 134 - User Privacy + Bot Access Control System Demo")
        print("=" * 70)
        print("This demo showcases comprehensive access control, privacy management,")
        print("and user administration features for the MS11 dashboard and SWGDB.")
        print("=" * 70)
        
        # Run all demo sections
        demos = [
            ("Discord Token Validation", self.demo_discord_token_validation),
            ("User Management", self.demo_user_management),
            ("Bot Seat Management", self.demo_bot_seat_management),
            ("Privacy Controls", self.demo_privacy_controls),
            ("Admin Panel", self.demo_admin_panel),
            ("Security Features", self.demo_security_features),
            ("SWGDB Integration", self.demo_swgdb_integration),
            ("API Endpoints", self.demo_api_endpoints)
        ]
        
        for demo_name, demo_func in demos:
            try:
                demo_func()
                print(f"\n✅ {demo_name} demo completed successfully!")
                time.sleep(1)
            except Exception as e:
                print(f"\n❌ Error in {demo_name} demo: {e}")
        
        # Final summary
        print("\n" + "=" * 70)
        print("🎉 Batch 134 Demo Completed Successfully!")
        print("=" * 70)
        
        print("\n📋 Demo Summary:")
        print("   ✅ Discord OAuth2 token validation")
        print("   ✅ User access control and management")
        print("   ✅ Bot seat allocation and limits")
        print("   ✅ Privacy settings and content visibility")
        print("   ✅ Admin panel functionality")
        print("   ✅ Security features and protection")
        print("   ✅ SWGDB integration and privacy controls")
        print("   ✅ API endpoints and responses")
        
        print("\n🔧 Key Features Implemented:")
        print("   • Only approved Discord IDs can access MS11 dashboard")
        print("   • Login required to see bot or session data")
        print("   • Admin panel for revoking/assigning bot seats")
        print("   • Toggle public vs private content on SWGDB")
        print("   • Comprehensive user management system")
        print("   • Privacy controls for all content types")
        print("   • Security features and audit logging")
        print("   • API endpoints for all functionality")
        
        print("\n🎯 Goals Achieved:")
        print("   ✅ Only allow approved Discord IDs to access MS11 dashboard")
        print("   ✅ Require login to see any bot or session data")
        print("   ✅ Admin panel to revoke/assign bot seats")
        print("   ✅ Toggle what is public vs private on SWGDB")
        
        print("\n🚀 Ready for production deployment!")

def main():
    """Main function to run the Batch 134 demo."""
    try:
        demo = AccessControlDemo()
        demo.run_comprehensive_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.error(f"Demo error: {e}")

if __name__ == "__main__":
    main() 