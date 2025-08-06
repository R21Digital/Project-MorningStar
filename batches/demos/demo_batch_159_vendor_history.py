#!/usr/bin/env python3
"""Demo script for Batch 159 - Dashboard: Vendor History Sync View

This demo showcases the vendor history management functionality:
- Loading vendor history data from existing JSON files
- Filtering and pagination capabilities
- Statistics calculation
- Export functionality
- Integration with the dashboard API
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import asdict

try:
    from core.vendor_history_manager import (
        VendorHistoryManager, VendorHistoryFilter, VendorHistoryEntry,
        get_vendor_history_manager
    )
    MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Vendor history manager not available: {e}")
    MANAGER_AVAILABLE = False


class VendorHistoryDemo:
    """Demo class for Batch 159 - Vendor History Sync View."""
    
    def __init__(self):
        """Initialize the demo."""
        self.vendor_manager = get_vendor_history_manager()
        self.demo_data = self._create_demo_data()
    
    def _create_demo_data(self) -> List[Dict]:
        """Create sample vendor history data for demonstration."""
        return [
            {
                "item_name": "Enhanced Composite Chest",
                "credits": 75000,
                "seller": "Corellian Armor Smith",
                "location": "Coronet City, Corellia",
                "timestamp": "2025-08-03T12:49:20.604874",
                "category": "Armor",
                "source": "Scanned by MS11",
                "quality": "Exceptional",
                "notes": "High-quality armor piece"
            },
            {
                "item_name": "Krayt Dragon Bone Sword",
                "credits": 150000,
                "seller": "Tatooine Weaponsmith",
                "location": "Mos Eisley, Tatooine",
                "timestamp": "2025-08-03T12:49:20.604897",
                "category": "Weapons",
                "source": "Scanned by MS11",
                "quality": "Mastercraft",
                "notes": "Rare weapon from Krayt Dragon bones"
            },
            {
                "item_name": "Stun Resist Enhancement",
                "credits": 25000,
                "seller": "Naboo Merchant",
                "location": "Theed, Naboo",
                "timestamp": "2025-08-03T12:49:20.604898",
                "category": "Enhancements",
                "source": "Scanned by MS11",
                "quality": "Good",
                "notes": "Essential for PvP combat"
            },
            {
                "item_name": "Rebel Combat Armor",
                "credits": 45000,
                "seller": "Rebel Armory",
                "location": "Tyrena, Corellia",
                "timestamp": "2025-08-03T12:49:20.604900",
                "category": "Armor",
                "source": "Scanned by MS11",
                "quality": "Excellent",
                "notes": "Faction-specific armor"
            },
            {
                "item_name": "Imperial Stormtrooper Armor",
                "credits": 50000,
                "seller": "Imperial Armory",
                "location": "Coronet City, Corellia",
                "timestamp": "2025-08-03T12:49:20.604901",
                "category": "Armor",
                "source": "Scanned by MS11",
                "quality": "Excellent",
                "notes": "Imperial faction armor"
            }
        ]
    
    def demo_basic_functionality(self):
        """Demo basic vendor history functionality."""
        print("🎯 Demo: Basic Vendor History Functionality")
        print("=" * 50)
        
        # Get all vendor history entries
        entries, total_count = self.vendor_manager.get_vendor_history()
        print(f"📊 Total vendor history entries: {total_count}")
        
        if entries:
            print(f"📋 Sample entries:")
            for i, entry in enumerate(entries[:3]):
                print(f"  {i+1}. {entry.item_name} - {entry.credits} credits")
                print(f"     Seller: {entry.seller}")
                print(f"     Location: {entry.location}")
                print(f"     Category: {entry.category}")
                print(f"     Source: {entry.source}")
                print()
        
        # Get statistics
        stats = self.vendor_manager.get_vendor_history_stats()
        print(f"📈 Statistics:")
        print(f"  • Total Items: {stats.total_items}")
        print(f"  • Total Vendors: {stats.total_vendors}")
        print(f"  • Total Locations: {stats.total_locations}")
        print(f"  • Total Categories: {stats.total_categories}")
        print(f"  • Average Price: {stats.average_price:.2f} credits")
        print(f"  • Price Range: {stats.min_price} - {stats.max_price} credits")
        print()
    
    def demo_filtering(self):
        """Demo filtering functionality."""
        print("🔍 Demo: Filtering Functionality")
        print("=" * 50)
        
        # Filter by category
        armor_filter = VendorHistoryFilter(category="Armor")
        armor_entries, armor_count = self.vendor_manager.get_vendor_history(armor_filter)
        print(f"🛡️  Armor items: {armor_count}")
        
        # Filter by price range
        expensive_filter = VendorHistoryFilter(min_price=50000)
        expensive_entries, expensive_count = self.vendor_manager.get_vendor_history(expensive_filter)
        print(f"💰 Expensive items (>50k): {expensive_count}")
        
        # Filter by location
        corellia_filter = VendorHistoryFilter(location="Corellia")
        corellia_entries, corellia_count = self.vendor_manager.get_vendor_history(corellia_filter)
        print(f"🌍 Corellia items: {corellia_count}")
        
        # Combined filter
        combined_filter = VendorHistoryFilter(
            category="Armor",
            min_price=40000,
            max_price=80000
        )
        combined_entries, combined_count = self.vendor_manager.get_vendor_history(combined_filter)
        print(f"🎯 Combined filter (Armor, 40k-80k): {combined_count}")
        print()
    
    def demo_pagination(self):
        """Demo pagination functionality."""
        print("📄 Demo: Pagination Functionality")
        print("=" * 50)
        
        # Get first page
        entries_page1, total_count = self.vendor_manager.get_vendor_history(page=1, page_size=2)
        print(f"📄 Page 1 (2 items): {len(entries_page1)} entries")
        for entry in entries_page1:
            print(f"  • {entry.item_name}")
        
        # Get second page
        entries_page2, _ = self.vendor_manager.get_vendor_history(page=2, page_size=2)
        print(f"📄 Page 2 (2 items): {len(entries_page2)} entries")
        for entry in entries_page2:
            print(f"  • {entry.item_name}")
        
        print(f"📊 Total pages: {(total_count + 1) // 2}")
        print()
    
    def demo_export_functionality(self):
        """Demo export functionality."""
        print("📤 Demo: Export Functionality")
        print("=" * 50)
        
        try:
            # Export JSON
            json_export = self.vendor_manager.export_vendor_history(format="json")
            print(f"📄 JSON Export: {len(json_export)} characters")
            
            # Export CSV
            csv_export = self.vendor_manager.export_vendor_history(format="csv")
            print(f"📊 CSV Export: {len(csv_export)} characters")
            
            print("✅ Export functionality working correctly")
        except Exception as e:
            print(f"❌ Export error: {e}")
        
        print()
    
    def demo_available_filters(self):
        """Demo available filter options."""
        print("🎛️  Demo: Available Filter Options")
        print("=" * 50)
        
        categories = self.vendor_manager.get_categories()
        vendors = self.vendor_manager.get_vendors()
        locations = self.vendor_manager.get_locations()
        
        print(f"📂 Available Categories ({len(categories)}):")
        for category in categories:
            print(f"  • {category}")
        
        print(f"\n🏪 Available Vendors ({len(vendors)}):")
        for vendor in vendors[:5]:  # Show first 5
            print(f"  • {vendor}")
        if len(vendors) > 5:
            print(f"  ... and {len(vendors) - 5} more")
        
        print(f"\n🌍 Available Locations ({len(locations)}):")
        for location in locations[:5]:  # Show first 5
            print(f"  • {location}")
        if len(locations) > 5:
            print(f"  ... and {len(locations) - 5} more")
        
        print()
    
    def demo_dashboard_integration(self):
        """Demo dashboard integration."""
        print("🖥️  Demo: Dashboard Integration")
        print("=" * 50)
        
        print("📋 Dashboard Features:")
        print("  • Table display with Item name, Credits, Seller, Location, Timestamp")
        print("  • Filtering by type, price range, or date")
        print("  • Source tag: 'Scanned by MS11' (private label)")
        print("  • Export functionality (JSON/CSV)")
        print("  • Statistics display")
        print("  • Pagination support")
        
        print("\n🌐 Dashboard URL: /dashboard/loot-history/")
        print("🔗 API Endpoints:")
        print("  • GET /api/vendor-history/data - Get vendor history data")
        print("  • GET /api/vendor-history/stats - Get statistics")
        print("  • GET /api/vendor-history/filters - Get available filters")
        print("  • GET /api/vendor-history/export - Export data")
        
        print("\n✅ Dashboard integration ready!")
        print()
    
    def run_full_demo(self):
        """Run the complete demo."""
        print("🚀 Batch 159 - Dashboard: Vendor History Sync View Demo")
        print("=" * 60)
        print("Purpose: Display loot items seen in vendors by MS11 on the user dashboard")
        print("Features: Table with Item name, Credits, Seller, Location, Timestamp")
        print("Filtering: By type, price range, or date")
        print("Source tag: 'Scanned by MS11' (private label)")
        print("=" * 60)
        print()
        
        if not MANAGER_AVAILABLE:
            print("❌ Vendor history manager not available - skipping demo")
            return
        
        try:
            self.demo_basic_functionality()
            self.demo_filtering()
            self.demo_pagination()
            self.demo_export_functionality()
            self.demo_available_filters()
            self.demo_dashboard_integration()
            
            print("🎉 Demo completed successfully!")
            print("\n📋 Next Steps:")
            print("  1. Start the dashboard server: python dashboard/app.py")
            print("  2. Visit: http://localhost:8000/dashboard/loot-history/")
            print("  3. Test filtering and export functionality")
            print("  4. Verify 'Scanned by MS11' source tags")
            
        except Exception as e:
            print(f"❌ Demo error: {e}")


def main():
    """Main demo function."""
    demo = VendorHistoryDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main() 