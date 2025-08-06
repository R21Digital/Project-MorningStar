#!/usr/bin/env python3
"""
MS11 Batch 080 - Vendor Map Tracker + Marketplace Discovery Demo

This demo showcases the comprehensive vendor mapping and marketplace discovery system:
- Vendor discovery and mapping
- Terminal OCR scanning
- Marketplace analysis
- Travel prioritization
- Profession-based vendor flagging
- Buyer logic and item requests
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import the core modules
from core.vendor_map_tracker import VendorMapTracker
from core.marketplace_discovery import MarketplaceDiscovery
from core.travel_prioritizer import TravelPrioritizer


class VendorMapTrackerDemo:
    """Demo class for showcasing Batch 080 functionality."""
    
    def __init__(self):
        """Initialize the demo with all core components."""
        print("🚀 Initializing MS11 Batch 080 - Vendor Map Tracker + Marketplace Discovery Demo")
        print("=" * 80)
        
        # Initialize core components
        self.vendor_map_tracker = VendorMapTracker()
        self.marketplace_discovery = MarketplaceDiscovery()
        self.travel_prioritizer = TravelPrioritizer()
        
        # Demo data
        self.demo_vendors = [
            {
                "name": "Medical Supply Store",
                "planet": "coronet",
                "city": "coronet",
                "coordinates": (3500, -4800),
                "type": "vendor"
            },
            {
                "name": "Weapon Shop",
                "planet": "tatooine",
                "city": "mos_eisley",
                "coordinates": (3600, -4700),
                "type": "vendor"
            },
            {
                "name": "Armor Dealer",
                "planet": "naboo",
                "city": "theed",
                "coordinates": (4000, -4500),
                "type": "vendor"
            },
            {
                "name": "Bazaar Terminal",
                "planet": "coronet",
                "city": "coronet",
                "coordinates": (3550, -4750),
                "type": "terminal"
            },
            {
                "name": "Crafting Terminal",
                "planet": "tatooine",
                "city": "mos_eisley",
                "coordinates": (3650, -4650),
                "type": "terminal"
            }
        ]
        
        self.demo_ocr_data = [
            "Rifle - 5 - 15000 - WeaponMaster",
            "Pistol - 10 - 8000 - ArmsDealer",
            "Medical Stim - 20 - 500 - MedSupply",
            "Armor Vest - 3 - 25000 - ArmorSmith",
            "Food Ration - 50 - 100 - FoodVendor",
            "Chemical Compound - 15 - 2000 - ChemDealer",
            "Droid Parts - 8 - 12000 - DroidEngineer",
            "Ship Components - 2 - 50000 - ShipWright"
        ]
        
        self.demo_requested_items = ["rifle", "medical stim", "armor vest"]
        
        print("✅ Demo initialized successfully")
        print()
    
    def run_full_demo(self):
        """Run the complete demo showcasing all functionality."""
        print("🎯 Running Complete Vendor Map Tracker + Marketplace Discovery Demo")
        print("=" * 80)
        
        # Demo 1: Vendor Discovery and Mapping
        self._demo_vendor_discovery()
        
        # Demo 2: Terminal OCR Scanning
        self._demo_terminal_ocr_scanning()
        
        # Demo 3: Marketplace Analysis
        self._demo_marketplace_analysis()
        
        # Demo 4: Travel Prioritization
        self._demo_travel_prioritization()
        
        # Demo 5: Profession-Based Vendor Flagging
        self._demo_profession_flagging()
        
        # Demo 6: Buyer Logic and Item Requests
        self._demo_buyer_logic()
        
        # Demo 7: Route Optimization
        self._demo_route_optimization()
        
        # Demo 8: Statistics and Reporting
        self._demo_statistics_and_reporting()
        
        print("\n🎉 Demo completed successfully!")
        print("=" * 80)
    
    def _demo_vendor_discovery(self):
        """Demo vendor discovery and mapping functionality."""
        print("\n📍 Demo 1: Vendor Discovery and Mapping")
        print("-" * 50)
        
        # Discover vendors
        discovered_vendors = []
        for vendor_data in self.demo_vendors:
            if vendor_data["type"] == "vendor":
                vendor_id = self.vendor_map_tracker.discover_vendor(
                    vendor_name=vendor_data["name"],
                    planet=vendor_data["planet"],
                    city=vendor_data["city"],
                    coordinates=vendor_data["coordinates"],
                    vendor_type=vendor_data["type"]
                )
                discovered_vendors.append(vendor_id)
                print(f"  ✅ Discovered vendor: {vendor_data['name']} in {vendor_data['city']}")
        
        # Discover terminals
        discovered_terminals = []
        for vendor_data in self.demo_vendors:
            if vendor_data["type"] == "terminal":
                terminal_id = self.vendor_map_tracker.discover_terminal(
                    terminal_name=vendor_data["name"],
                    planet=vendor_data["planet"],
                    city=vendor_data["city"],
                    coordinates=vendor_data["coordinates"],
                    terminal_type="bazaar"
                )
                discovered_terminals.append(terminal_id)
                print(f"  ✅ Discovered terminal: {vendor_data['name']} in {vendor_data['city']}")
        
        # Get vendor statistics
        stats = self.vendor_map_tracker.get_vendor_statistics()
        print(f"\n  📊 Vendor Statistics:")
        print(f"    - Total vendors: {stats['total_vendors']}")
        print(f"    - Total terminals: {stats['total_terminals']}")
        print(f"    - Total cities: {stats['total_cities']}")
        print(f"    - Active vendors: {stats['active_vendors']}")
        print(f"    - Active terminals: {stats['active_terminals']}")
        
        return discovered_vendors, discovered_terminals
    
    def _demo_terminal_ocr_scanning(self):
        """Demo terminal OCR scanning functionality."""
        print("\n🔍 Demo 2: Terminal OCR Scanning")
        print("-" * 50)
        
        # Simulate OCR scanning
        terminal_id = "Bazaar Terminal_coronet_coronet"
        
        # Create terminal if it doesn't exist
        if terminal_id not in self.vendor_map_tracker.known_terminals:
            self.vendor_map_tracker.discover_terminal(
                terminal_name="Bazaar Terminal",
                planet="coronet",
                city="coronet",
                coordinates=(3550, -4750),
                terminal_type="bazaar"
            )
        
        # Simulate OCR text
        ocr_text = "\n".join(self.demo_ocr_data)
        print(f"  📝 OCR Text from terminal:")
        for line in self.demo_ocr_data:
            print(f"    {line}")
        
        # Scan terminal with OCR
        scan_result = self.marketplace_discovery.scan_terminal_ocr(
            terminal_id=terminal_id,
            ocr_text=ocr_text
        )
        
        print(f"\n  📊 OCR Scan Results:")
        print(f"    - Items found: {len(scan_result.items_found)}")
        print(f"    - Scan confidence: {scan_result.scan_confidence:.2f}")
        print(f"    - Processing time: {scan_result.processing_time:.3f}s")
        
        # Display found items
        print(f"\n  🛍️ Found Items:")
        for item in scan_result.items_found[:5]:  # Show first 5 items
            print(f"    - {item.item_name}: {item.quantity}x @ {item.price} credits ({item.quality} quality)")
        
        return scan_result
    
    def _demo_marketplace_analysis(self):
        """Demo marketplace analysis functionality."""
        print("\n📈 Demo 3: Marketplace Analysis")
        print("-" * 50)
        
        # Analyze marketplace for different cities
        cities_to_analyze = ["coronet", "mos_eisley", "theed"]
        
        for city in cities_to_analyze:
            analysis = self.marketplace_discovery.analyze_marketplace(city)
            
            print(f"\n  🏙️ Marketplace Analysis for {city}:")
            print(f"    - Total listings: {analysis.total_listings}")
            print(f"    - Average price: {analysis.average_price:.0f} credits")
            print(f"    - Price range: {analysis.price_range[0]:,} - {analysis.price_range[1]:,} credits")
            print(f"    - Popular items: {len(analysis.popular_items)}")
            print(f"    - Rare items: {len(analysis.rare_items)}")
            
            if analysis.popular_items:
                print(f"    - Top popular items: {', '.join(analysis.popular_items[:3])}")
            
            if analysis.rare_items:
                print(f"    - Top rare items: {', '.join(analysis.rare_items[:3])}")
    
    def _demo_travel_prioritization(self):
        """Demo travel prioritization functionality."""
        print("\n🗺️ Demo 4: Travel Prioritization")
        print("-" * 50)
        
        # Get travel priorities
        destinations = self.travel_prioritizer.prioritize_vendor_travel(
            vendor_map_tracker=self.vendor_map_tracker,
            marketplace_discovery=self.marketplace_discovery,
            requested_items=self.demo_requested_items,
            current_location=("coronet", "coronet", (3500, -4800))
        )
        
        print(f"  🎯 Travel Priorities (Top 5):")
        for i, destination in enumerate(destinations[:5], 1):
            print(f"    {i}. {destination.destination_name}")
            print(f"       - Priority Score: {destination.priority_score:.2f}")
            print(f"       - Reason: {destination.reason}")
            print(f"       - Distance: {destination.distance:.0f} units")
            print(f"       - Estimated Reward: {destination.estimated_reward:.0f} credits")
            print(f"       - Population Level: {destination.population_level}")
            print(f"       - Vendors: {destination.vendor_count}, Terminals: {destination.terminal_count}")
            print()
    
    def _demo_profession_flagging(self):
        """Demo profession-based vendor flagging."""
        print("\n🏷️ Demo 5: Profession-Based Vendor Flagging")
        print("-" * 50)
        
        # Flag vendors by profession
        profession_vendors = [
            ("Medical Supply Store_coronet_coronet", "bio_engineer"),
            ("Weapon Shop_tatooine_mos_eisley", "weaponsmith"),
            ("Armor Dealer_naboo_theed", "armorsmith")
        ]
        
        for vendor_id, profession in profession_vendors:
            success = self.travel_prioritizer.flag_vendor_by_profession(
                vendor_id=vendor_id,
                profession=profession,
                vendor_map_tracker=self.vendor_map_tracker
            )
            
            if success:
                print(f"  ✅ Flagged vendor {vendor_id} for profession: {profession}")
            else:
                print(f"  ❌ Failed to flag vendor {vendor_id} for profession: {profession}")
        
        # Get profession hub priorities
        print(f"\n  🎯 Profession Hub Priorities:")
        for profession in ["bio_engineer", "weaponsmith", "armorsmith"]:
            hub_destinations = self.travel_prioritizer.get_profession_hub_priorities(
                profession=profession,
                vendor_map_tracker=self.vendor_map_tracker
            )
            
            if hub_destinations:
                print(f"    {profession.title()}:")
                for destination in hub_destinations[:3]:  # Show top 3
                    print(f"      - {destination.destination_name} (Score: {destination.priority_score:.2f})")
    
    def _demo_buyer_logic(self):
        """Demo buyer logic and item requests."""
        print("\n🛒 Demo 6: Buyer Logic and Item Requests")
        print("-" * 50)
        
        # Create buyer requests
        buyer_requests = []
        for item in self.demo_requested_items:
            request_id = self.marketplace_discovery.create_buyer_request(
                item_name=item,
                max_price=50000,
                min_quantity=1,
                preferred_quality="good",
                urgency="medium"
            )
            buyer_requests.append(request_id)
            print(f"  ✅ Created buyer request: {item} (ID: {request_id})")
        
        # Find items for requests
        print(f"\n  🔍 Finding items for requests:")
        for request_id in buyer_requests:
            matching_items = self.marketplace_discovery.find_items_for_request(request_id)
            
            if matching_items:
                print(f"    Request {request_id}:")
                for item in matching_items[:3]:  # Show top 3 matches
                    print(f"      - {item.item_name}: {item.quantity}x @ {item.price} credits ({item.quality})")
            else:
                print(f"    Request {request_id}: No matching items found")
        
        # Get buyer statistics
        buyer_stats = self.marketplace_discovery.get_buyer_statistics()
        print(f"\n  📊 Buyer Statistics:")
        print(f"    - Total listings: {buyer_stats['total_listings']}")
        print(f"    - Total requests: {buyer_stats['total_requests']}")
        print(f"    - Pending requests: {buyer_stats['pending_requests']}")
        print(f"    - Found requests: {buyer_stats['found_requests']}")
        print(f"    - Purchased requests: {buyer_stats['purchased_requests']}")
        print(f"    - Average price: {buyer_stats['price_statistics']['average_price']:.0f} credits")
    
    def _demo_route_optimization(self):
        """Demo travel route optimization."""
        print("\n🛣️ Demo 7: Route Optimization")
        print("-" * 50)
        
        # Get travel destinations
        destinations = self.travel_prioritizer.prioritize_vendor_travel(
            vendor_map_tracker=self.vendor_map_tracker,
            marketplace_discovery=self.marketplace_discovery,
            requested_items=self.demo_requested_items
        )
        
        # Optimize routes with different strategies
        optimization_types = ["balanced", "distance", "reward"]
        
        for opt_type in optimization_types:
            route = self.travel_prioritizer.optimize_travel_route(
                destinations=destinations[:5],  # Use top 5 destinations
                optimization_type=opt_type,
                max_destinations=3
            )
            
            if route:
                print(f"  🛣️ {opt_type.title()} Route:")
                print(f"    - Route ID: {route.route_id}")
                print(f"    - Destinations: {len(route.destinations)}")
                print(f"    - Total distance: {route.total_distance:.0f} units")
                print(f"    - Estimated duration: {route.estimated_duration:.1f} minutes")
                print(f"    - Total reward: {route.total_reward:.0f} credits")
                print(f"    - Priority score: {route.priority_score:.2f}")
                print(f"    - Route type: {route.route_type}")
                
                print(f"    - Destinations:")
                for dest in route.destinations:
                    print(f"      * {dest.destination_name} (Score: {dest.priority_score:.2f})")
                print()
    
    def _demo_statistics_and_reporting(self):
        """Demo statistics and reporting functionality."""
        print("\n📊 Demo 8: Statistics and Reporting")
        print("-" * 50)
        
        # Get vendor map statistics
        vendor_stats = self.vendor_map_tracker.get_vendor_statistics()
        print(f"  🗺️ Vendor Map Statistics:")
        print(f"    - Total vendors: {vendor_stats['total_vendors']}")
        print(f"    - Total terminals: {vendor_stats['total_terminals']}")
        print(f"    - Total cities: {vendor_stats['total_cities']}")
        print(f"    - Active vendors: {vendor_stats['active_vendors']}")
        print(f"    - Active terminals: {vendor_stats['active_terminals']}")
        
        # Get travel statistics
        travel_stats = self.travel_prioritizer.get_travel_statistics()
        print(f"\n  🗺️ Travel Statistics:")
        print(f"    - Total destinations: {travel_stats['total_destinations']}")
        print(f"    - Total routes: {travel_stats['total_routes']}")
        print(f"    - High priority destinations: {travel_stats['destination_priority_distribution']['high']}")
        print(f"    - Medium priority destinations: {travel_stats['destination_priority_distribution']['medium']}")
        print(f"    - Low priority destinations: {travel_stats['destination_priority_distribution']['low']}")
        print(f"    - Average priority score: {travel_stats['average_statistics']['priority_score']:.2f}")
        print(f"    - Average distance: {travel_stats['average_statistics']['distance']:.0f} units")
        print(f"    - Average reward: {travel_stats['average_statistics']['reward']:.0f} credits")
        
        # Get marketplace statistics
        marketplace_stats = self.marketplace_discovery.get_buyer_statistics()
        print(f"\n  🛒 Marketplace Statistics:")
        print(f"    - Total listings: {marketplace_stats['total_listings']}")
        print(f"    - Total requests: {marketplace_stats['total_requests']}")
        print(f"    - Pending requests: {marketplace_stats['pending_requests']}")
        print(f"    - Found requests: {marketplace_stats['found_requests']}")
        print(f"    - Purchased requests: {marketplace_stats['purchased_requests']}")
        print(f"    - Marketplace analyses: {marketplace_stats['marketplace_analyses']}")
        print(f"    - OCR scans: {marketplace_stats['ocr_scans']}")
        
        # Item type distribution
        if marketplace_stats['item_type_distribution']:
            print(f"    - Item type distribution:")
            for item_type, count in marketplace_stats['item_type_distribution'].items():
                print(f"      * {item_type}: {count}")
    
    def generate_demo_report(self) -> Dict[str, Any]:
        """Generate a comprehensive demo report."""
        print("\n📋 Generating Demo Report...")
        
        # Collect all statistics
        vendor_stats = self.vendor_map_tracker.get_vendor_statistics()
        travel_stats = self.travel_prioritizer.get_travel_statistics()
        marketplace_stats = self.marketplace_discovery.get_buyer_statistics()
        
        # Create comprehensive report
        report = {
            "demo_info": {
                "batch": "080",
                "title": "Vendor Map Tracker + Marketplace Discovery",
                "timestamp": datetime.now().isoformat(),
                "demo_duration": "Comprehensive functionality demonstration"
            },
            "vendor_mapping": {
                "total_vendors": vendor_stats['total_vendors'],
                "total_terminals": vendor_stats['total_terminals'],
                "total_cities": vendor_stats['total_cities'],
                "active_vendors": vendor_stats['active_vendors'],
                "active_terminals": vendor_stats['active_terminals'],
                "profession_statistics": vendor_stats['profession_statistics'],
                "city_statistics": vendor_stats['city_statistics']
            },
            "travel_prioritization": {
                "total_destinations": travel_stats['total_destinations'],
                "total_routes": travel_stats['total_routes'],
                "destination_priority_distribution": travel_stats['destination_priority_distribution'],
                "route_type_distribution": travel_stats['route_type_distribution'],
                "average_statistics": travel_stats['average_statistics']
            },
            "marketplace_discovery": {
                "total_listings": marketplace_stats['total_listings'],
                "total_requests": marketplace_stats['total_requests'],
                "request_status": {
                    "pending": marketplace_stats['pending_requests'],
                    "found": marketplace_stats['found_requests'],
                    "purchased": marketplace_stats['purchased_requests']
                },
                "price_statistics": marketplace_stats['price_statistics'],
                "item_type_distribution": marketplace_stats['item_type_distribution'],
                "marketplace_analyses": marketplace_stats['marketplace_analyses'],
                "ocr_scans": marketplace_stats['ocr_scans']
            },
            "demo_features": {
                "vendor_discovery": "✅ Vendor and terminal discovery with metadata",
                "ocr_scanning": "✅ Terminal OCR scanning with item extraction",
                "marketplace_analysis": "✅ Marketplace analysis with price tracking",
                "travel_prioritization": "✅ Intelligent travel prioritization",
                "profession_flagging": "✅ Profession-based vendor flagging",
                "buyer_logic": "✅ Buyer requests and item matching",
                "route_optimization": "✅ Travel route optimization",
                "statistics_reporting": "✅ Comprehensive statistics and reporting"
            },
            "integration_points": {
                "travel_system": "Ready for integration with travel/navigation modules",
                "inventory_system": "Ready for integration with inventory management",
                "quest_system": "Ready for integration with quest tracking",
                "crafting_system": "Ready for integration with crafting modules"
            }
        }
        
        # Save report to file
        report_file = f"vendor_map_tracker_demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"  📄 Demo report saved to: {report_file}")
        return report


def main():
    """Main demo execution."""
    print("🎮 MS11 Batch 080 - Vendor Map Tracker + Marketplace Discovery Demo")
    print("=" * 80)
    
    # Initialize and run demo
    demo = VendorMapTrackerDemo()
    demo.run_full_demo()
    
    # Generate and save report
    report = demo.generate_demo_report()
    
    print("\n🎯 Demo Summary:")
    print("✅ Vendor discovery and mapping system")
    print("✅ Terminal OCR scanning with item extraction")
    print("✅ Marketplace analysis and price tracking")
    print("✅ Travel prioritization based on vendor data")
    print("✅ Profession-based vendor flagging")
    print("✅ Buyer logic and item request system")
    print("✅ Route optimization for vendor discovery")
    print("✅ Comprehensive statistics and reporting")
    
    print("\n🚀 Batch 080 - Vendor Map Tracker + Marketplace Discovery is ready for deployment!")


if __name__ == "__main__":
    main() 