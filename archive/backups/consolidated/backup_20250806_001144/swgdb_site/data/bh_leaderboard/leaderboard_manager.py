#!/usr/bin/env python3
"""
Bounty Hunter Leaderboard Manager
Handles seasonal resets, archiving, and Discord notifications
"""

import os
import yaml
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

class BHLeaderboardManager:
    def __init__(self, data_dir: str = "swgdb_site/data/bh_leaderboard"):
        self.data_dir = Path(data_dir)
        self.current_file = self.data_dir / "current_season.yml"
        self.seasons_dir = self.data_dir / "seasons"
        self.seasons_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.data_dir / 'leaderboard.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_current_season(self) -> Dict:
        """Load current season data"""
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"Current season file not found: {self.current_file}")
            return self._create_new_season()
        except Exception as e:
            self.logger.error(f"Error loading current season: {e}")
            return self._create_new_season()
    
    def _create_new_season(self) -> Dict:
        """Create a new season with default data"""
        now = datetime.datetime.now()
        season_number = self._get_next_season_number()
        
        new_season = {
            'season': season_number,
            'start_date': now.strftime('%Y-%m-%d'),
            'end_date': (now.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1),
            'status': 'active',
            'last_updated': now.isoformat(),
            'entries': [],
            'season_stats': {
                'total_kills': 0,
                'total_bounty': 0,
                'active_hunters': 0,
                'average_kills': 0.0,
                'top_guild': None,
                'most_active_day': None
            },
            'settings': {
                'auto_reset': True,
                'reset_day': 1,
                'reset_month': True,
                'archive_enabled': True,
                'discord_alerts': True,
                'min_kills_for_ranking': 1
            }
        }
        
        self.save_current_season(new_season)
        return new_season
    
    def _get_next_season_number(self) -> int:
        """Get the next season number based on existing archives"""
        try:
            existing_seasons = [f for f in self.seasons_dir.glob("season_*.yml")]
            if not existing_seasons:
                return 1
            
            season_numbers = []
            for season_file in existing_seasons:
                try:
                    season_num = int(season_file.stem.split('_')[1])
                    season_numbers.append(season_num)
                except (ValueError, IndexError):
                    continue
            
            return max(season_numbers) + 1 if season_numbers else 1
        except Exception as e:
            self.logger.error(f"Error getting next season number: {e}")
            return 1
    
    def save_current_season(self, data: Dict) -> bool:
        """Save current season data"""
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            self.logger.info(f"Saved current season data")
            return True
        except Exception as e:
            self.logger.error(f"Error saving current season: {e}")
            return False
    
    def add_kill(self, hunter_name: str, guild: str, bounty: int = 3000, 
                 specializations: List[str] = None) -> bool:
        """Add a kill to the current season"""
        try:
            current_data = self.load_current_season()
            
            # Find existing hunter or create new entry
            hunter_entry = None
            for entry in current_data['entries']:
                if entry['name'] == hunter_name:
                    hunter_entry = entry
                    break
            
            if hunter_entry:
                # Update existing hunter
                hunter_entry['kills'] += 1
                hunter_entry['total_bounty'] += bounty
                hunter_entry['last_kill'] = datetime.datetime.now().isoformat()
            else:
                # Create new hunter entry
                hunter_entry = {
                    'name': hunter_name,
                    'kills': 1,
                    'guild': guild,
                    'rank': 0,  # Will be calculated
                    'last_kill': datetime.datetime.now().isoformat(),
                    'total_bounty': bounty,
                    'specializations': specializations or ['jedi_hunter']
                }
                current_data['entries'].append(hunter_entry)
            
            # Update season stats
            self._update_season_stats(current_data)
            
            # Recalculate ranks
            self._calculate_ranks(current_data)
            
            # Save updated data
            return self.save_current_season(current_data)
            
        except Exception as e:
            self.logger.error(f"Error adding kill: {e}")
            return False
    
    def _update_season_stats(self, data: Dict) -> None:
        """Update season statistics"""
        entries = data['entries']
        if not entries:
            return
        
        total_kills = sum(entry['kills'] for entry in entries)
        total_bounty = sum(entry['total_bounty'] for entry in entries)
        active_hunters = len(entries)
        
        # Find top guild
        guild_counts = {}
        for entry in entries:
            guild = entry['guild']
            guild_counts[guild] = guild_counts.get(guild, 0) + entry['kills']
        
        top_guild = max(guild_counts.items(), key=lambda x: x[1])[0] if guild_counts else None
        
        # Find most active day (simplified - could be enhanced)
        most_active_day = None
        if entries:
            most_active_day = max(entries, key=lambda x: x['kills'])['last_kill'][:10]
        
        data['season_stats'] = {
            'total_kills': total_kills,
            'total_bounty': total_bounty,
            'active_hunters': active_hunters,
            'average_kills': round(total_kills / active_hunters, 1) if active_hunters > 0 else 0.0,
            'top_guild': top_guild,
            'most_active_day': most_active_day
        }
        
        data['last_updated'] = datetime.datetime.now().isoformat()
    
    def _calculate_ranks(self, data: Dict) -> None:
        """Calculate ranks based on kills"""
        entries = data['entries']
        if not entries:
            return
        
        # Sort by kills (descending), then by total bounty (descending)
        sorted_entries = sorted(entries, key=lambda x: (x['kills'], x['total_bounty']), reverse=True)
        
        # Assign ranks
        for i, entry in enumerate(sorted_entries):
            entry['rank'] = i + 1
        
        # Update the entries list
        data['entries'] = sorted_entries
    
    def check_season_reset(self) -> bool:
        """Check if season should be reset and perform reset if needed"""
        try:
            current_data = self.load_current_season()
            settings = current_data.get('settings', {})
            
            if not settings.get('auto_reset', True):
                return False
            
            now = datetime.datetime.now()
            end_date = datetime.datetime.strptime(current_data['end_date'], '%Y-%m-%d')
            
            if now >= end_date:
                self.logger.info(f"Season {current_data['season']} has ended, performing reset")
                return self._perform_season_reset(current_data)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking season reset: {e}")
            return False
    
    def _perform_season_reset(self, current_data: Dict) -> bool:
        """Perform season reset and archive old season"""
        try:
            # Archive current season
            season_num = current_data['season']
            archive_file = self.seasons_dir / f"season_{season_num:02d}.yml"
            
            # Add winner information
            if current_data['entries']:
                winner = current_data['entries'][0]  # Top ranked player
                current_data['winner'] = {
                    'name': winner['name'],
                    'guild': winner['guild'],
                    'kills': winner['kills'],
                    'total_bounty': winner['total_bounty'],
                    'specializations': winner.get('specializations', [])
                }
            
            # Mark as archived
            current_data['status'] = 'archived'
            current_data['archived_date'] = datetime.datetime.now().isoformat()
            
            # Save archived season
            with open(archive_file, 'w', encoding='utf-8') as f:
                yaml.dump(current_data, f, default_flow_style=False, sort_keys=False)
            
            self.logger.info(f"Archived season {season_num} to {archive_file}")
            
            # Send Discord notification
            if current_data.get('settings', {}).get('discord_alerts', True):
                self._send_discord_notification(current_data)
            
            # Create new season
            new_season = self._create_new_season()
            self.logger.info(f"Created new season {new_season['season']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing season reset: {e}")
            return False
    
    def _send_discord_notification(self, archived_data: Dict) -> None:
        """Send Discord notification about season reset"""
        try:
            # This would integrate with your Discord bot
            # For now, just log the notification
            winner = archived_data.get('winner', {})
            season_num = archived_data['season']
            
            message = f"🏆 New BH Season Started: Top Jedi Killers Wanted!\n"
            message += f"Season {season_num} has ended!\n"
            
            if winner:
                message += f"🏅 Winner: {winner['name']} ({winner['guild']}) - {winner['kills']} kills\n"
            
            message += f"Season {season_num + 1} is now active - start hunting!"
            
            self.logger.info(f"Discord notification: {message}")
            
            # TODO: Integrate with actual Discord bot
            # discord_bot.send_message(channel_id, message)
            
        except Exception as e:
            self.logger.error(f"Error sending Discord notification: {e}")
    
    def get_season_history(self) -> List[Dict]:
        """Get list of all archived seasons"""
        try:
            seasons = []
            for season_file in self.seasons_dir.glob("season_*.yml"):
                try:
                    with open(season_file, 'r', encoding='utf-8') as f:
                        season_data = yaml.safe_load(f)
                        seasons.append(season_data)
                except Exception as e:
                    self.logger.error(f"Error loading season file {season_file}: {e}")
            
            # Sort by season number
            seasons.sort(key=lambda x: x['season'], reverse=True)
            return seasons
            
        except Exception as e:
            self.logger.error(f"Error getting season history: {e}")
            return []
    
    def get_hunter_stats(self, hunter_name: str) -> Optional[Dict]:
        """Get comprehensive stats for a specific hunter"""
        try:
            current_data = self.load_current_season()
            all_seasons = self.get_season_history()
            all_seasons.append(current_data)
            
            hunter_stats = {
                'name': hunter_name,
                'current_season': None,
                'all_time': {
                    'total_kills': 0,
                    'total_bounty': 0,
                    'seasons_played': 0,
                    'best_rank': None,
                    'best_season': None
                },
                'season_history': []
            }
            
            for season in all_seasons:
                for entry in season.get('entries', []):
                    if entry['name'] == hunter_name:
                        # Current season
                        if season['status'] == 'active':
                            hunter_stats['current_season'] = entry
                        
                        # All-time stats
                        hunter_stats['all_time']['total_kills'] += entry['kills']
                        hunter_stats['all_time']['total_bounty'] += entry['total_bounty']
                        hunter_stats['all_time']['seasons_played'] += 1
                        
                        # Track best rank
                        if (hunter_stats['all_time']['best_rank'] is None or 
                            entry['rank'] < hunter_stats['all_time']['best_rank']):
                            hunter_stats['all_time']['best_rank'] = entry['rank']
                            hunter_stats['all_time']['best_season'] = season['season']
                        
                        # Season history
                        hunter_stats['season_history'].append({
                            'season': season['season'],
                            'kills': entry['kills'],
                            'rank': entry['rank'],
                            'bounty': entry['total_bounty'],
                            'guild': entry['guild']
                        })
                        break
            
            return hunter_stats if hunter_stats['all_time']['seasons_played'] > 0 else None
            
        except Exception as e:
            self.logger.error(f"Error getting hunter stats: {e}")
            return None

def main():
    """Main function for testing and manual operations"""
    manager = BHLeaderboardManager()
    
    # Check for season reset
    if manager.check_season_reset():
        print("Season reset performed")
    else:
        print("No season reset needed")
    
    # Example: Add a kill
    # manager.add_kill("TestHunter", "TestGuild", 3000, ["jedi_hunter", "marksman"])
    
    # Get current season data
    current = manager.load_current_season()
    print(f"Current season: {current['season']}")
    print(f"Active hunters: {current['season_stats']['active_hunters']}")

if __name__ == "__main__":
    main() 