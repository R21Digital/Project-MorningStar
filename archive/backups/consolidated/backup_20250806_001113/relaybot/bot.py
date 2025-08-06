"""Entry point for launching the Discord relay bot."""

import json
import os
from discord.ext import commands

import discord_relay


def load_config(path: str = "config/discord_config.json") -> dict:
    """Load Discord bot configuration from ``path``.
    
    Security: Tokens should be loaded from environment variables, not hardcoded files.
    """
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    # Security: Always prefer environment variables for tokens
    env_token = os.getenv("DISCORD_TOKEN")
    if env_token:
        cfg["discord_token"] = env_token
    elif cfg.get("discord_token") == "${DISCORD_TOKEN}":
        raise ValueError("DISCORD_TOKEN environment variable not set. Please set it for security.")
    elif not cfg.get("discord_token"):
        raise ValueError("No Discord token found in config or environment variables.")
    
    return cfg


def start_bot() -> None:
    """Launch the Discord relay bot using the shared config."""
    try:
        config = load_config()
        bot = commands.Bot(command_prefix="!")
        discord_relay.setup(bot, config)
        bot.run(config["discord_token"])
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set the DISCORD_TOKEN environment variable for security.")
        return
    except Exception as e:
        print(f"Failed to start Discord bot: {e}")
        return


if __name__ == "__main__":
    start_bot()
