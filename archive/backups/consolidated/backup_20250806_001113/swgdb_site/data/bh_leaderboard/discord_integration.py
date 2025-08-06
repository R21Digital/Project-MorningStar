#!/usr/bin/env python3
"""
Discord Bot Integration for Bounty Hunter Leaderboard
Handles notifications and alerts for season resets and achievements
"""

import discord
from discord.ext import commands
import asyncio
import datetime
from typing import Optional, Dict, List
import logging
from pathlib import Path

# Import the leaderboard manager
import sys
sys.path.append(str(Path(__file__).parent))
from leaderboard_manager import BHLeaderboardManager

class BHLeaderboardBot(commands.Bot):
    def __init__(self, token: str, channel_id: int):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(command_prefix='!bh ', intents=intents)
        self.token = token
        self.channel_id = channel_id
        self.manager = BHLeaderboardManager()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Register commands
        self.add_commands()
    
    def add_commands(self):
        """Add bot commands"""
        
        @self.command(name='leaderboard')
        async def show_leaderboard(ctx):
            """Show current season leaderboard"""
            try:
                current_data = self.manager.load_current_season()
                embed = self.create_leaderboard_embed(current_data)
                await ctx.send(embed=embed)
            except Exception as e:
                self.logger.error(f"Error showing leaderboard: {e}")
                await ctx.send("❌ Error loading leaderboard")
        
        @self.command(name='stats')
        async def show_stats(ctx, hunter_name: str = None):
            """Show stats for a specific hunter or overall stats"""
            try:
                if hunter_name:
                    stats = self.manager.get_hunter_stats(hunter_name)
                    if stats:
                        embed = self.create_hunter_stats_embed(stats)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"❌ No stats found for {hunter_name}")
                else:
                    current_data = self.manager.load_current_season()
                    embed = self.create_season_stats_embed(current_data)
                    await ctx.send(embed=embed)
            except Exception as e:
                self.logger.error(f"Error showing stats: {e}")
                await ctx.send("❌ Error loading stats")
        
        @self.command(name='addkill')
        async def add_kill(ctx, hunter_name: str, guild: str, bounty: int = 3000):
            """Add a kill to the leaderboard (Admin only)"""
            # Check if user has admin permissions
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ You need administrator permissions to use this command")
                return
            
            try:
                success = self.manager.add_kill(hunter_name, guild, bounty)
                if success:
                    await ctx.send(f"✅ Added kill for {hunter_name} ({guild}) - {bounty} bounty")
                else:
                    await ctx.send("❌ Failed to add kill")
            except Exception as e:
                self.logger.error(f"Error adding kill: {e}")
                await ctx.send("❌ Error adding kill")
        
        @self.command(name='season')
        async def show_season_info(ctx):
            """Show current season information"""
            try:
                current_data = self.manager.load_current_season()
                embed = self.create_season_info_embed(current_data)
                await ctx.send(embed=embed)
            except Exception as e:
                self.logger.error(f"Error showing season info: {e}")
                await ctx.send("❌ Error loading season info")
    
    def create_leaderboard_embed(self, data: Dict) -> discord.Embed:
        """Create leaderboard embed"""
        embed = discord.Embed(
            title=f"🏆 Bounty Hunter Leaderboard - Season {data['season']}",
            description="Top Jedi hunters this season",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        
        # Add season info
        embed.add_field(
            name="📅 Season Info",
            value=f"**Start:** {data['start_date']}\n**End:** {data['end_date']}\n**Status:** {data['status'].title()}",
            inline=False
        )
        
        # Add top 5 hunters
        entries = data.get('entries', [])[:5]
        if entries:
            leaderboard_text = ""
            for i, entry in enumerate(entries):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                leaderboard_text += f"{medal} **{entry['name']}** ({entry['guild']}) - {entry['kills']} kills ({entry['total_bounty']:,} bounty)\n"
            
            embed.add_field(name="🏅 Top Hunters", value=leaderboard_text, inline=False)
        else:
            embed.add_field(name="🏅 Top Hunters", value="No hunters yet", inline=False)
        
        # Add season stats
        stats = data.get('season_stats', {})
        if stats:
            embed.add_field(
                name="📊 Season Stats",
                value=f"**Total Kills:** {stats.get('total_kills', 0)}\n**Total Bounty:** {stats.get('total_bounty', 0):,}\n**Active Hunters:** {stats.get('active_hunters', 0)}",
                inline=True
            )
        
        embed.set_footer(text="SWGDB Bounty Hunter Leaderboard")
        return embed
    
    def create_hunter_stats_embed(self, stats: Dict) -> discord.Embed:
        """Create hunter stats embed"""
        embed = discord.Embed(
            title=f"🎯 Hunter Stats - {stats['name']}",
            description="Comprehensive hunting statistics",
            color=0xff6b35,
            timestamp=datetime.datetime.now()
        )
        
        # All-time stats
        all_time = stats['all_time']
        embed.add_field(
            name="📈 All-Time Stats",
            value=f"**Total Kills:** {all_time['total_kills']}\n**Total Bounty:** {all_time['total_bounty']:,}\n**Seasons Played:** {all_time['seasons_played']}\n**Best Rank:** #{all_time['best_rank']} (Season {all_time['best_season']})",
            inline=False
        )
        
        # Current season
        if stats['current_season']:
            current = stats['current_season']
            embed.add_field(
                name="🎯 Current Season",
                value=f"**Rank:** #{current['rank']}\n**Kills:** {current['kills']}\n**Bounty:** {current['total_bounty']:,}\n**Guild:** {current['guild']}",
                inline=True
            )
        
        # Season history
        if stats['season_history']:
            history_text = ""
            for season in stats['season_history'][:5]:  # Show last 5 seasons
                history_text += f"**S{season['season']}:** #{season['rank']} ({season['kills']} kills)\n"
            
            embed.add_field(name="📚 Season History", value=history_text, inline=True)
        
        embed.set_footer(text="SWGDB Bounty Hunter Stats")
        return embed
    
    def create_season_stats_embed(self, data: Dict) -> discord.Embed:
        """Create season stats embed"""
        embed = discord.Embed(
            title=f"📊 Season {data['season']} Statistics",
            description="Current season overview",
            color=0x4ecdc4,
            timestamp=datetime.datetime.now()
        )
        
        stats = data.get('season_stats', {})
        embed.add_field(
            name="📈 Overall Stats",
            value=f"**Total Kills:** {stats.get('total_kills', 0)}\n**Total Bounty:** {stats.get('total_bounty', 0):,}\n**Active Hunters:** {stats.get('active_hunters', 0)}\n**Average Kills:** {stats.get('average_kills', 0)}",
            inline=False
        )
        
        if stats.get('top_guild'):
            embed.add_field(
                name="🏆 Top Guild",
                value=f"**{stats['top_guild']}**",
                inline=True
            )
        
        if stats.get('most_active_day'):
            embed.add_field(
                name="📅 Most Active Day",
                value=f"**{stats['most_active_day']}**",
                inline=True
            )
        
        embed.set_footer(text="SWGDB Season Statistics")
        return embed
    
    def create_season_info_embed(self, data: Dict) -> discord.Embed:
        """Create season info embed"""
        embed = discord.Embed(
            title=f"📅 Season {data['season']} Information",
            description="Current season details",
            color=0x9b59b6,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📅 Season Dates",
            value=f"**Start:** {data['start_date']}\n**End:** {data['end_date']}\n**Status:** {data['status'].title()}",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Settings",
            value=f"**Auto Reset:** {'Yes' if data.get('settings', {}).get('auto_reset', True) else 'No'}\n**Discord Alerts:** {'Yes' if data.get('settings', {}).get('discord_alerts', True) else 'No'}",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Last Updated",
            value=f"**{data.get('last_updated', 'Unknown')}**",
            inline=True
        )
        
        embed.set_footer(text="SWGDB Season Information")
        return embed
    
    async def send_season_reset_notification(self, archived_data: Dict) -> None:
        """Send season reset notification to Discord channel"""
        try:
            channel = self.get_channel(self.channel_id)
            if not channel:
                self.logger.error(f"Could not find channel with ID {self.channel_id}")
                return
            
            embed = discord.Embed(
                title="🏆 New BH Season Started: Top Jedi Killers Wanted!",
                description="A new bounty hunting season has begun!",
                color=0xffd700,
                timestamp=datetime.datetime.now()
            )
            
            # Add winner information
            winner = archived_data.get('winner', {})
            if winner:
                embed.add_field(
                    name="🏅 Previous Season Winner",
                    value=f"**{winner['name']}** ({winner['guild']})\n**Kills:** {winner['kills']}\n**Bounty:** {winner['total_bounty']:,}",
                    inline=False
                )
            
            # Add new season info
            new_season_num = archived_data['season'] + 1
            embed.add_field(
                name="🎯 New Season",
                value=f"**Season {new_season_num}** is now active!\nStart hunting Jedi to claim the top spot!",
                inline=False
            )
            
            embed.set_footer(text="SWGDB Bounty Hunter Leaderboard")
            
            await channel.send(embed=embed)
            self.logger.info(f"Sent season reset notification to Discord")
            
        except Exception as e:
            self.logger.error(f"Error sending Discord notification: {e}")
    
    async def send_kill_notification(self, hunter_name: str, guild: str, bounty: int) -> None:
        """Send kill notification to Discord channel"""
        try:
            channel = self.get_channel(self.channel_id)
            if not channel:
                return
            
            embed = discord.Embed(
                title="🎯 New Bounty Claimed!",
                description=f"**{hunter_name}** has claimed another Jedi bounty!",
                color=0xff4444,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(
                name="🏆 Hunter Info",
                value=f"**Name:** {hunter_name}\n**Guild:** {guild}\n**Bounty:** {bounty:,}",
                inline=False
            )
            
            embed.set_footer(text="SWGDB Bounty Hunter Leaderboard")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error sending kill notification: {e}")
    
    async def setup_hook(self):
        """Setup hook for bot initialization"""
        self.logger.info("Bounty Hunter Leaderboard Bot is starting...")
    
    async def on_ready(self):
        """Called when bot is ready"""
        self.logger.info(f"Bot is ready! Logged in as {self.user}")
        
        # Check for season reset
        if self.manager.check_season_reset():
            current_data = self.manager.load_current_season()
            # Get the archived data from the previous season
            archived_seasons = self.manager.get_season_history()
            if archived_seasons:
                await self.send_season_reset_notification(archived_seasons[0])

def main():
    """Main function to run the bot"""
    # Configuration - these would come from environment variables in production
    TOKEN = "your-discord-bot-token-here"
    CHANNEL_ID = 123456789  # Replace with actual channel ID
    
    bot = BHLeaderboardBot(TOKEN, CHANNEL_ID)
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error running bot: {e}")

if __name__ == "__main__":
    main() 