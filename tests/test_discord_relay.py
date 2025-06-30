import os
import sys
import os
import sys
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import types
import pytest

# Provide a stub for the discord module if it's missing
if "discord" not in sys.modules:
    discord_mod = types.ModuleType("discord")
    discord_mod.Message = object
    discord_mod.HTTPException = Exception
    discord_mod.DMChannel = object
    sys.modules["discord"] = discord_mod

    ext_mod = types.ModuleType("discord.ext")

    class DummyCog:
        @staticmethod
        def listener(*a, **k):
            def decorator(func):
                return func
            return decorator

    class DummyBot:
        pass

    commands_mod = types.ModuleType("discord.ext.commands")
    commands_mod.Cog = DummyCog
    commands_mod.Bot = DummyBot
    commands_mod.listener = DummyCog.listener

    ext_mod.commands = commands_mod
    sys.modules["discord.ext"] = ext_mod
    sys.modules["discord.ext.commands"] = commands_mod

import discord_relay

from discord_relay import generate_ai_reply, DiscordRelay


def test_generate_ai_reply_basic():
    result = generate_ai_reply('Alice', 'hello there')
    assert result == '[AI Reply] Hello Alice, I heard: hello there'


def test_relay_notify_mode():
    bot = MagicMock()
    bot.fetch_user = AsyncMock(return_value=MagicMock())
    config = {'relay_mode': 'notify', 'target_user_id': 1}
    relay = DiscordRelay(bot, config)
    relay.safe_send_user = AsyncMock()

    result = asyncio.run(relay.relay_to_discord('Bob', 'hi'))

    relay.safe_send_user.assert_awaited_once()
    assert 'Whisper from Bob' in relay.safe_send_user.call_args.args[0]
    assert result is None


def test_relay_auto_mode_generates_reply():
    bot = MagicMock()
    bot.fetch_user = AsyncMock(return_value=MagicMock())
    config = {'relay_mode': 'auto', 'target_user_id': 1}
    relay = DiscordRelay(bot, config)
    relay.safe_send_user = AsyncMock()

    with patch('discord_relay.generate_ai_reply', return_value='ACK') as gen_mock:
        result = asyncio.run(relay.relay_to_discord('Bob', 'hi'))

    gen_mock.assert_called_once_with('Bob', 'hi')
    relay.safe_send_user.assert_awaited_once()
    assert 'ACK' in relay.safe_send_user.call_args.args[0]
    assert result == 'ACK'


def test_relay_fetch_user_error():
    bot = MagicMock()
    bot.fetch_user = AsyncMock(side_effect=Exception('fail'))
    config = {'relay_mode': 'notify', 'target_user_id': 1}
    relay = DiscordRelay(bot, config)
    relay.safe_send_user = AsyncMock()

    result = asyncio.run(relay.relay_to_discord('Bob', 'hi'))

    relay.safe_send_user.assert_not_called()
    assert result is None


def test_on_message_extracts_manual_reply(monkeypatch):
    bot = MagicMock()
    config = {"relay_mode": "manual", "target_user_id": 99}
    relay = DiscordRelay(bot, config)

    class DummyDM:
        pass

    msg = MagicMock()
    msg.channel = DummyDM()
    msg.author.id = 99
    msg.content = "@bob hi there"

    monkeypatch.setattr(discord_relay.discord, "DMChannel", DummyDM, raising=False)

    asyncio.run(relay.on_message(msg))

    assert relay.config["reply_queue"] == [("bob", "hi there")]


def test_init_requires_user_id():
    bot = MagicMock()
    config = {"relay_mode": "notify"}
    with pytest.raises(ValueError):
        DiscordRelay(bot, config)
