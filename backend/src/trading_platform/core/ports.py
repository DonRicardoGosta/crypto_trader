"""Port interfaces — strategies depend only on these."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from trading_platform.core.models import (
    Balance,
    Kline,
    OrderIntent,
    OrderResult,
    PositionLeg,
    Ticker,
)


class ClockPort(ABC):
    @abstractmethod
    def now(self) -> datetime:
        """Current time (wall clock or simulated)."""


class MarketDataPort(ABC):
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Ticker:
        ...

    @abstractmethod
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
        start_ts: datetime | None = None,
        end_ts: datetime | None = None,
    ) -> list[Kline]:
        ...

    @abstractmethod
    def stream_tickers(self, symbols: list[str]) -> AsyncGenerator[Ticker, None]:
        ...


class ExecutionPort(ABC):
    @abstractmethod
    async def place_order(self, intent: OrderIntent) -> OrderResult:
        ...

    @abstractmethod
    async def cancel_order(self, symbol: str, exchange_order_id: str) -> bool:
        ...

    @abstractmethod
    async def get_positions(self) -> list[PositionLeg]:
        ...

    @abstractmethod
    async def get_balances(self) -> list[Balance]:
        ...

    @abstractmethod
    async def get_open_orders(self, symbol: str | None = None) -> list[OrderResult]:
        ...


class EventEmitter(ABC):
    """Fire-and-forget events — never blocks on DB."""

    @abstractmethod
    async def emit(self, topic: str, event_type: str, payload: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def emit_error(
        self,
        source: str,
        message: str,
        severity: str = "error",
        details: dict[str, Any] | None = None,
    ) -> None:
        ...
