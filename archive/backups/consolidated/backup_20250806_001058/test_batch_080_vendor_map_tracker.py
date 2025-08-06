#!/usr/bin/env python3
"""
MS11 Batch 080 - Vendor Map Tracker + Marketplace Discovery Test Suite

This test suite validates all functionality of the vendor mapping and marketplace discovery system:
- Vendor discovery and mapping
- Terminal OCR scanning
- Marketplace analysis
- Travel prioritization
- Profession-based vendor flagging
- Buyer logic and item requests
"""

import unittest
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import the core modules
from core.vendor_map_tracker import VendorMapTracker, VendorLocation, TerminalLocation
from core.marketplace_discovery import MarketplaceDiscovery, ItemListing, BuyerRequest
from core.travel_prioritizer import TravelPrioritizer, TravelDestination, TravelRoute


class TestVendorMapTracker(unittest.TestCase):
    """Test cases for VendorMapTracker functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / "vendor_map.json"
        
        # Create test configuration
        self.test_config = {
            "vendor_map": {
                "version": "1.0",
                "last_updated": "2025-01-27T00:00:00Z",
                "total_vendors": 0,
                "total_terminals": 0,
                "total_cities": 0
            },
            "vendor_locations": {
                "visited_vendors": {},
                "known_terminals": {},
                "vendor_cities": {},
                "profession_vendors": {}
            },
            "marketplace_discovery": {
                "high_population_cities": ["coronet", "mos_eisley", "theed"],
                "profession_hubs": {
                    "bio_engineer": ["coronet", "theed"],
                    "weaponsmith": ["coronet", "mos_eisley"],
                    "armorsmith": ["theed", "coronet"]
                }
            },
            "travel_priorities": {
                "requested_items": {"enabled": True, "priority_score": 10},
                "high_population_cities": {"enabled": True, "priority_score": 8},
                "profession_relevance": {"enabled": True, "priority_score": 6}
            },
            "ocr_settings": {
                "terminal_scanning": {"enabled": True, "scan_interval": 300},
                "item_recognition": {"confidence_threshold": 0.8, "fuzzy_matching": True}
            },
            "discovery_settings": {
                "auto_discovery": {"enabled": True, "scan_radius": 1000},
                "profession_flagging": {
                    "enabled": True,
                    "professions": {
                        "bio_engineer": {"keywords": ["medical", "clinic"]},
                        "weaponsmith": {"keywords": ["weapon", "arms"]},
                        "armorsmith": {"keywords": ["armor", "protection"]}
                    }
                }
            }
        }
        
        # Save test configuration
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.test_config, f, indent=2)
        
        # Initialize tracker
        self.tracker = VendorMapTracker(str(self.config_path))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_discover_vendor(self):
        """Test vendor discovery functionality."""
        # Discover a new vendor
        vendor_id = self.tracker.discover_vendor(
            vendor_name="Test Medical Store",
            planet="coronet",
            city="coronet",
            coordinates=(3500, -4800),
            vendor_type="vendor"
        )
        
        self.assertIsNotNone(vendor_id)
        self.assertIn(vendor_id, self.tracker.visited_vendors)
        
        vendor = self.tracker.visited_vendors[vendor_id]
        self.assertEqual(vendor.vendor_name, "Test Medical Store")
        self.assertEqual(vendor.planet, "coronet")
        self.assertEqual(vendor.city, "coronet")
        self.assertEqual(vendor.coordinates, (3500, -4800))
        self.assertEqual(vendor.visit_count, 1)
        self.assertTrue(vendor.is_active)
    
    def test_discover_terminal(self):
        """Test terminal discovery functionality."""
        # Discover a new terminal
        terminal_id = self.tracker.discover_terminal(
            terminal_name="Test Bazaar Terminal",
            planet="coronet",
            city="coronet",
            coordinates=(3550, -4750),
            terminal_type="bazaar"
        )
        
        self.assertIsNotNone(terminal_id)
        self.assertIn(terminal_id, self.tracker.known_terminals)
        
        terminal = self.tracker.known_terminals[terminal_id]
        self.assertEqual(terminal.terminal_name, "Test Bazaar Terminal")
        self.assertEqual(terminal.planet, "coronet")
        self.assertEqual(terminal.city, "coronet")
        self.assertEqual(terminal.coordinates, (3550, -4750))
        self.assertTrue(terminal.is_active)
    
    def test_profession_relevance_detection(self):
        """Test profession relevance detection."""
        # Test bio_engineer vendor
        vendor_id = self.tracker.discover_vendor(
            vendor_name="Medical Supply Store",
            planet="coronet",
            city="coronet",
            coordinates=(3500, -4800),
            vendor_type="vendor"
        )
        
        vendor = self.tracker.visited_vendors[vendor_id]
        self.assertIn("bio_engineer", vendor.profession_relevance)
        
        # Test weaponsmith vendor
        vendor_id2 = self.tracker.discover_vendor(
            vendor_name="Weapon Shop",
            planet="mos_eisley",
            city="mos_eisley",
            coordinates=(3600, -4700),
            vendor_type="vendor"
        )
        
        vendor2 = self.tracker.visited_vendors[vendor_id2]
        self.assertIn("weaponsmith", vendor2.profession_relevance)
    
    def test_find_vendors_for_items(self):
        """Test finding vendors for requested items."""
        # Discover vendors first
        self.tracker.discover_vendor(
            vendor_name="Medical Supply Store",
            planet="coronet",
            city="coronet",
            coordinates=(3500, -4800),
            vendor_type="vendor"
        )
        
        # Add items to vendor (simulate)
        vendor_id = "Medical Supply Store_coronet_coronet"
        if vendor_id in self.tracker.visited_vendors:
            self.tracker.visited_vendors[vendor_id].items_available = ["medical stim", "healing kit"]
        
        # Find vendors for items
        travel_priorities = self.tracker.find_vendors_for_items(["medical stim"])
        
        self.assertIsInstance(travel_priorities, list)
        if travel_priorities:
            self.assertIsInstance(travel_priorities[0].destination, str)
            self.assertIsInstance(travel_priorities[0].priority_score, float)
    
    def test_get_high_population_cities(self):
        """Test getting high population cities."""
        cities = self.tracker.get_high_population_cities()
        
        self.assertIsInstance(cities, list)
        self.assertIn("coronet", cities)
        self.assertIn("mos_eisley", cities)
        self.assertIn("theed", cities)
    
    def test_get_profession_hubs(self):
        """Test getting profession hubs."""
        hubs = self.tracker.get_profession_hubs("bio_engineer")
        
        self.assertIsInstance(hubs, list)
        self.assertIn("coronet", hubs)
        self.assertIn("theed", hubs)
    
    def test_flag_vendor_by_profession(self):
        """Test flagging vendors by profession."""
        # Discover a vendor first
        vendor_id = self.tracker.discover_vendor(
            vendor_name="Test Vendor",
            planet="coronet",
            city="coronet",
            coordinates=(3500, -4800),
            vendor_type="vendor"
        )
        
        # Flag vendor for profession
        success = self.tracker.flag_vendor_by_profession(vendor_id, "bio_engineer")
        
        self.assertTrue(success)
        
        # Check that vendor is now flagged
        vendor = self.tracker.visited_vendors[vendor_id]
        self.assertIn("bio_engineer", vendor.profession_relevance)
    
    def test_get_vendor_statistics(self):
        """Test getting vendor statistics."""
        # Discover some vendors first
        self.tracker.discover_vendor(
            vendor_name="Test Vendor 1",
            planet="coronet",
            city="coronet",
            coordinates=(3500, -4800),
            vendor_type="vendor"
        )
        
        self.tracker.discover_terminal(
            terminal_name="Test Terminal 1",
            planet="coronet",
            city="coronet",
            coordinates=(3550, -4750),
            terminal_type="bazaar"
        )
        
        stats = self.tracker.get_vendor_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_vendors", stats)
        self.assertIn("total_terminals", stats)
        self.assertIn("total_cities", stats)
        self.assertIn("active_vendors", stats)
        self.assertIn("active_terminals", stats)
        self.assertIn("profession_statistics", stats)
        self.assertIn("city_statistics", stats)
        self.assertIn("last_updated", stats)


class TestMarketplaceDiscovery(unittest.TestCase):
    """Test cases for MarketplaceDiscovery functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / "vendor_map.json"
        
        # Create test configuration
        self.test_config = {
            "ocr_settings": {
                "terminal_scanning": {
                    "enabled": True,
                    "scan_interval": 300,
                    "max_items_per_scan": 50,
                    "price_threshold": 1000000
                },
                "item_recognition": {
                    "confidence_threshold": 0.8,
                    "fuzzy_matching": True,
                    "common_mispellings": {
                        "rifle": ["rifel", "rife"],
                        "pistol": ["pistal", "pistel"]
                    }
                }
            },
            "marketplace_discovery": {
                "high_population_cities": ["coronet", "mos_eisley", "theed"]
            }
        }
        
        # Save test configuration
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.test_config, f, indent=2)
        
        # Initialize discovery system
        self.discovery = MarketplaceDiscovery(str(self.config_path))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_scan_terminal_ocr(self):
        """Test terminal OCR scanning."""
        # Test OCR text
        ocr_text = "Rifle - 5 - 15000 - WeaponMaster\nPistol - 10 - 8000 - ArmsDealer"
        
        scan_result = self.discovery.scan_terminal_ocr(
            terminal_id="test_terminal",
            ocr_text=ocr_text
        )
        
        self.assertIsNotNone(scan_result)
        self.assertEqual(scan_result.terminal_id, "test_terminal")
        self.assertIsInstance(scan_result.items_found, list)
        self.assertIsInstance(scan_result.scan_confidence, float)
        self.assertIsInstance(scan_result.processing_time, float)
        
        # Check that items were parsed
        self.assertGreater(len(scan_result.items_found), 0)
        
        # Check item structure
        if scan_result.items_found:
            item = scan_result.items_found[0]
            self.assertIsInstance(item.item_name, str)
            self.assertIsInstance(item.quantity, int)
            self.assertIsInstance(item.price, int)
            self.assertIsInstance(item.seller_name, str)
    
    def test_create_buyer_request(self):
        """Test creating buyer requests."""
        request_id = self.discovery.create_buyer_request(
            item_name="rifle",
            max_price=20000,
            min_quantity=1,
            preferred_quality="good",
            urgency="medium"
        )
        
        self.assertIsNotNone(request_id)
        self.assertIn(request_id, self.discovery.buyer_requests)
        
        request = self.discovery.buyer_requests[request_id]
        self.assertEqual(request.item_name, "rifle")
        self.assertEqual(request.max_price, 20000)
        self.assertEqual(request.min_quantity, 1)
        self.assertEqual(request.preferred_quality, "good")
        self.assertEqual(request.urgency, "medium")
        self.assertEqual(request.status, "pending")
    
    def test_find_items_for_request(self):
        """Test finding items for buyer requests."""
        # Create a buyer request
        request_id = self.discovery.create_buyer_request(
            item_name="rifle",
            max_price=20000,
            min_quantity=1,
            preferred_quality="good"
        )
        
        # Add some items to the marketplace
        item1 = ItemListing(
            item_name="rifle",
            quantity=5,
            price=15000,
            seller_name="WeaponMaster",
            listing_id="rifle_1",
            location="coronet",
            item_type="weapon",
            quality="good",
            last_updated=datetime.now().isoformat()
        )
        
        item2 = ItemListing(
            item_name="rifle",
            quantity=3,
            price=25000,  # Too expensive
            seller_name="ExpensiveDealer",
            listing_id="rifle_2",
            location="coronet",
            item_type="weapon",
            quality="excellent",
            last_updated=datetime.now().isoformat()
        )
        
        self.discovery.item_listings["rifle_1"] = item1
        self.discovery.item_listings["rifle_2"] = item2
        
        # Find items for request
        matching_items = self.discovery.find_items_for_request(request_id)
        
        self.assertIsInstance(matching_items, list)
        # Should find the first item but not the second (too expensive)
        self.assertEqual(len(matching_items), 1)
        self.assertEqual(matching_items[0].item_name, "rifle")
        self.assertEqual(matching_items[0].price, 15000)
    
    def test_analyze_marketplace(self):
        """Test marketplace analysis."""
        # Add some items to the marketplace
        items = [
            ItemListing("rifle", 5, 15000, "WeaponMaster", "rifle_1", "coronet", "weapon", "good", datetime.now().isoformat()),
            ItemListing("pistol", 10, 8000, "ArmsDealer", "pistol_1", "coronet", "weapon", "average", datetime.now().isoformat()),
            ItemListing("rifle", 3, 25000, "ExpensiveDealer", "rifle_2", "coronet", "weapon", "excellent", datetime.now().isoformat())
        ]
        
        for item in items:
            self.discovery.item_listings[item.listing_id] = item
        
        # Analyze marketplace
        analysis = self.discovery.analyze_marketplace("coronet")
        
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.location, "coronet")
        self.assertEqual(analysis.total_listings, 3)
        self.assertIsInstance(analysis.average_price, float)
        self.assertIsInstance(analysis.price_range, tuple)
        self.assertEqual(len(analysis.price_range), 2)
        self.assertIsInstance(analysis.popular_items, list)
        self.assertIsInstance(analysis.rare_items, list)
    
    def test_get_travel_priorities(self):
        """Test getting travel priorities."""
        priorities = self.discovery.get_travel_priorities(["rifle"])
        
        self.assertIsInstance(priorities, list)
        if priorities:
            priority = priorities[0]
            self.assertIn("destination", priority)
            self.assertIn("priority_score", priority)
            self.assertIn("reason", priority)
            self.assertIn("analysis", priority)
    
    def test_get_buyer_statistics(self):
        """Test getting buyer statistics."""
        # Create some buyer requests
        self.discovery.create_buyer_request("rifle", 20000)
        self.discovery.create_buyer_request("pistol", 15000)
        
        # Add some items
        item = ItemListing("rifle", 5, 15000, "WeaponMaster", "rifle_1", "coronet", "weapon", "good", datetime.now().isoformat())
        self.discovery.item_listings["rifle_1"] = item
        
        stats = self.discovery.get_buyer_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_listings", stats)
        self.assertIn("total_requests", stats)
        self.assertIn("pending_requests", stats)
        self.assertIn("found_requests", stats)
        self.assertIn("purchased_requests", stats)
        self.assertIn("price_statistics", stats)
        self.assertIn("item_type_distribution", stats)
        self.assertIn("marketplace_analyses", stats)
        self.assertIn("ocr_scans", stats)
        self.assertIn("last_updated", stats)


