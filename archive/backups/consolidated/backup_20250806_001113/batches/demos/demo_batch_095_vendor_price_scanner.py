"""Demo script for Batch 095 - Vendor/Bazaar Price Scanner.

This demo showcases the comprehensive vendor price scanning and analysis system:
1. OCR-based price detection from vendor windows
2. Price history tracking and analysis
3. Automated price recommendations
4. Discord alerts for underpriced items
5. Integration with existing bazaar module
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import the vendor price scanner modules
from core.vendor_price_scanner import vendor_price_scanner, ScannedPrice, PriceSource
from core.vendor_price_alerts import vendor_price_alerts, AlertPreferences


def demo_ocr_price_scanning():
    """Demo OCR-based price scanning functionality."""
    print("\n🔍 DEMO: OCR Price Scanning")
    print("=" * 50)
    
    # Simulate scanned prices (in real implementation, this would come from OCR)
    sample_scanned_prices = [
        ScannedPrice(
            item_name="Durindfire Crystal",
            price=50000,
            source=PriceSource.VENDOR,
            vendor_name="Coronet Vendor",
            location="Coronet, Corellia",
            timestamp=datetime.now().isoformat(),
            confidence=0.85,
            raw_text="Durindfire Crystal 50,000 credits"
        ),
        ScannedPrice(
            item_name="Spice Wine",
            price=150000,
            source=PriceSource.VENDOR,
            vendor_name="Coronet Vendor",
            location="Coronet, Corellia",
            timestamp=datetime.now().isoformat(),
            confidence=0.92,
            raw_text="Spice Wine 150,000 credits"
        ),
        ScannedPrice(
            item_name="Rare Gemstone",
            price=25000,
            source=PriceSource.VENDOR,
            vendor_name="Coronet Vendor",
            location="Coronet, Corellia",
            timestamp=datetime.now().isoformat(),
            confidence=0.78,
            raw_text="Rare Gemstone 25,000 credits"
        )
    ]
    
    print(f"✅ Scanned {len(sample_scanned_prices)} prices from vendor window")
    
    for price in sample_scanned_prices:
        print(f"  • {price.item_name}: {price.price:,} credits (confidence: {price.confidence:.1%})")
    
    # Save to price history
    vendor_price_scanner.save_price_history(sample_scanned_prices)
    print("✅ Prices saved to price history database")
    
    return sample_scanned_prices


def demo_price_analysis():
    """Demo price analysis and alert generation."""
    print("\n📊 DEMO: Price Analysis")
    print("=" * 50)
    
    # Create some sample scanned prices for analysis
    sample_prices = [
        ScannedPrice(
            item_name="Durindfire Crystal",
            price=50000,
            source=PriceSource.VENDOR,
            vendor_name="Test Vendor",
            location="Test Location",
            timestamp=datetime.now().isoformat(),
            confidence=0.85,
            raw_text="Durindfire Crystal 50,000 credits"
        ),
        ScannedPrice(
            item_name="Spice Wine",
            price=150000,
            source=PriceSource.VENDOR,
            vendor_name="Test Vendor",
            location="Test Location",
            timestamp=datetime.now().isoformat(),
            confidence=0.92,
            raw_text="Spice Wine 150,000 credits"
        )
    ]
    
    # Analyze prices for alerts
    alerts = vendor_price_scanner.analyze_prices(sample_prices)
    
    print(f"✅ Analyzed {len(sample_prices)} prices, found {len(alerts)} alerts")
    
    for alert in alerts:
        alert_type = "UNDERPRICED" if alert.alert_type == "underpriced" else "OVERPRICED"
        discount_text = f"{alert.discount_percentage:.1%} {'below' if alert.discount_percentage > 0 else 'above'} average"
        
        print(f"  🚨 {alert_type}: {alert.item_name}")
        print(f"     Current: {alert.current_price:,} credits")
        print(f"     Average: {alert.average_price:,.0f} credits")
        print(f"     Discount: {discount_text}")
        print(f"     Vendor: {alert.vendor_name}")
        print()


def demo_price_recommendations():
    """Demo price recommendation system."""
    print("\n💡 DEMO: Price Recommendations")
    print("=" * 50)
    
    # Get recommendations for sample items
    sample_items = ["Durindfire Crystal", "Spice Wine", "Rare Gemstone"]
    
    for item_name in sample_items:
        recommendation = vendor_price_scanner.get_price_recommendations(item_name)
        
        if recommendation:
            print(f"✅ {item_name}:")
            print(f"   Recommended Price: {recommendation.recommended_price:,} credits")
            print(f"   Confidence: {recommendation.confidence:.1%}")
            print(f"   Market Trend: {recommendation.market_trend}")
            print(f"   Reasoning: {recommendation.reasoning}")
            print()
        else:
            print(f"❌ {item_name}: Insufficient data for recommendation")
            print()


def demo_alert_system():
    """Demo Discord alert system."""
    print("\n🚨 DEMO: Alert System")
    print("=" * 50)
    
    # Test alert preferences
    print("📋 Alert Preferences:")
    alert_stats = vendor_price_alerts.get_alert_statistics()
    preferences = alert_stats.get("alert_preferences", {})
    
    for key, value in preferences.items():
        print(f"  • {key}: {value}")
    
    print()
    
    # Test sending an alert
    print("📤 Sending Test Alert...")
    alert_sent = vendor_price_alerts.send_price_alert(
        item_name="Test Item",
        current_price=50000,
        average_price=75000,
        discount_percentage=0.33,
        vendor_name="Test Vendor",
        location="Test Location"
    )
    
    if alert_sent:
        print("✅ Test alert sent successfully")
    else:
        print("❌ Test alert not sent (may be filtered by preferences)")
    
    print()
    
    # Show alert statistics
    print("📊 Alert Statistics:")
    stats = vendor_price_alerts.get_alert_statistics()
    print(f"  • Total Alerts: {stats.get('total_alerts', 0)}")
    print(f"  • Underpriced Alerts: {stats.get('underpriced_alerts', 0)}")
    print(f"  • Overpriced Alerts: {stats.get('overpriced_alerts', 0)}")
    print(f"  • Recent Alerts (24h): {stats.get('recent_alerts_24h', 0)}")
    print(f"  • Discord Enabled: {stats.get('discord_enabled', False)}")


def demo_configuration_management():
    """Demo configuration management."""
    print("\n⚙️ DEMO: Configuration Management")
    print("=" * 50)
    
    # Show current scanner statistics
    scanner_stats = vendor_price_scanner.get_statistics()
    print("📊 Scanner Statistics:")
    print(f"  • Items Tracked: {scanner_stats.get('total_items_tracked', 0)}")
    print(f"  • Price Entries: {scanner_stats.get('total_price_entries', 0)}")
    print(f"  • Alert Threshold: {scanner_stats.get('alert_threshold', 0.3):.1%}")
    print(f"  • Min Confidence: {scanner_stats.get('min_confidence', 0.7):.1%}")
    print()
    
    # Test updating alert preferences
    print("🔄 Updating Alert Preferences...")
    vendor_price_alerts.update_preferences(
        min_alert_price=2000,
        discount_threshold=0.25,
        enable_discord_alerts=True,
        enable_console_alerts=True
    )
    print("✅ Alert preferences updated")
    
    # Show updated preferences
    updated_stats = vendor_price_alerts.get_alert_statistics()
    updated_prefs = updated_stats.get("alert_preferences", {})
    print("📋 Updated Preferences:")
    for key, value in updated_prefs.items():
        print(f"  • {key}: {value}")


def demo_integration_with_existing_bazaar():
    """Demo integration with existing bazaar module."""
    print("\n🏪 DEMO: Bazaar Integration")
    print("=" * 50)
    
    try:
        # Import existing bazaar module
        from modules.bazaar import PriceTracker, VendorManager
        print("✅ Existing bazaar module available")
        
        # Show how vendor scanner complements existing bazaar functionality
        print("🔄 Integration Points:")
        print("  • Vendor Scanner: OCR-based price detection from vendor windows")
        print("  • Price Tracker: Historical price analysis and trends")
        print("  • Vendor Manager: Intelligent vendor interactions")
        print("  • Alert System: Real-time notifications for underpriced items")
        
        # Simulate data flow between modules
        print("\n📊 Data Flow Simulation:")
        print("  1. Vendor Scanner detects prices via OCR")
        print("  2. Prices saved to price history database")
        print("  3. Price Tracker analyzes trends and patterns")
        print("  4. Alert System checks for underpriced items")
        print("  5. Discord notifications sent for good deals")
        
    except ImportError as e:
        print(f"❌ Existing bazaar module not available: {e}")
        print("   (This is expected in demo environment)")


def demo_performance_and_scalability():
    """Demo performance and scalability features."""
    print("\n⚡ DEMO: Performance & Scalability")
    print("=" * 50)
    
    # Simulate scanning multiple vendors
    vendors = [
        ("Coronet Vendor", "Coronet, Corellia"),
        ("Theed Merchant", "Theed, Naboo"),
        ("Mos Eisley Trader", "Mos Eisley, Tatooine"),
        ("Bestine Vendor", "Bestine, Tatooine")
    ]
    
    print("🔄 Simulating multi-vendor scanning...")
    
    total_prices = 0
    total_alerts = 0
    
    for vendor_name, location in vendors:
        # Simulate scanning each vendor
        scanned_prices = [
            ScannedPrice(
                item_name=f"Item from {vendor_name}",
                price=50000 + (hash(vendor_name) % 100000),
                source=PriceSource.VENDOR,
                vendor_name=vendor_name,
                location=location,
                timestamp=datetime.now().isoformat(),
                confidence=0.8 + (hash(vendor_name) % 20) / 100,
                raw_text=f"Sample item from {vendor_name}"
            )
        ]
        
        vendor_price_scanner.save_price_history(scanned_prices)
        alerts = vendor_price_scanner.analyze_prices(scanned_prices)
        
        total_prices += len(scanned_prices)
        total_alerts += len(alerts)
        
        print(f"  ✅ {vendor_name}: {len(scanned_prices)} prices, {len(alerts)} alerts")
    
    print(f"\n📊 Total Performance:")
    print(f"  • Vendors Scanned: {len(vendors)}")
    print(f"  • Total Prices: {total_prices}")
    print(f"  • Total Alerts: {total_alerts}")
    print(f"  • Average Prices per Vendor: {total_prices / len(vendors):.1f}")


def demo_future_enhancements():
    """Demo potential future enhancements."""
    print("\n🚀 DEMO: Future Enhancements")
    print("=" * 50)
    
    enhancements = [
        "🤖 AI-powered price prediction using machine learning",
        "📱 Mobile app for real-time price alerts",
        "🌐 Web scraping integration for market data",
        "📊 Advanced analytics dashboard with charts and graphs",
        "🔗 Integration with crafting profitability calculator",
        "🎯 Automated buying/selling recommendations",
        "📈 Market trend analysis and forecasting",
        "🔄 Real-time price synchronization across servers"
    ]
    
    print("💡 Potential Future Features:")
    for enhancement in enhancements:
        print(f"  {enhancement}")
    
    print("\n📋 Implementation Roadmap:")
    print("  Phase 1: ✅ OCR price scanning (Current)")
    print("  Phase 2: 🔄 Advanced price analysis")
    print("  Phase 3: 📱 Mobile integration")
    print("  Phase 4: 🤖 AI-powered predictions")
    print("  Phase 5: 🌐 Multi-server support")


def main():
    """Run the comprehensive vendor price scanner demo."""
    print("🚀 BATCH 095 DEMO: Vendor/Bazaar Price Scanner")
    print("=" * 60)
    print("This demo showcases the comprehensive vendor price scanning and")
    print("analysis system for SWGDB, including OCR-based price detection,")
    print("automated alerts, and integration with existing bazaar modules.")
    print()
    
    # Run all demos
    demos = [
        demo_ocr_price_scanning,
        demo_price_analysis,
        demo_price_recommendations,
        demo_alert_system,
        demo_configuration_management,
        demo_integration_with_existing_bazaar,
        demo_performance_and_scalability,
        demo_future_enhancements
    ]
    
    for demo in demos:
        try:
            demo()
            time.sleep(1)  # Brief pause between demos
        except Exception as e:
            print(f"❌ Error in {demo.__name__}: {e}")
            print()
    
    print("\n🎉 BATCH 095 DEMO COMPLETED!")
    print("=" * 60)
    print("✅ Vendor Price Scanner System Features:")
    print("   • OCR-based price detection from vendor windows")
    print("   • Price history tracking and analysis")
    print("   • Automated price recommendations")
    print("   • Discord alerts for underpriced items")
    print("   • Integration with existing bazaar module")
    print("   • Real-time scanning and monitoring")
    print("   • Configurable alert thresholds and preferences")
    print("   • Comprehensive dashboard interface")
    print()
    print("🔗 Access the dashboard at: http://localhost:8000/vendor-price-scanner")
    print("📊 View statistics and manage alerts through the web interface")


if __name__ == "__main__":
    main() 