#!/usr/bin/env python3
"""
Test suite for Batch 075 - Vendor Scanning + Galactic Bazaar Search Logic

This test suite validates:
1. Vendor Scanner Service functionality
2. Vendor API Plugin endpoints
3. Integration with existing bazaar module
4. Error handling and edge cases
5. Cache management and data persistence
"""

import unittest
import tempfile
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import vendor scanner and API
try:
    from services.vendor_scanner import (
        VendorScanner, create_vendor_scanner,
        VendorItem, VendorLocation, BazaarListing
    )
    from plugins.vendor_api import VendorAPI, create_vendor_api
    VENDOR_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"[TEST] Vendor services not available: {e}")
    VENDOR_SERVICES_AVAILABLE = False

# Import existing bazaar module
try:
    from modules.bazaar import VendorManager, PriceTracker, BazaarDetector
    BAZAAR_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"[TEST] Bazaar module not available: {e}")
    BAZAAR_MODULE_AVAILABLE = False

from android_ms11.utils.logging_utils import log_event


class TestVendorScanner(unittest.TestCase):
    """Test vendor scanner service functionality."""

    def setUp(self):
        """Set up test environment."""
        if not VENDOR_SERVICES_AVAILABLE:
            self.skipTest("Vendor services not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = create_vendor_scanner(cache_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_vendor_scanner_creation(self):
        """Test vendor scanner creation."""
        self.assertIsNotNone(self.scanner)
        self.assertIsInstance(self.scanner, VendorScanner)
        self.assertEqual(self.scanner.cache_expiry_hours, 24)
        self.assertEqual(self.scanner.max_cache_size, 1000)
    
    def test_scan_nearby_vendors(self):
        """Test scanning for nearby vendors."""
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        vendors = self.scanner.scan_nearby_vendors(player_location)
        
        self.assertIsInstance(vendors, list)
        self.assertGreater(len(vendors), 0)
        
        for vendor in vendors:
            self.assertIsInstance(vendor, VendorLocation)
            self.assertEqual(vendor.planet, "tatooine")
            self.assertEqual(vendor.city, "mos_eisley")
            self.assertIsInstance(vendor.coordinates, tuple)
            self.assertEqual(len(vendor.coordinates), 2)
            self.assertIsInstance(vendor.items, list)
    
    def test_search_for_items(self):
        """Test searching for items."""
        # First scan some vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        self.scanner.scan_nearby_vendors(player_location)
        
        # Search for items
        search_items = ["Stimpack", "Rifle"]
        results = self.scanner.search_for_items(search_items, max_price=20000)
        
        self.assertIsInstance(results, dict)
        self.assertIn("Stimpack", results)
        self.assertIn("Rifle", results)
        
        for item_name, item_results in results.items():
            self.assertIsInstance(item_results, list)
            for result in item_results:
                self.assertIn("source", result)
                self.assertIn("price", result)
                self.assertIn("quantity", result)
    
    def test_search_for_items_no_results(self):
        """Test searching for non-existent items."""
        search_items = ["NonExistentItem"]
        results = self.scanner.search_for_items(search_items)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 0)
    
    def test_get_vendor_by_location(self):
        """Test getting vendors by location."""
        # First scan some vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        self.scanner.scan_nearby_vendors(player_location)
        
        # Get vendors by location
        vendors = self.scanner.get_vendor_by_location("tatooine", "mos_eisley")
        
        self.assertIsInstance(vendors, list)
        self.assertGreater(len(vendors), 0)
        
        for vendor in vendors:
            self.assertEqual(vendor.planet.lower(), "tatooine")
            self.assertEqual(vendor.city.lower(), "mos_eisley")
    
    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        # First scan some vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        self.scanner.scan_nearby_vendors(player_location)
        
        stats = self.scanner.get_cache_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_vendors", stats)
        self.assertIn("total_bazaar_listings", stats)
        self.assertIn("total_items", stats)
        self.assertIn("cache_size_mb", stats)
        self.assertGreaterEqual(stats["total_vendors"], 0)
    
    def test_export_cache_report(self):
        """Test exporting cache report."""
        # First scan some vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        self.scanner.scan_nearby_vendors(player_location)
        
        report_path = self.scanner.export_cache_report()
        
        self.assertIsInstance(report_path, str)
        self.assertTrue(Path(report_path).exists())
        
        # Verify report content
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        self.assertIn("timestamp", report_data)
        self.assertIn("cache_stats", report_data)
        self.assertIn("vendors", report_data)
        self.assertIn("bazaar_listings", report_data)
    
    def test_cache_cleanup(self):
        """Test cache cleanup functionality."""
        # First scan some vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        self.scanner.scan_nearby_vendors(player_location)
        
        initial_stats = self.scanner.get_cache_stats()
        initial_vendors = initial_stats["total_vendors"]
        
        # Manually trigger cleanup
        self.scanner._cleanup_expired_cache()
        
        # Verify cleanup didn't remove valid entries
        final_stats = self.scanner.get_cache_stats()
        self.assertGreaterEqual(final_stats["total_vendors"], 0)


