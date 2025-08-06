#!/usr/bin/env python3
"""Test script for Batch 061 - Auction House Integration (Vendor/Bazaar Logic)."""

import json
import unittest
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

from modules.bazaar import VendorManager, PriceTracker, BazaarDetector
from modules.bazaar.bazaar_detector import VendorTerminal, VendorInterface
from modules.bazaar.price_tracker import ItemPriceStats
from modules.bazaar.vendor_manager import InventoryItem, VendorTransaction


class TestBazaarDetector(unittest.TestCase):
    """Test bazaar detector functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = BazaarDetector()
        
    def test_load_config(self):
        """Test configuration loading."""
        config = self.detector.config
        self.assertIsInstance(config, dict)
        self.assertIn("auto_sell_junk", config)
        self.assertIn("loot_min_value_threshold", config)
        self.assertIn("excluded_items", config)
    
    def test_determine_terminal_type(self):
        """Test terminal type determination."""
        # Test bazaar detection
        self.assertEqual(self.detector._determine_terminal_type("Bazaar Terminal"), "bazaar")
        self.assertEqual(self.detector._determine_terminal_type("BAZAAR"), "bazaar")
        
        # Test vendor detection
        self.assertEqual(self.detector._determine_terminal_type("Vendor Terminal"), "vendor")
        self.assertEqual(self.detector._determine_terminal_type("VENDOR"), "vendor")
        
        # Test shop detection
        self.assertEqual(self.detector._determine_terminal_type("Shop Terminal"), "shop")
        self.assertEqual(self.detector._determine_terminal_type("STORE"), "shop")
        
        # Test default
        self.assertEqual(self.detector._determine_terminal_type("Unknown Terminal"), "vendor")
    
    @patch('modules.bazaar.bazaar_detector.screen_text')
    def test_detect_vendor_terminals(self, mock_screen_text):
        """Test vendor terminal detection."""
        # Mock screen text with vendor keywords
        mock_screen_text.return_value = "Vendor Terminal\nShop Interface\nBazaar Options"
        
        terminals = self.detector.detect_vendor_terminals()
        self.assertIsInstance(terminals, list)
    
    @patch('modules.bazaar.bazaar_detector.screen_text')
    def test_detect_vendor_interface(self, mock_screen_text):
        """Test vendor interface detection."""
        # Mock screen text with interface keywords
        mock_screen_text.return_value = "Sell Items\nBuy Items\nInventory"
        
        interface = self.detector.detect_vendor_interface()
        self.assertIsInstance(interface, VendorInterface)


class TestPriceTracker(unittest.TestCase):
    """Test price tracker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = PriceTracker("test_price_history.json")
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test file if it exists
        test_file = Path("test_price_history.json")
        if test_file.exists():
            test_file.unlink()
    
    def test_add_sale(self):
        """Test adding sales to tracker."""
        # Add test sales
        self.tracker.add_sale("Test Item", 1000)
        self.tracker.add_sale("Test Item", 1100)
        self.tracker.add_sale("Another Item", 500)
        
        # Check statistics
        stats = self.tracker.get_item_price_stats("Test Item")
        self.assertIsNotNone(stats)
        self.assertEqual(stats.item_name, "Test Item")
        self.assertEqual(stats.total_sales, 2)
        self.assertEqual(stats.min_price, 1000)
        self.assertEqual(stats.max_price, 1100)
        self.assertEqual(stats.average_price, 1050.0)
    
    def test_get_recommended_price(self):
        """Test recommended price calculation."""
        # Add some sales
        self.tracker.add_sale("Test Item", 1000)
        self.tracker.add_sale("Test Item", 1100)
        self.tracker.add_sale("Test Item", 1200)
        
        # Get recommended price (should be 10% above average)
        recommended = self.tracker.get_recommended_price("Test Item")
        expected = int(1100 * 1.1)  # 10% above average of 1100
        self.assertEqual(recommended, expected)
    
    def test_should_sell_item(self):
        """Test selling decision logic."""
        # Add sales for comparison
        self.tracker.add_sale("Test Item", 1000)
        self.tracker.add_sale("Test Item", 1100)
        self.tracker.add_sale("Test Item", 1200)
        
        # Test items above threshold
        self.assertTrue(self.tracker.should_sell_item("Test Item", 1000, 500))
        
        # Test items below threshold
        self.assertFalse(self.tracker.should_sell_item("Test Item", 300, 500))
        
        # Test items below average (20% below average = 880)
        self.assertFalse(self.tracker.should_sell_item("Test Item", 800, 500))
    
    def test_get_price_trend(self):
        """Test price trend calculation."""
        # Add sales over time
        self.tracker.add_sale("Trend Item", 1000)
        self.tracker.add_sale("Trend Item", 1100)
        self.tracker.add_sale("Trend Item", 1200)
        
        trend = self.tracker.get_price_trend("Trend Item", days=30)
        self.assertIsNotNone(trend)
        self.assertGreater(trend, 0)  # Should be increasing
    
    def test_cleanup_old_data(self):
        """Test data cleanup functionality."""
        # Add some sales
        self.tracker.add_sale("Old Item", 1000)
        self.tracker.add_sale("New Item", 1000)
        
        # Clean up old data (should keep recent data)
        self.tracker.cleanup_old_data(days=1)
        
        # Check that data still exists
        stats = self.tracker.get_item_price_stats("New Item")
        self.assertIsNotNone(stats)


