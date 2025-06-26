"""Entry point for launching the Discord relay bot."""

from queue import Queue

from discord_bridge import DiscordRelayBot


def start_bot() -> None:
    """Launch the Discord relay bot using default settings."""
    q = Queue()
    bot = DiscordRelayBot(q)
    bot.start()
    print("Discord relay bot started.")


if __name__ == "__main__":
    start_bot()