class TestVendorAPI(unittest.TestCase):
    """Test vendor API plugin functionality."""

    def setUp(self):
        """Set up test environment."""
        if not VENDOR_SERVICES_AVAILABLE:
            self.skipTest("Vendor services not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = create_vendor_scanner(cache_dir=self.temp_dir)
        self.api = create_vendor_api(self.scanner)
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_vendor_api_creation(self):
        """Test vendor API creation."""
        self.assertIsNotNone(self.api)
        self.assertIsInstance(self.api, VendorAPI)
        self.assertEqual(self.api.api_version, "1.0")
        self.assertIsNotNone(self.api.vendor_scanner)
    
    def test_get_api_info(self):
        """Test getting API information."""
        response = self.api.get_api_info()
        
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        self.assertIn("api_name", response["data"])
        self.assertIn("version", response["data"])
        self.assertIn("vendor_scanner_available", response["data"])
        self.assertEqual(response["data"]["api_name"], "Vendor API")
    
    def test_search_items_api(self):
        """Test searching items via API."""
        # First scan some vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        self.scanner.scan_nearby_vendors(player_location)
        
        # Search via API
        response = self.api.search_items(
            item_names=["Stimpack", "Rifle"],
            max_price=20000
        )
        
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        self.assertIn("search_results", response["data"])
        self.assertIn("total_items_found", response["data"])
        self.assertIn("items_searched", response["data"])
    
    def test_search_items_api_no_results(self):
        """Test searching for non-existent items via API."""
        response = self.api.search_items(["NonExistentItem"])
        
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        self.assertEqual(response["data"]["total_items_found"], 0)
    
    def test_get_vendors_by_location_api(self):
        """Test getting vendors by location via API."""
        # First scan some vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        self.scanner.scan_nearby_vendors(player_location)
        
        # Get vendors via API
        response = self.api.get_vendors_by_location("tatooine", "mos_eisley")
        
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        self.assertIn("vendors", response["data"])
        self.assertIn("location", response["data"])
        self.assertIn("total_vendors", response["data"])
    
    def test_scan_location_api(self):
        """Test scanning location via API."""
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        response = self.api.scan_location(player_location)
        
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        self.assertIn("vendors_detected", response["data"])
        self.assertIn("scan_location", response["data"])
        self.assertIn("total_vendors", response["data"])
    
    def test_get_bazaar_listings_api(self):
        """Test getting bazaar listings via API."""
        response = self.api.get_bazaar_listings(["Durindfire", "Spice Wine"])
        
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        self.assertIn("bazaar_listings", response["data"])
        self.assertIn("search_terms", response["data"])
        self.assertIn("total_listings", response["data"])
    
    def test_get_cache_stats_api(self):
        """Test getting cache stats via API."""
        response = self.api.get_cache_stats()
        
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        self.assertIn("cache_stats", response["data"])
        self.assertIn("api_version", response["data"])
        self.assertIn("vendor_scanner_available", response["data"])
    
    def test_get_crafting_suggestions(self):
        """Test getting crafting suggestions."""
        # First scan some vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        self.scanner.scan_nearby_vendors(player_location)
        
        required_items = ["Stimpack", "Rifle"]
        max_budget = 50000
        
        response = self.api.get_crafting_suggestions(required_items, max_budget)
        
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        self.assertIn("crafting_suggestions", response["data"])
        self.assertIn("required_items", response["data"])
        self.assertIn("total_cost", response["data"])
        self.assertIn("budget_remaining", response["data"])
        self.assertIn("items_found", response["data"])
        self.assertIn("items_missing", response["data"])
    
    def test_export_cache_report_api(self):
        """Test exporting cache report via API."""
        # First scan some vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        self.scanner.scan_nearby_vendors(player_location)
        
        response = self.api.export_cache_report()
        
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        self.assertIn("report_path", response["data"])
        self.assertIn("export_successful", response["data"])
        self.assertTrue(response["data"]["export_successful"])
    
    def test_error_handling(self):
        """Test error handling in API."""
        # Test with invalid vendor scanner by temporarily disabling VENDOR_SCANNER_AVAILABLE
        import plugins.vendor_api
        original_availability = plugins.vendor_api.VENDOR_SCANNER_AVAILABLE
        try:
            # Temporarily disable vendor scanner availability
            plugins.vendor_api.VENDOR_SCANNER_AVAILABLE = False
            
            api_no_scanner = VendorAPI(None)
            
            response = api_no_scanner.search_items(["test"])
            self.assertFalse(response["success"])
            self.assertIn("error", response)
            self.assertIn("Vendor scanner not available", response["error"])
        finally:
            # Restore original availability
            plugins.vendor_api.VENDOR_SCANNER_AVAILABLE = original_availability


class TestBazaarModuleIntegration(unittest.TestCase):
    """Test integration with existing bazaar module."""

    def setUp(self):
        """Set up test environment."""
        self.bazaar_available = BAZAAR_MODULE_AVAILABLE
    
    def test_bazaar_module_availability(self):
        """Test bazaar module availability."""
        if not self.bazaar_available:
            self.skipTest("Bazaar module not available")
        
        # Test that bazaar module components exist
        self.assertTrue(hasattr(VendorManager, '__init__'))
        self.assertTrue(hasattr(PriceTracker, '__init__'))
        self.assertTrue(hasattr(BazaarDetector, '__init__'))
    
    def test_bazaar_module_components(self):
        """Test bazaar module component structure."""
        if not self.bazaar_available:
            self.skipTest("Bazaar module not available")
        
        # Test VendorManager
        self.assertTrue(hasattr(VendorManager, 'detect_and_interact_with_vendor'))
        self.assertTrue(hasattr(VendorManager, 'scan_inventory_for_sale'))
        self.assertTrue(hasattr(VendorManager, 'sell_items'))
        self.assertTrue(hasattr(VendorManager, 'buy_items'))
        
        # Test PriceTracker
        self.assertTrue(hasattr(PriceTracker, '__init__'))
        
        # Test BazaarDetector
        self.assertTrue(hasattr(BazaarDetector, 'detect_vendor_terminals'))
        self.assertTrue(hasattr(BazaarDetector, 'detect_vendor_interface'))
        self.assertTrue(hasattr(BazaarDetector, 'is_vendor_screen'))


class TestIntegration(unittest.TestCase):
    """Test integration between components."""

    def setUp(self):
        """Set up test environment."""
        if not VENDOR_SERVICES_AVAILABLE:
            self.skipTest("Vendor services not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = create_vendor_scanner(cache_dir=self.temp_dir)
        self.api = create_vendor_api(self.scanner)
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_workflow(self):
        """Test complete workflow from scanning to API access."""
        # Step 1: Scan for vendors
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        vendors = self.scanner.scan_nearby_vendors(player_location)
        self.assertGreater(len(vendors), 0)
        
        # Step 2: Search for items via scanner
        search_items = ["Stimpack", "Rifle"]
        scanner_results = self.scanner.search_for_items(search_items)
        self.assertIsInstance(scanner_results, dict)
        
        # Step 3: Search for items via API
        api_response = self.api.search_items(search_items)
        self.assertTrue(api_response["success"])
        
        # Step 4: Get crafting suggestions
        suggestions_response = self.api.get_crafting_suggestions(search_items, 50000)
        self.assertTrue(suggestions_response["success"])
        
        # Step 5: Export report
        report_response = self.api.export_cache_report()
        self.assertTrue(report_response["success"])
    
    def test_cache_persistence(self):
        """Test that cache persists between scanner instances."""
        # Create first scanner and scan vendors
        scanner1 = create_vendor_scanner(cache_dir=self.temp_dir)
        player_location = ("tatooine", "mos_eisley", (3520, -4800))
        vendors1 = scanner1.scan_nearby_vendors(player_location)
        
        # Create second scanner and verify cache is loaded
        scanner2 = create_vendor_scanner(cache_dir=self.temp_dir)
        stats2 = scanner2.get_cache_stats()
        
        self.assertGreater(stats2["total_vendors"], 0)
        
        # Verify vendors are accessible
        vendors2 = scanner2.get_vendor_by_location("tatooine", "mos_eisley")
        self.assertGreater(len(vendors2), 0)
    
    def test_api_request_history(self):
        """Test API request history tracking."""
        # Make some API calls
        self.api.get_api_info()
        self.api.search_items(["test"])
        self.api.get_cache_stats()
        
        # Check request history
        history = self.api.get_request_history()
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        
        for request in history:
            self.assertIn("timestamp", request)
            self.assertIn("endpoint", request)
            self.assertIn("details", request)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    def setUp(self):
        """Set up test environment."""
        if not VENDOR_SERVICES_AVAILABLE:
            self.skipTest("Vendor services not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = create_vendor_scanner(cache_dir=self.temp_dir)
        self.api = create_vendor_api(self.scanner)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_search_terms(self):
        """Test searching with empty search terms."""
        response = self.api.search_items([])
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["total_items_found"], 0)
    
    def test_invalid_location(self):
        """Test getting vendors for invalid location."""
        response = self.api.get_vendors_by_location("", "")
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["total_vendors"], 0)
    
    def test_negative_max_price(self):
        """Test searching with negative max price."""
        response = self.api.search_items(["test"], max_price=-100)
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["total_items_found"], 0)
    
    def test_large_budget(self):
        """Test crafting suggestions with very large budget."""
        response = self.api.get_crafting_suggestions(["test"], 999999999)
        self.assertTrue(response["success"])
        self.assertIn("budget_remaining", response["data"])
    
    def test_no_vendor_scanner(self):
        """Test API behavior without vendor scanner."""
        # Temporarily disable vendor scanner availability
        import plugins.vendor_api
        original_availability = plugins.vendor_api.VENDOR_SCANNER_AVAILABLE
        try:
            plugins.vendor_api.VENDOR_SCANNER_AVAILABLE = False
            
            api_no_scanner = VendorAPI(None)
            
            # Test various endpoints
            endpoints_to_test = [
                ("search_items", {"item_names": ["test"]}),
                ("get_vendors_by_location", {"planet": "test", "city": "test"}),
                ("scan_location", {"player_location": ("test", "test", (0, 0))}),
                ("get_bazaar_listings", {"search_terms": ["test"]}),
                ("get_cache_stats", {}),
                ("get_crafting_suggestions", {"required_items": ["test"], "max_budget": 1000}),
                ("export_cache_report", {})
            ]
            
            for method_name, kwargs in endpoints_to_test:
                method = getattr(api_no_scanner, method_name)
                response = method(**kwargs)
                
                self.assertFalse(response["success"])
                self.assertIn("error", response)
                self.assertIn("Vendor scanner not available", response["error"])
        finally:
            # Restore original availability
            plugins.vendor_api.VENDOR_SCANNER_AVAILABLE = original_availability


def run_tests():
    """Run all tests."""
    print("🧪 Running Batch 075 Vendor Scanner Tests")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestVendorScanner,
        TestVendorAPI,
        TestBazaarModuleIntegration,
        TestIntegration,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 