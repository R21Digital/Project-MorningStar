import asyncio
import json
import threading
from queue import Queue

try:
    import discord  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    discord = None


class DiscordRelayBot(threading.Thread):
    """Relay whispers to a Discord channel and handle replies."""

    def __init__(self, message_queue: Queue, settings_path: str = "config/discord_settings.json"):
        super().__init__(daemon=True)
        self.queue = message_queue
        self.settings_path = settings_path
        self.token = ""
        self.channel_id = 0
        self.mode = "notify"
        self.client = None
        self.loop: asyncio.AbstractEventLoop | None = None

    def load_settings(self) -> None:
        if not discord:
            print("[DISCORD] discord.py not available")
            return
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.token = data.get("bot_token", "")
            self.channel_id = int(data.get("channel_id", 0))
            self.mode = data.get("mode", "notify")
        except FileNotFoundError:
            print(f"[DISCORD] Settings file not found: {self.settings_path}")

    def run(self) -> None:  # pragma: no cover - thread/async behavior
        if not discord:
            return
        self.load_settings()
        intents = discord.Intents.default()
        intents.messages = True
        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            print("[DISCORD] Relay bot connected.")

        @self.client.event
        async def on_message(message: discord.Message):
            if message.author == self.client.user:
                return
            if message.channel.id != self.channel_id:
                return
            if self.mode == "manual":
                self.queue.put(message.content)
            elif self.mode == "auto":
                await message.channel.send(message.content)

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.client.start(self.token))
        self.loop.create_task(self._dispatch_queue())
        self.loop.run_forever()

    async def _dispatch_queue(self) -> None:
        if not self.client:
            return
        channel = None
        while True:
            if channel is None:
                channel = self.client.get_channel(self.channel_id)
            text = await asyncio.get_event_loop().run_in_executor(None, self.queue.get)
            if channel:
                await channel.send(text)

    def send_notification(self, text: str) -> None:
        if not discord or not self.loop or not self.client:
            print(f"[DISCORD] {text}")
            return
        channel = self.client.get_channel(self.channel_id)
        if channel:
            asyncio.run_coroutine_threadsafe(channel.send(text), self.loop)

