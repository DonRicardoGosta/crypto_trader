from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from trading_platform.adapters.persistence.kafka_emitter import InMemoryEventEmitter
from trading_platform.core.enums import ExecutionMode
from trading_platform.core.models import BacktestParams, Kline, StrategyConfig, StrategyRiskConfig
from trading_platform.engine.config_cache import ConfigCache
from trading_platform.engine.runner import StrategyRunner


def _synthetic_klines(count=50):
    klines, price = [], Decimal("100")
    for i in range(count):
        price += Decimal("0.5") if i % 3 else Decimal("-0.3")
        klines.append(Kline("TESTUSDT", price, price+1, price-1, price, Decimal("1000"), datetime(2024,1,1,i%24,0,tzinfo=UTC)))
    return klines

@pytest.mark.asyncio
async def test_backtest_deterministic(monkeypatch):
    cfg = StrategyConfig(
        id=uuid4(), name="test", strategy_type="adaptive_ladder", mode=ExecutionMode.BACKTEST,
        enabled=True, parameters={"symbols": ["TESTUSDT"], "max_ladder_steps": 2},
        risk=StrategyRiskConfig(Decimal("500"), Decimal("1"), 2, 5),
    )
    runner = StrategyRunner(ConfigCache(), InMemoryEventEmitter())
    from trading_platform.adapters.bitunix import rest as rest_mod
    async def mock_klines(self, sym, interval="15min", limit=100):
        return _synthetic_klines()
    monkeypatch.setattr(rest_mod.BitunixRestClient, "get_klines", mock_klines)
    params = BacktestParams(cfg.id, datetime(2024,1,1,tzinfo=UTC), datetime(2024,1,2,tzinfo=UTC), ["TESTUSDT"])
    r1 = await runner.run_backtest(cfg, params)
    r2 = await runner.run_backtest(cfg, params)
    assert r1["fills"] == r2["fills"]
