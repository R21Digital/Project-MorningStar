import asyncio
import discord
from discord.ext import commands


def generate_ai_reply(sender: str, message: str) -> str:
    """Return an automated reply using placeholder logic."""
    return f"[AI Reply] Hello {sender}, I heard: {message}"


class DiscordRelay(commands.Cog):
    """Relay in-game whispers to Discord and optionally handle replies."""

    def __init__(self, bot: commands.Bot, config: dict) -> None:
        self.bot = bot
        self.config = config
        self.channel_id = config.get("relay_channel_id")
        self.user_id = config.get("relay_user_id")
        self.mode = config.get("relay_mode", "notify")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"[DiscordRelay] Connected as {self.bot.user}")

    async def safe_send_user(self, message: str) -> None:
        """Send a DM to the configured user with fallback to the relay channel."""
        try:
            user = await self.bot.fetch_user(self.user_id)
            await user.send(message)
        except discord.Forbidden:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                await channel.send(
                    f"\u274c Couldn't DM {user.name}. Here's the message:\n{message}"
                )
        except discord.HTTPException as e:
            print(f"[Error] Failed to send DM: {e}")

    async def relay_to_discord(self, sender: str, message: str) -> str | None:
        """Send a whisper to Discord based on the active mode."""
        try:
            user = await self.bot.fetch_user(self.user_id)
        except Exception as e:
            print(f"[Error] Could not fetch user: {e}")
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
            and message.author.id == self.user_id
            and message.content.startswith("@")
        ):
            parts = message.content[1:].split(" ", 1)
            if len(parts) == 2:
                target, reply = parts
                self.config.setdefault("reply_queue", []).append((target, reply))


def setup(bot: commands.Bot, config: dict) -> None:
    bot.add_cog(DiscordRelay(bot, config))

