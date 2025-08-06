#!/usr/bin/env python3
"""Demo script for Batch 061 - Auction House Integration (Vendor/Bazaar Logic)."""

import json
import time
from pathlib import Path
from typing import Dict, List, Any

from modules.bazaar import VendorManager, PriceTracker, BazaarDetector
from utils.logging_utils import log_event


def demo_bazaar_detection():
    """Demo vendor terminal detection."""
    print("\n" + "="*60)
    print("DEMO: Vendor Terminal Detection")
    print("="*60)
    
    detector = BazaarDetector()
    
    # Simulate vendor terminal detection (without OCR)
    print("🔍 Scanning for vendor terminals...")
    print("   (Note: OCR not available, using simulated detection)")
    
    # Simulate detection results
    print("✅ Simulated vendor terminal detection:")
    print("   1. vendor terminal at (100, 150)")
    print("      Confidence: 0.85")
    print("      Text: Vendor Terminal - Sell Items")
    
    print("\n🔍 Scanning for vendor interface elements...")
    print("✅ Simulated vendor interface detected:")
    print("   Sell button at: (400, 300)")
    print("   Buy button at: (500, 300)")
    print("   Inventory area: (50, 100, 300, 400)")
    print("   Price display area: (400, 100, 300, 400)")


def demo_price_tracking():
    """Demo price tracking functionality."""
    print("\n" + "="*60)
    print("DEMO: Price Tracking")
    print("="*60)
    
    tracker = PriceTracker()
    
    # Simulate some sales
    test_sales = [
        ("Bantha Hide", 5000),
        ("Bantha Hide", 5200),
        ("Bantha Hide", 4800),
        ("Krayt Scale", 15000),
        ("Krayt Scale", 16000),
        ("Bolma Meat", 800),
        ("Bolma Meat", 900),
        ("Bolma Meat", 850),
        ("Ancient Artifact", 50000),
        ("Rare Crystal", 25000)
    ]
    
    print("💰 Recording sample sales...")
    for item_name, price in test_sales:
        tracker.add_sale(item_name, price)
        print(f"   Sold {item_name} for {price:,} credits")
    
    # Test price statistics
    print("\n📊 Price Statistics:")
    for item_name in ["Bantha Hide", "Krayt Scale", "Bolma Meat", "Ancient Artifact"]:
        stats = tracker.get_item_price_stats(item_name)
        if stats:
            print(f"   {item_name}:")
            print(f"     Average: {stats.average_price:,.0f} credits")
            print(f"     Range: {stats.min_price:,} - {stats.max_price:,}")
            print(f"     Total sales: {stats.total_sales}")
    
    # Test recommended pricing
    print("\n💡 Recommended Prices:")
    for item_name in ["Bantha Hide", "Krayt Scale", "Bolma Meat", "New Item"]:
        recommended = tracker.get_recommended_price(item_name)
        print(f"   {item_name}: {recommended:,} credits")
    
    # Test selling decisions
    print("\n🤔 Selling Decisions:")
    test_items = [
        ("Bantha Hide", 4500),  # Below average
        ("Bantha Hide", 5500),  # Above average
        ("Krayt Scale", 12000), # Below average
        ("New Item", 3000),     # Below threshold
        ("Valuable Item", 8000)  # Above threshold
    ]
    
    for item_name, price in test_items:
        should_sell = tracker.should_sell_item(item_name, price, 5000)
        decision = "✅ SELL" if should_sell else "❌ KEEP"
        print(f"   {item_name} at {price:,}: {decision}")
    
    # Show global statistics
    global_stats = tracker.get_global_statistics()
    print(f"\n📈 Global Statistics:")
    print(f"   Total sales: {global_stats['total_sales']}")
    print(f"   Total revenue: {global_stats['total_revenue']:,} credits")
    print(f"   Average sale price: {global_stats['average_sale_price']:,.0f} credits")


