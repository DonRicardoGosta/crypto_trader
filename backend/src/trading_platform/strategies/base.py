"""Strategy base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from trading_platform.core.models import Kline, StrategyConfig, Ticker
from trading_platform.core.ports import ClockPort, ExecutionPort, MarketDataPort
from trading_platform.risk.engine import RiskEngine


class Strategy(ABC):
    def __init__(
        self,
        config: StrategyConfig,
        market: MarketDataPort,
        execution: ExecutionPort,
        risk: RiskEngine,
        clock: ClockPort,
    ) -> None:
        self.config = config
        self.market = market
        self.execution = execution
        self.risk = risk
        self.clock = clock

    @abstractmethod
    async def on_tick(self, tickers: dict[str, Ticker]) -> None:
        """Called each engine loop iteration."""

    @abstractmethod
    async def on_klines(self, symbol: str, klines: list[Kline]) -> None:
        """Called when new kline data available."""

    async def evaluate(self, symbol: str) -> None:
        """Default evaluate delegates to on_tick."""
        ticker = await self.market.get_ticker(symbol)
        await self.on_tick({symbol: ticker})

    def param(self, key: str, default: Any = None) -> Any:
        return self.config.parameters.get(key, default)