class TestTravelPrioritizer(unittest.TestCase):
    """Test cases for TravelPrioritizer functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / "vendor_map.json"
        
        # Create test configuration
        self.test_config = {
            "travel_priorities": {
                "requested_items": {"enabled": True, "priority_score": 10},
                "high_population_cities": {"enabled": True, "priority_score": 8},
                "profession_relevance": {"enabled": True, "priority_score": 6}
            },
            "marketplace_discovery": {
                "high_population_cities": ["coronet", "mos_eisley", "theed"]
            }
        }
        
        # Save test configuration
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.test_config, f, indent=2)
        
        # Initialize prioritizer
        self.prioritizer = TravelPrioritizer(str(self.config_path))
        
        # Create mock vendor map tracker and marketplace discovery
        self.mock_vendor_tracker = type('MockVendorTracker', (), {
            'get_high_population_cities': lambda: ["coronet", "mos_eisley", "theed"],
            'find_vendors_for_items': lambda items: [],
            'visited_vendors': {},
            'vendor_cities': {},
            'profession_vendors': {},
            'flag_vendor_by_profession': lambda vid, prof: True
        })()
        
        self.mock_marketplace = type('MockMarketplace', (), {
            'analyze_marketplace': lambda city: type('MockAnalysis', (), {
                'total_listings': 10,
                'average_price': 15000.0,
                'price_range': (5000, 25000),
                'popular_items': ['rifle', 'pistol'],
                'rare_items': ['rare_item']
            })(),
            'get_travel_priorities': lambda items: []
        })()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_prioritize_vendor_travel(self):
        """Test vendor travel prioritization."""
        destinations = self.prioritizer.prioritize_vendor_travel(
            vendor_map_tracker=self.mock_vendor_tracker,
            marketplace_discovery=self.mock_marketplace,
            requested_items=["rifle"],
            current_location=("coronet", "coronet", (3500, -4800))
        )
        
        self.assertIsInstance(destinations, list)
        if destinations:
            destination = destinations[0]
            self.assertIsInstance(destination, TravelDestination)
            self.assertIsInstance(destination.destination_id, str)
            self.assertIsInstance(destination.destination_name, str)
            self.assertIsInstance(destination.priority_score, float)
            self.assertIsInstance(destination.reason, str)
            self.assertIsInstance(destination.distance, float)
            self.assertIsInstance(destination.estimated_reward, float)
            self.assertIsInstance(destination.profession_relevance, list)
            self.assertIsInstance(destination.population_level, str)
            self.assertIsInstance(destination.vendor_count, int)
            self.assertIsInstance(destination.terminal_count, int)
    
    def test_optimize_travel_route(self):
        """Test travel route optimization."""
        # Create test destinations
        destinations = [
            TravelDestination(
                destination_id="city_coronet",
                destination_name="coronet",
                planet="corellia",
                city="coronet",
                coordinates=(3500, -4800),
                priority_score=8.5,
                reason="High population city",
                distance=1000.0,
                estimated_reward=5000.0,
                profession_relevance=["bio_engineer"],
                population_level="high",
                vendor_count=5,
                terminal_count=2
            ),
            TravelDestination(
                destination_id="city_mos_eisley",
                destination_name="mos_eisley",
                planet="tatooine",
                city="mos_eisley",
                coordinates=(3600, -4700),
                priority_score=7.2,
                reason="Weapon hub",
                distance=1500.0,
                estimated_reward=3000.0,
                profession_relevance=["weaponsmith"],
                population_level="high",
                vendor_count=3,
                terminal_count=1
            )
        ]
        
        # Test different optimization types
        for opt_type in ["balanced", "distance", "reward"]:
            route = self.prioritizer.optimize_travel_route(
                destinations=destinations,
                optimization_type=opt_type,
                max_destinations=2
            )
            
            self.assertIsNotNone(route)
            self.assertIsInstance(route, TravelRoute)
            self.assertIsInstance(route.route_id, str)
            self.assertIsInstance(route.destinations, list)
            self.assertIsInstance(route.total_distance, float)
            self.assertIsInstance(route.estimated_duration, float)
            self.assertIsInstance(route.total_reward, float)
            self.assertIsInstance(route.priority_score, float)
            self.assertEqual(route.route_type, opt_type)
    
    def test_get_profession_hub_priorities(self):
        """Test getting profession hub priorities."""
        destinations = self.prioritizer.get_profession_hub_priorities(
            profession="bio_engineer",
            vendor_map_tracker=self.mock_vendor_tracker
        )
        
        self.assertIsInstance(destinations, list)
        if destinations:
            destination = destinations[0]
            self.assertIsInstance(destination, TravelDestination)
            self.assertIn("bio_engineer", destination.profession_relevance)
    
    def test_flag_vendor_by_profession(self):
        """Test flagging vendors by profession."""
        success = self.prioritizer.flag_vendor_by_profession(
            vendor_id="test_vendor",
            profession="bio_engineer",
            vendor_map_tracker=self.mock_vendor_tracker
        )
        
        self.assertTrue(success)
    
    def test_get_travel_statistics(self):
        """Test getting travel statistics."""
        stats = self.prioritizer.get_travel_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_destinations", stats)
        self.assertIn("total_routes", stats)
        self.assertIn("destination_priority_distribution", stats)
        self.assertIn("route_type_distribution", stats)
        self.assertIn("average_statistics", stats)
        self.assertIn("travel_history", stats)
        self.assertIn("last_updated", stats)
        
        # Check structure of nested dictionaries
        self.assertIn("high", stats["destination_priority_distribution"])
        self.assertIn("medium", stats["destination_priority_distribution"])
        self.assertIn("low", stats["destination_priority_distribution"])
        
        self.assertIn("efficient", stats["route_type_distribution"])
        self.assertIn("comprehensive", stats["route_type_distribution"])
        self.assertIn("targeted", stats["route_type_distribution"])
        
        self.assertIn("priority_score", stats["average_statistics"])
        self.assertIn("distance", stats["average_statistics"])
        self.assertIn("reward", stats["average_statistics"])


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete vendor map tracker system."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / "vendor_map.json"
        
        # Create comprehensive test configuration
        self.test_config = {
            "vendor_map": {
                "version": "1.0",
                "last_updated": "2025-01-27T00:00:00Z",
                "total_vendors": 0,
                "total_terminals": 0,
                "total_cities": 0
            },
            "vendor_locations": {
                "visited_vendors": {},
                "known_terminals": {},
                "vendor_cities": {},
                "profession_vendors": {}
            },
            "marketplace_discovery": {
                "high_population_cities": ["coronet", "mos_eisley", "theed"],
                "profession_hubs": {
                    "bio_engineer": ["coronet", "theed"],
                    "weaponsmith": ["coronet", "mos_eisley"],
                    "armorsmith": ["theed", "coronet"]
                }
            },
            "travel_priorities": {
                "requested_items": {"enabled": True, "priority_score": 10},
                "high_population_cities": {"enabled": True, "priority_score": 8},
                "profession_relevance": {"enabled": True, "priority_score": 6}
            },
            "ocr_settings": {
                "terminal_scanning": {"enabled": True, "scan_interval": 300},
                "item_recognition": {"confidence_threshold": 0.8, "fuzzy_matching": True}
            },
            "discovery_settings": {
                "auto_discovery": {"enabled": True, "scan_radius": 1000},
                "profession_flagging": {
                    "enabled": True,
                    "professions": {
                        "bio_engineer": {"keywords": ["medical", "clinic"]},
                        "weaponsmith": {"keywords": ["weapon", "arms"]},
                        "armorsmith": {"keywords": ["armor", "protection"]}
                    }
                }
            }
        }
        
        # Save test configuration
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.test_config, f, indent=2)
        
        # Initialize all components
        self.vendor_tracker = VendorMapTracker(str(self.config_path))
        self.marketplace_discovery = MarketplaceDiscovery(str(self.config_path))
        self.travel_prioritizer = TravelPrioritizer(str(self.config_path))
    
    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_complete_workflow(self):
        """Test complete vendor mapping and marketplace discovery workflow."""
        # Step 1: Discover vendors
        vendor_id = self.vendor_tracker.discover_vendor(
            vendor_name="Medical Supply Store",
            planet="coronet",
            city="coronet",
            coordinates=(3500, -4800),
            vendor_type="vendor"
        )
        
        terminal_id = self.vendor_tracker.discover_terminal(
            terminal_name="Bazaar Terminal",
            planet="coronet",
            city="coronet",
            coordinates=(3550, -4750),
            terminal_type="bazaar"
        )
        
        # Step 2: Scan terminal with OCR
        ocr_text = "Medical Stim - 20 - 500 - MedSupply\nRifle - 5 - 15000 - WeaponMaster"
        scan_result = self.marketplace_discovery.scan_terminal_ocr(
            terminal_id=terminal_id,
            ocr_text=ocr_text
        )
        
        # Step 3: Create buyer request
        request_id = self.marketplace_discovery.create_buyer_request(
            item_name="medical stim",
            max_price=1000,
            min_quantity=1,
            preferred_quality="good"
        )
        
        # Step 4: Find items for request
        matching_items = self.marketplace_discovery.find_items_for_request(request_id)
        
        # Step 5: Get travel priorities
        destinations = self.travel_prioritizer.prioritize_vendor_travel(
            vendor_map_tracker=self.vendor_tracker,
            marketplace_discovery=self.marketplace_discovery,
            requested_items=["medical stim"],
            current_location=("coronet", "coronet", (3500, -4800))
        )
        
        # Step 6: Optimize travel route
        route = self.travel_prioritizer.optimize_travel_route(
            destinations=destinations,
            optimization_type="balanced",
            max_destinations=3
        )
        
        # Verify results
        self.assertIsNotNone(vendor_id)
        self.assertIsNotNone(terminal_id)
        self.assertIsNotNone(scan_result)
        self.assertIsNotNone(request_id)
        self.assertIsInstance(matching_items, list)
        self.assertIsInstance(destinations, list)
        self.assertIsNotNone(route)
        
        # Check that items were found
        self.assertGreater(len(scan_result.items_found), 0)
        
        # Check that buyer request was created
        self.assertIn(request_id, self.marketplace_discovery.buyer_requests)
        
        # Check that vendor was discovered
        self.assertIn(vendor_id, self.vendor_tracker.visited_vendors)
        
        # Check that terminal was discovered
        self.assertIn(terminal_id, self.vendor_tracker.known_terminals)
    
    def test_statistics_integration(self):
        """Test statistics integration across all components."""
        # Perform some operations
        self.vendor_tracker.discover_vendor("Test Vendor", "coronet", "coronet", (3500, -4800))
        self.marketplace_discovery.create_buyer_request("test item", 1000)
        
        # Get statistics from all components
        vendor_stats = self.vendor_tracker.get_vendor_statistics()
        marketplace_stats = self.marketplace_discovery.get_buyer_statistics()
        travel_stats = self.travel_prioritizer.get_travel_statistics()
        
        # Verify statistics structure
        self.assertIsInstance(vendor_stats, dict)
        self.assertIsInstance(marketplace_stats, dict)
        self.assertIsInstance(travel_stats, dict)
        
        # Check that statistics are consistent
        self.assertGreaterEqual(vendor_stats['total_vendors'], 0)
        self.assertGreaterEqual(marketplace_stats['total_requests'], 0)
        self.assertGreaterEqual(travel_stats['total_destinations'], 0)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestVendorMapTracker))
    test_suite.addTest(unittest.makeSuite(TestMarketplaceDiscovery))
    test_suite.addTest(unittest.makeSuite(TestTravelPrioritizer))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 