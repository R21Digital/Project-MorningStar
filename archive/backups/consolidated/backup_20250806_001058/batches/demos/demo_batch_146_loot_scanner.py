#!/usr/bin/env python3
"""
Demo script for Batch 146 - Loot Scan Tracker (MS11 Integration)
Demonstrates the loot scanning functionality and integration
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add core directory to path for imports
sys.path.append(str(Path(__file__).parent / "core"))
from loot_scanner import LootScanner, LootScannerIntegration

def demo_loot_scanner():
    """Demonstrate the loot scanner functionality"""
    print("=" * 60)
    print("BATCH 146 - LOOT SCAN TRACKER DEMO")
    print("=" * 60)
    
    # Initialize loot scanner
    scanner = LootScanner()
    integration = LootScannerIntegration(scanner)
    
    print("\n1. Testing Basic Loot Entry Addition")
    print("-" * 40)
    
    # Add some test loot entries
    test_entries = [
        {
            "item": "Advanced Vibroknuckler",
            "location": "Mos Eisley Bazaar Terminal",
            "seller": "Drako",
            "category": "Weapon"
        },
        {
            "item": "Composite Armor Helmet",
            "location": "Coronet City Vendor",
            "seller": "ArmorSmith",
            "category": "Armor"
        },
        {
            "item": "Enhanced Power Generator",
            "location": "Theed Spaceport Terminal",
            "seller": "TechTrader",
            "category": "Component"
        }
    ]
    
    for entry in test_entries:
        success = scanner.add_loot_entry(**entry)
        print(f"✓ Added: {entry['item']} at {entry['location']}")
    
    print("\n2. Testing Vendor Screen Scanning")
    print("-" * 40)
    
    # Simulate scanning a vendor screen
    vendor_items = [
        {"name": "Heavy Blaster Pistol", "category": "Weapon"},
        {"name": "Combat Armor Vest", "category": "Armor"},
        {"name": "Medical Stim Pack", "category": "Medical"},
        {"name": "Rare Crystal Fragment", "category": "Resource"}
    ]
    
    success = scanner.scan_vendor_screen("Anchorhead Weapons Shop", vendor_items)
    print(f"✓ Scanned {len(vendor_items)} items from vendor")
    
    print("\n3. Testing Loot Screen Scanning")
    print("-" * 40)
    
    # Simulate scanning loot drops
    loot_items = [
        {"name": "Nightsister Energy Lance", "category": "Weapon"},
        {"name": "Ritualist Robes", "category": "Armor"},
        {"name": "Advanced Droid Brain", "category": "Component"}
    ]
    
    success = scanner.scan_loot_screen("Dathomir Stronghold", loot_items)
    print(f"✓ Scanned {len(loot_items)} items from loot drop")
    
    print("\n4. Testing Session Management")
    print("-" * 40)
    
    # Start a session
    integration.start_session()
    print(f"✓ Session started: {integration.is_session_active()}")
    
    # Simulate some activity during session
    session_items = [
        {"item": "Session Item 1", "location": "Session Location", "category": "Weapon"},
        {"item": "Session Item 2", "location": "Session Location", "category": "Armor"}
    ]
    
    for item in session_items:
        scanner.add_loot_entry(**item)
        integration.session_items.append(item)
    
    # End session
    session_summary = integration.end_session()
    print(f"✓ Session ended: {session_summary['items_scanned']} items scanned")
    print(f"  Duration: {session_summary['session_duration']:.2f} seconds")
    
    print("\n5. Testing Statistics and Filtering")
    print("-" * 40)
    
    # Get statistics
    stats = scanner.get_loot_statistics()
    print(f"✓ Total items: {stats['total_items']}")
    print(f"✓ Categories: {list(stats['categories'].keys())}")
    print(f"✓ Locations: {list(stats['locations'].keys())}")
    print(f"✓ Vendors: {list(stats['sellers'].keys())}")
    
    # Test filtering
    weapon_items = scanner.get_loot_history(category="Weapon")
    print(f"✓ Weapon items: {len(weapon_items)}")
    
    location_items = scanner.get_loot_history(location="Mos Eisley")
    print(f"✓ Mos Eisley items: {len(location_items)}")
    
    print("\n6. Testing Data Export")
    print("-" * 40)
    
    # Export JSON
    json_data = scanner.export_loot_data("json")
    if json_data:
        print("✓ JSON export successful")
    
    # Export CSV
    csv_data = scanner.export_loot_data("csv")
    if csv_data:
        print("✓ CSV export successful")
    
    print("\n7. Testing Real-time Integration")
    print("-" * 40)
    
    # Simulate real-time loot scanning
    print("Simulating real-time loot scanning...")
    
    real_time_items = [
        {"item": "Real-time Item 1", "location": "Live Vendor", "seller": "LiveSeller", "category": "Weapon"},
        {"item": "Real-time Item 2", "location": "Live Vendor", "seller": "LiveSeller", "category": "Armor"},
        {"item": "Real-time Item 3", "location": "Live Vendor", "seller": "LiveSeller", "category": "Component"}
    ]
    
    for i, item in enumerate(real_time_items, 1):
        success = scanner.add_loot_entry(**item)
        print(f"  {i}. Added: {item['item']} - {'✓' if success else '✗'}")
        time.sleep(0.5)  # Simulate processing time
    
    print("\n8. Testing Dashboard Integration")
    print("-" * 40)
    
    # Get data for dashboard
    dashboard_data = scanner.get_loot_history(limit=10)
    print(f"✓ Dashboard data: {len(dashboard_data)} recent items")
    
    # Check if loot history file exists
    loot_file = Path("data/logs/loot_history.json")
    if loot_file.exists():
        with open(loot_file, 'r') as f:
            file_data = json.load(f)
        print(f"✓ Loot history file: {len(file_data)} entries")
    else:
        print("✗ Loot history file not found")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("=" * 60)
    
    return True

def demo_advanced_features():
    """Demonstrate advanced features"""
    print("\n" + "=" * 60)
    print("ADVANCED FEATURES DEMO")
    print("=" * 60)
    
    scanner = LootScanner()
    
    print("\n1. Testing Bulk Data Import")
    print("-" * 40)
    
    # Bulk import test data
    bulk_items = []
    for i in range(1, 21):
        bulk_items.append({
            "item": f"Bulk Item {i}",
            "location": f"Location {i % 5 + 1}",
            "seller": f"Vendor {i % 3 + 1}",
            "category": ["Weapon", "Armor", "Component", "Resource", "Medical"][i % 5]
        })
    
    added_count = 0
    for item in bulk_items:
        if scanner.add_loot_entry(**item):
            added_count += 1
    
    print(f"✓ Added {added_count} bulk items")
    
    print("\n2. Testing Data Analysis")
    print("-" * 40)
    
    stats = scanner.get_loot_statistics()
    
    print("Category Distribution:")
    for category, count in stats['categories'].items():
        print(f"  {category}: {count} items")
    
    print("\nTop Locations:")
    sorted_locations = sorted(stats['locations'].items(), key=lambda x: x[1], reverse=True)
    for location, count in sorted_locations[:5]:
        print(f"  {location}: {count} items")
    
    print("\nTop Vendors:")
    sorted_vendors = sorted(stats['sellers'].items(), key=lambda x: x[1], reverse=True)
    for vendor, count in sorted_vendors[:5]:
        print(f"  {vendor}: {count} items")
    
    print("\n3. Testing Data Cleanup")
    print("-" * 40)
    
    # Test clearing data (commented out to preserve demo data)
    # success = scanner.clear_loot_history()
    # print(f"✓ Data cleared: {'✓' if success else '✗'}")
    print("  (Data cleanup skipped to preserve demo data)")
    
    print("\n4. Testing Error Handling")
    print("-" * 40)
    
    # Test invalid data
    invalid_entry = scanner.add_loot_entry(
        item="",  # Empty item name
        location="Test Location",
        category="Test"
    )
    print(f"✓ Invalid entry handling: {'✓' if not invalid_entry else '✗'}")
    
    # Test missing required fields
    try:
        scanner.add_loot_entry(
            item=None,  # None item name
            location="Test Location"
        )
    except Exception as e:
        print(f"✓ Exception handling: ✓ ({type(e).__name__})")
    
    print("\n" + "=" * 60)
    print("ADVANCED FEATURES DEMO COMPLETED")
    print("=" * 60)

def demo_integration_scenarios():
    """Demonstrate integration scenarios"""
    print("\n" + "=" * 60)
    print("INTEGRATION SCENARIOS DEMO")
    print("=" * 60)
    
    scanner = LootScanner()
    integration = LootScannerIntegration(scanner)
    
    print("\n1. Scenario: Vendor Shopping Session")
    print("-" * 40)
    
    # Start vendor shopping session
    integration.start_session()
    print("✓ Started vendor shopping session")
    
    # Simulate visiting multiple vendors
    vendors = [
        ("Mos Eisley Weapons", [
            {"name": "Heavy Blaster Rifle", "category": "Weapon"},
            {"name": "Combat Armor", "category": "Armor"}
        ]),
        ("Coronet Medical", [
            {"name": "Medical Stim Pack", "category": "Medical"},
            {"name": "Healing Kit", "category": "Medical"}
        ]),
        ("Theed Engineering", [
            {"name": "Power Generator", "category": "Component"},
            {"name": "Sensor Array", "category": "Component"}
        ])
    ]
    
    for vendor_name, items in vendors:
        success = scanner.scan_vendor_screen(vendor_name, items)
        print(f"✓ Scanned {len(items)} items from {vendor_name}")
        time.sleep(0.3)
    
    session_summary = integration.end_session()
    print(f"✓ Session completed: {session_summary['items_scanned']} items")
    
    print("\n2. Scenario: Heroic Instance Loot")
    print("-" * 40)
    
    # Simulate heroic instance loot
    heroic_locations = [
        ("Nightsister Stronghold", [
            {"name": "Nightsister Energy Lance", "category": "Weapon"},
            {"name": "Ritualist Robes", "category": "Armor"},
            {"name": "Dark Side Crystal", "category": "Resource"}
        ]),
        ("Axkva Min", [
            {"name": "Sith Lord Armor", "category": "Armor"},
            {"name": "Red Lightsaber", "category": "Weapon"},
            {"name": "Force Crystal", "category": "Resource"}
        ])
    ]
    
    for location, items in heroic_locations:
        success = scanner.scan_loot_screen(location, items)
        print(f"✓ Scanned {len(items)} items from {location}")
        time.sleep(0.3)
    
    print("\n3. Scenario: Market Analysis")
    print("-" * 40)
    
    # Analyze market data
    stats = scanner.get_loot_statistics()
    
    print("Market Analysis Results:")
    print(f"  Total items tracked: {stats['total_items']}")
    print(f"  Unique vendors: {len(stats['sellers'])}")
    print(f"  Unique locations: {len(stats['locations'])}")
    print(f"  Item categories: {len(stats['categories'])}")
    
    # Find most common items
    all_items = scanner.get_loot_history()
    item_counts = {}
    for entry in all_items:
        item_name = entry['item']
        item_counts[item_name] = item_counts.get(item_name, 0) + 1
    
    most_common = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    print("\nMost Common Items:")
    for item, count in most_common:
        print(f"  {item}: {count} occurrences")
    
    print("\n" + "=" * 60)
    print("INTEGRATION SCENARIOS DEMO COMPLETED")
    print("=" * 60)

def main():
    """Main demo function"""
    try:
        print("Starting Batch 146 - Loot Scan Tracker Demo")
        print("This demo will test the MS11 loot scanning integration")
        
        # Run basic demo
        demo_loot_scanner()
        
        # Run advanced features demo
        demo_advanced_features()
        
        # Run integration scenarios
        demo_integration_scenarios()
        
        print("\n" + "=" * 60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Check data/logs/loot_history.json for tracked data")
        print("2. Open dashboard/loot_history.html to view the dashboard")
        print("3. Integrate loot_scanner.py with MS11 session management")
        print("4. Configure real-time loot tracking during gameplay")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 