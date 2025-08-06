#!/usr/bin/env python3
"""
Batch 176 - Seasonal Bounty Leaderboard Reset System
Auto-reset BH leaderboard monthly, archive previous seasons, highlight MVPs
"""

import os
import sys
import json
import yaml
import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import argparse

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from android_ms11.utils.logging_utils import log_event


@dataclass
class BountyHunter:
    """Bounty hunter data structure"""
    name: str
    guild: str
    kills: int = 0
    deaths: int = 0
    total_bounty: int = 0
    specializations: List[str] = None
    last_kill: Optional[str] = None
    last_death: Optional[str] = None
    rank: int = 0
    
    def __post_init__(self):
        if self.specializations is None:
            self.specializations = []
    
    @property
    def kd_ratio(self) -> float:
        """Calculate K/D ratio"""
        if self.deaths == 0:
            return float(self.kills) if self.kills > 0 else 0.0
        return round(self.kills / self.deaths, 2)
    
    @property
    def average_bounty(self) -> float:
        """Calculate average bounty per kill"""
        if self.kills == 0:
            return 0.0
        return round(self.total_bounty / self.kills, 2)


@dataclass
class SeasonStats:
    """Season statistics"""
    total_kills: int = 0
    total_deaths: int = 0
    total_bounty: int = 0
    active_hunters: int = 0
    average_kills: float = 0.0
    average_kd: float = 0.0
    top_guild: Optional[str] = None
    most_active_day: Optional[str] = None
    mvp_hunter: Optional[str] = None
    mvp_kills: int = 0
    mvp_kd: float = 0.0


