"""Compatibility wrapper for launching the Discord relay bot."""

from discord.bot import start_bot


def main() -> None:
    """Launch the Discord relay bot using the shared entry point."""
    start_bot()


if __name__ == "__main__":
    main()

