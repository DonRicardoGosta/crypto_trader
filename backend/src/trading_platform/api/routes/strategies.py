from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trading_platform.adapters.persistence.models import StrategyRiskRow, StrategyRow
from trading_platform.api.deps import get_session
from trading_platform.api.schemas import StrategyCreate, StrategyOut, StrategyUpdate

router = APIRouter()


@router.get("", response_model=list[StrategyOut])
async def list_strategies(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(StrategyRow))
    rows = result.scalars().all()
    return [
        StrategyOut(
            id=r.id,
            name=r.name,
            strategy_type=r.strategy_type,
            mode=r.mode,
            enabled=r.enabled,
            parameters=r.parameters or {},
        )
        for r in rows
    ]


@router.post("", response_model=StrategyOut)
async def create_strategy(body: StrategyCreate, session: AsyncSession = Depends(get_session)):
    row = StrategyRow(
        id=uuid.uuid4(),
        name=body.name,
        strategy_type=body.strategy_type,
        mode=body.mode,
        enabled=body.enabled,
        parameters=body.parameters,
    )
    session.add(row)
    session.add(
        StrategyRiskRow(
            strategy_id=row.id,
            max_capital_usd=body.risk.max_capital_usd,
            min_investment_usd=body.risk.min_investment_usd,
            leverage_multiplier=body.risk.leverage_multiplier,
            max_leverage_multiplier=body.risk.max_leverage_multiplier,
        )
    )
    await session.commit()
    from trading_platform.engine.redis_cache import get_notifier
    n = get_notifier()
    await n.connect()
    await n.notify_refresh()
    return StrategyOut(
        id=row.id,
        name=row.name,
        strategy_type=row.strategy_type,
        mode=row.mode,
        enabled=row.enabled,
        parameters=row.parameters or {},
    )


@router.put("/{strategy_id}", response_model=StrategyOut)
async def update_strategy(
    strategy_id: uuid.UUID,
    body: StrategyUpdate,
    session: AsyncSession = Depends(get_session),
):
    row = await session.get(StrategyRow, strategy_id)
    if not row:
        raise HTTPException(404, "Strategy not found")
    if body.name is not None:
        row.name = body.name
    if body.mode is not None:
        row.mode = body.mode
    if body.enabled is not None:
        row.enabled = body.enabled
    if body.parameters is not None:
        row.parameters = body.parameters
    if body.risk is not None:
        risk = await session.get(StrategyRiskRow, strategy_id)
        if risk:
            risk.max_capital_usd = body.risk.max_capital_usd
            risk.min_investment_usd = body.risk.min_investment_usd
            risk.leverage_multiplier = body.risk.leverage_multiplier
            risk.max_leverage_multiplier = body.risk.max_leverage_multiplier
    await session.commit()
    return StrategyOut(
        id=row.id,
        name=row.name,
        strategy_type=row.strategy_type,
        mode=row.mode,
        enabled=row.enabled,
        parameters=row.parameters or {},
    )