class SeasonalBountyLeaderboard:
    """Seasonal Bounty Hunter Leaderboard Manager"""
    
    def __init__(self, data_dir: str = "data/bounty"):
        self.data_dir = Path(data_dir)
        self.current_file = self.data_dir / "current_season.json"
        self.history_dir = self.data_dir / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.data_dir / 'bounty_leaderboard.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load or create current season
        self.current_season = self._load_current_season()
    
    def _load_current_season(self) -> Dict[str, Any]:
        """Load current season data or create new one"""
        try:
            if self.current_file.exists():
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.info(f"Loaded current season: {data.get('season', 'Unknown')}")
                    return data
            else:
                return self._create_new_season()
        except Exception as e:
            self.logger.error(f"Error loading current season: {e}")
            return self._create_new_season()
    
    def _create_new_season(self) -> Dict[str, Any]:
        """Create a new season with default data"""
        now = datetime.datetime.now()
        season_number = self._get_next_season_number()
        
        new_season = {
            'season': season_number,
            'start_date': now.strftime('%Y-%m-%d'),
            'end_date': (now.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1),
            'status': 'active',
            'last_updated': now.isoformat(),
            'hunters': [],
            'season_stats': asdict(SeasonStats()),
            'settings': {
                'auto_reset': True,
                'reset_day': 1,
                'reset_month': True,
                'archive_enabled': True,
                'discord_alerts': True,
                'min_kills_for_ranking': 1,
                'mvp_categories': ['most_kills', 'best_kd', 'highest_bounty']
            }
        }
        
        self._save_current_season(new_season)
        self.logger.info(f"Created new season: {season_number}")
        return new_season
    
    def _get_next_season_number(self) -> int:
        """Get the next season number based on existing archives"""
        try:
            existing_seasons = [f for f in self.history_dir.glob("*.json")]
            if not existing_seasons:
                return 1
            
            season_numbers = []
            for season_file in existing_seasons:
                try:
                    # Extract season number from filename (e.g., "2025-08.json" -> 8)
                    season_str = season_file.stem
                    if '-' in season_str:
                        month = int(season_str.split('-')[1])
                        season_numbers.append(month)
                except (ValueError, IndexError):
                    continue
            
            return max(season_numbers) + 1 if season_numbers else 1
        except Exception as e:
            self.logger.error(f"Error getting next season number: {e}")
            return 1
    
    def _save_current_season(self, data: Dict[str, Any]) -> bool:
        """Save current season data"""
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Error saving current season: {e}")
            return False
    
    def add_kill(self, hunter_name: str, guild: str, bounty: int = 3000, 
                 specializations: List[str] = None) -> bool:
        """Add a kill to the current season"""
        try:
            # Find or create hunter
            hunter = self._get_or_create_hunter(hunter_name, guild, specializations)
            
            # Update hunter stats
            hunter.kills += 1
            hunter.total_bounty += bounty
            hunter.last_kill = datetime.datetime.now().isoformat()
            
            # Update hunter in season data
            hunters = self.current_season.get('hunters', [])
            for i, hunter_data in enumerate(hunters):
                if hunter_data.get('name') == hunter_name:
                    hunters[i] = asdict(hunter)
                    break
            
            # Update season stats
            self._update_season_stats()
            
            # Save changes
            self._save_current_season(self.current_season)
            
            self.logger.info(f"Added kill for {hunter_name}: +{bounty} credits")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding kill: {e}")
            return False
    
    def add_death(self, hunter_name: str, guild: str, 
                  specializations: List[str] = None) -> bool:
        """Add a death to the current season"""
        try:
            # Find or create hunter
            hunter = self._get_or_create_hunter(hunter_name, guild, specializations)
            
            # Update hunter stats
            hunter.deaths += 1
            hunter.last_death = datetime.datetime.now().isoformat()
            
            # Update hunter in season data
            hunters = self.current_season.get('hunters', [])
            for i, hunter_data in enumerate(hunters):
                if hunter_data.get('name') == hunter_name:
                    hunters[i] = asdict(hunter)
                    break
            
            # Update season stats
            self._update_season_stats()
            
            # Save changes
            self._save_current_season(self.current_season)
            
            self.logger.info(f"Added death for {hunter_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding death: {e}")
            return False
    
    def _get_or_create_hunter(self, name: str, guild: str, 
                             specializations: List[str] = None) -> BountyHunter:
        """Get existing hunter or create new one"""
        hunters = self.current_season.get('hunters', [])
        
        # Find existing hunter
        for i, hunter_data in enumerate(hunters):
            if hunter_data.get('name') == name:
                # Update existing hunter data
                hunter = BountyHunter(**hunter_data)
                hunters[i] = asdict(hunter)
                self.current_season['hunters'] = hunters
                return hunter
        
        # Create new hunter
        new_hunter = BountyHunter(
            name=name,
            guild=guild,
            specializations=specializations or []
        )
        
        # Add to season
        hunters.append(asdict(new_hunter))
        self.current_season['hunters'] = hunters
        
        return new_hunter
    
    def _update_season_stats(self) -> None:
        """Update season statistics"""
        hunters = [BountyHunter(**h) for h in self.current_season.get('hunters', [])]
        
        if not hunters:
            return
        
        stats = SeasonStats()
        
        # Calculate totals
        stats.total_kills = sum(h.kills for h in hunters)
        stats.total_deaths = sum(h.deaths for h in hunters)
        stats.total_bounty = sum(h.total_bounty for h in hunters)
        stats.active_hunters = len([h for h in hunters if h.kills > 0])
        
        # Calculate averages
        if stats.active_hunters > 0:
            stats.average_kills = round(stats.total_kills / stats.active_hunters, 2)
        
        if stats.total_deaths > 0:
            stats.average_kd = round(stats.total_kills / stats.total_deaths, 2)
        
        # Find top guild
        guild_stats = {}
        for hunter in hunters:
            if hunter.kills > 0:
                guild_stats[hunter.guild] = guild_stats.get(hunter.guild, 0) + hunter.kills
        
        if guild_stats:
            stats.top_guild = max(guild_stats, key=guild_stats.get)
        
        # Find MVP hunter (most kills)
        if hunters:
            mvp = max(hunters, key=lambda h: h.kills)
            stats.mvp_hunter = mvp.name
            stats.mvp_kills = mvp.kills
            stats.mvp_kd = mvp.kd_ratio
        
        # Update season
        self.current_season['season_stats'] = asdict(stats)
        self.current_season['last_updated'] = datetime.datetime.now().isoformat()
    
    def check_season_reset(self) -> bool:
        """Check if season reset is needed"""
        try:
            settings = self.current_season.get('settings', {})
            
            if not settings.get('auto_reset', True):
                return False
            
            now = datetime.datetime.now()
            reset_day = settings.get('reset_day', 1)
            
            # Check if it's reset day
            if now.day == reset_day:
                # Check if we haven't already reset this month
                last_updated = self.current_season.get('last_updated')
                if last_updated:
                    last_update = datetime.datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    if last_update.month == now.month and last_update.year == now.year:
                        return False
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking season reset: {e}")
            return False
    
    def perform_season_reset(self) -> bool:
        """Perform season reset and archive current season"""
        try:
            if not self.check_season_reset():
                self.logger.info("No season reset needed")
                return False
            
            self.logger.info("Performing season reset...")
            
            # Archive current season
            archive_success = self._archive_current_season()
            if not archive_success:
                self.logger.error("Failed to archive current season")
                return False
            
            # Create new season
            new_season = self._create_new_season()
            self.current_season = new_season
            
            # Send notifications
            self._send_reset_notifications()
            
            self.logger.info("Season reset completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing season reset: {e}")
            return False
    
    def _archive_current_season(self) -> bool:
        """Archive current season to history"""
        try:
            if not self.current_season.get('hunters'):
                self.logger.info("No hunters to archive")
                return True
            
            # Create archive filename
            start_date = self.current_season.get('start_date', '')
            if start_date:
                year, month = start_date.split('-')[:2]
                archive_filename = f"{year}-{month}.json"
            else:
                archive_filename = f"season_{self.current_season.get('season', 'unknown')}.json"
            
            archive_path = self.history_dir / archive_filename
            
            # Prepare archive data
            archive_data = {
                'season_info': {
                    'season': self.current_season.get('season'),
                    'start_date': self.current_season.get('start_date'),
                    'end_date': self.current_season.get('end_date'),
                    'status': 'archived',
                    'archived_at': datetime.datetime.now().isoformat()
                },
                'hunters': self.current_season.get('hunters', []),
                'season_stats': self.current_season.get('season_stats', {}),
                'mvp_highlights': self._generate_mvp_highlights()
            }
            
            # Save archive
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, indent=2, default=str)
            
            self.logger.info(f"Archived season to: {archive_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error archiving season: {e}")
            return False
    
    def _generate_mvp_highlights(self) -> Dict[str, Any]:
        """Generate MVP highlights for the season"""
        try:
            hunters = [BountyHunter(**h) for h in self.current_season.get('hunters', [])]
            
            if not hunters:
                return {}
            
            # Find MVPs in different categories
            mvp_highlights = {
                'most_kills': None,
                'best_kd_ratio': None,
                'highest_bounty': None,
                'most_active': None
            }
            
            # Most kills
            if hunters:
                most_kills = max(hunters, key=lambda h: h.kills)
                if most_kills.kills > 0:
                    mvp_highlights['most_kills'] = {
                        'name': most_kills.name,
                        'guild': most_kills.guild,
                        'kills': most_kills.kills,
                        'total_bounty': most_kills.total_bounty
                    }
            
            # Best K/D ratio (minimum 1 kill)
            kd_hunters = [h for h in hunters if h.kills >= 1]
            if kd_hunters:
                best_kd = max(kd_hunters, key=lambda h: h.kd_ratio)
                mvp_highlights['best_kd_ratio'] = {
                    'name': best_kd.name,
                    'guild': best_kd.guild,
                    'kd_ratio': best_kd.kd_ratio,
                    'kills': best_kd.kills,
                    'deaths': best_kd.deaths
                }
            
            # Highest total bounty
            if hunters:
                highest_bounty = max(hunters, key=lambda h: h.total_bounty)
                if highest_bounty.total_bounty > 0:
                    mvp_highlights['highest_bounty'] = {
                        'name': highest_bounty.name,
                        'guild': highest_bounty.guild,
                        'total_bounty': highest_bounty.total_bounty,
                        'kills': highest_bounty.kills
                    }
            
            # Most active (most recent activity)
            active_hunters = [h for h in hunters if h.last_kill or h.last_death]
            if active_hunters:
                most_active = max(active_hunters, key=lambda h: h.last_kill or h.last_death or '')
                mvp_highlights['most_active'] = {
                    'name': most_active.name,
                    'guild': most_active.guild,
                    'last_activity': most_active.last_kill or most_active.last_death
                }
            
            return mvp_highlights
            
        except Exception as e:
            self.logger.error(f"Error generating MVP highlights: {e}")
            return {}
    
    def _send_reset_notifications(self) -> None:
        """Send notifications about season reset"""
        try:
            # Log reset event
            log_event("🎯 BH Leaderboard: Season reset completed")
            
            # TODO: Add Discord integration if needed
            # TODO: Add email notifications if needed
            
        except Exception as e:
            self.logger.error(f"Error sending reset notifications: {e}")
    
    def get_current_leaderboard(self) -> List[Dict[str, Any]]:
        """Get current leaderboard sorted by kills"""
        try:
            hunters = [BountyHunter(**h) for h in self.current_season.get('hunters', [])]
            
            # Sort by kills (descending), then by K/D ratio
            sorted_hunters = sorted(
                hunters,
                key=lambda h: (h.kills, h.kd_ratio),
                reverse=True
            )
            
            # Add ranks and ensure kd_ratio is included
            for i, hunter in enumerate(sorted_hunters, 1):
                hunter.rank = i
            
            return [asdict(h) for h in sorted_hunters]
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return []
    
    def get_season_history(self) -> List[Dict[str, Any]]:
        """Get list of archived seasons"""
        try:
            history = []
            for archive_file in self.history_dir.glob("*.json"):
                try:
                    with open(archive_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        history.append({
                            'filename': archive_file.name,
                            'season_info': data.get('season_info', {}),
                            'mvp_highlights': data.get('mvp_highlights', {})
                        })
                except Exception as e:
                    self.logger.error(f"Error reading archive {archive_file}: {e}")
            
            # Sort by season number (descending)
            history.sort(key=lambda x: x['season_info'].get('season', 0), reverse=True)
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting season history: {e}")
            return []


def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Seasonal Bounty Leaderboard Reset System")
    parser.add_argument("--reset", action="store_true", help="Force season reset")
    parser.add_argument("--check", action="store_true", help="Check if reset is needed")
    parser.add_argument("--add-kill", nargs=3, metavar=("NAME", "GUILD", "BOUNTY"), 
                       help="Add a kill to current season")
    parser.add_argument("--add-death", nargs=2, metavar=("NAME", "GUILD"), 
                       help="Add a death to current season")
    parser.add_argument("--leaderboard", action="store_true", help="Show current leaderboard")
    parser.add_argument("--history", action="store_true", help="Show season history")
    parser.add_argument("--mvp", action="store_true", help="Show current MVP highlights")
    
    args = parser.parse_args()
    
    # Initialize leaderboard
    leaderboard = SeasonalBountyLeaderboard()
    
    try:
        if args.reset:
            if leaderboard.perform_season_reset():
                print("✅ Season reset completed successfully")
            else:
                print("ℹ️ No season reset performed")
        
        elif args.check:
            if leaderboard.check_season_reset():
                print("🔄 Season reset needed")
            else:
                print("ℹ️ No season reset needed")
        
        elif args.add_kill:
            name, guild, bounty = args.add_kill
            if leaderboard.add_kill(name, guild, int(bounty)):
                print(f"✅ Added kill for {name}")
            else:
                print(f"❌ Failed to add kill for {name}")
        
        elif args.add_death:
            name, guild = args.add_death
            if leaderboard.add_death(name, guild):
                print(f"✅ Added death for {name}")
            else:
                print(f"❌ Failed to add death for {name}")
        
        elif args.leaderboard:
            hunters = leaderboard.get_current_leaderboard()
            if hunters:
                print("\n🏆 Current Bounty Hunter Leaderboard:")
                print("-" * 60)
                for hunter in hunters[:10]:  # Top 10
                    print(f"{hunter['rank']:2d}. {hunter['name']:<15} "
                          f"({hunter['guild']:<15}) "
                          f"Kills: {hunter['kills']:2d} "
                          f"K/D: {hunter['kd_ratio']:4.2f} "
                          f"Bounty: {hunter['total_bounty']:,}")
            else:
                print("No hunters in current season")
        
        elif args.history:
            history = leaderboard.get_season_history()
            if history:
                print("\n📚 Season History:")
                print("-" * 60)
                for season in history:
                    info = season['season_info']
                    print(f"Season {info.get('season', 'Unknown')} "
                          f"({info.get('start_date', 'Unknown')} - {info.get('end_date', 'Unknown')})")
            else:
                print("No archived seasons found")
        
        elif args.mvp:
            mvp_highlights = leaderboard._generate_mvp_highlights()
            if mvp_highlights:
                print("\n🏅 Current Season MVP Highlights:")
                print("-" * 60)
                for category, mvp in mvp_highlights.items():
                    if mvp:
                        print(f"{category.replace('_', ' ').title()}: {mvp['name']} ({mvp['guild']})")
            else:
                print("No MVP data available")
        
        else:
            # Default: check for reset
            if leaderboard.check_season_reset():
                print("🔄 Season reset needed - run with --reset to perform reset")
            else:
                print("ℹ️ No season reset needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 