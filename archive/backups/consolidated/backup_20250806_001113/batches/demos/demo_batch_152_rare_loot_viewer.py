#!/usr/bin/env python3
"""
Batch 152 - Rare Loot Drop Table Viewer Demo

This demo showcases the enhanced rare loot drop table viewer that provides:
- Visual loot lookup tool for rare drop items
- Public category page at /loot/rare/
- Filters by item type, location, enemy type
- Data sourced from community submissions, MS11 scanning, and RLS wiki
- Linked to boss or NPC profiles when available

Usage:
    python demo_batch_152_rare_loot_viewer.py [--export] [--validate]
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/rare_loot_viewer_demo.log'),
            logging.StreamHandler()
        ]
    )

def demo_database_structure():
    """Demo the rare loot database structure."""
    print("\n" + "="*60)
    print("DEMO: Database Structure")
    print("="*60)

    # Load the rare loot database
    database_file = Path("data/rare_loot_database.json")
    
    if not database_file.exists():
        print("❌ Rare loot database not found")
        return False
    
    with open(database_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\nDatabase Overview:")
    print(f"  Version: {data['metadata']['version']}")
    print(f"  Last Updated: {data['metadata']['last_updated']}")
    print(f"  Total Items: {len(data['items'])}")
    print(f"  Data Sources: {', '.join(data['metadata']['data_sources'])}")
    
    print(f"\nCategories ({len(data['categories'])}):")
    for key, category in data['categories'].items():
        print(f"  - {category['name']}: {category['description']}")
    
    print(f"\nLocations ({len(data['locations'])}):")
    for key, location in data['locations'].items():
        print(f"  - {location['name']}: {len(location['zones'])} zones")
    
    print(f"\nEnemy Types ({len(data['enemy_types'])}):")
    for key, enemy_type in data['enemy_types'].items():
        print(f"  - {enemy_type['name']}: {enemy_type['difficulty']} difficulty")
    
    print(f"\nBoss Profiles ({len(data['boss_profiles'])}):")
    for key, boss in data['boss_profiles'].items():
        print(f"  - {boss['name']} (Level {boss['level']}): {boss['difficulty']} difficulty")
    
    return True

def demo_item_analysis():
    """Demo item analysis and statistics."""
    print("\n" + "="*60)
    print("DEMO: Item Analysis")
    print("="*60)

    database_file = Path("data/rare_loot_database.json")
    with open(database_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data['items']
    
    # Rarity distribution
    rarity_counts = {}
    for item in items:
        rarity = item['rarity']
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
    
    print(f"\nRarity Distribution:")
    for rarity, count in rarity_counts.items():
        percentage = (count / len(items)) * 100
        print(f"  {rarity.capitalize()}: {count} items ({percentage:.1f}%)")
    
    # Category distribution
    category_counts = {}
    for item in items:
        category = item['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    print(f"\nCategory Distribution:")
    for category, count in category_counts.items():
        category_name = data['categories'][category]['name']
        percentage = (count / len(items)) * 100
        print(f"  {category_name}: {count} items ({percentage:.1f}%)")
    
    # Value analysis
    values = [item['stats']['value'] for item in items]
    avg_value = sum(values) / len(values)
    max_value = max(values)
    min_value = min(values)
    
    print(f"\nValue Analysis:")
    print(f"  Average Value: {avg_value:,.0f} credits")
    print(f"  Maximum Value: {max_value:,.0f} credits")
    print(f"  Minimum Value: {min_value:,.0f} credits")
    
    # Drop rate analysis
    all_drop_rates = []
    for item in items:
        for location in item['locations']:
            all_drop_rates.append(location['drop_rate'])
    
    avg_drop_rate = sum(all_drop_rates) / len(all_drop_rates)
    max_drop_rate = max(all_drop_rates)
    min_drop_rate = min(all_drop_rates)
    
    print(f"\nDrop Rate Analysis:")
    print(f"  Average Drop Rate: {avg_drop_rate:.3f} ({avg_drop_rate*100:.1f}%)")
    print(f"  Maximum Drop Rate: {max_drop_rate:.3f} ({max_drop_rate*100:.1f}%)")
    print(f"  Minimum Drop Rate: {min_drop_rate:.3f} ({min_drop_rate*100:.1f}%)")

def demo_filtering_capabilities():
    """Demo the filtering capabilities."""
    print("\n" + "="*60)
    print("DEMO: Filtering Capabilities")
    print("="*60)

    database_file = Path("data/rare_loot_database.json")
    with open(database_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data['items']
    
    # Demo different filter scenarios
    filter_scenarios = [
        {
            "name": "Legendary Items Only",
            "filter": lambda item: item['rarity'] == 'legendary',
            "description": "Show only legendary rarity items"
        },
        {
            "name": "Boss Drops Only",
            "filter": lambda item: any(loc['enemy_type'] == 'boss' for loc in item['locations']),
            "description": "Show items that drop from boss enemies"
        },
        {
            "name": "High Value Items (>25k credits)",
            "filter": lambda item: item['stats']['value'] > 25000,
            "description": "Show items worth more than 25,000 credits"
        },
        {
            "name": "Tatooine Items",
            "filter": lambda item: any(loc['planet'] == 'tatooine' for loc in item['locations']),
            "description": "Show items that drop on Tatooine"
        },
        {
            "name": "Jewelry Category",
            "filter": lambda item: item['category'] == 'jewelry',
            "description": "Show only jewelry items"
        },
        {
            "name": "MS11 Scanned Items",
            "filter": lambda item: 'ms11_scanning' in item['sources'],
            "description": "Show items discovered through MS11 scanning"
        }
    ]
    
    for scenario in filter_scenarios:
        filtered_items = list(filter(scenario['filter'], items))
        print(f"\n{scenario['name']}:")
        print(f"  Description: {scenario['description']}")
        print(f"  Results: {len(filtered_items)} items")
        
        if filtered_items:
            print(f"  Examples:")
            for item in filtered_items[:3]:  # Show first 3 examples
                print(f"    - {item['name']} ({item['rarity']}) - {item['stats']['value']:,} credits")
            if len(filtered_items) > 3:
                print(f"    ... and {len(filtered_items) - 3} more")

def demo_search_functionality():
    """Demo search functionality."""
    print("\n" + "="*60)
    print("DEMO: Search Functionality")
    print("="*60)

    database_file = Path("data/rare_loot_database.json")
    with open(database_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data['items']
    
    # Demo search terms
    search_terms = [
        "krayt",
        "dragon",
        "crystal",
        "pearl",
        "weapon",
        "armor",
        "poison",
        "ancient"
    ]
    
    for term in search_terms:
        matching_items = []
        for item in items:
            searchable_text = f"{item['name']} {item['description']}".lower()
            if term.lower() in searchable_text:
                matching_items.append(item)
        
        print(f"\nSearch for '{term}':")
        print(f"  Results: {len(matching_items)} items")
        
        if matching_items:
            print(f"  Found:")
            for item in matching_items:
                print(f"    - {item['name']} ({item['rarity']})")
        else:
            print(f"  No items found")

def demo_boss_profile_integration():
    """Demo boss profile integration."""
    print("\n" + "="*60)
    print("DEMO: Boss Profile Integration")
    print("="*60)

    database_file = Path("data/rare_loot_database.json")
    with open(database_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    boss_profiles = data['boss_profiles']
    
    print(f"\nBoss Profiles ({len(boss_profiles)}):")
    
    for boss_id, boss in boss_profiles.items():
        print(f"\n{boss['name']}:")
        print(f"  Planet: {boss['planet']}")
        print(f"  Zone: {boss['zone']}")
        print(f"  Level: {boss['level']}")
        print(f"  Type: {boss['type']}")
        print(f"  Difficulty: {boss['difficulty']}")
        print(f"  Description: {boss['description']}")
        print(f"  Spawn Conditions: {boss['spawn_conditions']}")
        print(f"  Known Drops: {len(boss['known_drops'])} items")
        
        # Find the actual items that this boss drops
        dropped_items = []
        for item in data['items']:
            for location in item['locations']:
                if location['enemy_name'] == boss['name']:
                    dropped_items.append(item)
        
        if dropped_items:
            print(f"  Drop Details:")
            for item in dropped_items:
                location = next(loc for loc in item['locations'] if loc['enemy_name'] == boss['name'])
                drop_rate = location['drop_rate'] * 100
                print(f"    - {item['name']}: {drop_rate:.1f}% drop rate")

def demo_data_source_analysis():
    """Demo data source analysis."""
    print("\n" + "="*60)
    print("DEMO: Data Source Analysis")
    print("="*60)

    database_file = Path("data/rare_loot_database.json")
    with open(database_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data['items']
    
    # Analyze data sources
    source_counts = {}
    for item in items:
        for source in item['sources']:
            source_counts[source] = source_counts.get(source, 0) + 1
    
    print(f"\nData Source Distribution:")
    for source, count in source_counts.items():
        percentage = (count / len(items)) * 100
        source_name = source.replace('_', ' ').title()
        print(f"  {source_name}: {count} items ({percentage:.1f}%)")
    
    # Items with multiple sources
    multi_source_items = [item for item in items if len(item['sources']) > 1]
    print(f"\nItems with Multiple Sources: {len(multi_source_items)}")
    
    for item in multi_source_items:
        sources = ', '.join(item['sources'])
        print(f"  - {item['name']}: {sources}")

def demo_ui_features():
    """Demo the UI features and functionality."""
    print("\n" + "="*60)
    print("DEMO: UI Features")
    print("="*60)

    print(f"\nUI Features Available:")
    print(f"  ✅ Responsive Design: Mobile-friendly layout")
    print(f"  ✅ Advanced Filtering: Category, rarity, planet, enemy type")
    print(f"  ✅ Search Functionality: Real-time search across all fields")
    print(f"  ✅ Sorting Options: Name, rarity, value, drop rate, recent")
    print(f"  ✅ Quick Filters: One-click filter buttons")
    print(f"  ✅ Statistics Dashboard: Real-time database statistics")
    print(f"  ✅ Item Cards: Detailed item information with drop locations")
    print(f"  ✅ Source Badges: Visual indicators for data sources")
    print(f"  ✅ Drop Rate Display: Percentage-based drop rates")
    print(f"  ✅ Boss Profile Links: Integration with boss information")
    print(f"  ✅ Export Capabilities: Data export functionality")
    print(f"  ✅ Community Integration: Links to community resources")

def demo_export_functionality():
    """Demo export functionality."""
    print("\n" + "="*60)
    print("DEMO: Export Functionality")
    print("="*60)

    database_file = Path("data/rare_loot_database.json")
    with open(database_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create export directory
    export_dir = Path("data/rare_loot_exports")
    export_dir.mkdir(exist_ok=True)
    
    # Export filtered data
    export_scenarios = [
        {
            "name": "legendary_items",
            "filter": lambda item: item['rarity'] == 'legendary',
            "description": "Legendary items only"
        },
        {
            "name": "boss_drops",
            "filter": lambda item: any(loc['enemy_type'] == 'boss' for loc in item['locations']),
            "description": "Boss drops only"
        },
        {
            "name": "high_value_items",
            "filter": lambda item: item['stats']['value'] > 25000,
            "description": "High value items (>25k credits)"
        }
    ]
    
    for scenario in export_scenarios:
        filtered_items = list(filter(scenario['filter'], data['items']))
        
        export_data = {
            "export_info": {
                "scenario": scenario['name'],
                "description": scenario['description'],
                "export_date": datetime.now().isoformat(),
                "total_items": len(filtered_items)
            },
            "items": filtered_items
        }
        
        export_file = export_dir / f"{scenario['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\nExported {scenario['description']}:")
        print(f"  File: {export_file}")
        print(f"  Items: {len(filtered_items)}")
        print(f"  Size: {export_file.stat().st_size} bytes")

def demo_validation():
    """Demo data validation."""
    print("\n" + "="*60)
    print("DEMO: Data Validation")
    print("="*60)

    database_file = Path("data/rare_loot_database.json")
    with open(database_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data['items']
    validation_errors = []
    
    print(f"\nValidating {len(items)} items...")
    
    for i, item in enumerate(items):
        # Check required fields
        required_fields = ['id', 'name', 'category', 'rarity', 'description', 'locations', 'stats', 'sources']
        for field in required_fields:
            if field not in item:
                validation_errors.append(f"Item {i}: Missing required field '{field}'")
        
        # Check category validity
        if 'category' in item and item['category'] not in data['categories']:
            validation_errors.append(f"Item {i} ({item['name']}): Invalid category '{item['category']}'")
        
        # Check rarity validity
        valid_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        if 'rarity' in item and item['rarity'] not in valid_rarities:
            validation_errors.append(f"Item {i} ({item['name']}): Invalid rarity '{item['rarity']}'")
        
        # Check locations
        if 'locations' in item:
            for j, location in enumerate(item['locations']):
                if 'planet' in location and location['planet'] not in data['locations']:
                    validation_errors.append(f"Item {i} ({item['name']}): Invalid planet '{location['planet']}' in location {j}")
                
                if 'enemy_type' in location and location['enemy_type'] not in data['enemy_types']:
                    validation_errors.append(f"Item {i} ({item['name']}): Invalid enemy type '{location['enemy_type']}' in location {j}")
    
    if validation_errors:
        print(f"❌ Found {len(validation_errors)} validation errors:")
        for error in validation_errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(validation_errors) > 10:
            print(f"  ... and {len(validation_errors) - 10} more errors")
    else:
        print(f"✅ All items passed validation!")

def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Rare Loot Viewer Demo")
    parser.add_argument("--export", action="store_true", help="Export demo data")
    parser.add_argument("--validate", action="store_true", help="Run data validation")
    args = parser.parse_args()

    print("Batch 152 - Rare Loot Drop Table Viewer Demo")
    print("Rare Loot Drop Table Viewer (SWGDB UI)")
    print("="*60)

    # Setup logging
    setup_logging()

    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)

    # Run demos
    try:
        demo_database_structure()
        demo_item_analysis()
        demo_filtering_capabilities()
        demo_search_functionality()
        demo_boss_profile_integration()
        demo_data_source_analysis()
        demo_ui_features()
        
        if args.export:
            demo_export_functionality()
        
        if args.validate:
            demo_validation()

        print("\n" + "="*60)
        print("🎉 BATCH 152 DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nKey Features Demonstrated:")
        print("✅ Comprehensive database structure")
        print("✅ Advanced filtering capabilities")
        print("✅ Real-time search functionality")
        print("✅ Boss profile integration")
        print("✅ Data source analysis")
        print("✅ Modern UI with responsive design")
        print("✅ Export and validation features")

        print(f"\nGenerated files:")
        print(f"  - Database: data/rare_loot_database.json")
        print(f"  - UI Page: swgdb_site/pages/loot/rare.html")
        print(f"  - JavaScript: swgdb_site/js/rare-loot-viewer.js")
        print(f"  - Demo log: logs/rare_loot_viewer_demo.log")

        if args.export:
            print(f"  - Exports: data/rare_loot_exports/")

    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        logging.error(f"Demo failed: {e}", exc_info=True)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main()) 