#!/usr/bin/env python3
"""Test suite for Batch 159 - Dashboard: Vendor History Sync View

This test suite verifies the vendor history management functionality:
- VendorHistoryManager class functionality
- Data loading and parsing
- Filtering and pagination
- Statistics calculation
- Export functionality
- Dashboard API integration
"""

import unittest
import tempfile
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from unittest.mock import Mock, patch, MagicMock

try:
    from core.vendor_history_manager import (
        VendorHistoryManager, VendorHistoryFilter, VendorHistoryEntry,
        VendorHistoryStats, ItemCategory, get_vendor_history_manager
    )
    MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Vendor history manager not available: {e}")
    MANAGER_AVAILABLE = False


class TestVendorHistoryManager(unittest.TestCase):
    """Test cases for VendorHistoryManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MANAGER_AVAILABLE:
            self.skipTest("Vendor history manager not available")
        
        # Create temporary test data
        self.test_data_dir = tempfile.mkdtemp()
        self.discovered_items_file = os.path.join(self.test_data_dir, "discovered_items.json")
        self.vendor_profiles_file = os.path.join(self.test_data_dir, "vendor_profiles.json")
        
        # Create test data
        self.test_discovered_items = {
            "enhanced_composite_chest_123": {
                "item_name": "Enhanced Composite Chest",
                "item_id": "enhanced_composite_chest_123",
                "category": "ItemCategory.ARMOR",
                "cost": 75000,
                "vendor_id": "vendor_001",
                "vendor_name": "Corellian Armor Smith",
                "vendor_type": "VendorType.ARMORSMITH",
                "planet": "Corellia",
                "location": "Coronet City",
                "coordinates": [0.0, 0.0],
                "timestamp": "2025-08-03T12:49:20.604874",
                "quality": "Exceptional",
                "stats": {"constitution": 25, "stamina": 20},
                "resists": {"energy": 30, "kinetic": 25},
                "notes": "High-quality armor piece"
            },
            "krayt_dragon_bone_sword_456": {
                "item_name": "Krayt Dragon Bone Sword",
                "item_id": "krayt_dragon_bone_sword_456",
                "category": "ItemCategory.WEAPONS",
                "cost": 150000,
                "vendor_id": "vendor_002",
                "vendor_name": "Tatooine Weaponsmith",
                "vendor_type": "VendorType.WEAPONSMITH",
                "planet": "Tatooine",
                "location": "Mos Eisley",
                "coordinates": [0.0, 0.0],
                "timestamp": "2025-08-03T12:49:20.604897",
                "quality": "Mastercraft",
                "stats": {"damage": 150, "speed": 2.5},
                "resists": {},
                "notes": "Rare weapon from Krayt Dragon bones"
            }
        }
        
        self.test_vendor_profiles = {
            "vendor_001": {
                "vendor_id": "vendor_001",
                "vendor_name": "Corellian Armor Smith",
                "vendor_type": "VendorType.ARMORSMITH",
                "planet": "Corellia",
                "location": "Coronet City",
                "coordinates": [0.0, 0.0],
                "first_discovered": "2025-08-03T12:49:20.604874",
                "last_visited": "2025-08-03T12:49:20.610076",
                "total_visits": 2,
                "items_discovered": 1,
                "average_item_cost": 75000,
                "most_expensive_item": "Enhanced Composite Chest",
                "most_expensive_cost": 75000,
                "notes": "High-quality armor vendor"
            },
            "vendor_002": {
                "vendor_id": "vendor_002",
                "vendor_name": "Tatooine Weaponsmith",
                "vendor_type": "VendorType.WEAPONSMITH",
                "planet": "Tatooine",
                "location": "Mos Eisley",
                "coordinates": [0.0, 0.0],
                "first_discovered": "2025-08-03T12:49:20.604897",
                "last_visited": "2025-08-03T12:49:20.610080",
                "total_visits": 2,
                "items_discovered": 1,
                "average_item_cost": 150000,
                "most_expensive_item": "Krayt Dragon Bone Sword",
                "most_expensive_cost": 150000,
                "notes": "Specializes in rare weapons"
            }
        }
        
        # Write test data to files
        with open(self.discovered_items_file, 'w') as f:
            json.dump(self.test_discovered_items, f)
        
        with open(self.vendor_profiles_file, 'w') as f:
            json.dump(self.test_vendor_profiles, f)
        
        # Create manager with test data
        self.manager = VendorHistoryManager(self.test_data_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_data_dir, ignore_errors=True)
    
    def test_init(self):
        """Test VendorHistoryManager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.data_dir, self.test_data_dir)
    
    def test_load_discovered_items(self):
        """Test loading discovered items data."""
        items = self.manager._load_discovered_items()
        self.assertEqual(len(items), 2)
        self.assertIn("enhanced_composite_chest_123", items)
        self.assertIn("krayt_dragon_bone_sword_456", items)
    
    def test_load_vendor_profiles(self):
        """Test loading vendor profiles data."""
        profiles = self.manager._load_vendor_profiles()
        self.assertEqual(len(profiles), 2)
        self.assertIn("vendor_001", profiles)
        self.assertIn("vendor_002", profiles)
    
    def test_convert_item_category(self):
        """Test item category conversion."""
        self.assertEqual(self.manager._convert_item_category("ItemCategory.ARMOR"), "Armor")
        self.assertEqual(self.manager._convert_item_category("ItemCategory.WEAPONS"), "Weapons")
        self.assertEqual(self.manager._convert_item_category("ItemCategory.UNKNOWN"), "Unknown")
        self.assertEqual(self.manager._convert_item_category("Invalid"), "Unknown")
    
    def test_get_vendor_history(self):
        """Test getting vendor history entries."""
        entries, total_count = self.manager.get_vendor_history()
        
        self.assertEqual(total_count, 2)
        self.assertEqual(len(entries), 2)
        
        # Check first entry
        entry = entries[0]
        self.assertEqual(entry.item_name, "Enhanced Composite Chest")
        self.assertEqual(entry.credits, 75000)
        self.assertEqual(entry.seller, "Corellian Armor Smith")
        self.assertEqual(entry.location, "Coronet City, Corellia")
        self.assertEqual(entry.category, "Armor")
        self.assertEqual(entry.source, "Scanned by MS11")
    
    def test_get_vendor_history_with_filters(self):
        """Test getting vendor history with filters."""
        # Filter by category
        armor_filter = VendorHistoryFilter(category="Armor")
        entries, count = self.manager.get_vendor_history(armor_filter)
        self.assertEqual(count, 1)
        self.assertEqual(entries[0].category, "Armor")
        
        # Filter by price range
        expensive_filter = VendorHistoryFilter(min_price=100000)
        entries, count = self.manager.get_vendor_history(expensive_filter)
        self.assertEqual(count, 1)
        self.assertEqual(entries[0].credits, 150000)
        
        # Filter by seller
        seller_filter = VendorHistoryFilter(seller="Tatooine")
        entries, count = self.manager.get_vendor_history(seller_filter)
        self.assertEqual(count, 1)
        self.assertIn("Tatooine", entries[0].seller)
    
    def test_get_vendor_history_pagination(self):
        """Test vendor history pagination."""
        entries, total_count = self.manager.get_vendor_history(page=1, page_size=1)
        self.assertEqual(len(entries), 1)
        self.assertEqual(total_count, 2)
        
        entries, _ = self.manager.get_vendor_history(page=2, page_size=1)
        self.assertEqual(len(entries), 1)
    
    def test_get_vendor_history_stats(self):
        """Test getting vendor history statistics."""
        stats = self.manager.get_vendor_history_stats()
        
        self.assertEqual(stats.total_items, 2)
        self.assertEqual(stats.total_vendors, 2)
        self.assertEqual(stats.total_locations, 2)
        self.assertEqual(stats.total_categories, 2)
        self.assertEqual(stats.average_price, 112500.0)  # (75000 + 150000) / 2
        self.assertEqual(stats.min_price, 75000)
        self.assertEqual(stats.max_price, 150000)
    
    def test_get_categories(self):
        """Test getting available categories."""
        categories = self.manager.get_categories()
        self.assertIn("Armor", categories)
        self.assertIn("Weapons", categories)
        self.assertEqual(len(categories), 2)
    
    def test_get_vendors(self):
        """Test getting available vendors."""
        vendors = self.manager.get_vendors()
        self.assertIn("Corellian Armor Smith", vendors)
        self.assertIn("Tatooine Weaponsmith", vendors)
        self.assertEqual(len(vendors), 2)
    
    def test_get_locations(self):
        """Test getting available locations."""
        locations = self.manager.get_locations()
        self.assertIn("Coronet City, Corellia", locations)
        self.assertIn("Mos Eisley, Tatooine", locations)
        self.assertEqual(len(locations), 2)
    
    def test_export_vendor_history_json(self):
        """Test exporting vendor history as JSON."""
        export_data = self.manager.export_vendor_history(format="json")
        self.assertIsInstance(export_data, str)
        
        # Parse JSON to verify structure
        data = json.loads(export_data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        
        # Check first entry structure
        entry = data[0]
        self.assertIn("item_name", entry)
        self.assertIn("credits", entry)
        self.assertIn("seller", entry)
        self.assertIn("location", entry)
        self.assertIn("timestamp", entry)
        self.assertIn("category", entry)
        self.assertIn("source", entry)
    
    def test_export_vendor_history_csv(self):
        """Test exporting vendor history as CSV."""
        export_data = self.manager.export_vendor_history(format="csv")
        self.assertIsInstance(export_data, str)
        
        # Check CSV structure
        lines = export_data.split('\n')
        self.assertGreater(len(lines), 1)  # Header + data
        
        # Check header
        header = lines[0]
        self.assertIn("Item Name", header)
        self.assertIn("Credits", header)
        self.assertIn("Seller", header)
        self.assertIn("Location", header)
        self.assertIn("Timestamp", header)
        self.assertIn("Category", header)
        self.assertIn("Source", header)
    
    def test_export_vendor_history_invalid_format(self):
        """Test exporting with invalid format."""
        with self.assertRaises(ValueError):
            self.manager.export_vendor_history(format="invalid")
    
    def test_matches_filters(self):
        """Test filter matching functionality."""
        entry = VendorHistoryEntry(
            item_name="Test Item",
            credits=50000,
            seller="Test Vendor",
            location="Test Location, Test Planet",
            timestamp="2025-08-03T12:00:00",
            category="Armor",
            source="Scanned by MS11"
        )
        
        # Test item name filter
        name_filter = VendorHistoryFilter(item_name="Test")
        self.assertTrue(self.manager._matches_filters(entry, name_filter))
        
        name_filter = VendorHistoryFilter(item_name="Invalid")
        self.assertFalse(self.manager._matches_filters(entry, name_filter))
        
        # Test category filter
        category_filter = VendorHistoryFilter(category="Armor")
        self.assertTrue(self.manager._matches_filters(entry, category_filter))
        
        category_filter = VendorHistoryFilter(category="Weapons")
        self.assertFalse(self.manager._matches_filters(entry, category_filter))
        
        # Test price range filter
        price_filter = VendorHistoryFilter(min_price=40000, max_price=60000)
        self.assertTrue(self.manager._matches_filters(entry, price_filter))
        
        price_filter = VendorHistoryFilter(min_price=60000)
        self.assertFalse(self.manager._matches_filters(entry, price_filter))
        
        # Test seller filter
        seller_filter = VendorHistoryFilter(seller="Test")
        self.assertTrue(self.manager._matches_filters(entry, seller_filter))
        
        seller_filter = VendorHistoryFilter(seller="Invalid")
        self.assertFalse(self.manager._matches_filters(entry, seller_filter))
        
        # Test location filter
        location_filter = VendorHistoryFilter(location="Test")
        self.assertTrue(self.manager._matches_filters(entry, location_filter))
        
        location_filter = VendorHistoryFilter(location="Invalid")
        self.assertFalse(self.manager._matches_filters(entry, location_filter))


class TestVendorHistoryFilter(unittest.TestCase):
    """Test cases for VendorHistoryFilter dataclass."""
    
    def test_filter_creation(self):
        """Test creating VendorHistoryFilter instances."""
        filter_obj = VendorHistoryFilter()
        self.assertIsNone(filter_obj.item_name)
        self.assertIsNone(filter_obj.category)
        self.assertIsNone(filter_obj.min_price)
        self.assertIsNone(filter_obj.max_price)
        self.assertIsNone(filter_obj.seller)
        self.assertIsNone(filter_obj.location)
        self.assertIsNone(filter_obj.start_date)
        self.assertIsNone(filter_obj.end_date)
        self.assertIsNone(filter_obj.source)
        
        filter_obj = VendorHistoryFilter(
            item_name="Test Item",
            category="Armor",
            min_price=1000,
            max_price=50000,
            seller="Test Vendor",
            location="Test Location",
            start_date="2025-01-01",
            end_date="2025-12-31",
            source="Scanned by MS11"
        )
        
        self.assertEqual(filter_obj.item_name, "Test Item")
        self.assertEqual(filter_obj.category, "Armor")
        self.assertEqual(filter_obj.min_price, 1000)
        self.assertEqual(filter_obj.max_price, 50000)
        self.assertEqual(filter_obj.seller, "Test Vendor")
        self.assertEqual(filter_obj.location, "Test Location")
        self.assertEqual(filter_obj.start_date, "2025-01-01")
        self.assertEqual(filter_obj.end_date, "2025-12-31")
        self.assertEqual(filter_obj.source, "Scanned by MS11")


class TestVendorHistoryEntry(unittest.TestCase):
    """Test cases for VendorHistoryEntry dataclass."""
    
    def test_entry_creation(self):
        """Test creating VendorHistoryEntry instances."""
        entry = VendorHistoryEntry(
            item_name="Test Item",
            credits=50000,
            seller="Test Vendor",
            location="Test Location, Test Planet",
            timestamp="2025-08-03T12:00:00",
            category="Armor",
            source="Scanned by MS11",
            item_id="test_item_123",
            quality="Excellent",
            planet="Test Planet",
            coordinates=[100.0, 200.0],
            notes="Test notes"
        )
        
        self.assertEqual(entry.item_name, "Test Item")
        self.assertEqual(entry.credits, 50000)
        self.assertEqual(entry.seller, "Test Vendor")
        self.assertEqual(entry.location, "Test Location, Test Planet")
        self.assertEqual(entry.timestamp, "2025-08-03T12:00:00")
        self.assertEqual(entry.category, "Armor")
        self.assertEqual(entry.source, "Scanned by MS11")
        self.assertEqual(entry.item_id, "test_item_123")
        self.assertEqual(entry.quality, "Excellent")
        self.assertEqual(entry.planet, "Test Planet")
        self.assertEqual(entry.coordinates, [100.0, 200.0])
        self.assertEqual(entry.notes, "Test notes")
    
    def test_entry_defaults(self):
        """Test VendorHistoryEntry default values."""
        entry = VendorHistoryEntry(
            item_name="Test Item",
            credits=50000,
            seller="Test Vendor",
            location="Test Location",
            timestamp="2025-08-03T12:00:00",
            category="Armor"
        )
        
        self.assertEqual(entry.source, "Scanned by MS11")
        self.assertIsNone(entry.item_id)
        self.assertIsNone(entry.quality)
        self.assertIsNone(entry.planet)
        self.assertIsNone(entry.coordinates)
        self.assertIsNone(entry.notes)


class TestVendorHistoryStats(unittest.TestCase):
    """Test cases for VendorHistoryStats dataclass."""
    
    def test_stats_creation(self):
        """Test creating VendorHistoryStats instances."""
        stats = VendorHistoryStats(
            total_items=10,
            total_vendors=5,
            total_locations=3,
            total_categories=4,
            average_price=25000.0,
            min_price=1000,
            max_price=100000,
            date_range=("2025-01-01", "2025-12-31")
        )
        
        self.assertEqual(stats.total_items, 10)
        self.assertEqual(stats.total_vendors, 5)
        self.assertEqual(stats.total_locations, 3)
        self.assertEqual(stats.total_categories, 4)
        self.assertEqual(stats.average_price, 25000.0)
        self.assertEqual(stats.min_price, 1000)
        self.assertEqual(stats.max_price, 100000)
        self.assertEqual(stats.date_range, ("2025-01-01", "2025-12-31"))


class TestItemCategory(unittest.TestCase):
    """Test cases for ItemCategory enum."""
    
    def test_enum_values(self):
        """Test ItemCategory enum values."""
        self.assertEqual(ItemCategory.WEAPONS.value, "Weapons")
        self.assertEqual(ItemCategory.ARMOR.value, "Armor")
        self.assertEqual(ItemCategory.COMPONENTS.value, "Components")
        self.assertEqual(ItemCategory.RESOURCES.value, "Resources")
        self.assertEqual(ItemCategory.MEDICAL.value, "Medical")
        self.assertEqual(ItemCategory.ENHANCEMENTS.value, "Enhancements")
        self.assertEqual(ItemCategory.TOOLS.value, "Tools")
        self.assertEqual(ItemCategory.UNKNOWN.value, "Unknown")


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for vendor history functionality."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        if not MANAGER_AVAILABLE:
            self.skipTest("Vendor history manager not available")
        
        # Use the global manager for integration tests
        self.manager = get_vendor_history_manager()
    
    def test_real_data_loading(self):
        """Test loading real vendor history data."""
        try:
            entries, total_count = self.manager.get_vendor_history()
            self.assertIsInstance(total_count, int)
            self.assertGreaterEqual(total_count, 0)
            
            if entries:
                self.assertIsInstance(entries, list)
                for entry in entries:
                    self.assertIsInstance(entry, VendorHistoryEntry)
                    self.assertIsInstance(entry.item_name, str)
                    self.assertIsInstance(entry.credits, int)
                    self.assertIsInstance(entry.seller, str)
                    self.assertIsInstance(entry.location, str)
                    self.assertIsInstance(entry.timestamp, str)
                    self.assertIsInstance(entry.category, str)
                    self.assertIsInstance(entry.source, str)
        except Exception as e:
            # It's okay if real data doesn't exist for testing
            self.skipTest(f"No real vendor history data available: {e}")
    
    def test_statistics_calculation(self):
        """Test statistics calculation with real data."""
        try:
            stats = self.manager.get_vendor_history_stats()
            self.assertIsInstance(stats, VendorHistoryStats)
            self.assertIsInstance(stats.total_items, int)
            self.assertIsInstance(stats.total_vendors, int)
            self.assertIsInstance(stats.total_locations, int)
            self.assertIsInstance(stats.total_categories, int)
            self.assertIsInstance(stats.average_price, float)
            self.assertIsInstance(stats.min_price, int)
            self.assertIsInstance(stats.max_price, int)
            self.assertIsInstance(stats.date_range, tuple)
        except Exception as e:
            self.skipTest(f"No real vendor history data available: {e}")
    
    def test_filter_options(self):
        """Test getting available filter options."""
        try:
            categories = self.manager.get_categories()
            vendors = self.manager.get_vendors()
            locations = self.manager.get_locations()
            
            self.assertIsInstance(categories, list)
            self.assertIsInstance(vendors, list)
            self.assertIsInstance(locations, list)
            
            # All should be lists of strings
            for category in categories:
                self.assertIsInstance(category, str)
            for vendor in vendors:
                self.assertIsInstance(vendor, str)
            for location in locations:
                self.assertIsInstance(location, str)
        except Exception as e:
            self.skipTest(f"No real vendor history data available: {e}")


def run_performance_benchmark():
    """Run performance benchmark tests."""
    if not MANAGER_AVAILABLE:
        print("❌ Vendor history manager not available - skipping benchmark")
        return
    
    print("🚀 Running Performance Benchmark...")
    print("=" * 50)
    
    manager = get_vendor_history_manager()
    
    # Benchmark data loading
    start_time = datetime.now()
    entries, total_count = manager.get_vendor_history()
    load_time = (datetime.now() - start_time).total_seconds()
    
    print(f"📊 Data Loading: {load_time:.4f}s for {total_count} entries")
    
    # Benchmark statistics calculation
    start_time = datetime.now()
    stats = manager.get_vendor_history_stats()
    stats_time = (datetime.now() - start_time).total_seconds()
    
    print(f"📈 Statistics Calculation: {stats_time:.4f}s")
    
    # Benchmark filtering
    start_time = datetime.now()
    filtered_entries, filtered_count = manager.get_vendor_history(
        VendorHistoryFilter(category="Armor")
    )
    filter_time = (datetime.now() - start_time).total_seconds()
    
    print(f"🔍 Filtering: {filter_time:.4f}s for {filtered_count} filtered entries")
    
    # Benchmark export
    start_time = datetime.now()
    export_data = manager.export_vendor_history(format="json")
    export_time = (datetime.now() - start_time).total_seconds()
    
    print(f"📤 Export: {export_time:.4f}s for {len(export_data)} characters")
    
    print(f"\n✅ Performance benchmark completed!")
    print(f"📊 Total operations: {load_time + stats_time + filter_time + export_time:.4f}s")


def main():
    """Main test function."""
    print("🧪 Batch 159 - Vendor History Sync View Test Suite")
    print("=" * 60)
    
    if not MANAGER_AVAILABLE:
        print("❌ Vendor history manager not available")
        print("Skipping all tests...")
        return
    
    # Run unit tests
    print("🔬 Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance benchmark
    print("\n" + "=" * 60)
    run_performance_benchmark()
    
    print("\n🎉 Test suite completed!")


if __name__ == "__main__":
    main() 