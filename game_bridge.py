import asyncio
from typing import Any

from profession_logic.utils.logger import logger


class GameBridge:
    """Simple bridge between the game and the Discord relay."""

    def __init__(self, discord_cog: Any) -> None:
        self.discord_cog = discord_cog

    def on_whisper_received(self, sender: str, message: str) -> None:
        """Forward a whisper to Discord and optionally send a reply."""
        if not self.discord_cog:
            return
        coro = self.discord_cog.relay_to_discord(sender, message)
        future = asyncio.run_coroutine_threadsafe(coro, self.discord_cog.bot.loop)
        reply = future.result()
        if reply:
            self._send_in_game_whisper(sender, reply)

    def dispatch_reply_queue(self) -> None:
        """Send all queued replies back to the game."""
        if not self.discord_cog:
            return
        queue = self.discord_cog.config.get("reply_queue", [])
        while queue:
            target, reply = queue.pop(0)
            self._send_in_game_whisper(target, reply)

    def _send_in_game_whisper(self, target: str, text: str) -> None:
        """Placeholder for sending a whisper in-game."""
        logger.info("[GAME] whisper to %s: %s", target, text)


