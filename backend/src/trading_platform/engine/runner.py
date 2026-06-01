"""Strategy runner — unified path for all modes."""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal

from trading_platform.adapters.bitunix.market_data import BitunixMarketData
from trading_platform.adapters.bitunix.rest import BitunixRestClient
from trading_platform.adapters.execution.backtest import (
    BacktestClock,
    BacktestExecution,
    BacktestMarketData,
)
from trading_platform.adapters.execution.dry_run import BitunixDryRunExecution
from trading_platform.adapters.execution.live import BitunixLiveExecution
from trading_platform.core.clock import WallClock
from trading_platform.core.enums import ExecutionMode
from trading_platform.core.ledger import SimulatedLedger, SlippageModel
from trading_platform.core.models import BacktestParams, StrategyConfig
from trading_platform.core.ports import EventEmitter
from trading_platform.engine.config_cache import ConfigCache
from trading_platform.risk.engine import RiskEngine
from trading_platform.strategies.base import Strategy
from trading_platform.strategies.registry import get_strategy_class

logger = logging.getLogger(__name__)


class StrategyRunner:
    def __init__(
        self,
        config_cache: ConfigCache,
        emitter: EventEmitter,
        api_key: str = "",
        secret_key: str = "",
    ) -> None:
        self._cache = config_cache
        self._emitter = emitter
        self._api_key = api_key
        self._secret_key = secret_key
        self._tasks: list[asyncio.Task] = []
        self._stop = asyncio.Event()

    async def start(self) -> None:
        await self._cache.start()
        for cfg in self._cache.get_enabled():
            self._tasks.append(asyncio.create_task(self._run_strategy(cfg)))

    async def stop(self) -> None:
        self._stop.set()
        for t in self._tasks:
            t.cancel()

    def _build_components(self, cfg: StrategyConfig):
        clock = WallClock()
        ledger = SimulatedLedger(initial_balance_usd=cfg.risk.max_capital_usd)
        risk = RiskEngine(cfg.risk, ledger)
        client = BitunixRestClient(self._api_key, self._secret_key, self._emitter)
        market = BitunixMarketData(client)

        if cfg.mode == ExecutionMode.LIVE:
            execution = BitunixLiveExecution(
                client, self._emitter, str(cfg.id), ledger
            )
        elif cfg.mode == ExecutionMode.DRY_RUN:
            execution = BitunixDryRunExecution(
                market, clock, ledger, self._emitter, str(cfg.id)
            )
        else:
            execution = BitunixDryRunExecution(
                market, clock, ledger, self._emitter, str(cfg.id)
            )
        return market, execution, risk, clock, client

    async def _run_strategy(self, cfg: StrategyConfig) -> None:
        market, execution, risk, clock, client = self._build_components(cfg)
        cls = get_strategy_class(cfg.strategy_type)
        strategy: Strategy = cls(cfg, market, execution, risk, clock)
        interval = float(cfg.parameters.get("tick_interval_seconds", 5))
        try:
            while not self._stop.is_set():
                symbols = cfg.parameters.get("symbols") or ["BTCUSDT"]
                tickers = {}
                for sym in symbols:
                    tickers[sym] = await market.get_ticker(sym)
                await strategy.on_tick(tickers)
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass
        finally:
            await client.close()

    async def run_backtest(
        self, cfg: StrategyConfig, params: BacktestParams
    ) -> dict:
        clock = BacktestClock()
        slippage = SlippageModel(bps=Decimal(str(params.slippage_bps)))
        ledger = SimulatedLedger(initial_balance_usd=cfg.risk.max_capital_usd)
        risk = RiskEngine(cfg.risk, ledger)
        client = BitunixRestClient(emitter=self._emitter)
        symbols = params.symbols or list(cfg.parameters.get("symbols", ["BTCUSDT"]))
        klines_map = {}
        for sym in symbols:
            klines_map[sym] = await client.get_klines(sym, "15min", 500)
        market = BacktestMarketData(klines_map, clock)
        execution = BacktestExecution(
            market, clock, ledger, self._emitter, str(cfg.id), slippage
        )
        cls = get_strategy_class(cfg.strategy_type)
        strategy = cls(cfg, market, execution, risk, clock)
        fills_before = len(ledger.legs)
        for sym in symbols:
            klines = klines_map.get(sym, [])
            for i in range(len(klines)):
                clock.set(klines[i].ts)
                market._index[sym] = i
                await strategy.evaluate(sym)
        await client.close()
        return {
            "fills": len(ledger.legs) - fills_before,
            "realized_pnl": float(ledger.realized_pnl),
            "balance_usd": float(ledger.balance_usd),
            "fees": float(ledger.total_fees),
        }
