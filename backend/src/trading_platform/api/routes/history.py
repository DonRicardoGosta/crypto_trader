from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trading_platform.adapters.persistence.models import ErrorRow, EventRow, OrderRow
from trading_platform.api.deps import get_session

router = APIRouter()


@router.get("/orders")
async def list_orders(
    limit: int = Query(100, le=500),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(OrderRow).order_by(OrderRow.created_at.desc()).limit(limit))
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "symbol": r.symbol,
            "side": r.side,
            "status": r.status,
            "quantity": float(r.quantity),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/events")
async def list_events(limit: int = 100, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(EventRow).order_by(EventRow.ts.desc()).limit(limit))
    return [
        {"event_type": r.event_type, "payload": r.payload, "ts": r.ts.isoformat()}
        for r in result.scalars().all()
    ]


@router.get("/errors")
async def list_errors(limit: int = 100, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ErrorRow).order_by(ErrorRow.ts.desc()).limit(limit))
    return [
        {"source": r.source, "severity": r.severity, "message": r.message, "ts": r.ts.isoformat()}
        for r in result.scalars().all()
    ]
