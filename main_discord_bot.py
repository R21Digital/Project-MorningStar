"""Simple entry point for running the Discord relay bot."""

import json
from discord.ext import commands

from discord_relay import DiscordRelay
from profession_logic.utils.logger import logger


def main() -> None:
    """Load configuration and launch the bot."""
    with open("config/discord_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    bot = commands.Bot(command_prefix="!")
    bot.add_cog(DiscordRelay(bot, config))

    @bot.event
    async def on_ready() -> None:
        logger.info("[Bot] Logged in as %s", bot.user)

    bot.run(config["discord_token"])


if __name__ == "__main__":
    main()

