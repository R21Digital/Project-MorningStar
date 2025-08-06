#!/usr/bin/env python3
"""
Batch 171 - Heroics Loot Table Builder Demo
Demonstrates the loot table functionality with data loading, filtering, and UI generation.
"""

import yaml
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class HeroicsLootTableDemo:
    def __init__(self):
        self.data_dir = Path("swgdb_site/data/loot")
        self.loot_file = self.data_dir / "heroics.yml"
        self.loot_data = None
        
    def load_loot_data(self) -> Dict[str, Any]:
        """Load loot data from YAML file."""
        try:
            with open(self.loot_file, 'r', encoding='utf-8') as f:
                self.loot_data = yaml.safe_load(f)
            print(f"✅ Loaded loot data from {self.loot_file}")
            return self.loot_data
        except FileNotFoundError:
            print(f"❌ Loot data file not found: {self.loot_file}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML: {e}")
            return {}
    
    def validate_data_structure(self) -> Dict[str, Any]:
        """Validate the loot data structure."""
        if not self.loot_data:
            return {"valid": False, "errors": ["No data loaded"]}
        
        errors = []
        warnings = []
        
        # Check required sections
        required_sections = ['heroics', 'rarity_levels', 'loot_types']
        for section in required_sections:
            if section not in self.loot_data:
                errors.append(f"Missing required section: {section}")
        
        # Validate heroics structure
        if 'heroics' in self.loot_data:
            for heroic_id, heroic in self.loot_data['heroics'].items():
                if 'name' not in heroic:
                    errors.append(f"Heroic {heroic_id} missing name")
                
                if 'planet' not in heroic:
                    errors.append(f"Heroic {heroic_id} missing planet")
                
                if 'bosses' not in heroic or not isinstance(heroic['bosses'], list):
                    errors.append(f"Heroic {heroic_id} missing or invalid bosses array")
                else:
                    for boss in heroic['bosses']:
                        if 'name' not in boss:
                            errors.append(f"Boss missing name in heroic {heroic_id}")
                        
                        if 'loot' not in boss or not isinstance(boss['loot'], list):
                            errors.append(f"Boss {boss.get('name', 'unknown')} missing or invalid loot array")
                        else:
                            for item in boss['loot']:
                                if 'name' not in item:
                                    errors.append(f"Loot item missing name in boss {boss.get('name', 'unknown')}")
                                
                                if 'rarity' not in item:
                                    warnings.append(f"Loot item {item.get('name', 'unknown')} missing rarity")
                                
                                if 'type' not in item:
                                    warnings.append(f"Loot item {item.get('name', 'unknown')} missing type")
                                
                                if 'drop_chance' not in item:
                                    warnings.append(f"Loot item {item.get('name', 'unknown')} missing drop chance")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loot data."""
        if not self.loot_data:
            return {}
        
        stats = {
            "total_heroics": len(self.loot_data.get('heroics', {})),
            "total_bosses": 0,
            "total_loot_items": 0,
            "rarity_distribution": {},
            "type_distribution": {},
            "profession_distribution": {}
        }
        
        # Count bosses and loot items
        for heroic in self.loot_data.get('heroics', {}).values():
            stats["total_bosses"] += len(heroic.get('bosses', []))
            for boss in heroic.get('bosses', []):
                stats["total_loot_items"] += len(boss.get('loot', []))
                
                # Count rarity and type distribution
                for item in boss.get('loot', []):
                    rarity = item.get('rarity', 'unknown')
                    item_type = item.get('type', 'unknown')
                    
                    stats["rarity_distribution"][rarity] = stats["rarity_distribution"].get(rarity, 0) + 1
                    stats["type_distribution"][item_type] = stats["type_distribution"].get(item_type, 0) + 1
        
        # Count profession relevance
        for profession, items in self.loot_data.get('profession_relevance', {}).items():
            stats["profession_distribution"][profession] = len(items)
        
        return stats
    
    def filter_loot(self, filters: Dict[str, str]) -> Dict[str, Any]:
        """Filter loot data based on criteria."""
        if not self.loot_data:
            return {}
        
        filtered = {}
        
        for heroic_id, heroic in self.loot_data.get('heroics', {}).items():
            # Apply heroic filter
            if 'heroic' in filters and filters['heroic'] != 'all' and filters['heroic'] != heroic_id:
                continue
            
            # Apply planet filter
            if 'planet' in filters and filters['planet'] != 'all' and filters['planet'] != heroic.get('planet'):
                continue
            
            # Filter bosses and their loot
            filtered_bosses = []
            for boss in heroic.get('bosses', []):
                filtered_loot = []
                for item in boss.get('loot', []):
                    # Rarity filter
                    if 'rarity' in filters and filters['rarity'] != 'all' and item.get('rarity') != filters['rarity']:
                        continue
                    
                    # Type filter
                    if 'type' in filters and filters['type'] != 'all' and item.get('type') != filters['type']:
                        continue
                    
                    # Profession filter
                    if 'profession' in filters and filters['profession'] != 'all':
                        profession_items = self.loot_data.get('profession_relevance', {}).get(filters['profession'], [])
                        if item.get('name') not in profession_items:
                            continue
                    
                    filtered_loot.append(item)
                
                if filtered_loot:
                    filtered_bosses.append({
                        **boss,
                        'loot': filtered_loot
                    })
            
            if filtered_bosses:
                filtered[heroic_id] = {
                    **heroic,
                    'bosses': filtered_bosses
                }
        
        return filtered
    
    def generate_sample_filters(self) -> List[Dict[str, str]]:
        """Generate sample filter combinations for demonstration."""
        return [
            {"heroic": "all", "rarity": "all", "type": "all", "profession": "all"},
            {"heroic": "axkva_min", "rarity": "all", "type": "all", "profession": "all"},
            {"heroic": "all", "rarity": "legendary", "type": "all", "profession": "all"},
            {"heroic": "all", "rarity": "all", "type": "weapon", "profession": "all"},
            {"heroic": "all", "rarity": "all", "type": "all", "profession": "jedi"},
            {"heroic": "all", "rarity": "epic", "type": "weapon", "profession": "bounty_hunter"},
        ]
    
    def demo_filtering(self):
        """Demonstrate filtering functionality."""
        print("\n🔍 DEMO: Filtering Functionality")
        print("=" * 50)
        
        sample_filters = self.generate_sample_filters()
        
        for i, filters in enumerate(sample_filters, 1):
            print(f"\n📋 Filter Set {i}:")
            for key, value in filters.items():
                print(f"  {key}: {value}")
            
            filtered_data = self.filter_loot(filters)
            total_items = sum(
                len(boss.get('loot', []))
                for heroic in filtered_data.values()
                for boss in heroic.get('bosses', [])
            )
            
            print(f"  Results: {len(filtered_data)} heroics, {total_items} loot items")
            
            # Show some sample items
            for heroic_id, heroic in filtered_data.items():
                print(f"    {heroic['name']}:")
                for boss in heroic.get('bosses', []):
                    print(f"      {boss['name']}: {len(boss['loot'])} items")
                    for item in boss['loot'][:3]:  # Show first 3 items
                        print(f"        - {item['name']} ({item['rarity']})")
                    if len(boss['loot']) > 3:
                        print(f"        ... and {len(boss['loot']) - 3} more")
    
    def demo_statistics(self):
        """Demonstrate statistics functionality."""
        print("\n📊 DEMO: Statistics")
        print("=" * 50)
        
        stats = self.get_statistics()
        
        print(f"Total Heroics: {stats.get('total_heroics', 0)}")
        print(f"Total Bosses: {stats.get('total_bosses', 0)}")
        print(f"Total Loot Items: {stats.get('total_loot_items', 0)}")
        
        print("\nRarity Distribution:")
        for rarity, count in stats.get('rarity_distribution', {}).items():
            print(f"  {rarity.title()}: {count}")
        
        print("\nType Distribution:")
        for item_type, count in stats.get('type_distribution', {}).items():
            print(f"  {item_type.title()}: {count}")
        
        print("\nProfession Relevance:")
        for profession, count in stats.get('profession_distribution', {}).items():
            print(f"  {profession.title()}: {count} relevant items")
    
    def demo_data_validation(self):
        """Demonstrate data validation."""
        print("\n✅ DEMO: Data Validation")
        print("=" * 50)
        
        validation = self.validate_data_structure()
        
        if validation['valid']:
            print("✅ Data structure is valid!")
        else:
            print("❌ Data structure has errors:")
            for error in validation['errors']:
                print(f"  - {error}")
        
        if validation['warnings']:
            print("\n⚠️  Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
    
    def demo_ui_features(self):
        """Demonstrate UI features."""
        print("\n🎨 DEMO: UI Features")
        print("=" * 50)
        
        features = [
            "AtlasLoot-style interface with color-coded rarity",
            "Interactive filters for heroic, rarity, type, and profession",
            "Responsive grid layout for loot items",
            "Detailed item information with stats and descriptions",
            "Drop chance percentages and use case information",
            "Source attribution: 'Generated by SWGDB'",
            "Mobile-friendly responsive design",
            "Real-time filtering without page reload"
        ]
        
        for i, feature in enumerate(features, 1):
            print(f"{i}. {feature}")
    
    def demo_file_structure(self):
        """Show the file structure created."""
        print("\n📁 DEMO: File Structure")
        print("=" * 50)
        
        files = [
            "swgdb_site/data/loot/heroics.yml - Comprehensive loot data",
            "swgdb_site/pages/heroics.11ty.js - Dynamic page generation",
            "swgdb_site/templates/partials/lootTable.njk - Reusable template",
            "swgdb_site/utils/yaml_loader.js - Data loading utility"
        ]
        
        for file in files:
            print(f"✅ {file}")
    
    def run_demo(self):
        """Run the complete demo."""
        print("BATCH 171 - HEROICS LOOT TABLE BUILDER DEMO")
        print("=" * 60)
        
        # Load data
        self.load_loot_data()
        
        if not self.loot_data:
            print("❌ Cannot run demo without loot data")
            return
        
        # Run demo sections
        self.demo_data_validation()
        self.demo_statistics()
        self.demo_filtering()
        self.demo_ui_features()
        self.demo_file_structure()
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Install js-yaml: npm install js-yaml")
        print("2. Build the site: npx @11ty/eleventy")
        print("3. Visit /heroics/loot-table/ to see the interface")
        print("4. Test filtering and interaction features")

def main():
    """Main demo function."""
    demo = HeroicsLootTableDemo()
    demo.run_demo()

if __name__ == "__main__":
    main() 