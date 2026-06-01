"""Backtest execution with historical kline replay."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from trading_platform.adapters.execution.simulated import SimulatedExecutionBase
from trading_platform.core.models import Kline, Ticker
from trading_platform.core.ports import ClockPort, ExecutionPort, MarketDataPort


class BacktestMarketData(MarketDataPort):
    def __init__(self, klines_by_symbol: dict[str, list[Kline]], clock: ClockPort) -> None:
        self._klines = klines_by_symbol
        self._clock = clock
        self._index: dict[str, int] = {s: 0 for s in klines_by_symbol}

    def _current_kline(self, symbol: str) -> Kline | None:
        klines = self._klines.get(symbol, [])
        idx = self._index.get(symbol, 0)
        if idx < len(klines):
            return klines[idx]
        return None

    async def get_ticker(self, symbol: str) -> Ticker:
        k = self._current_kline(symbol)
        if not k:
            return Ticker(symbol=symbol, last_price=Decimal("0"))
        return Ticker(symbol=symbol, last_price=k.close, ts=k.ts)

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
        start_ts: datetime | None = None,
        end_ts: datetime | None = None,
    ) -> list[Kline]:
        klines = self._klines.get(symbol, [])
        idx = self._index.get(symbol, 0)
        return klines[max(0, idx - limit + 1) : idx + 1]

    async def stream_tickers(self, symbols: list[str]):
        raise NotImplementedError("Use BacktestRunner.advance() instead")

    def advance(self, symbol: str) -> bool:
        klines = self._klines.get(symbol, [])
        idx = self._index.get(symbol, 0)
        if idx + 1 >= len(klines):
            return False
        self._index[symbol] = idx + 1
        return True


class BacktestClock(ClockPort):
    def __init__(self) -> None:
        self._now = datetime.now()

    def set(self, ts: datetime) -> None:
        self._now = ts

    def now(self) -> datetime:
        return self._now


class BacktestExecution(SimulatedExecutionBase, ExecutionPort):
    pass
