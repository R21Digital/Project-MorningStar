#!/usr/bin/env python3
"""
Batch 193 - Heroic Guide Pages Demo
Demonstrates the heroic guide system with interactive maps, loot tables, and boss phases.
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, Any

def demo_heroic_guide_system():
    """Demo the complete heroic guide system"""
    print("🏛️ Heroic Guide Pages System Demo")
    print("Batch 193 - Interactive Maps, Loot Tables, and Boss Phases")
    print("=" * 60)

def demo_dynamic_page_generation():
    """Demo dynamic page generation with 11ty"""
    print("\n🏗️ Dynamic Page Generation Demo")
    print("=" * 50)
    
    page_path = "src/pages/heroics/[name]/index.11ty.js"
    if os.path.exists(page_path):
        print("✅ Dynamic Page Generator Found:")
        print(f"   Location: {page_path}")
        
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key features
        features = {
            "Pagination Support": "pagination:" in content,
            "Dynamic Routes": "permalink:" in content,
            "Data Loading": "eleventyComputed:" in content,
            "Tab Navigation": "nav-tabs" in content,
            "Boss Phase Toggle": "phase-btn" in content,
            "Map Integration": "map-viewer" in content,
            "Loot Table Display": "loot-table-component" in content
        }
        
        print("\n📋 Page Generator Features:")
        for feature, available in features.items():
            status = "✅" if available else "❌"
            print(f"   {status} {feature}")
        
        print("\n🔄 Dynamic Route Generation:")
        print("   Pattern: /heroics/{heroic_name}/")
        print("   Examples:")
        print("     • /heroics/axkva-min/")
        print("     • /heroics/ancient-jedi-temple/")
        print("     • /heroics/sith-academy/")
        
    else:
        print("❌ Dynamic page generator not found")

def demo_heroic_data_structure():
    """Demo heroic data structure and content"""
    print("\n📊 Heroic Data Structure Demo")
    print("=" * 50)
    
    # Load heroics index
    index_path = "data/heroics/heroics_index.yml"
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = yaml.safe_load(f)
        
        print("🗂️ Heroics Index:")
        print(f"   Total Heroics: {index_data.get('metadata', {}).get('total_heroics', 'Unknown')}")
        
        heroics = index_data.get('heroics', {})
        for heroic_id, heroic_info in heroics.items():
            print(f"\n📍 {heroic_info['name']}:")
            print(f"   ID: {heroic_id}")
            print(f"   Planet: {heroic_info['planet']}")
            print(f"   Location: {heroic_info['location']}")
            print(f"   Coordinates: {heroic_info['coordinates']}")
            print(f"   Level Requirement: {heroic_info['level_requirement']}+")
            print(f"   Group Size: {heroic_info['group_size']}")
            print(f"   Difficulty Tiers: {', '.join(heroic_info['difficulty_tiers'])}")
            
    # Demo detailed heroic data
    heroic_path = "data/heroics/axkva_min.yml"
    if os.path.exists(heroic_path):
        with open(heroic_path, 'r', encoding='utf-8') as f:
            heroic_data = yaml.safe_load(f)
        
        print(f"\n⚔️ Detailed Data Example - {heroic_data['name']}:")
        
        encounters = heroic_data.get('encounters', [])
        print(f"   Boss Encounters: {len(encounters)}")
        
        for encounter in encounters:
            print(f"\n   🏴 {encounter['boss_name']}:")
            print(f"      Level: {encounter['level']}")
            print(f"      Health: {encounter['health']:,}")
            print(f"      Phase: {encounter['phase']}")
            print(f"      Abilities: {len(encounter.get('abilities', []))}")
        
        if 'general_tactics' in heroic_data:
            print("\n   📖 Enhanced Content:")
            print("      ✅ General tactics and strategy")
            print("      ✅ Detailed ability descriptions")
            print("      ✅ Phase-specific mechanics")
            print("      ✅ Group composition recommendations")

def demo_interactive_maps():
    """Demo interactive map system"""
    print("\n🗺️ Interactive Map System Demo")
    print("=" * 50)
    
    # Check map data
    map_path = "src/data/maps/axkva_min.json"
    if os.path.exists(map_path):
        with open(map_path, 'r', encoding='utf-8') as f:
            map_data = json.load(f)
        
        print(f"🗺️ Map Data Example - {map_data['name']}:")
        print(f"   Map ID: {map_data['mapId']}")
        print(f"   Planet: {map_data['planet']}")
        print(f"   Coordinates: {map_data['coordinates']}")
        
        # Map features
        zones = map_data.get('zones', [])
        markers = map_data.get('markers', [])
        paths = map_data.get('paths', [])
        hazards = map_data.get('hazards', [])
        secrets = map_data.get('secrets', [])
        
        print(f"\n📍 Map Features:")
        print(f"   Zones: {len(zones)} (entrance, encounters, boss chambers)")
        print(f"   Markers: {len(markers)} (spawn, loot, checkpoints)")
        print(f"   Paths: {len(paths)} (normal route, speed run)")
        print(f"   Hazards: {len(hazards)} (traps, environmental dangers)")
        print(f"   Secrets: {len(secrets)} (hidden areas, bonus content)")
        
        print(f"\n🎮 Zone Types:")
        zone_types = {}
        for zone in zones:
            zone_type = zone['type']
            zone_types[zone_type] = zone_types.get(zone_type, 0) + 1
        
        for zone_type, count in zone_types.items():
            print(f"   {zone_type.title()}: {count}")
        
        print(f"\n📦 Marker Types:")
        marker_types = {}
        for marker in markers:
            marker_type = marker['type']
            marker_types[marker_type] = marker_types.get(marker_type, 0) + 1
        
        for marker_type, count in marker_types.items():
            print(f"   {marker_type.title()}: {count}")
    
    # Check MapViewer component
    component_path = "src/components/MapViewer.svelte"
    if os.path.exists(component_path):
        print(f"\n🎨 MapViewer Component Features:")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            component_content = f.read()
        
        features = {
            "Interactive Canvas": "canvas" in component_content,
            "Zoom Controls": "zoom-controls" in component_content,
            "Pan & Drag": "isDragging" in component_content,
            "Hover Tooltips": "tooltip" in component_content,
            "Layer Toggle": "toggleLayer" in component_content,
            "Click Selection": "selectedZone" in component_content,
            "Grid Overlay": "renderGrid" in component_content,
            "Path Rendering": "renderPaths" in component_content,
            "Marker Display": "renderMarkers" in component_content,
            "Legend Display": "map-legend" in component_content
        }
        
        for feature, available in features.items():
            status = "✅" if available else "❌"
            print(f"   {status} {feature}")

def demo_loot_table_integration():
    """Demo enhanced loot table system"""
    print("\n💎 Enhanced Loot Table System Demo")
    print("=" * 50)
    
    loot_path = "data/loot_tables/axkva_min.json"
    if os.path.exists(loot_path):
        with open(loot_path, 'r', encoding='utf-8') as f:
            loot_data = json.load(f)
        
        print(f"💰 Loot Table Example - {loot_data['name']}:")
        print(f"   Heroic ID: {loot_data['heroic_id']}")
        print(f"   Planet: {loot_data['planet']}")
        print(f"   Data Confidence: {loot_data['metadata']['data_confidence']}%")
        print(f"   Total Kills Tracked: {loot_data['metadata']['total_kills_tracked']:,}")
        
        drops = loot_data.get('drops', {})
        print(f"\n💎 Loot Items: {len(drops)}")
        
        # Categorize items by rarity
        rarity_counts = {}
        total_value = 0
        
        for item_id, item_data in drops.items():
            rarity = item_data['rarity']
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
            
            if 'market_value' in item_data:
                total_value += item_data['market_value']
        
        print(f"\n🏆 Items by Rarity:")
        for rarity in ['legendary', 'epic', 'rare', 'uncommon', 'common']:
            if rarity in rarity_counts:
                print(f"   {rarity.title()}: {rarity_counts[rarity]} items")
        
        # Showcase specific items
        print(f"\n⭐ Featured Items:")
        featured_items = ['axkva_lightsaber', 'ancient_jedi_robe', 'ancient_datacron']
        
        for item_id in featured_items:
            if item_id in drops:
                item = drops[item_id]
                print(f"\n   {item['name']} ({item['rarity'].title()}):")
                print(f"      Drop Rate: {item['drop_rate']}%")
                print(f"      Source: {item['drop_source']}")
                print(f"      Category: {item['category']}")
                if 'market_value' in item:
                    print(f"      Value: {item['market_value']:,} credits")
                print(f"      Description: {item['description'][:80]}...")
        
        # Drop sources
        sources = loot_data.get('drop_sources', {})
        print(f"\n🎯 Drop Sources: {len(sources)}")
        for source_id, source_data in sources.items():
            print(f"   {source_data['name']} ({source_data['type']})")
            print(f"      Level: {source_data['level']}")
            print(f"      Guaranteed Drops: {source_data['guaranteed_drops']}")

def demo_boss_phase_system():
    """Demo boss phase toggle functionality"""
    print("\n⚔️ Boss Phase System Demo")
    print("=" * 50)
    
    # Load heroic data to show phases
    heroic_path = "data/heroics/axkva_min.yml"
    if os.path.exists(heroic_path):
        with open(heroic_path, 'r', encoding='utf-8') as f:
            heroic_data = yaml.safe_load(f)
        
        encounters = heroic_data.get('encounters', [])
        print(f"🏴 Boss Encounters with Phases:")
        
        # Group encounters by boss and phase
        boss_phases = {}
        for encounter in encounters:
            boss_name = encounter['boss_name']
            phase = encounter['phase']
            
            if boss_name not in boss_phases:
                boss_phases[boss_name] = []
            
            boss_phases[boss_name].append({
                'phase': phase,
                'difficulty': encounter['difficulty'],
                'health': encounter['health'],
                'abilities': len(encounter.get('abilities', []))
            })
        
        for boss_name, phases in boss_phases.items():
            print(f"\n   👑 {boss_name}:")
            print(f"      Total Phases: {len(phases)}")
            
            for phase_data in sorted(phases, key=lambda x: x['phase']):
                phase_num = phase_data['phase']
                difficulty = phase_data['difficulty']
                health = phase_data['health']
                abilities = phase_data['abilities']
                
                print(f"      Phase {phase_num} ({difficulty}):")
                print(f"         Health: {health:,}")
                print(f"         Abilities: {abilities}")
        
        print(f"\n🎮 Phase Toggle Features:")
        print("   ✅ Dynamic phase button generation")
        print("   ✅ Phase-specific ability listings")
        print("   ✅ Difficulty-based phase filtering")
        print("   ✅ Interactive phase switching")
        print("   ✅ Phase-specific tactics display")
        
        # Show tactics example
        for encounter in encounters:
            if 'tactics' in encounter and encounter['tactics'].strip():
                print(f"\n📖 Example Tactics (Phase {encounter['phase']}):")
                tactics_preview = encounter['tactics'][:200].replace('\n', ' ')
                print(f"   {tactics_preview}...")
                break

def demo_markdown_yaml_features():
    """Demo Markdown + YAML content structure"""
    print("\n📝 Markdown + YAML Content Structure Demo")
    print("=" * 50)
    
    heroic_path = "data/heroics/axkva_min.yml"
    if os.path.exists(heroic_path):
        with open(heroic_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📄 Content Structure Features:")
        
        features = {
            "YAML Front Matter": content.startswith('#') or 'heroic_id:' in content,
            "Embedded HTML": '<p>' in content or '<ul>' in content,
            "Multiline Content": '|' in content,
            "Structured Data": 'encounters:' in content and 'abilities:' in content,
            "Rich Descriptions": 'description:' in content,
            "Tactical Content": 'tactics:' in content or 'general_tactics:' in content
        }
        
        for feature, available in features.items():
            status = "✅" if available else "❌"
            print(f"   {status} {feature}")
        
        # Show content organization
        print(f"\n🗂️ Content Organization:")
        sections = [
            'metadata', 'instance_type', 'difficulty_tiers', 
            'prerequisites', 'encounters', 'general_tactics',
            'recommended_group', 'rewards'
        ]
        
        for section in sections:
            if f"{section}:" in content:
                print(f"   ✅ {section.replace('_', ' ').title()}")
        
        # Extract and display tactics content
        if 'general_tactics:' in content:
            print(f"\n📖 Rich Content Example:")
            print("   General tactics include:")
            print("   • HTML formatting for better readability")
            print("   • Structured lists and sections")
            print("   • Strategic guidance and tips")
            print("   • Group composition recommendations")

def demo_system_integration():
    """Demo how all components work together"""
    print("\n🔗 System Integration Demo")
    print("=" * 50)
    
    print("🎯 Complete User Journey:")
    print("\n1. 📍 Discovery:")
    print("   • User visits /heroics/ page")
    print("   • Sees list of available heroic instances")
    print("   • Clicks on 'Axkva Min' heroic")
    
    print("\n2. 🏛️ Heroic Guide Page:")
    print("   • Dynamic page loads at /heroics/axkva-min/")
    print("   • Displays heroic overview with metadata")
    print("   • Shows difficulty tiers and requirements")
    
    print("\n3. 🗺️ Interactive Map:")
    print("   • User clicks 'Map & Location' tab")
    print("   • Interactive map loads with zones and markers")
    print("   • Can zoom, pan, and click for details")
    print("   • Hover tooltips provide quick info")
    
    print("\n4. ⚔️ Boss Encounters:")
    print("   • User switches to 'Boss Encounters' tab")
    print("   • Phase buttons allow toggling between encounters")
    print("   • Each phase shows specific abilities and tactics")
    print("   • Rich HTML content provides detailed strategy")
    
    print("\n5. 💎 Loot Tables:")
    print("   • 'Loot Tables' tab displays comprehensive drop data")
    print("   • Items organized by rarity and source")
    print("   • Drop rates and market values shown")
    print("   • Links to individual item pages")
    
    print("\n6. 📖 Tactics & Strategy:")
    print("   • 'Tactics' tab provides general strategy guide")
    print("   • Group composition recommendations")
    print("   • Common mistakes and how to avoid them")
    print("   • Difficulty-specific advice")
    
    print(f"\n🔧 Technical Integration:")
    print("   • 11ty generates static pages from YAML data")
    print("   • Svelte components provide interactivity")
    print("   • JSON map data drives visual representations")
    print("   • Progressive enhancement for better UX")
    print("   • Responsive design for all devices")

def demo_benefits_and_features():
    """Demo key benefits and features"""
    print("\n💡 Key Benefits and Features")
    print("=" * 50)
    
    print("🎯 For Players:")
    print("   • Comprehensive heroic instance guides")
    print("   • Interactive maps with detailed markers")
    print("   • Phase-by-phase boss strategies")
    print("   • Accurate loot drop information")
    print("   • Mobile-friendly responsive design")
    
    print("\n🔧 For Developers:")
    print("   • YAML-based content management")
    print("   • Component-driven architecture")
    print("   • Static site generation for performance")
    print("   • Modular and extensible design")
    print("   • Easy content updates and maintenance")
    
    print("\n📊 Technical Achievements:")
    print("   • Dynamic route generation")
    print("   • Interactive canvas-based maps")
    print("   • Real-time phase switching")
    print("   • Rich content with embedded HTML")
    print("   • Structured data integration")
    
    print("\n🚀 Future Enhancements:")
    print("   • Real-time kill statistics")
    print("   • User-contributed content")
    print("   • Video guide integration")
    print("   • Community ratings and reviews")
    print("   • Advanced search and filtering")

def main():
    """Main demo runner"""
    try:
        demo_heroic_guide_system()
        demo_dynamic_page_generation()
        demo_heroic_data_structure()
        demo_interactive_maps()
        demo_loot_table_integration()
        demo_boss_phase_system()
        demo_markdown_yaml_features()
        demo_system_integration()
        demo_benefits_and_features()
        
        print("\n" + "=" * 60)
        print("✅ Demo Complete!")
        print("\n💡 Next Steps:")
        print("   1. Set up 11ty build environment")
        print("   2. Configure Svelte component compilation")
        print("   3. Test responsive design on different devices")
        print("   4. Add more heroic instances and data")
        print("   5. Integrate with live game data if available")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")

if __name__ == "__main__":
    main()