def demo_vendor_operations():
    """Demo vendor operations."""
    print("\n" + "="*60)
    print("DEMO: Vendor Operations")
    print("="*60)
    
    vendor = VendorManager()
    
    # Test auto-sell junk
    print("🛍️ Testing auto-sell junk functionality...")
    
    # Simulate inventory scan
    print("   Scanning inventory for saleable items...")
    
    # In a real scenario, this would use OCR to read inventory
    # For demo purposes, we'll simulate the process
    print("   Found items in inventory:")
    print("     - Bantha Hide x3 (estimated: 5,200 credits)")
    print("     - Bolma Meat x5 (estimated: 850 credits)")
    print("     - Ancient Artifact x1 (estimated: 50,000 credits)")
    print("     - Junk Item x10 (estimated: 100 credits)")
    
    # Simulate selling decisions
    print("\n   Evaluating items for sale:")
    print("     ✅ Bantha Hide: Above threshold, good price")
    print("     ❌ Bolma Meat: Below threshold")
    print("     ✅ Ancient Artifact: Above threshold, valuable")
    print("     ❌ Junk Item: Below threshold")
    
    # Simulate transactions
    print("\n   Executing sales...")
    transactions = [
        {"item": "Bantha Hide", "quantity": 3, "price": 5200},
        {"item": "Ancient Artifact", "quantity": 1, "price": 50000}
    ]
    
    total_revenue = 0
    for tx in transactions:
        revenue = tx["price"] * tx["quantity"]
        total_revenue += revenue
        print(f"     Sold {tx['item']} x{tx['quantity']} for {revenue:,} credits")
    
    print(f"\n💰 Total revenue: {total_revenue:,} credits")
    
    # Test buying functionality
    print("\n🛒 Testing buying functionality...")
    target_items = ["Health Pack", "Stimpack", "Energy Cell"]
    max_spend = 1000
    
    print(f"   Target items: {', '.join(target_items)}")
    print(f"   Max spend: {max_spend:,} credits")
    
    # Simulate purchases
    purchases = [
        {"item": "Health Pack", "price": 100},
        {"item": "Stimpack", "price": 50},
        {"item": "Energy Cell", "price": 25}
    ]
    
    total_spent = 0
    for purchase in purchases:
        if total_spent + purchase["price"] <= max_spend:
            total_spent += purchase["price"]
            print(f"     Bought {purchase['item']} for {purchase['price']} credits")
    
    print(f"\n💸 Total spent: {total_spent:,} credits")


def demo_configuration():
    """Demo bazaar configuration."""
    print("\n" + "="*60)
    print("DEMO: Bazaar Configuration")
    print("="*60)
    
    config_path = Path("config/bazaar_config.json")
    
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as fh:
            config = json.load(fh)
        
        print("📋 Current Configuration:")
        print(f"   Auto-sell junk: {config.get('auto_sell_junk', False)}")
        print(f"   Min value threshold: {config.get('loot_min_value_threshold', 0):,} credits")
        print(f"   Excluded items: {len(config.get('excluded_items', []))} items")
        print(f"   Price tracking: {config.get('price_tracking', {}).get('enabled', False)}")
        print(f"   Auto-buy: {config.get('auto_buy', {}).get('enabled', False)}")
        
        print("\n   Terminal keywords:")
        for keyword in config.get("vendor_detection", {}).get("terminal_keywords", []):
            print(f"     - {keyword}")
        
        print("\n   Excluded items:")
        for item in config.get("excluded_items", [])[:5]:  # Show first 5
            print(f"     - {item}")
        if len(config.get("excluded_items", [])) > 5:
            print(f"     ... and {len(config.get('excluded_items', [])) - 5} more")
    else:
        print("❌ Configuration file not found")


def demo_space_station_integration():
    """Demo space station vendor integration."""
    print("\n" + "="*60)
    print("DEMO: Space Station Vendor Integration")
    print("="*60)
    
    print("🚀 Space station vendor features:")
    print("   ✅ Vendor detection via OCR")
    print("   ✅ Price tracking across stations")
    print("   ✅ Travel threshold logic")
    print("   ✅ Preferred station selection")
    print("   ✅ Cross-station price comparison")
    
    print("\n   Future expansion features:")
    print("   🔮 Advanced price analytics")
    print("   🔮 Market trend analysis")
    print("   🔮 Automated arbitrage")
    print("   🔮 Supply/demand tracking")


def main():
    """Run the bazaar integration demo."""
    print("🎮 BATCH 061 - Auction House Integration Demo")
    print("="*60)
    print("This demo showcases the vendor/bazaar logic implementation")
    print("including terminal detection, price tracking, and intelligent selling.")
    
    try:
        # Run demos
        demo_configuration()
        demo_bazaar_detection()
        demo_price_tracking()
        demo_vendor_operations()
        demo_space_station_integration()
        
        print("\n" + "="*60)
        print("✅ Demo completed successfully!")
        print("="*60)
        
        print("\n📝 Key Features Implemented:")
        print("   ✅ Vendor/Bazaar terminal detection via OCR")
        print("   ✅ Intelligent price tracking and analysis")
        print("   ✅ Auto-sell junk with configurable thresholds")
        print("   ✅ Excluded items management")
        print("   ✅ Price history and trend analysis")
        print("   ✅ Future space station vendor support")
        
        print("\n🔧 Configuration:")
        print("   - config/bazaar_config.json: Main configuration")
        print("   - data/bazaar/price_history.json: Price tracking data")
        print("   - modules/bazaar/: Core implementation")
        
        print("\n⚠️  Note:")
        print("   OCR functionality requires Tesseract installation.")
        print("   Demo uses simulated data when OCR is unavailable.")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 