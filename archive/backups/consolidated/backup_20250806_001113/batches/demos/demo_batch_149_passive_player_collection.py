#!/usr/bin/env python3
"""
Batch 149 - Passive Player Data Collection Demo

This demo showcases the passive player data collection system that gathers
visible player data during gameplay for SWGDB intelligence.

Features demonstrated:
- Passive OCR-based player detection
- Guild, faction, title, and location tracking
- NPC detection based on cross-zone encounters
- Data enrichment for /players and /guilds endpoints
- Real-time statistics and reporting
"""

import os
import sys
import time
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.passive_player_collector import PassivePlayerCollector, PassivePlayerData
from profession_logic.utils.logger import logger


class PassivePlayerCollectionDemo:
    """Demo class for Batch 149 passive player data collection."""
    
    def __init__(self):
        """Initialize the demo."""
        self.collector = PassivePlayerCollector()
        self.demo_data = self._generate_demo_data()
        
        logger.info("[DEMO] Initialized Batch 149 Passive Player Collection Demo")
    
    def _generate_demo_data(self) -> List[Dict[str, Any]]:
        """Generate realistic demo player data."""
        return [
            # Imperial players
            {"name": "Jevon", "guild": "Corellian Elite", "faction": "Imperial", "title": "Master Rifleman", "location": "Theed"},
            {"name": "DarthVader", "guild": "Imperial Order", "faction": "Imperial", "title": "Sith Lord", "location": "Coronet"},
            {"name": "StormTrooper", "guild": "Imperial Army", "faction": "Imperial", "title": "Sergeant", "location": "Mos Eisley"},
            {"name": "ImperialAgent", "guild": "Imperial Intelligence", "faction": "Imperial", "title": "Agent", "location": "Theed"},
            
            # Rebel players
            {"name": "LukeSkywalker", "guild": "Rebel Alliance", "faction": "Rebel", "title": "Jedi Knight", "location": "Aldera"},
            {"name": "HanSolo", "guild": "Smugglers Guild", "faction": "Rebel", "title": "Captain", "location": "Mos Eisley"},
            {"name": "LeiaOrgana", "guild": "Rebel Alliance", "faction": "Rebel", "title": "Princess", "location": "Aldera"},
            {"name": "Chewbacca", "guild": "Wookiee Clan", "faction": "Rebel", "title": "Warrior", "location": "Kashyyyk"},
            
            # Neutral players
            {"name": "JabbaHutt", "guild": "Hutt Cartel", "faction": "Neutral", "title": "Crime Lord", "location": "Tatooine"},
            {"name": "BobaFett", "guild": "Bounty Hunters", "faction": "Neutral", "title": "Mandalorian", "location": "Tatooine"},
            {"name": "ObiWan", "guild": "Jedi Order", "faction": "Jedi", "title": "Jedi Master", "location": "Coronet"},
            {"name": "Yoda", "guild": "Jedi Council", "faction": "Jedi", "title": "Grand Master", "location": "Dagobah"},
            
            # Possible NPCs (same name across zones)
            {"name": "Merchant", "guild": "Trade Federation", "faction": "Neutral", "title": "Trader", "location": "Theed"},
            {"name": "Merchant", "guild": "Trade Federation", "faction": "Neutral", "title": "Trader", "location": "Coronet"},
            {"name": "Merchant", "guild": "Trade Federation", "faction": "Neutral", "title": "Trader", "location": "Mos Eisley"},
            {"name": "Guard", "guild": "City Watch", "faction": "Neutral", "title": "Guard", "location": "Theed"},
            {"name": "Guard", "guild": "City Watch", "faction": "Neutral", "title": "Guard", "location": "Coronet"},
            {"name": "Guard", "guild": "City Watch", "faction": "Neutral", "title": "Guard", "location": "Aldera"},
        ]
    
    def run_demo(self) -> None:
        """Run the complete demo."""
        print("\n" + "="*80)
        print("🎯 BATCH 149 - PASSIVE PLAYER DATA COLLECTION DEMO")
        print("="*80)
        
        print("\n📋 Demo Overview:")
        print("• Passive collection of visible player data during gameplay")
        print("• OCR-based player name and info detection")
        print("• Guild, faction, title, and location tracking")
        print("• NPC detection based on cross-zone encounters")
        print("• Data enrichment for /players and /guilds endpoints")
        
        # Step 1: Initial state
        self._show_initial_state()
        
        # Step 2: Simulate passive collection
        self._simulate_passive_collection()
        
        # Step 3: Show statistics
        self._show_statistics()
        
        # Step 4: Demonstrate NPC detection
        self._demonstrate_npc_detection()
        
        # Step 5: Show SWGDB export
        self._show_swgdb_export()
        
        # Step 6: Data file inspection
        self._inspect_data_file()
        
        print("\n✅ Demo completed successfully!")
        print("📁 Data saved to: data/encounters/players_seen.json")
    
    def _show_initial_state(self) -> None:
        """Show initial state of the collector."""
        print("\n" + "-"*60)
        print("🔍 STEP 1: INITIAL STATE")
        print("-"*60)
        
        stats = self.collector.get_player_statistics()
        print(f"📊 Initial Statistics:")
        print(f"   • Total Players: {stats['total_players']}")
        print(f"   • Total Encounters: {stats['total_encounters']}")
        print(f"   • Possible NPCs: {stats['possible_npcs']}")
        print(f"   • Guilds: {len(stats['guilds'])}")
        print(f"   • Factions: {len(stats['factions'])}")
        
        if stats['total_players'] > 0:
            print(f"\n📋 Known Players:")
            for player_name in list(self.collector.known_players.keys())[:5]:
                player = self.collector.known_players[player_name]
                print(f"   • {player.name} ({player.guild or 'No Guild'}) - {player.faction or 'Unknown'}")
            if len(self.collector.known_players) > 5:
                print(f"   ... and {len(self.collector.known_players) - 5} more")
    
    def _simulate_passive_collection(self) -> None:
        """Simulate passive data collection during gameplay."""
        print("\n" + "-"*60)
        print("🎮 STEP 2: SIMULATING PASSIVE COLLECTION")
        print("-"*60)
        
        print("🔄 Simulating gameplay scenarios...")
        
        # Scenario 1: Theed (Naboo)
        print("\n📍 Scenario 1: Exploring Theed (Naboo)")
        self._simulate_zone_encounters("Theed", [
            {"name": "Jevon", "guild": "Corellian Elite", "faction": "Imperial", "title": "Master Rifleman"},
            {"name": "ImperialAgent", "guild": "Imperial Intelligence", "faction": "Imperial", "title": "Agent"},
            {"name": "Merchant", "guild": "Trade Federation", "faction": "Neutral", "title": "Trader"},
            {"name": "Guard", "guild": "City Watch", "faction": "Neutral", "title": "Guard"},
        ])
        
        # Scenario 2: Coronet (Corellia)
        print("\n📍 Scenario 2: Visiting Coronet (Corellia)")
        self._simulate_zone_encounters("Coronet", [
            {"name": "DarthVader", "guild": "Imperial Order", "faction": "Imperial", "title": "Sith Lord"},
            {"name": "ObiWan", "guild": "Jedi Order", "faction": "Jedi", "title": "Jedi Master"},
            {"name": "Merchant", "guild": "Trade Federation", "faction": "Neutral", "title": "Trader"},
            {"name": "Guard", "guild": "City Watch", "faction": "Neutral", "title": "Guard"},
        ])
        
        # Scenario 3: Mos Eisley (Tatooine)
        print("\n📍 Scenario 3: Exploring Mos Eisley (Tatooine)")
        self._simulate_zone_encounters("Mos Eisley", [
            {"name": "HanSolo", "guild": "Smugglers Guild", "faction": "Rebel", "title": "Captain"},
            {"name": "JabbaHutt", "guild": "Hutt Cartel", "faction": "Neutral", "title": "Crime Lord"},
            {"name": "BobaFett", "guild": "Bounty Hunters", "faction": "Neutral", "title": "Mandalorian"},
            {"name": "Merchant", "guild": "Trade Federation", "faction": "Neutral", "title": "Trader"},
        ])
        
        # Scenario 4: Aldera (Alderaan)
        print("\n📍 Scenario 4: Visiting Aldera (Alderaan)")
        self._simulate_zone_encounters("Aldera", [
            {"name": "LukeSkywalker", "guild": "Rebel Alliance", "faction": "Rebel", "title": "Jedi Knight"},
            {"name": "LeiaOrgana", "guild": "Rebel Alliance", "faction": "Rebel", "title": "Princess"},
            {"name": "Guard", "guild": "City Watch", "faction": "Neutral", "title": "Guard"},
        ])
        
        print(f"\n✅ Collection completed! Total encounters: {len(self.collector.known_players)}")
    
    def _simulate_zone_encounters(self, zone: str, players: List[Dict[str, Any]]) -> None:
        """Simulate encountering players in a specific zone."""
        print(f"   🎯 Zone: {zone}")
        
        for player_data in players:
            # Simulate current location
            current_location = {
                "planet": zone.split('/')[0] if '/' in zone else "Unknown",
                "city": zone.split('/')[1] if '/' in zone else zone,
                "coordinates": [random.randint(100, 500), random.randint(100, 500)]
            }
            
            # Create encounter data
            encounter = PassivePlayerData(
                name=player_data["name"],
                guild=player_data.get("guild"),
                faction=player_data.get("faction"),
                title=player_data.get("title"),
                location=zone,
                timestamp=datetime.now().isoformat()
            )
            
            # Update collector
            self.collector._update_known_player(encounter)
            
            print(f"      👤 Detected: {player_data['name']} ({player_data.get('guild', 'No Guild')})")
            
            # Small delay for realism
            time.sleep(0.1)
    
    def _show_statistics(self) -> None:
        """Show comprehensive statistics."""
        print("\n" + "-"*60)
        print("📊 STEP 3: COLLECTION STATISTICS")
        print("-"*60)
        
        stats = self.collector.get_player_statistics()
        
        print(f"📈 Overall Statistics:")
        print(f"   • Total Players: {stats['total_players']}")
        print(f"   • Total Encounters: {stats['total_encounters']}")
        print(f"   • Possible NPCs: {stats['possible_npcs']}")
        
        print(f"\n🏛️ Guild Distribution:")
        for guild, count in sorted(stats['guilds'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {guild}: {count} players")
        
        print(f"\n⚔️ Faction Distribution:")
        for faction, count in sorted(stats['factions'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {faction.title()}: {count} players")
        
        print(f"\n👥 Player Details:")
        for player_name, player in list(self.collector.known_players.items())[:10]:
            npc_flag = " (Possible NPC)" if player.possible_npc else ""
            print(f"   • {player.name} - {player.guild or 'No Guild'} - {player.faction or 'Unknown'}{npc_flag}")
            print(f"     Encounters: {player.encounter_count}, Zones: {len(player.zones_seen)}")
    
    def _demonstrate_npc_detection(self) -> None:
        """Demonstrate NPC detection functionality."""
        print("\n" + "-"*60)
        print("🤖 STEP 4: NPC DETECTION DEMONSTRATION")
        print("-"*60)
        
        npc_players = [p for p in self.collector.known_players.values() if p.possible_npc]
        
        if npc_players:
            print("🎯 Detected Possible NPCs:")
            for player in npc_players:
                print(f"   🤖 {player.name}")
                print(f"      Guild: {player.guild or 'Unknown'}")
                print(f"      Faction: {player.faction or 'Unknown'}")
                print(f"      Title: {player.title or 'Unknown'}")
                print(f"      Zones Seen: {', '.join(player.zones_seen)}")
                print(f"      Encounter Count: {player.encounter_count}")
                print()
        else:
            print("📝 No NPCs detected yet (need more cross-zone encounters)")
        
        print("💡 NPC Detection Logic:")
        print("   • Players seen in 3+ different zones are flagged as possible NPCs")
        print("   • This helps distinguish between real players and game NPCs")
        print("   • Useful for data quality and SWGDB intelligence")
    
    def _show_swgdb_export(self) -> None:
        """Show SWGDB export format."""
        print("\n" + "-"*60)
        print("🌐 STEP 5: SWGDB EXPORT FORMAT")
        print("-"*60)
        
        export_data = self.collector.export_for_swgdb()
        
        print("📤 Export Data Structure:")
        print(f"   • Players: {len(export_data['players'])} records")
        print(f"   • Statistics: {len(export_data['statistics'])} metrics")
        print(f"   • Export Timestamp: {export_data['export_timestamp']}")
        
        print(f"\n📋 Sample Player Records:")
        for player in export_data['players'][:3]:
            print(f"   👤 {player['name']}")
            print(f"      Guild: {player.get('guild', 'Unknown')}")
            print(f"      Faction: {player.get('faction', 'Unknown')}")
            print(f"      Title: {player.get('title', 'Unknown')}")
            print(f"      Encounters: {player['encounter_count']}")
            print(f"      Possible NPC: {player['possible_npc']}")
            print(f"      Zones: {', '.join(player['zones_seen'])}")
            print()
        
        print("🎯 Use Cases:")
        print("   • /players endpoint enrichment")
        print("   • /guilds endpoint population")
        print("   • Player activity analytics")
        print("   • Guild and faction statistics")
    
    def _inspect_data_file(self) -> None:
        """Inspect the generated data file."""
        print("\n" + "-"*60)
        print("📁 STEP 6: DATA FILE INSPECTION")
        print("-"*60)
        
        data_file = Path("data/encounters/players_seen.json")
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📄 File: {data_file}")
            print(f"📊 Records: {len(data)}")
            print(f"💾 Size: {data_file.stat().st_size} bytes")
            
            print(f"\n📋 Sample Records:")
            for i, record in enumerate(data[:3]):
                print(f"   {i+1}. {record['name']} - {record.get('guild', 'No Guild')} - {record.get('faction', 'Unknown')}")
                print(f"      Location: {record.get('location', 'Unknown')}")
                print(f"      Encounters: {record.get('encounter_count', 1)}")
                print(f"      Possible NPC: {record.get('possible_npc', False)}")
                print()
        else:
            print("❌ Data file not found")
    
    def cleanup(self) -> None:
        """Cleanup demo resources."""
        self.collector.cleanup()
        logger.info("[DEMO] Cleanup completed")


def main():
    """Run the Batch 149 demo."""
    try:
        demo = PassivePlayerCollectionDemo()
        demo.run_demo()
        demo.cleanup()
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        logger.error(f"[DEMO] Error: {e}")
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    main() 