class TestVendorManager(unittest.TestCase):
    """Test vendor manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.vendor = VendorManager()
    
    def test_load_config(self):
        """Test configuration loading."""
        config = self.vendor.config
        self.assertIsInstance(config, dict)
        self.assertIn("auto_sell_junk", config)
        self.assertIn("loot_min_value_threshold", config)
        self.assertIn("excluded_items", config)
    
    def test_should_sell_item(self):
        """Test item selling decision logic."""
        # Create test items
        excluded_item = InventoryItem("Janta Blood", 1, 10000, False)
        low_value_item = InventoryItem("Junk Item", 1, 100, False)
        valuable_item = InventoryItem("Valuable Item", 1, 10000, False)
        
        # Test excluded item
        self.assertFalse(self.vendor._should_sell_item(excluded_item))
        
        # Test low value item
        self.assertFalse(self.vendor._should_sell_item(low_value_item))
        
        # Test valuable item
        self.assertTrue(self.vendor._should_sell_item(valuable_item))
    
    def test_parse_inventory_text(self):
        """Test inventory text parsing."""
        # Test inventory text
        inventory_text = "Bantha Hide 3 5200\nBolma Meat 5 850\nJunk Item 10 100"
        
        items = self.vendor._parse_inventory_text(inventory_text)
        
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].name, "Bantha Hide")
        self.assertEqual(items[0].quantity, 3)
        self.assertEqual(items[0].estimated_value, 5200)
    
    @patch('modules.bazaar.vendor_manager.screen_text')
    def test_scan_inventory_for_sale(self, mock_screen_text):
        """Test inventory scanning."""
        # Mock inventory text
        mock_screen_text.return_value = "Valuable Item 1 10000\nJunk Item 1 100"
        
        items = self.vendor.scan_inventory_for_sale()
        self.assertIsInstance(items, list)
    
    def test_get_vendor_price(self):
        """Test vendor price retrieval."""
        # Test known items
        self.assertEqual(self.vendor._get_vendor_price("health pack"), 100)
        self.assertEqual(self.vendor._get_vendor_price("stimpack"), 50)
        
        # Test unknown item
        self.assertEqual(self.vendor._get_vendor_price("unknown item"), 100)


class TestIntegration(unittest.TestCase):
    """Integration tests for bazaar functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.vendor = VendorManager()
        self.tracker = PriceTracker()
        self.detector = BazaarDetector()
    
    def test_full_vendor_workflow(self):
        """Test complete vendor workflow."""
        # Simulate vendor detection
        with patch.object(self.detector, 'detect_vendor_terminals') as mock_detect:
            mock_detect.return_value = [
                VendorTerminal(100, 100, 200, 150, "vendor", 0.8, "Vendor Terminal")
            ]
            
            terminals = self.detector.detect_vendor_terminals()
            self.assertEqual(len(terminals), 1)
            self.assertEqual(terminals[0].terminal_type, "vendor")
    
    def test_price_tracking_integration(self):
        """Test price tracking integration."""
        # Add sales through vendor manager
        self.vendor.price_tracker.add_sale("Integration Item", 1000)
        self.vendor.price_tracker.add_sale("Integration Item", 1100)
        
        # Check that vendor manager can access price data
        stats = self.vendor.price_tracker.get_item_price_stats("Integration Item")
        self.assertIsNotNone(stats)
        self.assertEqual(stats.average_price, 1050.0)
    
    def test_configuration_integration(self):
        """Test configuration integration."""
        # Check that all components use the same configuration
        vendor_config = self.vendor.config
        detector_config = self.detector.config
        
        self.assertEqual(vendor_config.get("auto_sell_junk"), 
                        detector_config.get("auto_sell_junk"))
        self.assertEqual(vendor_config.get("loot_min_value_threshold"), 
                        detector_config.get("loot_min_value_threshold"))


