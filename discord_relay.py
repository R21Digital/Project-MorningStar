import discord
from discord.ext import commands
from utils.logger import logger


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

        if self.mode == "notify":
            await self.safe_send_user(
                f"\U0001F4E9 **Whisper from {sender}**: {message}"
            )
            return None

        if self.mode == "manual":
            await self.safe_send_user(
                f"\u270F\ufe0f **Whisper from {sender}**: {message}\n"
                f"_Reply with_ `@{sender} your message`"
            )
            return None

        if self.mode == "auto":
            reply = generate_ai_reply(sender, message)
            await self.safe_send_user(
                f"\U0001F916 **{sender}:** {message}\n**Bot Replied:** {reply}"
            )
            return reply

        return None

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


def setup(bot: commands.Bot, config: dict) -> None:
    bot.add_cog(DiscordRelay(bot, config))

