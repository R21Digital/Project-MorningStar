import discord
from discord.ext import commands
from profession_logic.utils.logger import logger

# Import guild alert system
try:
    from modules.guild_alert_system import GuildAlertSystem
    GUILD_ALERT_AVAILABLE = True
except ImportError:
    GUILD_ALERT_AVAILABLE = False
    GuildAlertSystem = None


def generate_ai_reply(sender: str, message: str) -> str:
    """Return an automated reply using placeholder logic."""
    return f"[AI Reply] Hello {sender}, I heard: {message}"


class DiscordRelay(commands.Cog):
    """Relay in-game whispers to Discord and optionally handle replies."""

    def __init__(self, bot: commands.Bot, config: dict) -> None:
        self.bot = bot
        self.config = config
        self.target_user_id = config.get("target_user_id")
        self.mode = config.get("relay_mode", "notify")

        if not self.target_user_id:
            raise ValueError("target_user_id must be configured for DiscordRelay")

        # Initialize guild alert system if available
        self.guild_alert_system = None
        if GUILD_ALERT_AVAILABLE:
            try:
                self.guild_alert_system = GuildAlertSystem()
                logger.info("[DiscordRelay] Guild alert system initialized")
            except Exception as e:
                logger.error(f"[DiscordRelay] Failed to initialize guild alert system: {e}")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        logger.info("[DiscordRelay] Connected as %s", self.bot.user)

    async def safe_send_user(self, message: str) -> None:
        """Send a DM to the configured user."""
        try:
            user = await self.bot.fetch_user(self.target_user_id)
            await user.send(message)
        except discord.HTTPException as e:
            logger.error("[Error] Failed to send DM: %s", e)

    async def relay_to_discord(self, sender: str, message: str) -> str | None:
        """Send a whisper to Discord based on the active mode."""
        try:
            await self.bot.fetch_user(self.target_user_id)
        except Exception as e:
            logger.error("[Error] Could not fetch user: %s", e)
            return None

        # Check if this is a guild alert first
        guild_alert = None
        if self.guild_alert_system:
            guild_alert = self.guild_alert_system.process_guild_whisper(sender, message)
            
            if guild_alert:
                # Send priority alert for guild messages
                await self._send_guild_priority_alert(guild_alert)
                
                # Return auto-reply if one was generated
                if guild_alert.auto_reply_sent and guild_alert.reply_message:
                    return guild_alert.reply_message

        # Handle regular whisper relay
        if self.mode == "notify":
            prefix = "🚨 **GUILD PRIORITY**" if guild_alert else "📧"
            await self.safe_send_user(
                f"{prefix} **Whisper from {sender}**: {message}"
            )
            return None

        if self.mode == "manual":
            prefix = "🚨 **GUILD PRIORITY**" if guild_alert else "✏️"
            await self.safe_send_user(
                f"{prefix} **Whisper from {sender}**: {message}\n"
                f"_Reply with_ `@{sender} your message`"
            )
            return None

        if self.mode == "auto":
            reply = generate_ai_reply(sender, message)
            prefix = "🚨 **GUILD PRIORITY**" if guild_alert else "🤖"
            await self.safe_send_user(
                f"{prefix} **{sender}:** {message}\n**Bot Replied:** {reply}"
            )
            return reply

        return None

    async def _send_guild_priority_alert(self, guild_alert):
        """Send a priority Discord alert for guild messages."""
        try:
            # Create priority embed
            embed = discord.Embed(
                title=f"🚨 Guild Alert: {guild_alert.alert_type.replace('_', ' ').title()}",
                description=f"**{guild_alert.sender}**: {guild_alert.message}",
                color=self._get_priority_color(guild_alert.priority),
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(name="Priority", value=guild_alert.priority.upper(), inline=True)
            embed.add_field(name="Type", value=guild_alert.alert_type.replace('_', ' ').title(), inline=True)
            
            if guild_alert.auto_reply_sent and guild_alert.reply_message:
                embed.add_field(name="Auto-Reply", value=guild_alert.reply_message, inline=False)
            
            # Send to target user
            user = await self.bot.fetch_user(self.target_user_id)
            await user.send(embed=embed)
            
            logger.info(f"[GUILD_ALERT] Priority alert sent for {guild_alert.sender}")
            
        except Exception as e:
            logger.error(f"[GUILD_ALERT] Failed to send priority alert: {e}")

    def _get_priority_color(self, priority: str) -> discord.Color:
        """Get Discord color based on priority level."""
        colors = {
            "high": discord.Color.red(),
            "medium": discord.Color.orange(),
            "low": discord.Color.blue()
        }
        return colors.get(priority, discord.Color.blue())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if (
            self.mode == "manual"
            and isinstance(message.channel, discord.DMChannel)
            and message.author.id == self.target_user_id
            and message.content.startswith("@")
        ):
            parts = message.content[1:].split(" ", 1)
            if len(parts) == 2:
                target, reply = parts
                self.config.setdefault("reply_queue", []).append((target, reply))

    def get_guild_analytics(self):
        """Get guild alert analytics for session tracking."""
        if self.guild_alert_system:
            return self.guild_alert_system.get_session_analytics()
        return {}


def setup(bot: commands.Bot, config: dict) -> None:
    bot.add_cog(DiscordRelay(bot, config))

