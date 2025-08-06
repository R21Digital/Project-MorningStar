#!/usr/bin/env python3
"""
Demo script for Batch 075 - Vendor Scanning + Galactic Bazaar Search Logic

This demo showcases:
1. Vendor Scanner Service functionality
2. Vendor API Plugin endpoints
3. Integration with existing bazaar module
4. Crafting Mode integration
5. Cache management and reporting
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import vendor scanner and API
try:
    from services.vendor_scanner import VendorScanner, create_vendor_scanner
    from plugins.vendor_api import VendorAPI, create_vendor_api
    VENDOR_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"[DEMO] Vendor services not available: {e}")
    VENDOR_SERVICES_AVAILABLE = False

# Import existing bazaar module
try:
    from modules.bazaar import VendorManager, PriceTracker, BazaarDetector
    BAZAAR_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"[DEMO] Bazaar module not available: {e}")
    BAZAAR_MODULE_AVAILABLE = False

from android_ms11.utils.logging_utils import log_event


def demo_vendor_scanner_service():
    """Demo the vendor scanner service functionality."""
    print("\n" + "="*60)
    print("DEMO: Vendor Scanner Service")
    print("="*60)
    
    if not VENDOR_SERVICES_AVAILABLE:
        print("❌ Vendor services not available")
        return
    
    # Create vendor scanner
    scanner = create_vendor_scanner()
    print("✅ Vendor scanner created")
    
    # Demo 1: Scan nearby vendors
    print("\n📍 Scanning nearby vendors...")
    player_location = ("tatooine", "mos_eisley", (3520, -4800))
    vendors = scanner.scan_nearby_vendors(player_location)
    
    print(f"Found {len(vendors)} vendors:")
    for vendor in vendors:
        print(f"  - {vendor.vendor_name} ({vendor.vendor_type}) at {vendor.coordinates}")
        print(f"    Items: {len(vendor.items)}")
        for item in vendor.items[:3]:  # Show first 3 items
            print(f"      • {item.name}: {item.quantity} @ {item.price} credits")
    
    # Demo 2: Search for specific items
    print("\n🔍 Searching for items...")
    search_items = ["Stimpack", "Rifle", "Durindfire"]
    search_results = scanner.search_for_items(search_items, max_price=10000)
    
    print(f"Search results:")
    for item_name, results in search_results.items():
        print(f"  {item_name}: {len(results)} sources found")
        for result in results[:2]:  # Show first 2 results
            source = result["source"]
            price = result["price"]
            location = result.get("location", "Unknown")
            print(f"    • {source}: {price} credits at {location}")
    
    # Demo 3: Get cache statistics
    print("\n📊 Cache statistics:")
    stats = scanner.get_cache_stats()
    print(f"  Total vendors: {stats['total_vendors']}")
    print(f"  Total bazaar listings: {stats['total_bazaar_listings']}")
    print(f"  Total items: {stats['total_items']}")
    print(f"  Cache size: {stats['cache_size_mb']} MB")
    
    # Demo 4: Export cache report
    print("\n📄 Exporting cache report...")
    report_path = scanner.export_cache_report()
    print(f"  Report exported to: {report_path}")
    
    return scanner


def demo_vendor_api_plugin():
    """Demo the vendor API plugin functionality."""
    print("\n" + "="*60)
    print("DEMO: Vendor API Plugin")
    print("="*60)
    
    if not VENDOR_SERVICES_AVAILABLE:
        print("❌ Vendor services not available")
        return
    
    # Create vendor API
    api = create_vendor_api()
    print("✅ Vendor API created")
    
    # Demo 1: API info
    print("\nℹ️ API Information:")
    api_info = api.get_api_info()
    print(f"  API Name: {api_info['data']['api_name']}")
    print(f"  Version: {api_info['data']['version']}")
    print(f"  Vendor Scanner Available: {api_info['data']['vendor_scanner_available']}")
    print(f"  Endpoints: {list(api_info['data']['endpoints'].keys())}")
    
    # Demo 2: Search items via API
    print("\n🔍 API Search for items...")
    search_response = api.search_items(
        item_names=["Stimpack", "Rifle"],
        max_price=15000,
        include_bazaar=True
    )
    
    if search_response["success"]:
        data = search_response["data"]
        print(f"  Items searched: {data['items_searched']}")
        print(f"  Total items found: {data['total_items_found']}")
        
        for item_name, results in data["search_results"].items():
            print(f"  {item_name}: {len(results)} sources")
    else:
        print(f"  ❌ Search failed: {search_response['error']}")
    
    # Demo 3: Get vendors by location
    print("\n📍 API Get vendors by location...")
    vendors_response = api.get_vendors_by_location("tatooine", "mos_eisley")
    
    if vendors_response["success"]:
        data = vendors_response["data"]
        print(f"  Location: {data['location']}")
        print(f"  Total vendors: {data['total_vendors']}")
        
        for vendor in data["vendors"][:2]:  # Show first 2 vendors
            print(f"    • {vendor['vendor_name']} ({vendor['vendor_type']})")
    else:
        print(f"  ❌ Failed to get vendors: {vendors_response['error']}")
    
    # Demo 4: Scan location via API
    print("\n🔍 API Scan location...")
    scan_response = api.scan_location(("tatooine", "mos_eisley", (3520, -4800)))
    
    if scan_response["success"]:
        data = scan_response["data"]
        print(f"  Scan location: {data['scan_location']}")
        print(f"  Vendors detected: {data['total_vendors']}")
    else:
        print(f"  ❌ Scan failed: {scan_response['error']}")
    
    # Demo 5: Get bazaar listings
    print("\n🏪 API Get bazaar listings...")
    bazaar_response = api.get_bazaar_listings(["Durindfire", "Spice Wine"])
    
    if bazaar_response["success"]:
        data = bazaar_response["data"]
        print(f"  Search terms: {data['search_terms']}")
        print(f"  Total listings: {data['total_listings']}")
        
        for listing in data["bazaar_listings"][:3]:  # Show first 3 listings
            print(f"    • {listing['item_name']}: {listing['quantity']} @ {listing['price']} credits")
    else:
        print(f"  ❌ Failed to get bazaar listings: {bazaar_response['error']}")
    
    # Demo 6: Get cache stats via API
    print("\n📊 API Cache statistics:")
    stats_response = api.get_cache_stats()
    
    if stats_response["success"]:
        stats = stats_response["data"]["cache_stats"]
        print(f"  Total vendors: {stats['total_vendors']}")
        print(f"  Total bazaar listings: {stats['total_bazaar_listings']}")
        print(f"  Cache size: {stats['cache_size_mb']} MB")
    else:
        print(f"  ❌ Failed to get cache stats: {stats_response['error']}")
    
    return api


def demo_crafting_integration():
    """Demo integration with crafting mode."""
    print("\n" + "="*60)
    print("DEMO: Crafting Mode Integration")
    print("="*60)
    
    if not VENDOR_SERVICES_AVAILABLE:
        print("❌ Vendor services not available")
        return
    
    api = create_vendor_api()
    
    # Demo 1: Crafting suggestions
    print("\n🛠️ Crafting suggestions...")
    required_items = ["Stimpack", "Durindfire", "Rifle", "Ammo Pack"]
    max_budget = 50000
    
    suggestions_response = api.get_crafting_suggestions(required_items, max_budget)
    
    if suggestions_response["success"]:
        data = suggestions_response["data"]
        print(f"  Required items: {data['required_items']}")
        print(f"  Items found: {data['items_found']}")
        print(f"  Items missing: {data['items_missing']}")
        print(f"  Total cost: {data['total_cost']} credits")
        print(f"  Budget remaining: {data['budget_remaining']} credits")
        
        print("\n  Best deals:")
        for suggestion in data["crafting_suggestions"]:
            item_name = suggestion["item_name"]
            best_deal = suggestion["best_deal"]
            price = best_deal["price"]
            source = best_deal["source"]
            location = best_deal.get("location", "Unknown")
            print(f"    • {item_name}: {price} credits at {source} ({location})")
    else:
        print(f"  ❌ Failed to get crafting suggestions: {suggestions_response['error']}")
    
    # Demo 2: Export cache report via API
    print("\n📄 API Export cache report...")
    export_response = api.export_cache_report()
    
    if export_response["success"]:
        print(f"  Report exported to: {export_response['data']['report_path']}")
    else:
        print(f"  ❌ Failed to export report: {export_response['error']}")


def demo_bazaar_module_integration():
    """Demo integration with existing bazaar module."""
    print("\n" + "="*60)
    print("DEMO: Bazaar Module Integration")
    print("="*60)
    
    if not BAZAAR_MODULE_AVAILABLE:
        print("❌ Bazaar module not available")
        return
    
    print("✅ Bazaar module available")
    
    # Demo existing bazaar functionality
    print("\n🏪 Existing bazaar module components:")
    print("  • VendorManager: Main vendor manager for intelligent bazaar operations")
    print("  • PriceTracker: Track and analyze price trends")
    print("  • BazaarDetector: Detect vendor terminals and interface elements")
    
    # Show how vendor scanner complements existing bazaar module
    print("\n🔄 Integration points:")
    print("  • VendorScanner provides enhanced scanning and caching")
    print("  • VendorAPI provides RESTful endpoints for external access")
    print("  • Existing bazaar module handles real-time interactions")
    print("  • Combined system provides comprehensive vendor intelligence")


def demo_comprehensive_workflow():
    """Demo a comprehensive workflow combining all components."""
    print("\n" + "="*60)
    print("DEMO: Comprehensive Workflow")
    print("="*60)
    
    if not VENDOR_SERVICES_AVAILABLE:
        print("❌ Vendor services not available")
        return
    
    # Create both scanner and API
    scanner = create_vendor_scanner()
    api = create_vendor_api(scanner)
    
    print("✅ Comprehensive workflow initialized")
    
    # Step 1: Player arrives at new location
    print("\n📍 Step 1: Player arrives at new location")
    player_location = ("naboo", "theed", (5000, -3000))
    print(f"  Location: {player_location}")
    
    # Step 2: Scan for nearby vendors
    print("\n🔍 Step 2: Scan for nearby vendors")
    vendors = scanner.scan_nearby_vendors(player_location)
    print(f"  Detected {len(vendors)} vendors")
    
    # Step 3: Crafting mode needs resources
    print("\n🛠️ Step 3: Crafting mode needs resources")
    required_items = ["Stimpack", "Durindfire", "Basic Supply"]
    print(f"  Required items: {required_items}")
    
    # Step 4: Search for items via API
    print("\n🔍 Step 4: Search for items via API")
    search_response = api.search_items(required_items, max_price=10000)
    
    if search_response["success"]:
        data = search_response["data"]
        print(f"  Found {data['total_items_found']} items")
        
        # Step 5: Generate crafting suggestions
        print("\n💡 Step 5: Generate crafting suggestions")
        suggestions_response = api.get_crafting_suggestions(required_items, 25000)
        
        if suggestions_response["success"]:
            suggestions_data = suggestions_response["data"]
            print(f"  Items found: {suggestions_data['items_found']}/{len(required_items)}")
            print(f"  Total cost: {suggestions_data['total_cost']} credits")
            print(f"  Budget remaining: {suggestions_data['budget_remaining']} credits")
            
            # Step 6: Export report for analysis
            print("\n📄 Step 6: Export analysis report")
            report_response = api.export_cache_report()
            if report_response["success"]:
                print(f"  Report exported: {report_response['data']['report_path']}")
    
    print("\n✅ Comprehensive workflow completed")


def demo_error_handling():
    """Demo error handling and edge cases."""
    print("\n" + "="*60)
    print("DEMO: Error Handling")
    print("="*60)
    
    if not VENDOR_SERVICES_AVAILABLE:
        print("❌ Vendor services not available")
        return
    
    api = create_vendor_api()
    
    # Demo 1: Search with no results
    print("\n🔍 Demo: Search with no results")
    no_results_response = api.search_items(["NonExistentItem"])
    
    if no_results_response["success"]:
        data = no_results_response["data"]
        print(f"  Items searched: {data['items_searched']}")
        print(f"  Total items found: {data['total_items_found']}")
    else:
        print(f"  ❌ Search failed: {no_results_response['error']}")
    
    # Demo 2: Invalid location
    print("\n📍 Demo: Invalid location")
    invalid_location_response = api.get_vendors_by_location("", "")
    
    if invalid_location_response["success"]:
        data = invalid_location_response["data"]
        print(f"  Vendors found: {data['total_vendors']}")
    else:
        print(f"  ❌ Failed: {invalid_location_response['error']}")
    
    # Demo 3: API info without vendor scanner
    print("\nℹ️ Demo: API info without vendor scanner")
    # Create API without scanner
    api_no_scanner = VendorAPI(None)
    info_response = api_no_scanner.get_api_info()
    
    if info_response["success"]:
        data = info_response["data"]
        print(f"  Vendor Scanner Available: {data['vendor_scanner_available']}")
    else:
        print(f"  ❌ Failed: {info_response['error']}")


def main():
    """Run the comprehensive demo."""
    print("🚀 BATCH 075 DEMO: Vendor Scanning + Galactic Bazaar Search Logic")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check availability
    print(f"\n📋 Component Availability:")
    print(f"  Vendor Services: {'✅ Available' if VENDOR_SERVICES_AVAILABLE else '❌ Not Available'}")
    print(f"  Bazaar Module: {'✅ Available' if BAZAAR_MODULE_AVAILABLE else '❌ Not Available'}")
    
    # Run demos
    try:
        # Core functionality demos
        scanner = demo_vendor_scanner_service()
        api = demo_vendor_api_plugin()
        
        # Integration demos
        demo_crafting_integration()
        demo_bazaar_module_integration()
        
        # Workflow demos
        demo_comprehensive_workflow()
        
        # Error handling demos
        demo_error_handling()
        
        print("\n" + "="*80)
        print("✅ BATCH 075 DEMO COMPLETED SUCCESSFULLY")
        print("="*80)
        
        # Summary
        print("\n📊 Demo Summary:")
        print("  • Vendor Scanner Service: Enhanced vendor tracking and caching")
        print("  • Vendor API Plugin: RESTful endpoints for external access")
        print("  • Crafting Integration: Smart suggestions for crafting mode")
        print("  • Bazaar Module Integration: Complementary to existing bazaar functionality")
        print("  • Comprehensive Workflow: End-to-end vendor intelligence system")
        print("  • Error Handling: Robust error handling and edge case management")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        log_event(f"[DEMO] Error in main demo: {e}")


if __name__ == "__main__":
    main() 