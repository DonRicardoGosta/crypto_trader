"""Bitunix WebSocket client (public + private) with reconnect."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

from trading_platform.adapters.bitunix.signing import generate_nonce, sign_ws_params
from trading_platform.core.ports import EventEmitter

logger = logging.getLogger(__name__)

PUBLIC_WS = "wss://fapi.bitunix.com/public/"
PRIVATE_WS = "wss://fapi.bitunix.com/private/"


class BitunixWebSocketClient:
    def __init__(
        self,
        emitter: EventEmitter | None = None,
        api_key: str = "",
        secret_key: str = "",
    ) -> None:
        self._emitter = emitter
        self._api_key = api_key
        self._secret_key = secret_key
        self._ws: ClientConnection | None = None
        self._backoff = 1.0

    async def connect_public(self) -> None:
        self._ws = await websockets.connect(PUBLIC_WS)
        self._backoff = 1.0
        logger.info("Connected to Bitunix public WS")

    async def connect_private(self) -> None:
        self._ws = await websockets.connect(PRIVATE_WS)
        await self._login_private()
        self._backoff = 1.0

    async def _login_private(self) -> None:
        if not self._ws or not self._api_key:
            return
        import time

        params = sign_ws_params(
            self._api_key,
            self._secret_key,
            {"apiKey": self._api_key, "timestamp": str(int(time.time() * 1000)), "nonce": generate_nonce()},
        )
        msg = {"op": "login", "args": [params]}
        await self._ws.send(json.dumps(msg))

    async def subscribe(self, channel: str, symbol: str) -> None:
        if not self._ws:
            raise RuntimeError("WebSocket not connected")
        await self._ws.send(
            json.dumps({"op": "subscribe", "args": [{"ch": channel, "symbol": symbol}]})
        )

    async def stream_messages(self) -> AsyncIterator[dict[str, Any]]:
        while True:
            try:
                if not self._ws:
                    await self.connect_public()
                assert self._ws is not None
                raw = await self._ws.recv()
                data = json.loads(raw)
                yield data
            except Exception as e:
                logger.warning("WS error, reconnecting: %s", e)
                if self._emitter:
                    await self._emitter.emit_error("bitunix.ws", str(e))
                await asyncio.sleep(self._backoff)
                self._backoff = min(self._backoff * 2, 60)
                self._ws = None

    async def close(self) -> None:
        if self._ws:
            await self._ws.close()
            self._ws = None
