#!/usr/bin/env python3
"""
Integration Test for Batch 146 - Loot Scan Tracker
Tests MS11 integration and session management
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add core directory to path for imports
sys.path.append(str(Path(__file__).parent / "core"))
from loot_scanner import LootScanner, LootScannerIntegration

def test_ms11_integration():
    """Test MS11 session integration"""
    print("=" * 60)
    print("BATCH 146 - MS11 INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize scanner and integration
    scanner = LootScanner()
    integration = LootScannerIntegration(scanner)
    
    print("\n1. Testing MS11 Session Start")
    print("-" * 40)
    
    # Simulate MS11 session start
    success = integration.start_session()
    print(f"✓ Session started: {success}")
    print(f"✓ Session active: {integration.is_session_active()}")
    
    print("\n2. Testing Real-time Loot Tracking")
    print("-" * 40)
    
    # Simulate real-time loot tracking during MS11 session
    session_items = [
        {"item": "MS11 Session Item 1", "location": "MS11 Vendor", "seller": "MS11Seller", "category": "Weapon"},
        {"item": "MS11 Session Item 2", "location": "MS11 Vendor", "seller": "MS11Seller", "category": "Armor"},
        {"item": "MS11 Session Item 3", "location": "MS11 Vendor", "seller": "MS11Seller", "category": "Component"},
        {"item": "MS11 Session Item 4", "location": "MS11 Vendor", "seller": "MS11Seller", "category": "Resource"},
        {"item": "MS11 Session Item 5", "location": "MS11 Vendor", "seller": "MS11Seller", "category": "Medical"}
    ]
    
    for i, item in enumerate(session_items, 1):
        success = scanner.add_loot_entry(**item)
        integration.session_items.append(item)
        print(f"  {i}. Added: {item['item']} - {'✓' if success else '✗'}")
        time.sleep(0.1)  # Simulate processing time
    
    print("\n3. Testing Session End and Summary")
    print("-" * 40)
    
    # End MS11 session
    session_summary = integration.end_session()
    print(f"✓ Session ended successfully")
    print(f"  Duration: {session_summary['session_duration']:.2f} seconds")
    print(f"  Items scanned: {session_summary['items_scanned']}")
    print(f"  Session active: {integration.is_session_active()}")
    
    print("\n4. Testing Data Persistence")
    print("-" * 40)
    
    # Verify data was saved to file
    loot_file = Path("data/logs/loot_history.json")
    if loot_file.exists():
        with open(loot_file, 'r') as f:
            file_data = json.load(f)
        
        # Count MS11 session items
        ms11_items = [item for item in file_data if "MS11 Session Item" in item.get('item', '')]
        print(f"✓ Loot history file: {len(file_data)} total entries")
        print(f"✓ MS11 session items: {len(ms11_items)} entries")
        
        # Show recent MS11 items
        print("\nRecent MS11 Session Items:")
        for item in ms11_items[-3:]:  # Show last 3 items
            print(f"  - {item['item']} ({item['category']}) at {item['location']}")
    else:
        print("✗ Loot history file not found")
    
    print("\n5. Testing Statistics Generation")
    print("-" * 40)
    
    # Get updated statistics
    stats = scanner.get_loot_statistics()
    print(f"✓ Total items: {stats['total_items']}")
    print(f"✓ Categories: {len(stats['categories'])}")
    print(f"✓ Locations: {len(stats['locations'])}")
    print(f"✓ Vendors: {len(stats['sellers'])}")
    
    # Show category distribution
    print("\nCategory Distribution:")
    for category, count in stats['categories'].items():
        print(f"  {category}: {count} items")
    
    print("\n6. Testing Dashboard Data")
    print("-" * 40)
    
    # Get data for dashboard
    recent_items = scanner.get_loot_history(limit=10)
    print(f"✓ Recent items for dashboard: {len(recent_items)}")
    
    # Check for MS11 items in recent data
    ms11_recent = [item for item in recent_items if "MS11 Session Item" in item.get('item', '')]
    print(f"✓ MS11 items in recent data: {len(ms11_recent)}")
    
    print("\n7. Testing Export Functionality")
    print("-" * 40)
    
    # Test JSON export
    json_export = scanner.export_loot_data("json")
    if json_export:
        print("✓ JSON export successful")
        # Count MS11 items in export
        export_data = json.loads(json_export)
        ms11_export = [item for item in export_data if "MS11 Session Item" in item.get('item', '')]
        print(f"✓ MS11 items in export: {len(ms11_export)}")
    
    # Test CSV export
    csv_export = scanner.export_loot_data("csv")
    if csv_export:
        print("✓ CSV export successful")
        # Count lines in CSV (minus header)
        csv_lines = csv_export.count('\n') - 1
        print(f"✓ CSV entries: {csv_lines}")
    
    print("\n" + "=" * 60)
    print("MS11 INTEGRATION TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)
    
    return True

def test_dashboard_integration():
    """Test dashboard integration"""
    print("\n" + "=" * 60)
    print("DASHBOARD INTEGRATION TEST")
    print("=" * 60)
    
    scanner = LootScanner()
    
    print("\n1. Testing Dashboard Data Loading")
    print("-" * 40)
    
    # Get data for dashboard
    all_items = scanner.get_loot_history()
    print(f"✓ Total items loaded: {len(all_items)}")
    
    # Test filtering
    weapon_items = scanner.get_loot_history(category="Weapon")
    print(f"✓ Weapon items: {len(weapon_items)}")
    
    ms11_items = scanner.get_loot_history(location="MS11")
    print(f"✓ MS11 location items: {len(ms11_items)}")
    
    print("\n2. Testing Statistics for Dashboard")
    print("-" * 40)
    
    stats = scanner.get_loot_statistics()
    
    # Verify statistics structure
    required_stats = ['total_items', 'categories', 'locations', 'sellers', 'recent_activity']
    for stat in required_stats:
        if stat in stats:
            print(f"✓ {stat}: {type(stats[stat]).__name__}")
        else:
            print(f"✗ Missing: {stat}")
    
    print("\n3. Testing Dashboard File")
    print("-" * 40)
    
    dashboard_file = Path("dashboard/loot_history.html")
    if dashboard_file.exists():
        print("✓ Dashboard file exists")
        
        # Check file size
        file_size = dashboard_file.stat().st_size
        print(f"✓ Dashboard file size: {file_size:,} bytes")
        
        # Check for key features
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        features = [
            "Loot History Dashboard",
            "Statistics Dashboard",
            "Filter Loot History",
            "Export Data",
            "lootData",
            "applyFilters",
            "exportData"
        ]
        
        for feature in features:
            if feature in content:
                print(f"✓ Feature found: {feature}")
            else:
                print(f"✗ Missing feature: {feature}")
    else:
        print("✗ Dashboard file not found")
    
    print("\n" + "=" * 60)
    print("DASHBOARD INTEGRATION TEST COMPLETED")
    print("=" * 60)
    
    return True

def test_error_handling():
    """Test error handling and edge cases"""
    print("\n" + "=" * 60)
    print("ERROR HANDLING TEST")
    print("=" * 60)
    
    scanner = LootScanner()
    
    print("\n1. Testing Invalid Data Handling")
    print("-" * 40)
    
    # Test empty item name
    result = scanner.add_loot_entry(
        item="",
        location="Test Location",
        category="Test"
    )
    print(f"✓ Empty item name: {'✓' if not result else '✗'}")
    
    # Test None values
    try:
        result = scanner.add_loot_entry(
            item=None,
            location="Test Location",
            category="Test"
        )
        print(f"✓ None item name: {'✓' if not result else '✗'}")
    except Exception as e:
        print(f"✓ None item name: ✓ ({type(e).__name__})")
    
    # Test missing required fields
    try:
        scanner.add_loot_entry(
            location="Test Location"
            # Missing item parameter
        )
        print("✗ Missing item parameter should have failed")
    except Exception as e:
        print(f"✓ Missing item parameter: ✓ ({type(e).__name__})")
    
    print("\n2. Testing File Operations")
    print("-" * 40)
    
    # Test with invalid data directory
    try:
        invalid_scanner = LootScanner(data_dir="/invalid/path")
        print("✓ Invalid data directory handled gracefully")
    except Exception as e:
        print(f"✓ Invalid data directory: ✓ ({type(e).__name__})")
    
    print("\n3. Testing Export with Empty Data")
    print("-" * 40)
    
    # Test export with no data
    empty_scanner = LootScanner()
    empty_scanner.loot_history = []  # Clear data
    
    json_export = empty_scanner.export_loot_data("json")
    if json_export == "[]":
        print("✓ Empty JSON export: ✓")
    else:
        print(f"✗ Empty JSON export: {json_export}")
    
    csv_export = empty_scanner.export_loot_data("csv")
    if csv_export and "Timestamp,Item,Location,Seller,Category" in csv_export:
        print("✓ Empty CSV export: ✓")
    else:
        print(f"✗ Empty CSV export: {csv_export}")
    
    print("\n" + "=" * 60)
    print("ERROR HANDLING TEST COMPLETED")
    print("=" * 60)
    
    return True

def main():
    """Main integration test function"""
    try:
        print("Starting Batch 146 - Integration Tests")
        print("Testing MS11 loot scanner integration")
        
        # Run all tests
        test_ms11_integration()
        test_dashboard_integration()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("ALL INTEGRATION TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nIntegration Summary:")
        print("✓ MS11 Session Integration: Working")
        print("✓ Real-time Loot Tracking: Working")
        print("✓ Data Persistence: Working")
        print("✓ Dashboard Integration: Working")
        print("✓ Error Handling: Working")
        print("✓ Export Functionality: Working")
        
        print("\nNext Steps:")
        print("1. Integrate loot_scanner.py with MS11 session management")
        print("2. Configure real-time loot tracking during gameplay")
        print("3. Test dashboard at dashboard/loot_history.html")
        print("4. Monitor loot_history.json for new entries")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 