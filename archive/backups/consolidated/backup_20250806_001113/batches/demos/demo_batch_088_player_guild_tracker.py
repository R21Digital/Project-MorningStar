#!/usr/bin/env python3
"""
Demo script for Batch 088 - Guild Tracker + Player Lookup Tool

This script demonstrates the player and guild tracking functionality by:
1. Creating sample player and guild data
2. Testing search and lookup functionality
3. Starting the dashboard server for web interface testing
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.player_guild_tracker import (
    PlayerGuildTracker, PlayerData, GuildMemberData, 
    EnhancedGuildData, PlayerStatus, ProfessionType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_players():
    """Create sample player data for testing."""
    logger.info("Creating sample player data...")
    
    sample_players = [
        PlayerData(
            name="CommanderRex",
            title="Master Commando",
            guild="GalacticDefenders",
            guild_tag="GDEF",
            profession="commando",
            profession_type="combat",
            level=90,
            faction="rebel",
            city="Theed",
            planet="naboo",
            location="Theed Palace",
            last_seen=datetime.now().isoformat(),
            status="online",
            playtime_hours=1200,
            achievements=["Master Commando", "Hero of Naboo", "Elite Defender"],
            skills={
                "Rifle": 4000,
                "Heavy Weapons": 4000,
                "Unarmed": 4000,
                "Tactics": 4000
            },
            equipment={
                "Weapon": "DC-15 Rifle",
                "Armor": "Commando Armor",
                "Backpack": "Tactical Pack"
            },
            notes="Elite commando unit leader"
        ),
        PlayerData(
            name="ArtisanCraft",
            title="Master Artisan",
            guild="CraftersGuild",
            guild_tag="CRAFT",
            profession="artisan",
            profession_type="crafting",
            level=85,
            faction="neutral",
            city="Coronet",
            planet="corellia",
            location="Crafting Station",
            last_seen=(datetime.now() - timedelta(hours=2)).isoformat(),
            status="offline",
            playtime_hours=800,
            achievements=["Master Artisan", "Crafting Expert", "Resource Master"],
            skills={
                "Engineering": 4000,
                "Science": 4000,
                "Surveying": 4000
            },
            equipment={
                "Tool": "Advanced Crafting Tool",
                "Backpack": "Resource Pack"
            },
            notes="Specializes in weapon crafting"
        ),
        PlayerData(
            name="DoctorHeal",
            title="Chief Medical Officer",
            guild="HealersUnited",
            guild_tag="HEAL",
            profession="doctor",
            profession_type="social",
            level=88,
            faction="neutral",
            city="Theed",
            planet="naboo",
            location="Medical Center",
            last_seen=(datetime.now() - timedelta(minutes=30)).isoformat(),
            status="online",
            playtime_hours=950,
            achievements=["Master Doctor", "Healing Expert", "Medical Pioneer"],
            skills={
                "Healing": 4000,
                "Medical": 4000,
                "Biology": 4000
            },
            equipment={
                "Tool": "Medical Scanner",
                "Backpack": "Medical Supplies"
            },
            notes="Specializes in advanced healing techniques"
        ),
        PlayerData(
            name="SmugglerHan",
            title="Legendary Smuggler",
            guild="Freetraders",
            guild_tag="FREE",
            profession="smuggler",
            profession_type="combat",
            level=92,
            faction="neutral",
            city="Mos Eisley",
            planet="tatooine",
            location="Cantina",
            last_seen=(datetime.now() - timedelta(hours=1)).isoformat(),
            status="online",
            playtime_hours=1500,
            achievements=["Master Smuggler", "Legendary Pilot", "Underworld King"],
            skills={
                "Pistol": 4000,
                "Pilot": 4000,
                "Smuggling": 4000
            },
            equipment={
                "Weapon": "DL-44 Blaster",
                "Ship": "Millennium Falcon",
                "Backpack": "Smuggler's Pack"
            },
            notes="Famous smuggler with a heart of gold"
        ),
        PlayerData(
            name="JediKnight",
            title="Jedi Knight",
            guild="JediOrder",
            guild_tag="JEDI",
            profession="jedi",
            profession_type="hybrid",
            level=95,
            faction="rebel",
            city="Anchorhead",
            planet="tatooine",
            location="Jedi Temple",
            last_seen=(datetime.now() - timedelta(days=1)).isoformat(),
            status="offline",
            playtime_hours=2000,
            achievements=["Jedi Knight", "Force Master", "Lightsaber Expert"],
            skills={
                "Lightsaber": 4000,
                "Force": 4000,
                "Meditation": 4000
            },
            equipment={
                "Weapon": "Blue Lightsaber",
                "Robe": "Jedi Robes",
                "Backpack": "Force Pack"
            },
            notes="Guardian of peace and justice"
        )
    ]
    
    return sample_players


def create_sample_guilds():
    """Create sample guild data for testing."""
    logger.info("Creating sample guild data...")
    
    sample_guilds = [
        EnhancedGuildData(
            name="Galactic Defenders",
            tag="GDEF",
            faction="rebel",
            leader="CommanderRex",
            members_total=45,
            members_active=32,
            active_percentage=71.1,
            description="Elite military unit dedicated to protecting the galaxy from Imperial tyranny",
            website="https://galacticdefenders.com",
            recruitment_status="open",
            city="Theed",
            planet="naboo",
            founded_date="2023-01-15",
            last_updated=datetime.now().isoformat(),
            members=[
                GuildMemberData(
                    name="CommanderRex",
                    rank="Leader",
                    join_date="2023-01-15",
                    last_active=datetime.now().isoformat(),
                    profession="commando",
                    level=90,
                    contribution=1000
                ),
                GuildMemberData(
                    name="SniperShot",
                    rank="Officer",
                    join_date="2023-02-01",
                    last_active=(datetime.now() - timedelta(hours=3)).isoformat(),
                    profession="marksman",
                    level=85,
                    contribution=750
                ),
                GuildMemberData(
                    name="TankDriver",
                    rank="Member",
                    join_date="2023-03-10",
                    last_active=(datetime.now() - timedelta(days=1)).isoformat(),
                    profession="officer",
                    level=82,
                    contribution=500
                )
            ],
            territories=["Naboo", "Corellia", "Tatooine"],
            achievements=["Elite Unit", "Heroic Defenders", "Galactic Heroes"]
        ),
        EnhancedGuildData(
            name="Crafters Guild",
            tag="CRAFT",
            faction="neutral",
            leader="ArtisanCraft",
            members_total=28,
            members_active=18,
            active_percentage=64.3,
            description="Master craftsmen and artisans dedicated to creating the finest goods in the galaxy",
            website="https://craftersguild.org",
            recruitment_status="invite",
            city="Coronet",
            planet="corellia",
            founded_date="2022-11-20",
            last_updated=datetime.now().isoformat(),
            members=[
                GuildMemberData(
                    name="ArtisanCraft",
                    rank="Leader",
                    join_date="2022-11-20",
                    last_active=(datetime.now() - timedelta(hours=2)).isoformat(),
                    profession="artisan",
                    level=85,
                    contribution=1200
                ),
                GuildMemberData(
                    name="WeaponSmith",
                    rank="Officer",
                    join_date="2022-12-05",
                    last_active=(datetime.now() - timedelta(hours=5)).isoformat(),
                    profession="weaponsmith",
                    level=88,
                    contribution=900
                ),
                GuildMemberData(
                    name="ArmorMaker",
                    rank="Member",
                    join_date="2023-01-10",
                    last_active=(datetime.now() - timedelta(days=2)).isoformat(),
                    profession="armorsmith",
                    level=80,
                    contribution=600
                )
            ],
            territories=["Corellia", "Naboo"],
            achievements=["Master Crafters", "Quality Guaranteed", "Artisan Excellence"]
        ),
        EnhancedGuildData(
            name="Healers United",
            tag="HEAL",
            faction="neutral",
            leader="DoctorHeal",
            members_total=35,
            members_active=25,
            active_percentage=71.4,
            description="Medical professionals dedicated to healing and helping others across the galaxy",
            website="https://healersunited.net",
            recruitment_status="open",
            city="Theed",
            planet="naboo",
            founded_date="2023-02-10",
            last_updated=datetime.now().isoformat(),
            members=[
                GuildMemberData(
                    name="DoctorHeal",
                    rank="Leader",
                    join_date="2023-02-10",
                    last_active=(datetime.now() - timedelta(minutes=30)).isoformat(),
                    profession="doctor",
                    level=88,
                    contribution=1100
                ),
                GuildMemberData(
                    name="NurseCare",
                    rank="Officer",
                    join_date="2023-02-15",
                    last_active=(datetime.now() - timedelta(hours=1)).isoformat(),
                    profession="doctor",
                    level=82,
                    contribution=800
                ),
                GuildMemberData(
                    name="MedicQuick",
                    rank="Member",
                    join_date="2023-03-01",
                    last_active=(datetime.now() - timedelta(hours=4)).isoformat(),
                    profession="combat_medic",
                    level=78,
                    contribution=500
                )
            ],
            territories=["Naboo", "Corellia"],
            achievements=["Healing Masters", "Medical Excellence", "Life Savers"]
        ),
        EnhancedGuildData(
            name="Freetraders",
            tag="FREE",
            faction="neutral",
            leader="SmugglerHan",
            members_total=22,
            members_active=15,
            active_percentage=68.2,
            description="Independent traders and smugglers operating outside Imperial control",
            website="https://freetraders.org",
            recruitment_status="closed",
            city="Mos Eisley",
            planet="tatooine",
            founded_date="2022-09-15",
            last_updated=datetime.now().isoformat(),
            members=[
                GuildMemberData(
                    name="SmugglerHan",
                    rank="Leader",
                    join_date="2022-09-15",
                    last_active=(datetime.now() - timedelta(hours=1)).isoformat(),
                    profession="smuggler",
                    level=92,
                    contribution=1500
                ),
                GuildMemberData(
                    name="PilotChewie",
                    rank="Officer",
                    join_date="2022-09-20",
                    last_active=(datetime.now() - timedelta(hours=2)).isoformat(),
                    profession="pilot",
                    level=85,
                    contribution=1000
                ),
                GuildMemberData(
                    name="TraderLando",
                    rank="Member",
                    join_date="2022-10-01",
                    last_active=(datetime.now() - timedelta(days=1)).isoformat(),
                    profession="merchant",
                    level=80,
                    contribution=700
                )
            ],
            territories=["Tatooine", "Corellia"],
            achievements=["Smuggling Legends", "Trade Masters", "Freedom Fighters"]
        ),
        EnhancedGuildData(
            name="Jedi Order",
            tag="JEDI",
            faction="rebel",
            leader="JediKnight",
            members_total=15,
            members_active=8,
            active_percentage=53.3,
            description="Ancient order of Force-sensitive warriors dedicated to peace and justice",
            website="https://jediorder.org",
            recruitment_status="invite",
            city="Anchorhead",
            planet="tatooine",
            founded_date="2022-06-01",
            last_updated=datetime.now().isoformat(),
            members=[
                GuildMemberData(
                    name="JediKnight",
                    rank="Master",
                    join_date="2022-06-01",
                    last_active=(datetime.now() - timedelta(days=1)).isoformat(),
                    profession="jedi",
                    level=95,
                    contribution=2000
                ),
                GuildMemberData(
                    name="PadawanLuke",
                    rank="Knight",
                    join_date="2022-08-15",
                    last_active=(datetime.now() - timedelta(hours=6)).isoformat(),
                    profession="jedi",
                    level=75,
                    contribution=600
                ),
                GuildMemberData(
                    name="ForceSage",
                    rank="Knight",
                    join_date="2022-09-01",
                    last_active=(datetime.now() - timedelta(days=2)).isoformat(),
                    profession="jedi",
                    level=82,
                    contribution=800
                )
            ],
            territories=["Tatooine"],
            achievements=["Force Masters", "Guardians of Peace", "Lightsaber Legends"]
        )
    ]
    
    return sample_guilds


def test_player_guild_tracker():
    """Test the player/guild tracker functionality."""
    logger.info("Testing player/guild tracker functionality...")
    
    # Initialize tracker
    tracker = PlayerGuildTracker()
    
    # Create sample data
    players = create_sample_players()
    guilds = create_sample_guilds()
    
    # Save sample data
    for player in players:
        tracker._save_player_data(player)
        logger.info(f"Saved player: {player.name}")
    
    for guild in guilds:
        tracker._save_guild_data(guild)
        logger.info(f"Saved guild: {guild.name} [{guild.tag}]")
    
    # Test player search
    logger.info("\n--- Testing Player Search ---")
    search_results = tracker.search_players("commando")
    logger.info(f"Found {len(search_results)} players matching 'commando'")
    for result in search_results[:3]:
        logger.info(f"  - {result.player.name} (Score: {result.relevance_score:.1f})")
    
    # Test guild search
    logger.info("\n--- Testing Guild Search ---")
    guild_results = tracker.search_guilds("rebel")
    logger.info(f"Found {len(guild_results)} guilds matching 'rebel'")
    for result in guild_results[:3]:
        logger.info(f"  - {result.guild.name} [{result.guild.tag}] (Score: {result.relevance_score:.1f})")
    
    # Test player lookup
    logger.info("\n--- Testing Player Lookup ---")
    player = tracker.get_player("CommanderRex")
    if player:
        logger.info(f"Found player: {player.name} - {player.profession} Level {player.level}")
    
    # Test guild lookup
    logger.info("\n--- Testing Guild Lookup ---")
    guild = tracker.get_guild("GDEF")
    if guild:
        logger.info(f"Found guild: {guild.name} [{guild.tag}] - {guild.members_total} members")
    
    # Test statistics
    logger.info("\n--- Testing Statistics ---")
    stats = tracker.get_statistics()
    logger.info(f"Total players: {stats['total_players']}")
    logger.info(f"Online players: {stats['online_players']}")
    logger.info(f"Total guilds: {stats['total_guilds']}")
    logger.info(f"Active guilds: {stats['active_guilds']}")
    
    logger.info("\nPlayer/Guild tracker testing completed successfully!")


def start_dashboard_server():
    """Start the dashboard server for web interface testing."""
    logger.info("Starting dashboard server...")
    
    try:
        from dashboard.app import app
        logger.info("Dashboard server starting on http://127.0.0.1:8000")
        logger.info("Available pages:")
        logger.info("  - http://127.0.0.1:8000/players (Player Lookup)")
        logger.info("  - http://127.0.0.1:8000/guilds (Guild Tracker)")
        logger.info("  - http://127.0.0.1:8000/players/CommanderRex (Sample Player)")
        logger.info("  - http://127.0.0.1:8000/guilds/GDEF (Sample Guild)")
        
        app.run(host="127.0.0.1", port=8000, debug=True)
        
    except ImportError as e:
        logger.error(f"Failed to import dashboard app: {e}")
        logger.info("Make sure the dashboard app is properly configured")
    except Exception as e:
        logger.error(f"Failed to start dashboard server: {e}")


def main():
    """Main demo function."""
    logger.info("Starting Batch 088 Player/Guild Tracker Demo")
    
    # Test tracker functionality
    test_player_guild_tracker()
    
    # Start dashboard server
    logger.info("\nStarting web interface...")
    start_dashboard_server()


if __name__ == "__main__":
    main() 