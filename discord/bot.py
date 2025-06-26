"""Entry point for launching the Discord relay bot."""

import json
from discord.ext import commands

import discord_relay


def load_config(path: str = "config/discord_config.json") -> dict:
    """Load Discord bot configuration from ``path``."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def start_bot() -> None:
    """Launch the Discord relay bot using the shared config."""
    config = load_config()
    bot = commands.Bot(command_prefix="!")
    discord_relay.setup(bot, config)
    bot.run(config["discord_token"])


if __name__ == "__main__":
    start_bot()