class TestConfiguration(unittest.TestCase):
    """Test configuration functionality."""
    
    def test_bazaar_config_structure(self):
        """Test bazaar configuration structure."""
        config_path = Path("config/bazaar_config.json")
        
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as fh:
                config = json.load(fh)
            
            # Check required fields
            required_fields = [
                "auto_sell_junk",
                "loot_min_value_threshold", 
                "excluded_items",
                "vendor_detection",
                "price_tracking",
                "auto_buy",
                "space_station_vendors"
            ]
            
            for field in required_fields:
                self.assertIn(field, config, f"Missing required field: {field}")
            
            # Check data types
            self.assertIsInstance(config["auto_sell_junk"], bool)
            self.assertIsInstance(config["loot_min_value_threshold"], int)
            self.assertIsInstance(config["excluded_items"], list)
            self.assertIsInstance(config["vendor_detection"], dict)
            self.assertIsInstance(config["price_tracking"], dict)
    
    def test_price_history_structure(self):
        """Test price history data structure."""
        history_path = Path("data/bazaar/price_history.json")
        
        if history_path.exists():
            with history_path.open("r", encoding="utf-8") as fh:
                history = json.load(fh)
            
            # Check required fields
            self.assertIn("last_updated", history)
            self.assertIn("items", history)
            self.assertIn("statistics", history)
            
            # Check statistics structure
            stats = history["statistics"]
            self.assertIn("total_sales", stats)
            self.assertIn("total_revenue", stats)
            self.assertIn("average_sale_price", stats)


def run_performance_tests():
    """Run performance tests."""
    print("\n" + "="*60)
    print("PERFORMANCE TESTS")
    print("="*60)
    
    import time
    
    # Test price tracker performance
    tracker = PriceTracker()
    
    start_time = time.time()
    for i in range(1000):
        tracker.add_sale(f"Item_{i}", 1000 + i)
    end_time = time.time()
    
    print(f"Price tracker: 1000 sales in {end_time - start_time:.3f} seconds")
    
    # Test vendor manager performance
    vendor = VendorManager()
    
    start_time = time.time()
    for i in range(100):
        item = InventoryItem(f"Test_Item_{i}", 1, 1000 + i, False)
        vendor._should_sell_item(item)
    end_time = time.time()
    
    print(f"Vendor manager: 100 item evaluations in {end_time - start_time:.3f} seconds")


def main():
    """Run all tests."""
    print("🧪 BATCH 061 - Bazaar Integration Tests")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestBazaarDetector,
        TestPriceTracker,
        TestVendorManager,
        TestIntegration,
        TestConfiguration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run performance tests
    run_performance_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 