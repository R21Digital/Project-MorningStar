"""Standalone DM-ready Discord relay bot launcher."""

import json
import os

import discord
from discord.ext import commands

import discord_relay


CONFIG_PATH = "config/discord_config.json"


def load_config(path: str = CONFIG_PATH) -> dict:
    """Load Discord configuration from ``path`` and env vars."""
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if not cfg.get("discord_token"):
        env_token = os.getenv("DISCORD_TOKEN")
        if env_token:
            cfg["discord_token"] = env_token
    return cfg


def main() -> None:
    """Create the bot with DM intents and run it."""
    config = load_config()
    intents = discord.Intents.default()
    intents.dm_messages = True
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    discord_relay.setup(bot, config)
    bot.run(config["discord_token"])


if __name__ == "__main__":
    main()
