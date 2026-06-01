"""Bitunix market data port."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime

from trading_platform.adapters.bitunix.rest import BitunixRestClient
from trading_platform.core.models import Kline, Ticker
from trading_platform.core.ports import MarketDataPort


class BitunixMarketData(MarketDataPort):
    def __init__(self, client: BitunixRestClient) -> None:
        self._client = client
        self._cache: dict[str, Ticker] = {}

    async def get_ticker(self, symbol: str) -> Ticker:
        ticker = await self._client.get_ticker(symbol)
        self._cache[symbol] = ticker
        return ticker

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
        start_ts: datetime | None = None,
        end_ts: datetime | None = None,
    ) -> list[Kline]:
        return await self._client.get_klines(symbol, interval, limit)

    async def stream_tickers(self, symbols: list[str]) -> AsyncIterator[Ticker]:
        while True:
            for sym in symbols:
                ticker = await self.get_ticker(sym)
                yield ticker
            import asyncio

            await asyncio.sleep(1)
