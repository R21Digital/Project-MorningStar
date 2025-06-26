from discord.ext import commands
import json
import discord_relay


def load_config(path: str = "config/discord_config.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    config = load_config()
    bot = commands.Bot(command_prefix="!")
    discord_relay.setup(bot, config)
    bot.run(config["discord_token"])


if __name__ == "__main__":
    main()

