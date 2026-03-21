"""
WebSocket client for real-time game communication.
"""
import asyncio
import json
import websockets
from typing import Callable, Awaitable
from app.utils.constants import WS_BASE_URL

EventHandler = Callable[[str, dict], Awaitable[None]]


class GameWebSocketClient:
    def __init__(self, session_id: str, token: str, on_event: EventHandler):
        self._session_id = session_id
        self._token = token
        self._on_event = on_event
        self._ws = None
        self._running = False

    @property
    def ws_url(self) -> str:
        return f"{WS_BASE_URL}/ws/session/{self._session_id}?token={self._token}"

    async def connect(self):
        self._running = True
        async with websockets.connect(self.ws_url) as ws:
            self._ws = ws
            async for raw in ws:
                if not self._running:
                    break
                try:
                    msg = json.loads(raw)
                    await self._on_event(msg["event"], msg.get("payload", {}))
                except Exception as e:
                    await self._on_event("error", {"detail": str(e)})

    async def disconnect(self):
        self._running = False
        if self._ws:
            await self._ws.close()

    async def throw_dart(self, target_user_id: str, dart_type: str = "default"):
        await self._send("throw_dart", {"target_user_id": target_user_id, "dart_type": dart_type})

    async def catch_dart(self, region: str):
        """region: 'inner' | 'middle' | 'outer'"""
        await self._send("catch_dart", {"region": region})

    async def _send(self, event: str, payload: dict):
        if self._ws:
            await self._ws.send(json.dumps({"event": event, "payload": payload}))
