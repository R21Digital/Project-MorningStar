#!/usr/bin/env python3
"""
Batch 186 Demo - Loot Tables Page (Heroics) + Loot Sync Logic
Demonstrates the new loot table system with filtering, statistics, and MS11 sync
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

class LootTableDemo:
    def __init__(self):
        self.loot_tables_dir = Path("src/data/loot_tables")
        self.demo_data = {}
        self.stats = {}
        
    def load_loot_tables(self):
        """Load all loot table JSON files"""
        print("📁 Loading loot tables...")
        
        for json_file in self.loot_tables_dir.glob("*.json"):
            planet = json_file.stem
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    self.demo_data[planet] = data
                    print(f"  ✅ Loaded {planet}: {len(data.get('heroics', {}))} heroics")
            except Exception as e:
                print(f"  ❌ Error loading {planet}: {e}")
                
        print(f"📊 Total planets loaded: {len(self.demo_data)}")
        
    def generate_demo_statistics(self):
        """Generate comprehensive statistics for all loot tables"""
        print("\n📈 Generating statistics...")
        
        total_stats = {
            'total_planets': len(self.demo_data),
            'total_heroics': 0,
            'total_items': 0,
            'rarity_breakdown': {},
            'type_breakdown': {},
            'profession_breakdown': {},
            'source_breakdown': {}
        }
        
        for planet, data in self.demo_data.items():
            planet_stats = {
                'planet': planet,
                'heroics': len(data.get('heroics', {})),
                'items': 0,
                'rarity_breakdown': {},
                'type_breakdown': {},
                'profession_breakdown': {},
                'source_breakdown': {}
            }
            
            for heroic_key, heroic_data in data.get('heroics', {}).items():
                total_stats['total_heroics'] += 1
                
                for item_key, item_data in heroic_data.get('items', {}).items():
                    planet_stats['items'] += 1
                    total_stats['total_items'] += 1
                    
                    # Rarity breakdown
                    rarity = item_data.get('rarity', 'unknown')
                    planet_stats['rarity_breakdown'][rarity] = planet_stats['rarity_breakdown'].get(rarity, 0) + 1
                    total_stats['rarity_breakdown'][rarity] = total_stats['rarity_breakdown'].get(rarity, 0) + 1
                    
                    # Type breakdown
                    item_type = item_data.get('type', 'unknown')
                    planet_stats['type_breakdown'][item_type] = planet_stats['type_breakdown'].get(item_type, 0) + 1
                    total_stats['type_breakdown'][item_type] = total_stats['type_breakdown'].get(item_type, 0) + 1
                    
                    # Source breakdown
                    source = item_data.get('source', 'unknown')
                    planet_stats['source_breakdown'][source] = planet_stats['source_breakdown'].get(source, 0) + 1
                    total_stats['source_breakdown'][source] = total_stats['source_breakdown'].get(source, 0) + 1
                    
                    # Profession breakdown
                    professions = item_data.get('profession_relevance', [])
                    for profession in professions:
                        planet_stats['profession_breakdown'][profession] = planet_stats['profession_breakdown'].get(profession, 0) + 1
                        total_stats['profession_breakdown'][profession] = total_stats['profession_breakdown'].get(profession, 0) + 1
            
            self.stats[planet] = planet_stats
            
        self.stats['total'] = total_stats
        print(f"  ✅ Generated stats for {len(self.stats) - 1} planets")
        
    def demo_filtering_system(self):
        """Demonstrate the filtering system"""
        print("\n🔍 Testing filtering system...")
        
        # Test filters
        test_filters = [
            {'rarity': 'legendary'},
            {'type': 'weapon'},
            {'profession': 'weaponsmith'},
            {'source': 'SWGDB Generated'},
            {'search': 'crystal'}
        ]
        
        for i, filter_config in enumerate(test_filters, 1):
            print(f"\n  Filter {i}: {filter_config}")
            filtered_items = self.apply_filters(filter_config)
            print(f"    Found {len(filtered_items)} items")
            
            for item in filtered_items[:3]:  # Show first 3
                print(f"      - {item['name']} ({item['rarity']})")
                
    def apply_filters(self, filters):
        """Apply filters to all items"""
        filtered_items = []
        
        for planet, data in self.demo_data.items():
            for heroic_key, heroic_data in data.get('heroics', {}).items():
                for item_key, item_data in heroic_data.get('items', {}).items():
                    if self.item_matches_filters(item_data, filters):
                        filtered_items.append({
                            'planet': planet,
                            'heroic': heroic_data['boss'],
                            'name': item_data['name'],
                            'rarity': item_data['rarity'],
                            'type': item_data['type'],
                            'source': item_data.get('source', 'Unknown')
                        })
                        
        return filtered_items
        
    def item_matches_filters(self, item, filters):
        """Check if item matches all filters"""
        for filter_type, filter_value in filters.items():
            if filter_type == 'rarity':
                if item.get('rarity') != filter_value:
                    return False
            elif filter_type == 'type':
                if item.get('type') != filter_value:
                    return False
            elif filter_type == 'profession':
                professions = item.get('profession_relevance', [])
                if filter_value not in professions:
                    return False
            elif filter_type == 'source':
                if item.get('source') != filter_value:
                    return False
            elif filter_type == 'search':
                search_term = filter_value.lower()
                item_name = item.get('name', '').lower()
                item_use_case = item.get('use_case', '').lower()
                if search_term not in item_name and search_term not in item_use_case:
                    return False
                    
        return True
        
    def demo_ms11_export(self):
        """Demonstrate MS11 export functionality"""
        print("\n🔄 Testing MS11 export...")
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'source': 'SWGDB Loot Tables',
            'version': '1.0.0',
            'planets': {}
        }
        
        for planet, data in self.demo_data.items():
            export_data['planets'][planet] = {
                'planet': data.get('planet'),
                'total_runs': data.get('total_runs', 0),
                'total_loot': data.get('total_loot', 0),
                'last_updated': data.get('last_updated'),
                'heroics': {}
            }
            
            for heroic_key, heroic_data in data.get('heroics', {}).items():
                export_data['planets'][planet]['heroics'][heroic_key] = {
                    'boss': heroic_data['boss'],
                    'location': heroic_data['location'],
                    'level': heroic_data['level'],
                    'items': []
                }
                
                for item_key, item_data in heroic_data.get('items', {}).items():
                    export_data['planets'][planet]['heroics'][heroic_key]['items'].append({
                        'name': item_data['name'],
                        'type': item_data['type'],
                        'rarity': item_data['rarity'],
                        'drop_chance': item_data.get('drop_chance', 0),
                        'profession_relevance': item_data.get('profession_relevance', []),
                        'use_case': item_data.get('use_case', '')
                    })
        
        # Save export file
        export_file = f"BATCH_186_MS11_EXPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        print(f"  ✅ Exported MS11 data to {export_file}")
        print(f"  📊 Export contains {len(export_data['planets'])} planets")
        
        return export_file
        
    def demo_loot_sync_logic(self):
        """Demonstrate loot sync logic between manual and bot data"""
        print("\n🔄 Testing loot sync logic...")
        
        # Simulate bot-generated data
        bot_data = {
            'heroic': 'krayt_dragon',
            'boss': 'Krayt Dragon',
            'location': 'Tatooine - Dune Sea',
            'level': 80,
            'total_kills': 50,
            'items': {
                'krayt_scale_bot': {
                    'name': 'Krayt Dragon Scale',
                    'rarity': 'rare',
                    'total_drops': 12,
                    'total_quantity': 45,
                    'first_seen': '2025-08-01T10:00:00',
                    'last_seen': '2025-08-05T15:30:00'
                },
                'new_item': {
                    'name': 'Krayt Dragon Heart',
                    'rarity': 'epic',
                    'total_drops': 3,
                    'total_quantity': 3,
                    'first_seen': '2025-08-03T14:20:00',
                    'last_seen': '2025-08-05T16:45:00'
                }
            }
        }
        
        # Merge with existing data
        merged_data = self.merge_loot_data(self.demo_data.get('tatooine', {}), bot_data)
        
        print(f"  ✅ Merged bot data with manual data")
        print(f"  📊 Total heroics after merge: {len(merged_data.get('heroics', {}))}")
        
        # Show merged items
        krayt_heroic = merged_data.get('heroics', {}).get('krayt_dragon', {})
        print(f"  🐉 Krayt Dragon items: {len(krayt_heroic.get('items', {}))}")
        
        return merged_data
        
    def merge_loot_data(self, manual_data, bot_data):
        """Merge bot-generated data with manual data"""
        merged = manual_data.copy()
        
        if 'heroics' not in merged:
            merged['heroics'] = {}
            
        heroic_key = bot_data['heroic']
        if heroic_key not in merged['heroics']:
            merged['heroics'][heroic_key] = {
                'boss': bot_data['boss'],
                'location': bot_data['location'],
                'level': bot_data['level'],
                'total_kills': bot_data['total_kills'],
                'items': {}
            }
        
        # Merge items
        for item_key, bot_item in bot_data['items'].items():
            # Check if item already exists
            existing_item = None
            for existing_key, existing_data in merged['heroics'][heroic_key]['items'].items():
                if existing_data['name'].lower() == bot_item['name'].lower():
                    existing_item = existing_key
                    break
            
            if existing_item:
                # Update existing item
                merged['heroics'][heroic_key]['items'][existing_item].update({
                    'total_drops': (merged['heroics'][heroic_key]['items'][existing_item].get('total_drops', 0) + 
                                  bot_item['total_drops']),
                    'total_quantity': (merged['heroics'][heroic_key]['items'][existing_item].get('total_quantity', 0) + 
                                     bot_item['total_quantity']),
                    'first_seen': (merged['heroics'][heroic_key]['items'][existing_item].get('first_seen') or 
                                 bot_item['first_seen']),
                    'last_seen': bot_item['last_seen'],
                    'source': 'Bot Generated + Manual'
                })
            else:
                # Add new item
                merged['heroics'][heroic_key]['items'][item_key] = {
                    'name': bot_item['name'],
                    'rarity': bot_item['rarity'],
                    'total_drops': bot_item['total_drops'],
                    'total_quantity': bot_item['total_quantity'],
                    'first_seen': bot_item['first_seen'],
                    'last_seen': bot_item['last_seen'],
                    'source': 'Bot Generated'
                }
        
        return merged
        
    def print_statistics_report(self):
        """Print a comprehensive statistics report"""
        print("\n📊 Loot Tables Statistics Report")
        print("=" * 50)
        
        total_stats = self.stats['total']
        print(f"Total Planets: {total_stats['total_planets']}")
        print(f"Total Heroics: {total_stats['total_heroics']}")
        print(f"Total Items: {total_stats['total_items']}")
        
        print("\nRarity Breakdown:")
        for rarity, count in sorted(total_stats['rarity_breakdown'].items()):
            percentage = (count / total_stats['total_items']) * 100
            print(f"  {rarity.capitalize()}: {count} ({percentage:.1f}%)")
            
        print("\nType Breakdown:")
        for item_type, count in sorted(total_stats['type_breakdown'].items()):
            percentage = (count / total_stats['total_items']) * 100
            print(f"  {item_type.capitalize()}: {count} ({percentage:.1f}%)")
            
        print("\nSource Breakdown:")
        for source, count in sorted(total_stats['source_breakdown'].items()):
            percentage = (count / total_stats['total_items']) * 100
            print(f"  {source}: {count} ({percentage:.1f}%)")
            
        print("\nTop Professions:")
        sorted_professions = sorted(total_stats['profession_breakdown'].items(), 
                                  key=lambda x: x[1], reverse=True)
        for profession, count in sorted_professions[:5]:
            percentage = (count / total_stats['total_items']) * 100
            print(f"  {profession.capitalize()}: {count} ({percentage:.1f}%)")
            
    def run_demo(self):
        """Run the complete demo"""
        print("🚀 Batch 186 Demo - Loot Tables Page (Heroics) + Loot Sync Logic")
        print("=" * 70)
        
        # Load loot tables
        self.load_loot_tables()
        
        # Generate statistics
        self.generate_demo_statistics()
        
        # Print statistics report
        self.print_statistics_report()
        
        # Test filtering system
        self.demo_filtering_system()
        
        # Test MS11 export
        export_file = self.demo_ms11_export()
        
        # Test loot sync logic
        merged_data = self.demo_loot_sync_logic()
        
        # Final summary
        print("\n" + "=" * 70)
        print("✅ Batch 186 Demo Complete!")
        print(f"📁 Loot tables loaded: {len(self.demo_data)} planets")
        print(f"📊 Total items: {self.stats['total']['total_items']}")
        print(f"🔄 MS11 export: {export_file}")
        print("🎯 Features demonstrated:")
        print("  - Manual + bot-generated loot data")
        print("  - Filter by rarity, item type, profession, source")
        print("  - Display sources (SWGDB Generated, User Submitted)")
        print("  - MS11 sync option (internal only)")
        print("  - Comprehensive statistics and reporting")
        
        return {
            'planets_loaded': len(self.demo_data),
            'total_items': self.stats['total']['total_items'],
            'export_file': export_file,
            'merged_data': merged_data
        }

def main():
    """Main demo function"""
    demo = LootTableDemo()
    results = demo.run_demo()
    
    # Save demo results
    results_file = f"BATCH_186_DEMO_RESULTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\n📄 Demo results saved to: {results_file}")
    
if __name__ == "__main__":
    main() 