#!/usr/bin/env python3
"""
Batch 133 – Item Scanner + Loot Memory Logger Demo

This demo showcases the complete loot scanning and memory system including:
- OCR and macro-based loot detection
- Combat log parsing and creature matching
- Loot table building and drop rate analysis
- Dashboard integration with "Last 20 items looted" and "Krayt loot memory"
- Real-time monitoring and data persistence

Features:
• OCR-based loot detection with confidence scoring
• Macro-based detection for reliable item capture
• Combat log parsing to match loot to creatures
• Comprehensive loot tables with drop rate analysis
• Real-time dashboard with filtering and search
• Krayt Dragon specific loot memory tracking
• Session-based loot tracking and statistics
• Data export and API endpoints
"""

import time
import json
import random
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import the item scanner
from tracking.item_scanner import ItemScanner, LootItem, LootSource, ItemRarity

class LootMemoryDemo:
    """Demo class for showcasing the loot memory system."""
    
    def __init__(self):
        self.item_scanner = ItemScanner()
        self.demo_running = False
        self.demo_thread = None
        
        # Sample creatures for demo
        self.creatures = [
            "Krayt Dragon",
            "Rancor", 
            "Acklay",
            "Giant Spider",
            "Nexu",
            "Gurreck",
            "Bantha",
            "Dewback",
            "Ronto",
            "Eopie"
        ]
        
        # Sample loot items with rarities
        self.loot_items = [
            # Legendary items
            ("Krayt Dragon Pearl", ItemRarity.LEGENDARY, 1),
            ("Ancient Artifact", ItemRarity.LEGENDARY, 1),
            ("Crystal of Power", ItemRarity.LEGENDARY, 1),
            
            # Epic items
            ("Krayt Dragon Scale", ItemRarity.EPIC, 3),
            ("Rancor Hide", ItemRarity.EPIC, 2),
            ("Acklay Claw", ItemRarity.EPIC, 1),
            ("Power Crystal", ItemRarity.EPIC, 2),
            ("Composite Armor", ItemRarity.EPIC, 1),
            ("Rare Gem", ItemRarity.EPIC, 1),
            
            # Rare items
            ("Krayt Dragon Tissue", ItemRarity.RARE, 5),
            ("Rancor Bone", ItemRarity.RARE, 3),
            ("Acklay Brain", ItemRarity.RARE, 1),
            ("Spider Silk", ItemRarity.RARE, 4),
            ("Nexu Fang", ItemRarity.RARE, 2),
            ("Gurreck Horn", ItemRarity.RARE, 1),
            ("Bantha Wool", ItemRarity.RARE, 6),
            ("Dewback Scale", ItemRarity.RARE, 3),
            
            # Uncommon items
            ("Krayt Dragon Bone", ItemRarity.UNCOMMON, 8),
            ("Rancor Meat", ItemRarity.UNCOMMON, 5),
            ("Acklay Leg", ItemRarity.UNCOMMON, 2),
            ("Spider Venom", ItemRarity.UNCOMMON, 3),
            ("Nexu Claw", ItemRarity.UNCOMMON, 2),
            ("Gurreck Hide", ItemRarity.UNCOMMON, 4),
            ("Bantha Meat", ItemRarity.UNCOMMON, 7),
            ("Dewback Meat", ItemRarity.UNCOMMON, 4),
            ("Ronto Hide", ItemRarity.UNCOMMON, 3),
            ("Eopie Wool", ItemRarity.UNCOMMON, 2),
            
            # Common items
            ("Krayt Dragon Hide", ItemRarity.COMMON, 12),
            ("Rancor Hide", ItemRarity.COMMON, 8),
            ("Acklay Hide", ItemRarity.COMMON, 4),
            ("Spider Web", ItemRarity.COMMON, 6),
            ("Nexu Hide", ItemRarity.COMMON, 3),
            ("Gurreck Hide", ItemRarity.COMMON, 5),
            ("Bantha Hide", ItemRarity.COMMON, 10),
            ("Dewback Hide", ItemRarity.COMMON, 6),
            ("Ronto Hide", ItemRarity.COMMON, 4),
            ("Eopie Hide", ItemRarity.COMMON, 3),
            ("Credits", ItemRarity.COMMON, 5000),
            ("Credits", ItemRarity.COMMON, 2500),
            ("Credits", ItemRarity.COMMON, 1000),
        ]
    
    def start_demo(self):
        """Start the loot memory demo."""
        print("🐉 Starting Batch 133 - Loot Memory Logger Demo")
        print("=" * 60)
        
        # Initialize the item scanner
        print("📦 Initializing Item Scanner...")
        self.item_scanner.start_monitoring()
        
        # Start demo thread
        self.demo_running = True
        self.demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
        self.demo_thread.start()
        
        print("✅ Demo started! Press Ctrl+C to stop.")
        print("\n📊 Dashboard available at: http://localhost:5000")
        print("🔍 Loot Memory Tool: http://localhost:5000/swgdb_site/pages/tools/loot-memory.html")
        print("\n🎯 Features being demonstrated:")
        print("   • OCR-based loot detection")
        print("   • Macro-based detection")
        print("   • Combat log parsing")
        print("   • Loot table building")
        print("   • Drop rate analysis")
        print("   • Real-time dashboard")
        print("   • Krayt loot memory")
        print("   • API: /api/loot/*")
        
        try:
            while self.demo_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_demo()
    
    def stop_demo(self):
        """Stop the loot memory demo."""
        print("\n🛑 Stopping demo...")
        self.demo_running = False
        self.item_scanner.stop_monitoring()
        
        if self.demo_thread:
            self.demo_thread.join(timeout=5)
        
        print("✅ Demo stopped!")
        self._show_final_statistics()
    
    def _demo_loop(self):
        """Main demo loop that simulates loot detection."""
        while self.demo_running:
            try:
                # Simulate loot detection every 3-8 seconds
                time.sleep(random.uniform(3, 8))
                
                if not self.demo_running:
                    break
                
                # Simulate different detection methods
                detection_method = random.choice(["ocr", "macro", "combat_log"])
                
                if detection_method == "ocr":
                    self._simulate_ocr_detection()
                elif detection_method == "macro":
                    self._simulate_macro_detection()
                else:
                    self._simulate_combat_log_detection()
                
                # Show periodic statistics
                if random.random() < 0.2:  # 20% chance
                    self._show_periodic_stats()
                    
            except Exception as e:
                print(f"❌ Error in demo loop: {e}")
                time.sleep(5)
    
    def _simulate_ocr_detection(self):
        """Simulate OCR-based loot detection."""
        creature = random.choice(self.creatures)
        item_name, rarity, quantity = random.choice(self.loot_items)
        
        # Simulate OCR confidence
        confidence = random.uniform(0.7, 0.95)
        
        print(f"👁️  OCR Detection: {quantity}x {item_name} from {creature} (Confidence: {confidence:.1%})")
        
        self.item_scanner._process_loot_detection(
            item_name=item_name,
            quantity=quantity,
            rarity=rarity,
            source_name=creature,
            detection_method="ocr",
            confidence=confidence
        )
    
    def _simulate_macro_detection(self):
        """Simulate macro-based loot detection."""
        creature = random.choice(self.creatures)
        item_name, rarity, quantity = random.choice(self.loot_items)
        
        print(f"🤖 Macro Detection: {quantity}x {item_name} from {creature}")
        
        self.item_scanner._process_loot_detection(
            item_name=item_name,
            quantity=quantity,
            rarity=rarity,
            source_name=creature,
            detection_method="macro",
            confidence=1.0
        )
    
    def _simulate_combat_log_detection(self):
        """Simulate combat log-based loot detection."""
        creature = random.choice(self.creatures)
        item_name, rarity, quantity = random.choice(self.loot_items)
        
        # Simulate combat log entry
        log_entry = f"You looted {quantity} {item_name} from {creature}"
        print(f"📜 Combat Log: {log_entry}")
        
        self.item_scanner._process_combat_log_entry(log_entry)
    
    def _show_periodic_stats(self):
        """Show periodic statistics."""
        stats = self.item_scanner.get_loot_statistics()
        
        print(f"\n📊 Current Stats:")
        print(f"   • Total Items: {stats.get('total_items', 0)}")
        print(f"   • Sources: {stats.get('total_sources', 0)}")
        print(f"   • Sessions: {stats.get('total_sessions', 0)}")
        print(f"   • Recent Loot: {stats.get('recent_loot_count', 0)}")
        print(f"   • Monitoring: {'✅' if stats.get('monitoring_active', False) else '❌'}")
        
        # Show Krayt-specific stats
        krayt_table = self.item_scanner.get_loot_table("Krayt Dragon")
        if krayt_table:
            pearl_count = 0
            for item_data in krayt_table.items.values():
                if "Pearl" in item_data['name']:
                    pearl_count = item_data['total_drops']
                    break
            
            print(f"   • Krayt Kills: {krayt_table.total_kills}")
            print(f"   • Krayt Loot: {krayt_table.total_loot}")
            print(f"   • Pearls Found: {pearl_count}")
        
        print()
    
    def _show_final_statistics(self):
        """Show final statistics when demo ends."""
        print("\n🎯 Final Statistics:")
        print("=" * 40)
        
        stats = self.item_scanner.get_loot_statistics()
        
        print(f"📦 Total Items Tracked: {stats.get('total_items', 0)}")
        print(f"🎯 Sources Encountered: {stats.get('total_sources', 0)}")
        print(f"⏱️  Active Sessions: {stats.get('total_sessions', 0)}")
        print(f"💰 Total Value: {stats.get('total_value', 0):,}")
        print(f"🔄 Recent Loot Items: {stats.get('recent_loot_count', 0)}")
        
        # Show rarity distribution
        rarity_dist = stats.get('rarity_distribution', {})
        if rarity_dist:
            print("\n📊 Rarity Distribution:")
            for rarity, count in rarity_dist.items():
                print(f"   • {rarity.title()}: {count}")
        
        # Show top sources
        loot_tables = self.item_scanner.get_all_loot_tables()
        if loot_tables:
            print("\n🏆 Top Sources by Loot Count:")
            sorted_sources = sorted(
                loot_tables.items(),
                key=lambda x: x[1].total_loot,
                reverse=True
            )[:5]
            
            for source_name, table in sorted_sources:
                print(f"   • {source_name}: {table.total_loot} items")
        
        # Show Krayt specific stats
        krayt_table = self.item_scanner.get_loot_table("Krayt Dragon")
        if krayt_table:
            print(f"\n🐉 Krayt Dragon Statistics:")
            print(f"   • Total Kills: {krayt_table.total_kills}")
            print(f"   • Total Loot: {krayt_table.total_loot}")
            print(f"   • Unique Items: {len(krayt_table.items)}")
            
            # Find pearl count
            pearl_count = 0
            for item_data in krayt_table.items.values():
                if "Pearl" in item_data['name']:
                    pearl_count = item_data['total_drops']
                    break
            
            print(f"   • Pearls Found: {pearl_count}")
            
            # Show top Krayt drops
            print(f"   • Top Drops:")
            sorted_items = sorted(
                krayt_table.items.items(),
                key=lambda x: x[1]['total_drops'],
                reverse=True
            )[:3]
            
            for item_id, item_data in sorted_items:
                drop_rate = krayt_table.drop_rates.get(item_id, 0)
                print(f"     - {item_data['name']}: {item_data['total_drops']} drops ({drop_rate}%)")
        
        print("\n✅ Demo completed successfully!")
        print("📁 Loot tables saved to: data/loot_tables/")
        print("🌐 Dashboard data available via API endpoints")

def main():
    """Main demo function."""
    print("🚀 Batch 133 - Item Scanner + Loot Memory Logger")
    print("=" * 60)
    print()
    print("This demo showcases:")
    print("• OCR and macro-based loot detection")
    print("• Combat log parsing and creature matching") 
    print("• Loot table building and drop rate analysis")
    print("• Dashboard with 'Last 20 items looted' and 'Krayt loot memory'")
    print("• Real-time monitoring and data persistence")
    print()
    
    demo = LootMemoryDemo()
    
    try:
        demo.start_demo()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        demo.stop_demo()

if __name__ == "__main__":
    main() 