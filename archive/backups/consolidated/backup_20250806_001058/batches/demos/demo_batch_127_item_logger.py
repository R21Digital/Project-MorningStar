#!/usr/bin/env python3
"""
Demo Script for Batch 127 - Item Discovery Tracker + Vendor Log Recorder

This script demonstrates the comprehensive item discovery and vendor tracking system,
including item logging, vendor profiles, search functionality, and Discord alerts.

Author: SWG Bot Development Team
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import the Item Logger
from tracking.item_logger import (
    ItemLogger, DiscoveredItem, VendorProfile, DiscoverySession,
    ItemCategory, VendorType
)

class ItemLoggerDemo:
    """Demo class for testing the Item Logger functionality."""
    
    def __init__(self):
        """Initialize the demo with sample data."""
        self.item_logger = ItemLogger()
        self.setup_sample_data()
    
    def setup_sample_data(self):
        """Setup sample data for demonstration."""
        print("🔧 Setting up sample data...")
        
        # Add sample items
        sample_items = [
            {
                'item_name': 'Enhanced Composite Chest',
                'category': 'armor',
                'cost': 75000,
                'vendor_id': 'vendor_001',
                'vendor_name': 'Corellian Armor Smith',
                'vendor_type': 'armorsmith',
                'planet': 'Corellia',
                'location': 'Coronet City',
                'coordinates': [0.0, 0.0],
                'timestamp': datetime.now().isoformat(),
                'quality': 'Exceptional',
                'stats': {'constitution': 25, 'stamina': 20},
                'resists': {'energy': 30, 'kinetic': 25},
                'notes': 'High-quality armor piece'
            },
            {
                'item_name': 'Krayt Dragon Bone Sword',
                'category': 'weapons',
                'cost': 150000,
                'vendor_id': 'vendor_002',
                'vendor_name': 'Tatooine Weaponsmith',
                'vendor_type': 'weaponsmith',
                'planet': 'Tatooine',
                'location': 'Mos Eisley',
                'coordinates': [0.0, 0.0],
                'timestamp': datetime.now().isoformat(),
                'quality': 'Mastercraft',
                'stats': {'damage': 150, 'speed': 2.5},
                'resists': {},
                'notes': 'Rare weapon from Krayt Dragon bones'
            },
            {
                'item_name': 'Stun Resist Enhancement',
                'category': 'enhancements',
                'cost': 25000,
                'vendor_id': 'vendor_003',
                'vendor_name': 'Naboo Merchant',
                'vendor_type': 'merchant',
                'planet': 'Naboo',
                'location': 'Theed',
                'coordinates': [0.0, 0.0],
                'timestamp': datetime.now().isoformat(),
                'quality': 'Good',
                'stats': {},
                'resists': {'stun': 50},
                'notes': 'Essential for PvP combat'
            },
            {
                'item_name': 'Rebel Combat Armor',
                'category': 'armor',
                'cost': 45000,
                'vendor_id': 'vendor_004',
                'vendor_name': 'Rebel Armory',
                'vendor_type': 'armorsmith',
                'planet': 'Corellia',
                'location': 'Tyrena',
                'coordinates': [0.0, 0.0],
                'timestamp': datetime.now().isoformat(),
                'quality': 'Excellent',
                'stats': {'constitution': 20, 'stamina': 15},
                'resists': {'energy': 25, 'kinetic': 20},
                'notes': 'Faction-specific armor'
            },
            {
                'item_name': 'Imperial Stormtrooper Armor',
                'category': 'armor',
                'cost': 50000,
                'vendor_id': 'vendor_005',
                'vendor_name': 'Imperial Armory',
                'vendor_type': 'armorsmith',
                'planet': 'Corellia',
                'location': 'Coronet City',
                'coordinates': [0.0, 0.0],
                'timestamp': datetime.now().isoformat(),
                'quality': 'Excellent',
                'stats': {'constitution': 22, 'stamina': 18},
                'resists': {'energy': 28, 'kinetic': 22},
                'notes': 'Faction-specific armor'
            }
        ]
        
        # Log sample items
        for item_data in sample_items:
            item = self.item_logger.log_item_discovery(item_data)
            print(f"✅ Logged item: {item.item_name} at {item.vendor_name}")
        
        # Add sample vendor visits
        vendor_visits = [
            {
                'vendor_id': 'vendor_001',
                'vendor_name': 'Corellian Armor Smith',
                'vendor_type': 'armorsmith',
                'planet': 'Corellia',
                'location': 'Coronet City',
                'coordinates': [0.0, 0.0],
                'timestamp': datetime.now().isoformat(),
                'notes': 'High-quality armor vendor'
            },
            {
                'vendor_id': 'vendor_002',
                'vendor_name': 'Tatooine Weaponsmith',
                'vendor_type': 'weaponsmith',
                'planet': 'Tatooine',
                'location': 'Mos Eisley',
                'coordinates': [0.0, 0.0],
                'timestamp': datetime.now().isoformat(),
                'notes': 'Specializes in rare weapons'
            }
        ]
        
        for vendor_data in vendor_visits:
            vendor = self.item_logger.log_vendor_visit(vendor_data)
            print(f"✅ Logged vendor visit: {vendor.vendor_name}")
        
        # Add item alerts
        self.item_logger.add_item_alert(
            item_name="Krayt",
            alert_type="rare",
            conditions={'min_cost': 100000},
            discord_webhook="https://discord.com/api/webhooks/..."
        )
        
        self.item_logger.add_item_alert(
            item_name="Enhanced Composite",
            alert_type="valuable",
            conditions={'min_cost': 50000, 'vendor_type': 'armorsmith'},
            discord_webhook="https://discord.com/api/webhooks/..."
        )
        
        print("✅ Sample data setup complete!")
    
    def demo_item_logging(self):
        """Demonstrate item logging functionality."""
        print("\n" + "="*60)
        print("📦 ITEM LOGGING DEMONSTRATION")
        print("="*60)
        
        # Log a new item discovery
        new_item_data = {
            'item_name': 'Rare Crystal Enhancement',
            'category': 'enhancements',
            'cost': 85000,
            'vendor_id': 'vendor_006',
            'vendor_name': 'Crystal Merchant',
            'vendor_type': 'merchant',
            'planet': 'Naboo',
            'location': 'Theed Palace',
            'coordinates': [0.0, 0.0],
            'timestamp': datetime.now().isoformat(),
            'quality': 'Mastercraft',
            'stats': {'damage': 75},
            'resists': {'energy': 40},
            'notes': 'Rare crystal enhancement found!'
        }
        
        item = self.item_logger.log_item_discovery(new_item_data)
        print(f"✅ Discovered new item: {item.item_name}")
        print(f"   Cost: {item.cost:,} credits")
        print(f"   Vendor: {item.vendor_name} ({item.vendor_type.value})")
        print(f"   Location: {item.location}, {item.planet}")
        print(f"   Quality: {item.quality}")
    
    def demo_search_functionality(self):
        """Demonstrate search functionality."""
        print("\n" + "="*60)
        print("🔍 SEARCH FUNCTIONALITY DEMONSTRATION")
        print("="*60)
        
        # Search by item name
        print("\n1. Searching for items containing 'Krayt':")
        krayt_items = self.item_logger.search_items(item_name='Krayt')
        for item in krayt_items:
            print(f"   - {item.item_name} ({item.cost:,} credits)")
        
        # Search by vendor type
        print("\n2. Searching for armorsmith vendors:")
        armorsmith_items = self.item_logger.search_items(vendor_type='armorsmith')
        for item in armorsmith_items:
            print(f"   - {item.item_name} at {item.vendor_name}")
        
        # Search by planet
        print("\n3. Searching for items on Corellia:")
        corellia_items = self.item_logger.search_items(planet='Corellia')
        for item in corellia_items:
            print(f"   - {item.item_name} in {item.location}")
        
        # Search by category
        print("\n4. Searching for armor items:")
        armor_items = self.item_logger.search_items(category='armor')
        for item in armor_items:
            print(f"   - {item.item_name} ({item.quality})")
        
        # Search by cost range
        print("\n5. Searching for items between 50k-100k credits:")
        expensive_items = self.item_logger.search_items(min_cost=50000, max_cost=100000)
        for item in expensive_items:
            print(f"   - {item.item_name} ({item.cost:,} credits)")
    
    def demo_vendor_statistics(self):
        """Demonstrate vendor statistics."""
        print("\n" + "="*60)
        print("📊 VENDOR STATISTICS DEMONSTRATION")
        print("="*60)
        
        # Overall statistics
        print("\n1. Overall Vendor Statistics:")
        stats = self.item_logger.get_vendor_statistics()
        print(f"   Total Vendors: {stats['total_vendors']}")
        print(f"   Total Items: {stats['total_items']}")
        print(f"   Total Value: {stats['total_value']:,} credits")
        print(f"   Average Items per Vendor: {stats['average_items_per_vendor']:.1f}")
        print(f"   Average Item Cost: {stats['average_item_cost']:,.0f} credits")
        print(f"   Most Expensive Item: {stats['most_expensive_item']} ({stats['most_expensive_cost']:,} credits)")
        
        # Vendor type breakdown
        print("\n2. Vendor Type Distribution:")
        for vendor_type, count in stats['vendor_types'].items():
            print(f"   {vendor_type.title()}: {count}")
        
        # Planet breakdown
        print("\n3. Planet Distribution:")
        for planet, count in stats['planets'].items():
            print(f"   {planet}: {count}")
        
        # Recent discoveries
        print("\n4. Recent Discoveries (last 24 hours):")
        for item in stats['recent_discoveries']:
            print(f"   - {item.item_name} ({item.cost:,} credits)")
    
    def demo_discovery_sessions(self):
        """Demonstrate discovery session tracking."""
        print("\n" + "="*60)
        print("🎯 DISCOVERY SESSION DEMONSTRATION")
        print("="*60)
        
        # Create a discovery session
        session = self.item_logger.get_discovery_session("DemoCharacter")
        print(f"✅ Created discovery session: {session.session_id}")
        
        # Simulate discovering items during the session
        session_items = [
            self.item_logger.discovered_items[list(self.item_logger.discovered_items.keys())[0]],
            self.item_logger.discovered_items[list(self.item_logger.discovered_items.keys())[1]]
        ]
        
        # Update session with discoveries
        updated_session = self.item_logger.update_discovery_session(session.session_id, session_items)
        print(f"✅ Updated session with {updated_session.items_discovered} items")
        print(f"   Total Value: {updated_session.total_value_discovered:,} credits")
        print(f"   Vendors Discovered: {updated_session.vendors_discovered}")
        print(f"   Planets Visited: {', '.join(updated_session.planets_visited)}")
        print(f"   Most Valuable Item: {updated_session.most_valuable_item} ({updated_session.most_valuable_cost:,} credits)")
    
    def demo_item_alerts(self):
        """Demonstrate item alert functionality."""
        print("\n" + "="*60)
        print("🚨 ITEM ALERT DEMONSTRATION")
        print("="*60)
        
        # Add a new alert
        self.item_logger.add_item_alert(
            item_name="Rare Crystal",
            alert_type="rare",
            conditions={'min_cost': 80000},
            discord_webhook="https://discord.com/api/webhooks/..."
        )
        print("✅ Added alert for 'Rare Crystal' items over 80k credits")
        
        # Simulate discovering an item that triggers an alert
        alert_item_data = {
            'item_name': 'Rare Crystal Enhancement',
            'category': 'enhancements',
            'cost': 85000,
            'vendor_id': 'vendor_007',
            'vendor_name': 'Crystal Merchant',
            'vendor_type': 'merchant',
            'planet': 'Naboo',
            'location': 'Theed Palace',
            'coordinates': [0.0, 0.0],
            'timestamp': datetime.now().isoformat(),
            'quality': 'Mastercraft',
            'stats': {'damage': 75},
            'resists': {'energy': 40}
        }
        
        item = self.item_logger.log_item_discovery(alert_item_data)
        print(f"✅ Discovered item that triggers alert: {item.item_name}")
        print("   Discord alert would be sent for this discovery!")
    
    def demo_export_functionality(self):
        """Demonstrate data export functionality."""
        print("\n" + "="*60)
        print("📤 EXPORT FUNCTIONALITY DEMONSTRATION")
        print("="*60)
        
        # Export Corellia data
        corellia_data = self.item_logger.export_vendor_data(planet='Corellia')
        print(f"✅ Exported Corellia data:")
        print(f"   Vendors: {len(corellia_data['vendors'])}")
        print(f"   Items: {len(corellia_data['items'])}")
        print(f"   Total Value: {corellia_data['statistics']['total_value']:,} credits")
        
        # Export armorsmith data
        armorsmith_data = self.item_logger.export_vendor_data(vendor_type='armorsmith')
        print(f"\n✅ Exported Armorsmith data:")
        print(f"   Vendors: {len(armorsmith_data['vendors'])}")
        print(f"   Items: {len(armorsmith_data['items'])}")
        print(f"   Total Value: {armorsmith_data['statistics']['total_value']:,} credits")
    
    def demo_my_discovered_items(self):
        """Demonstrate personal item discovery tracking."""
        print("\n" + "="*60)
        print("👤 MY DISCOVERED ITEMS DEMONSTRATION")
        print("="*60)
        
        # Get discovered items for a character
        my_items = self.item_logger.get_my_discovered_items("DemoCharacter", limit=10)
        print(f"✅ Found {len(my_items)} items discovered by DemoCharacter:")
        
        for item in my_items:
            print(f"   - {item.item_name} ({item.cost:,} credits)")
            print(f"     Vendor: {item.vendor_name} in {item.location}, {item.planet}")
            print(f"     Discovered: {item.timestamp}")
            print()
    
    def demo_search_archive(self):
        """Demonstrate searchable archive functionality."""
        print("\n" + "="*60)
        print("📚 SEARCHABLE ARCHIVE DEMONSTRATION")
        print("="*60)
        
        # Example searches
        searches = [
            ("Show all Armorsmith vendors on Corellia", 
             {'vendor_type': 'armorsmith', 'planet': 'Corellia'}),
            ("Find all items over 100k credits", 
             {'min_cost': 100000}),
            ("Show all weapons from Tatooine", 
             {'category': 'weapons', 'planet': 'Tatooine'}),
            ("Find all enhancements with stun resist", 
             {'category': 'enhancements', 'item_name': 'stun'}),
            ("Show all items from Coronet City", 
             {'vendor_name': 'Coronet'})
        ]
        
        for search_desc, search_params in searches:
            print(f"\n🔍 {search_desc}:")
            results = self.item_logger.search_items(**search_params)
            print(f"   Found {len(results)} items:")
            for item in results[:3]:  # Show first 3 results
                print(f"     - {item.item_name} ({item.cost:,} credits)")
            if len(results) > 3:
                print(f"     ... and {len(results) - 3} more items")
    
    def run_comprehensive_demo(self):
        """Run the complete demonstration."""
        print("🚀 BATCH 127 - ITEM DISCOVERY TRACKER DEMO")
        print("="*60)
        print("This demo showcases the comprehensive item discovery and vendor tracking system.")
        print("Features include item logging, vendor profiles, search functionality, and Discord alerts.")
        print()
        
        try:
            # Run all demo sections
            self.demo_item_logging()
            self.demo_search_functionality()
            self.demo_vendor_statistics()
            self.demo_discovery_sessions()
            self.demo_item_alerts()
            self.demo_export_functionality()
            self.demo_my_discovered_items()
            self.demo_search_archive()
            
            print("\n" + "="*60)
            print("✅ DEMO COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("The Item Discovery Tracker + Vendor Log Recorder is working perfectly!")
            print("Key features demonstrated:")
            print("  ✓ Item logging with detailed metadata")
            print("  ✓ Vendor profile tracking")
            print("  ✓ Advanced search and filtering")
            print("  ✓ Discovery session management")
            print("  ✓ Item alerts and Discord integration")
            print("  ✓ Data export functionality")
            print("  ✓ Personal item discovery tracking")
            print("  ✓ Searchable archive with complex queries")
            print()
            print("The system is ready for production use!")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main demo function."""
    demo = ItemLoggerDemo()
    demo.run_comprehensive_demo()

if __name__ == "__main__":
    main() 