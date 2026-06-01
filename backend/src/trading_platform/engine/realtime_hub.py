"""Broadcast hub for realtime WebSocket clients."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import WebSocket


class RealtimeHub:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._clients.add(ws)

    async def register_client(self, ws: WebSocket) -> None:
        """Register without accept (for tests)."""
        async with self._lock:
            self._clients.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def broadcast(self, event_type: str, payload: dict[str, Any]) -> None:
        msg = json.dumps({"type": event_type, "payload": payload}, default=str)
        dead: list[WebSocket] = []
        async with self._lock:
            clients = list(self._clients)
        for ws in clients:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)


hub = RealtimeHub()
