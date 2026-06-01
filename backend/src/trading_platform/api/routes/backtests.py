from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from trading_platform.adapters.persistence.kafka_emitter import InMemoryEventEmitter
from trading_platform.adapters.persistence.models import (
    BacktestRunRow,
    StrategyRiskRow,
    StrategyRow,
)
from trading_platform.api.deps import get_session
from trading_platform.api.schemas import BacktestRequest
from trading_platform.core.enums import ExecutionMode
from trading_platform.core.models import BacktestParams, StrategyConfig, StrategyRiskConfig
from trading_platform.engine.config_cache import ConfigCache
from trading_platform.engine.runner import StrategyRunner

router = APIRouter()


@router.post("")
async def run_backtest(body: BacktestRequest, session: AsyncSession = Depends(get_session)):
    row = await session.get(StrategyRow, body.strategy_id)
    if not row:
        raise HTTPException(404, "Strategy not found")
    risk = await session.get(StrategyRiskRow, body.strategy_id)
    if not risk:
        raise HTTPException(400, "Risk config missing")
    cfg = StrategyConfig(
        id=row.id,
        name=row.name,
        strategy_type=row.strategy_type,
        mode=ExecutionMode.BACKTEST,
        enabled=True,
        parameters=dict(row.parameters or {}),
        risk=StrategyRiskConfig(
            max_capital_usd=Decimal(str(risk.max_capital_usd)),
            min_investment_usd=Decimal(str(risk.min_investment_usd)),
            leverage_multiplier=risk.leverage_multiplier,
            max_leverage_multiplier=risk.max_leverage_multiplier,
        ),
    )
    run = BacktestRunRow(
        id=uuid.uuid4(),
        strategy_id=body.strategy_id,
        start_ts=body.start_ts,
        end_ts=body.end_ts,
        parameters={"symbols": body.symbols},
        status="running",
    )
    session.add(run)
    await session.commit()

    emitter = InMemoryEventEmitter()
    runner = StrategyRunner(ConfigCache(), emitter)
    params = BacktestParams(
        strategy_id=body.strategy_id,
        start_ts=body.start_ts,
        end_ts=body.end_ts,
        symbols=body.symbols,
        slippage_bps=body.slippage_bps,
    )
    result = await runner.run_backtest(cfg, params)
    run.status = "completed"
    run.result_summary = result
    run.completed_at = datetime.now(UTC)
    await session.commit()
    return {"run_id": str(run.id), "result": result}
