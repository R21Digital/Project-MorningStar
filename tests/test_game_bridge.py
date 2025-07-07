import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


def fake_run_coroutine_threadsafe(coro, loop):
    result = asyncio.run(coro)
    fut = MagicMock()
    fut.result.return_value = result
    return fut


from game_bridge import GameBridge


def _setup_relay():
    relay = MagicMock()
    relay.bot = MagicMock()
    relay.bot.loop = MagicMock()
    relay.relay_to_discord = AsyncMock()
    return relay


def test_on_whisper_forward_no_reply():
    relay = _setup_relay()
    relay.relay_to_discord.return_value = None
    gb = GameBridge(relay)

    with patch("asyncio.run_coroutine_threadsafe", side_effect=fake_run_coroutine_threadsafe) as run_coro:
        gb._send_in_game_whisper = MagicMock()
        gb.on_whisper_received("Alice", "hi")

        relay.relay_to_discord.assert_called_once_with("Alice", "hi")
        run_coro.assert_called_once()
        assert run_coro.call_args.args[1] == relay.bot.loop
        gb._send_in_game_whisper.assert_not_called()


def test_on_whisper_forward_with_reply():
    relay = _setup_relay()
    relay.relay_to_discord.return_value = "pong"
    gb = GameBridge(relay)

    with patch("asyncio.run_coroutine_threadsafe", side_effect=fake_run_coroutine_threadsafe) as run_coro:
        gb._send_in_game_whisper = MagicMock()
        gb.on_whisper_received("Bob", "ping")

        run_coro.assert_called_once()
        assert run_coro.call_args.args[1] == relay.bot.loop
        gb._send_in_game_whisper.assert_called_once_with("Bob", "pong")
