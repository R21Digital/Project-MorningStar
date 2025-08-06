"""Demo script for Batch 100 - Vendor Transaction Ledger System.

This demo showcases the comprehensive vendor transaction ledger system:
- Logging vendor transactions with detailed information
- Price analysis and trend detection
- Duplicate entry detection
- Underpriced/overpriced item identification
- Web dashboard integration
- Data filtering and export capabilities
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from core.vendor_transaction_ledger import (
    VendorTransactionLedger,
    TransactionType,
    ItemCategory,
    vendor_ledger,
    log_vendor_transaction
)


def create_sample_transactions():
    """Create sample vendor transactions for demonstration."""
    sample_data = [
        # Durindfire Crystal transactions
        {
            "item_name": "Durindfire Crystal",
            "price": 75000,
            "location": "tatooine_mos_eisley",
            "seller": "Crystal Vendor",
            "transaction_type": TransactionType.OBSERVED,
            "item_category": ItemCategory.RESOURCE,
            "quantity": 1,
            "notes": "High quality crystal",
            "confidence": 0.95,
            "raw_text": "Durindfire Crystal - 75,000 credits"
        },
        {
            "item_name": "Durindfire Crystal",
            "price": 70000,
            "location": "tatooine_mos_eisley",
            "seller": "Crystal Vendor",
            "transaction_type": TransactionType.OBSERVED,
            "item_category": ItemCategory.RESOURCE,
            "quantity": 1,
            "notes": "Lower price than usual",
            "confidence": 0.92,
            "raw_text": "Durindfire Crystal - 70,000 credits"
        },
        {
            "item_name": "Durindfire Crystal",
            "price": 80000,
            "location": "tatooine_mos_eisley",
            "seller": "Crystal Vendor",
            "transaction_type": TransactionType.SALE,
            "item_category": ItemCategory.RESOURCE,
            "quantity": 2,
            "notes": "Premium quality",
            "confidence": 0.98,
            "raw_text": "Durindfire Crystal x2 - 80,000 credits each"
        },
        # Spice Wine transactions
        {
            "item_name": "Spice Wine",
            "price": 120000,
            "location": "tatooine_mos_eisley",
            "seller": "Wine Merchant",
            "transaction_type": TransactionType.SALE,
            "item_category": ItemCategory.CONSUMABLE,
            "quantity": 1,
            "notes": "Premium vintage",
            "confidence": 0.98,
            "raw_text": "Spice Wine - 120,000 credits"
        },
        {
            "item_name": "Spice Wine",
            "price": 110000,
            "location": "tatooine_mos_eisley",
            "seller": "Wine Merchant",
            "transaction_type": TransactionType.OBSERVED,
            "item_category": ItemCategory.CONSUMABLE,
            "quantity": 1,
            "notes": "Standard vintage",
            "confidence": 0.94,
            "raw_text": "Spice Wine - 110,000 credits"
        },
        # Weapon transactions
        {
            "item_name": "Rifle",
            "price": 15000,
            "location": "tatooine_mos_eisley",
            "seller": "Weapon Shop",
            "transaction_type": TransactionType.PURCHASE,
            "item_category": ItemCategory.WEAPON,
            "quantity": 1,
            "notes": "Standard rifle",
            "confidence": 0.96,
            "raw_text": "Rifle - 15,000 credits"
        },
        {
            "item_name": "Pistol",
            "price": 8000,
            "location": "tatooine_mos_eisley",
            "seller": "Weapon Shop",
            "transaction_type": TransactionType.PURCHASE,
            "item_category": ItemCategory.WEAPON,
            "quantity": 1,
            "notes": "Standard pistol",
            "confidence": 0.93,
            "raw_text": "Pistol - 8,000 credits"
        },
        # Supply transactions
        {
            "item_name": "Basic Supply",
            "price": 100,
            "location": "tatooine_mos_eisley",
            "seller": "General Store",
            "transaction_type": TransactionType.OBSERVED,
            "item_category": ItemCategory.SUPPLY,
            "quantity": 25,
            "notes": "Basic supplies",
            "confidence": 0.99,
            "raw_text": "Basic Supply x25 - 100 credits each"
        },
        {
            "item_name": "Local Item",
            "price": 200,
            "location": "tatooine_mos_eisley",
            "seller": "General Store",
            "transaction_type": TransactionType.OBSERVED,
            "item_category": ItemCategory.SUPPLY,
            "quantity": 15,
            "notes": "Local specialty",
            "confidence": 0.97,
            "raw_text": "Local Item x15 - 200 credits each"
        }
    ]
    
    return sample_data


def demo_transaction_logging():
    """Demonstrate transaction logging functionality."""
    print("🔍 DEMO: Transaction Logging")
    print("=" * 50)
    
    # Create a temporary ledger for demo
    temp_dir = tempfile.mkdtemp()
    ledger_path = Path(temp_dir) / "demo_ledger.json"
    ledger = VendorTransactionLedger(str(ledger_path))
    
    # Log sample transactions
    sample_data = create_sample_transactions()
    
    print(f"Logging {len(sample_data)} sample transactions...")
    for i, tx_data in enumerate(sample_data, 1):
        transaction = ledger.log_transaction(
            item_name=tx_data["item_name"],
            price=tx_data["price"],
            location=tx_data["location"],
            seller=tx_data["seller"],
            transaction_type=tx_data["transaction_type"],
            item_category=tx_data["item_category"],
            quantity=tx_data["quantity"],
            notes=tx_data["notes"],
            confidence=tx_data["confidence"],
            raw_text=tx_data["raw_text"]
        )
        
        print(f"  {i:2d}. {transaction.item_name:20s} @ {transaction.price:8,} credits from {transaction.seller}")
    
    print(f"\n✅ Successfully logged {len(ledger.transactions)} transactions")
    print(f"📊 Created {len(ledger.price_analyses)} price analyses")
    print(f"🔄 Detected {len(ledger.duplicate_entries)} duplicate entries")
    
    return ledger


def demo_price_analysis():
    """Demonstrate price analysis functionality."""
    print("\n📈 DEMO: Price Analysis")
    print("=" * 50)
    
    ledger = demo_transaction_logging()
    
    # Show price analyses
    print("\nPrice Analysis Results:")
    for item_name, analysis in ledger.price_analyses.items():
        print(f"\n📦 {item_name}:")
        print(f"   Average Price: {analysis.average_price:,.0f} credits")
        print(f"   Median Price:  {analysis.median_price:,.0f} credits")
        print(f"   Price Range:   {analysis.min_price:,} - {analysis.max_price:,} credits")
        print(f"   Price Count:   {analysis.price_count} transactions")
        print(f"   Price Trend:   {analysis.price_trend.upper()}")
        print(f"   Underpriced Threshold: {analysis.underpriced_threshold:,} credits")
        print(f"   Overpriced Threshold:  {analysis.overpriced_threshold:,} credits")
    
    # Show price comparisons
    print("\n🔍 Price Comparison Details:")
    for item_name in ["Durindfire Crystal", "Spice Wine"]:
        comparison = ledger.get_price_comparison(item_name)
        if comparison:
            print(f"\n📊 {item_name} Price Analysis:")
            print(f"   Total Transactions: {comparison['total_transactions']}")
            print(f"   Price Range: {comparison['price_range']:,} credits")
            print(f"   Price Volatility: {comparison['price_volatility']:.2f}")
            print("   Seller Averages:")
            for seller, avg_price in comparison['seller_averages'].items():
                print(f"     {seller}: {avg_price:,.0f} credits")


def demo_duplicate_detection():
    """Demonstrate duplicate detection functionality."""
    print("\n🔄 DEMO: Duplicate Detection")
    print("=" * 50)
    
    ledger = demo_transaction_logging()
    
    # Log a duplicate transaction
    print("\nLogging duplicate transaction...")
    duplicate_tx = ledger.log_transaction(
        item_name="Durindfire Crystal",
        price=75000,
        location="tatooine_mos_eisley",
        seller="Crystal Vendor",
        transaction_type=TransactionType.OBSERVED,
        item_category=ItemCategory.RESOURCE,
        quantity=1,
        notes="Duplicate entry",
        confidence=0.95,
        raw_text="Durindfire Crystal - 75,000 credits"
    )
    
    print(f"✅ Logged duplicate transaction: {duplicate_tx.item_name}")
    
    # Show duplicate entries
    if ledger.duplicate_entries:
        print(f"\n🔄 Detected {len(ledger.duplicate_entries)} duplicate entries:")
        for i, dup in enumerate(ledger.duplicate_entries, 1):
            print(f"\n  {i}. Duplicate Type: {dup.duplicate_type.upper()}")
            print(f"     Similarity Score: {dup.similarity_score:.3f}")
            print(f"     Original: {dup.original_transaction.item_name} @ {dup.original_transaction.price:,} credits")
            print(f"     Duplicate: {dup.duplicate_transaction.item_name} @ {dup.duplicate_transaction.price:,} credits")
            print(f"     Time Difference: {abs((datetime.fromisoformat(dup.duplicate_transaction.timestamp) - datetime.fromisoformat(dup.original_transaction.timestamp)).total_seconds()):.0f} seconds")
    else:
        print("✅ No duplicate entries detected")


def demo_underpriced_overpriced_detection():
    """Demonstrate underpriced and overpriced item detection."""
    print("\n💰 DEMO: Underpriced/Overpriced Detection")
    print("=" * 50)
    
    ledger = demo_transaction_logging()
    
    # Log underpriced transaction
    print("\nLogging underpriced transaction...")
    underpriced_tx = ledger.log_transaction(
        item_name="Durindfire Crystal",
        price=50000,  # Underpriced
        location="tatooine_mos_eisley",
        seller="Crystal Vendor",
        transaction_type=TransactionType.OBSERVED,
        item_category=ItemCategory.RESOURCE,
        quantity=1,
        notes="Great deal!",
        confidence=0.98,
        raw_text="Durindfire Crystal - 50,000 credits"
    )
    
    # Log overpriced transaction
    print("Logging overpriced transaction...")
    overpriced_tx = ledger.log_transaction(
        item_name="Spice Wine",
        price=150000,  # Overpriced
        location="tatooine_mos_eisley",
        seller="Wine Merchant",
        transaction_type=TransactionType.OBSERVED,
        item_category=ItemCategory.CONSUMABLE,
        quantity=1,
        notes="Expensive!",
        confidence=0.96,
        raw_text="Spice Wine - 150,000 credits"
    )
    
    # Show underpriced items
    underpriced = ledger.get_underpriced_items()
    if underpriced:
        print(f"\n🟢 Found {len(underpriced)} underpriced items:")
        for tx, analysis in underpriced:
            discount = ((analysis.average_price - tx.price) / analysis.average_price) * 100
            print(f"   💎 {tx.item_name}: {tx.price:,} credits (vs avg {analysis.average_price:,.0f}) - {discount:.1f}% discount")
    else:
        print("✅ No underpriced items found")
    
    # Show overpriced items
    overpriced = ledger.get_overpriced_items()
    if overpriced:
        print(f"\n🔴 Found {len(overpriced)} overpriced items:")
        for tx, analysis in overpriced:
            markup = ((tx.price - analysis.average_price) / analysis.average_price) * 100
            print(f"   💰 {tx.item_name}: {tx.price:,} credits (vs avg {analysis.average_price:,.0f}) - {markup:.1f}% markup")
    else:
        print("✅ No overpriced items found")


def demo_filtering_and_search():
    """Demonstrate filtering and search functionality."""
    print("\n🔍 DEMO: Filtering and Search")
    print("=" * 50)
    
    ledger = demo_transaction_logging()
    
    # Test various filters
    filters = [
        ("Item Name", {"item_name": "Durindfire"}),
        ("Seller", {"seller": "Crystal"}),
        ("Category", {"item_category": ItemCategory.WEAPON}),
        ("Price Range", {"min_price": 10000, "max_price": 20000}),
        ("Transaction Type", {"transaction_type": TransactionType.SALE}),
    ]
    
    for filter_name, filter_params in filters:
        filtered = ledger.get_transactions(**filter_params)
        print(f"\n📋 {filter_name} Filter ({len(filtered)} results):")
        for tx in filtered[:3]:  # Show first 3 results
            print(f"   • {tx.item_name:20s} @ {tx.price:8,} credits from {tx.seller}")
        if len(filtered) > 3:
            print(f"   ... and {len(filtered) - 3} more")


def demo_statistics():
    """Demonstrate statistics generation."""
    print("\n📊 DEMO: Statistics Generation")
    print("=" * 50)
    
    ledger = demo_transaction_logging()
    
    stats = ledger.get_statistics()
    
    print("📈 Ledger Statistics:")
    print(f"   Total Transactions: {stats['total_transactions']}")
    print(f"   Unique Items: {stats['unique_items']}")
    print(f"   Unique Sellers: {stats['unique_sellers']}")
    print(f"   Unique Locations: {stats['unique_locations']}")
    print(f"   Duplicate Entries: {stats['duplicate_entries']}")
    print(f"   Price Analyses: {stats['price_analyses']}")
    
    print("\n📋 Transaction Type Breakdown:")
    for tx_type, count in stats['transaction_types'].items():
        print(f"   {tx_type.title()}: {count}")
    
    print("\n📦 Item Category Breakdown:")
    for category, count in stats['item_categories'].items():
        print(f"   {category.title()}: {count}")
    
    print("\n💰 Price Statistics:")
    price_stats = stats['price_statistics']
    print(f"   Average Price: {price_stats['average_price']:,.0f} credits")
    print(f"   Min Price: {price_stats['min_price']:,} credits")
    print(f"   Max Price: {price_stats['max_price']:,} credits")
    print(f"   Total Value: {price_stats['total_value']:,} credits")


def demo_web_dashboard_integration():
    """Demonstrate web dashboard integration."""
    print("\n🌐 DEMO: Web Dashboard Integration")
    print("=" * 50)
    
    print("The vendor transaction ledger integrates with the web dashboard at:")
    print("   📍 URL: http://localhost:8000/market-insights/vendor-history")
    print("   📊 Features:")
    print("      • Real-time transaction display")
    print("      • Advanced filtering and search")
    print("      • Price analysis visualization")
    print("      • Duplicate entry highlighting")
    print("      • Underpriced/overpriced alerts")
    print("      • Export functionality")
    print("      • Sortable columns")
    print("      • Responsive design")
    
    print("\n🔗 API Endpoints Available:")
    api_endpoints = [
        "/api/vendor-ledger/statistics",
        "/api/vendor-ledger/transactions",
        "/api/vendor-ledger/underpriced",
        "/api/vendor-ledger/overpriced",
        "/api/vendor-ledger/duplicates",
        "/api/vendor-ledger/price-analysis/<item_name>",
        "/api/vendor-ledger/log-transaction"
    ]
    
    for endpoint in api_endpoints:
        print(f"   • {endpoint}")


def demo_data_export():
    """Demonstrate data export functionality."""
    print("\n📤 DEMO: Data Export")
    print("=" * 50)
    
    ledger = demo_transaction_logging()
    
    # Export filtered data
    crystal_transactions = ledger.get_transactions(item_name="Durindfire Crystal")
    
    export_data = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "filter": "Durindfire Crystal transactions",
            "total_transactions": len(crystal_transactions)
        },
        "transactions": [
            {
                "item_name": tx.item_name,
                "price": tx.price,
                "location": tx.location,
                "seller": tx.seller,
                "timestamp": tx.timestamp,
                "transaction_type": tx.transaction_type.value,
                "item_category": tx.item_category.value,
                "quantity": tx.quantity,
                "notes": tx.notes,
                "confidence": tx.confidence
            }
            for tx in crystal_transactions
        ]
    }
    
    # Save to file
    export_file = Path("demo_export.json")
    with open(export_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(crystal_transactions)} transactions to {export_file}")
    print(f"📄 File size: {export_file.stat().st_size:,} bytes")
    
    # Show export preview
    print("\n📋 Export Preview:")
    for i, tx in enumerate(crystal_transactions[:3], 1):
        print(f"   {i}. {tx.item_name} @ {tx.price:,} credits from {tx.seller}")
    if len(crystal_transactions) > 3:
        print(f"   ... and {len(crystal_transactions) - 3} more")


def demo_integration_with_existing_systems():
    """Demonstrate integration with existing vendor systems."""
    print("\n🔗 DEMO: Integration with Existing Systems")
    print("=" * 50)
    
    print("The vendor transaction ledger integrates with existing systems:")
    
    integrations = [
        ("Vendor Price Scanner", "core/vendor_price_scanner.py", "OCR-based price detection"),
        ("Bazaar Module", "modules/bazaar/vendor_manager.py", "Vendor interaction management"),
        ("Vendor Cache", "data/vendors/vendors_cache.json", "Existing vendor data"),
        ("Web Dashboard", "dashboard/app.py", "Flask-based web interface"),
        ("Logging System", "utils/logging_utils.py", "Event logging and tracking")
    ]
    
    for system, file_path, description in integrations:
        print(f"\n🔧 {system}:")
        print(f"   📁 File: {file_path}")
        print(f"   📝 Description: {description}")
    
    print("\n✅ Integration Benefits:")
    benefits = [
        "Seamless data flow between systems",
        "Unified vendor interaction tracking",
        "Enhanced price analysis capabilities",
        "Comprehensive market insights",
        "Real-time dashboard updates"
    ]
    
    for benefit in benefits:
        print(f"   • {benefit}")


def main():
    """Run the comprehensive vendor transaction ledger demo."""
    print("🚀 BATCH 100 DEMO: Vendor Transaction Ledger System")
    print("=" * 60)
    print("This demo showcases the comprehensive vendor transaction ledger system:")
    print("• Transaction logging with detailed metadata")
    print("• Price analysis and trend detection")
    print("• Duplicate entry detection")
    print("• Underpriced/overpriced item identification")
    print("• Web dashboard integration")
    print("• Data filtering and export capabilities")
    print("• Integration with existing vendor systems")
    print()
    
    try:
        # Run all demos
        demo_transaction_logging()
        demo_price_analysis()
        demo_duplicate_detection()
        demo_underpriced_overpriced_detection()
        demo_filtering_and_search()
        demo_statistics()
        demo_web_dashboard_integration()
        demo_data_export()
        demo_integration_with_existing_systems()
        
        print("\n" + "=" * 60)
        print("✅ BATCH 100 DEMO COMPLETED SUCCESSFULLY!")
        print("\n🎯 Key Features Demonstrated:")
        features = [
            "Comprehensive transaction logging",
            "Real-time price analysis",
            "Intelligent duplicate detection",
            "Market price anomaly detection",
            "Advanced filtering and search",
            "Detailed statistics generation",
            "Web dashboard integration",
            "Data export capabilities",
            "System integration"
        ]
        
        for i, feature in enumerate(features, 1):
            print(f"   {i:2d}. {feature}")
        
        print("\n🌐 Access the web dashboard at:")
        print("   http://localhost:8000/market-insights/vendor-history")
        
        print("\n📚 Next Steps:")
        print("   • Configure vendor scanning automation")
        print("   • Set up price alert notifications")
        print("   • Customize duplicate detection thresholds")
        print("   • Implement cross-vendor price comparisons")
        print("   • Add trend analysis and predictions")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 